#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <stdexcept>
#include <vector>

namespace ont {
struct Demand {
    double arrivals_per_second;
    double service_seconds;
    unsigned queued, busy, current;
};
struct Policy {
    unsigned minimum=1, maximum=100, max_step=10;
    double target_utilization=0.7, queue_drain_seconds=10, headroom=1.2;
};
struct Forecast {
    double rate=0;
    bool initialized=false;
    void observe(double arrivals, double seconds, double alpha=0.3) {
        if (!std::isfinite(arrivals)||arrivals<0||!std::isfinite(seconds)||seconds<=0||!std::isfinite(alpha)||alpha<=0||alpha>1)
            throw std::invalid_argument("invalid observation");
        const double sample=arrivals/seconds;
        if (!std::isfinite(sample)) throw std::invalid_argument("observation overflow");
        rate=initialized ? alpha*sample+(1-alpha)*rate : sample;
        initialized=true;
    }
};
inline unsigned desired(const Demand& d,const Policy& p) {
    if (!std::isfinite(d.arrivals_per_second)||d.arrivals_per_second<0||!std::isfinite(d.service_seconds)||d.service_seconds<=0||
        d.busy>d.current||p.minimum>p.maximum||p.maximum>1000000||!p.max_step||!std::isfinite(p.target_utilization)||p.target_utilization<=0||p.target_utilization>1||
        !std::isfinite(p.queue_drain_seconds)||p.queue_drain_seconds<=0||!std::isfinite(p.headroom)||p.headroom<1)
        throw std::invalid_argument("invalid demand or policy");
    double load=(d.arrivals_per_second+d.queued/p.queue_drain_seconds)*d.service_seconds*p.headroom/p.target_utilization;
    unsigned target=load>=p.maximum ? p.maximum : static_cast<unsigned>(std::ceil(load));
    target=std::clamp(target,p.minimum,p.maximum);
    // Never recommend eviction of busy allocations, including temporary over-capacity.
    target=std::max(target,d.busy);
    if (target>d.current) return static_cast<unsigned>(std::min<std::uint64_t>(target,static_cast<std::uint64_t>(d.current)+p.max_step));
    unsigned floor=d.current>p.max_step ? d.current-p.max_step : 0;
    return std::max(target,floor);
}
struct Slot { unsigned id,cpu_millis,memory_mib; bool ready,leased; };
inline int select(const std::vector<Slot>& slots,unsigned cpu,unsigned memory) {
    if (!cpu||!memory) throw std::invalid_argument("resource request must be positive");
    int best=-1;
    std::uint64_t waste=UINT64_MAX;
    for (std::size_t i=0;i<slots.size();++i) {
        const auto& s=slots[i];
        if (!s.ready||s.leased||s.cpu_millis<cpu||s.memory_mib<memory) continue;
        const std::uint64_t score=static_cast<std::uint64_t>(s.cpu_millis-cpu)+s.memory_mib-memory;
        if(score<waste) {best=static_cast<int>(i);waste=score;}
    }
    return best;
}
}
