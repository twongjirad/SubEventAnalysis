#include "FlashList.hh"

namespace subevent {

  FlashList::FlashList() {
    fFlashes.reserve(10);
  }
  FlashList::~FlashList() {}

  int FlashList::add( Flash&& opflash ) {
    fFlashes.emplace_back( opflash );
  }

  Flash& FlashList::get( int i ) {
    return fFlashes.at(i);
  }

  FlashListIter FlashList::begin() {
    return fFlashes.begin();
  }


}
