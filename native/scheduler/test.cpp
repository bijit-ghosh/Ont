#include "planner.hpp"
#include <cassert>
#include <iostream>
int main() {
    ont::Policy p;
    assert(ont::desired({0,1,0,0,1},p)==1);
    assert(ont::desired({100,1,100,0,1},p)==11);
    assert(ont::desired({0,1,0,40,40},p)==40);
    assert(ont::desired({0,1,0,0,40},p)==30);
    assert(ont::desired({100000,1,0,0,95},p)==100);
    ont::Forecast f;f.observe(10,2);assert(f.rate==5);f.observe(20,2);assert(f.rate>5&&f.rate<10);
    bool failed=false;try{f.observe(1,0);}catch(const std::invalid_argument&){failed=true;}assert(failed);
    failed=false;try{ont::desired({NAN,1,0,0,1},p);}catch(const std::invalid_argument&){failed=true;}assert(failed);
    std::vector<ont::Slot> slots={{1,2000,2048,true,false},{2,1000,1024,true,false},{3,1000,1024,true,true}};
    assert(ont::select(slots,500,512)==1);assert(ont::select(slots,3000,512)==-1);
    slots[1].leased=true;assert(ont::select(slots,500,512)==0);
    slots[0].ready=false;assert(ont::select(slots,500,512)==-1);
    std::cout<<"Native scheduler checks passed\n";
}
