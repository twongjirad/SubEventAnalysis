#include "SubEventList.hh"

namespace subevent {

  SubEventList::SubEventList() {
    fSubEventes.reserve(10);
  }
  SubEventList::~SubEventList() {}

  int SubEventList::add( SubEvent&& opflash ) {
    fSubEventes.emplace_back( opflash );
    return fSubEventes.size();
  }

  SubEvent& SubEventList::get( int i ) {
    return fSubEventes.at(i);
  }

  SubEventListIter SubEventList::begin() {
    return fSubEventes.begin();
  }
  
  SubEventListIter SubEventList::end() {
    return fSubEventes.end();
  }

  void SubEventList::sortByTime() {
    std::sort( begin(), end(), SubEventList::compareTime );
    sortMethod = kByTime;
  }

  void SubEventList::sortByCharge() {
    std::sort( begin(), end(), SubEventList::compareArea );
    sortMethod = kByCharge;
  }

  void SubEventList::sortByAmp() {
    std::sort( begin(), end(), SubEventList::compareAmp );
    sortMethod = kByAmp;
  }

}
