#ifndef __SUBEVENT__
#define __SUBEVENT__

#include "TObject.h"
#include "Flash.hh"
#include "FlashList.hh"

namespace subevent {

  class SubEvent : public TObject {
    
  public:
    
    SubEvent();
    ~SubEvent();

    int tstart_sample;
    int tend_sample;
    double tstart_ns;
    double tend_ns;

    double totpe;
    double maxamp;

    FlashList flashes;
    
    ClassDef( SubEvent, 1 );
    
  };

}

#endif
