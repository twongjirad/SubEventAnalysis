#ifndef __FLASHLIST__
#define __FLASHLIST__

#include "Flash.hh"

namespace subevent {

  typedef FlashListIter std::vector< Flash >::iterator;

  class FlashList { 

  public:
    FlashList();
    ~FlashList();
    
    std::vector< Flash > fFlashes;
    int add( Flash&& opflash );
    Flash& get( int i );
    FlashListIter begin();
    FlashListIter end();

  };



#endif
