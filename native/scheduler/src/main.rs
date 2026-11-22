#![forbid(unsafe_code)]
use ont_scheduler::{desired, select, Demand, Policy, Slot};
use std::hint::black_box;
use std::io::{self, BufRead};
use std::process::ExitCode;
use std::time::Instant;

fn benchmark() {
    let slots: Vec<_> = (0..256)
        .map(|i| Slot {
            id: i,
            cpu_millis: 1000 + i,
            memory_mib: 1024 + i,
            ready: true,
            leased: false,
        })
        .collect();
    let mut samples = Vec::with_capacity(10000);
    for i in 0..11000 {
        let start = Instant::now();
        black_box(select(black_box(&slots), black_box(500 + (i % 500)), 512).unwrap());
        let ns = start.elapsed().as_nanos();
        if i >= 1000 {
            samples.push(ns);
        }
    }
    samples.sort_unstable();
    println!("{{\"operation\":\"placement_scan\",\"language\":\"rust\",\"slots\":256,\"samples\":10000,\"p50_ns\":{},\"p95_ns\":{},\"p99_ns\":{}}}", samples[5000], samples[9500], samples[9900]);
}

fn run() -> Result<(), String> {
    let args: Vec<_> = std::env::args().skip(1).collect();
    if args == ["--benchmark"] {
        benchmark();
        return Ok(());
    }
    if !args.is_empty() {
        return Err("usage: ont-scheduler [--benchmark]".into());
    }
    for line in io::stdin().lock().lines() {
        let line = line.map_err(|e| e.to_string())?;
        if line.trim().is_empty() {
            continue;
        }
        if line.len() > 4096 {
            return Err("input line too large".into());
        }
        let v: Vec<_> = line.split_whitespace().collect();
        if v.len() != 5 {
            return Err("expected: arrival_rate service_seconds queued busy current".into());
        }
        let float = |i: usize| {
            v[i].parse::<f64>()
                .map_err(|_| "invalid number".to_string())
        };
        let integer = |i: usize| v[i].parse::<u32>().map_err(|_| "invalid count".to_string());
        let d = Demand {
            arrivals_per_second: float(0)?,
            service_seconds: float(1)?,
            queued: integer(2)?,
            busy: integer(3)?,
            current: integer(4)?,
        };
        let count = desired(d, Policy::default()).map_err(str::to_string)?;
        println!("{{\"desired\":{count}}}");
    }
    Ok(())
}

fn main() -> ExitCode {
    match run() {
        Ok(()) => ExitCode::SUCCESS,
        Err(error) => {
            eprintln!("{error}");
            ExitCode::FAILURE
        }
    }
}
