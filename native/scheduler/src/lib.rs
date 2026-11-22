#![forbid(unsafe_code)]
//! Pure planning functions. Recommendations are not leases or provisioning actions.

#[derive(Clone, Copy, Debug)]
pub struct Demand {
    pub arrivals_per_second: f64,
    pub service_seconds: f64,
    pub queued: u32,
    pub busy: u32,
    pub current: u32,
}

#[derive(Clone, Copy, Debug)]
pub struct Policy {
    pub minimum: u32,
    pub maximum: u32,
    pub max_step: u32,
    pub target_utilization: f64,
    pub queue_drain_seconds: f64,
    pub headroom: f64,
}

impl Default for Policy {
    fn default() -> Self {
        Self {
            minimum: 1,
            maximum: 100,
            max_step: 10,
            target_utilization: 0.7,
            queue_drain_seconds: 10.0,
            headroom: 1.2,
        }
    }
}

#[derive(Default, Debug)]
pub struct Forecast {
    rate: Option<f64>,
}

impl Forecast {
    pub fn rate(&self) -> Option<f64> {
        self.rate
    }

    pub fn observe(
        &mut self,
        arrivals: f64,
        seconds: f64,
        alpha: f64,
    ) -> Result<f64, &'static str> {
        if !arrivals.is_finite()
            || arrivals < 0.0
            || !seconds.is_finite()
            || seconds <= 0.0
            || !alpha.is_finite()
            || alpha <= 0.0
            || alpha > 1.0
        {
            return Err("invalid observation");
        }
        let sample = arrivals / seconds;
        if !sample.is_finite() {
            return Err("observation overflow");
        }
        let rate = self
            .rate
            .map_or(sample, |previous| alpha * sample + (1.0 - alpha) * previous);
        self.rate = Some(rate);
        Ok(rate)
    }
}

pub fn desired(d: Demand, p: Policy) -> Result<u32, &'static str> {
    if !d.arrivals_per_second.is_finite()
        || d.arrivals_per_second < 0.0
        || !d.service_seconds.is_finite()
        || d.service_seconds <= 0.0
        || d.busy > d.current
        || p.minimum > p.maximum
        || p.maximum > 1_000_000
        || p.max_step == 0
        || !p.target_utilization.is_finite()
        || p.target_utilization <= 0.0
        || p.target_utilization > 1.0
        || !p.queue_drain_seconds.is_finite()
        || p.queue_drain_seconds <= 0.0
        || !p.headroom.is_finite()
        || p.headroom < 1.0
    {
        return Err("invalid demand or policy");
    }
    let load = (d.arrivals_per_second + f64::from(d.queued) / p.queue_drain_seconds)
        * d.service_seconds
        * p.headroom
        / p.target_utilization;
    let target = if load >= f64::from(p.maximum) {
        p.maximum
    } else {
        load.ceil() as u32
    };
    let target = target.clamp(p.minimum, p.maximum).max(d.busy);
    // Busy allocations survive even when a new policy lowers the capacity ceiling.
    if target > d.current {
        Ok(target.min(d.current.saturating_add(p.max_step)))
    } else {
        Ok(target.max(d.current.saturating_sub(p.max_step)))
    }
}

#[derive(Clone, Copy, Debug)]
pub struct Slot {
    pub id: u32,
    pub cpu_millis: u32,
    pub memory_mib: u32,
    pub ready: bool,
    pub leased: bool,
}

