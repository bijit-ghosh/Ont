#include "planner.hpp"
#include <chrono>
#include <iostream>
#include <string>
int main(int argc,char** argv) {
    if(argc==2&&std::string(argv[1])=="--benchmark") {
        std::vector<ont::Slot> slots;
        for(unsigned i=0;i<256;i++)slots.push_back({i,1000+i,1024+i,true,false});
        std::vector<double> samples;samples.reserve(10000);volatile int sink=0;
        for(unsigned i=0;i<11000;i++) {
            auto start=std::chrono::steady_clock::now();
            sink=ont::select(slots,500+(i%500),512);
            auto ns=std::chrono::duration<double,std::nano>(std::chrono::steady_clock::now()-start).count();
            if(i>=1000)samples.push_back(ns);
        }
        std::sort(samples.begin(),samples.end());
        std::cout<<"{\"operation\":\"placement_scan\",\"slots\":256,\"samples\":10000,\"p50_ns\":"<<samples[5000]<<",\"p95_ns\":"<<samples[9500]<<",\"p99_ns\":"<<samples[9900]<<"}\n";
        return sink<0;
    }
    // Streaming numeric protocol: rate service_seconds queued busy current.
    // This process recommends counts only. It never provisions or authorizes jobs.
    ont::Demand d{};ont::Policy p;
    while(std::cin>>d.arrivals_per_second>>d.service_seconds>>d.queued>>d.busy>>d.current) {
        try {std::cout<<"{\"desired\":"<<ont::desired(d,p)<<"}\n";}
        catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
    }
    return std::cin.eof()?0:1;
}