pub fn select(slots: &[Slot], cpu: u32, memory: u32) -> Result<Option<usize>, &'static str> {
    if cpu == 0 || memory == 0 {
        return Err("resource request must be positive");
    }
    let mut best = None;
    let mut waste = u64::MAX;
    for (index, slot) in slots.iter().enumerate() {
        if !slot.ready || slot.leased || slot.cpu_millis < cpu || slot.memory_mib < memory {
            continue;
        }
        let score = u64::from(slot.cpu_millis - cpu) + u64::from(slot.memory_mib - memory);
        if score < waste {
            best = Some(index);
            waste = score;
        }
    }
    Ok(best)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn demand(rate: f64, queued: u32, busy: u32, current: u32) -> Demand {
        Demand {
            arrivals_per_second: rate,
            service_seconds: 1.0,
            queued,
            busy,
            current,
        }
    }

    #[test]
    fn capacity_matches_original_contract() {
        let p = Policy::default();
        for (d, expected) in [
            (demand(0.0, 0, 0, 1), 1),
            (demand(100.0, 100, 0, 1), 11),
            (demand(0.0, 0, 40, 40), 40),
            (demand(0.0, 0, 0, 40), 30),
            (demand(100000.0, 0, 0, 95), 100),
        ] {
            assert_eq!(desired(d, p), Ok(expected));
        }
    }

    #[test]
    fn capacity_properties_across_workloads() {
        let p = Policy::default();
        for current in 0..150 {
            for busy in 0..=current {
                for rate in [0.0, 0.1, 10.0, 10000.0, f64::MAX] {
                    let next = desired(demand(rate, 20, busy, current), p).unwrap();
                    assert!(next >= busy);
                    assert!(next.abs_diff(current) <= p.max_step);
                    if current <= p.maximum {
                        assert!(next <= p.maximum);
                    }
                }
            }
        }
    }

    #[test]
    fn invalid_inputs_are_errors() {
        for rate in [f64::NAN, f64::INFINITY, -1.0] {
            assert!(desired(demand(rate, 0, 0, 1), Policy::default()).is_err());
        }
        assert!(desired(demand(1.0, 0, 2, 1), Policy::default()).is_err());
        for p in [
            Policy {
                max_step: 0,
                ..Policy::default()
            },
            Policy {
                minimum: 101,
                ..Policy::default()
            },
            Policy {
                target_utilization: 0.0,
                ..Policy::default()
            },
        ] {
            assert!(desired(demand(1.0, 0, 0, 1), p).is_err());
        }
    }

    #[test]
    fn forecasting_rejects_bad_samples_without_mutation() {
        let mut f = Forecast::default();
        assert_eq!(f.rate(), None);
        assert_eq!(f.observe(10.0, 2.0, 0.3), Ok(5.0));
        assert_eq!(f.observe(20.0, 2.0, 0.3), Ok(6.5));
        assert!(f.observe(1.0, 0.0, 0.3).is_err());
        assert!(f.observe(f64::MAX, f64::MIN_POSITIVE, 0.3).is_err());
        assert_eq!(f.rate(), Some(6.5));
    }

    #[test]
    fn placement_filters_and_ties_are_stable() {
        let mut slots = vec![
            Slot {
                id: 1,
                cpu_millis: 2000,
                memory_mib: 2048,
                ready: true,
                leased: false,
            },
            Slot {
                id: 2,
                cpu_millis: 1000,
                memory_mib: 1024,
                ready: true,
                leased: false,
            },
            Slot {
                id: 3,
                cpu_millis: 1000,
                memory_mib: 1024,
                ready: true,
                leased: true,
            },
        ];
        assert_eq!(select(&slots, 500, 512), Ok(Some(1)));
        assert_eq!(select(&slots, 3000, 512), Ok(None));
        slots[1].leased = true;
        assert_eq!(select(&slots, 500, 512), Ok(Some(0)));
        slots[0].ready = false;
        assert_eq!(select(&slots, 500, 512), Ok(None));
        assert!(select(&slots, 0, 512).is_err());
        assert_eq!(select(&[], 1, 1), Ok(None));
        slots[0].ready = true;
        slots[1] = slots[0];
        assert_eq!(select(&slots, 1, 1), Ok(Some(0)));
    }

    #[test]
    fn resource_score_does_not_overflow_u32() {
        let slot = Slot {
            id: 0,
            cpu_millis: u32::MAX,
            memory_mib: u32::MAX,
            ready: true,
            leased: false,
        };
        assert_eq!(select(&[slot], 1, 1), Ok(Some(0)));
        let p = Policy {
            max_step: u32::MAX,
            ..Policy::default()
        };
        assert_eq!(desired(demand(1.0, 0, u32::MAX, u32::MAX), p), Ok(u32::MAX));
    }
}
