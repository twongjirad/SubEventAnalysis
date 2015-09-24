#ifndef __SUBEVENT__
#include "TObject.h"

namespace subevent {

  class SubEvent : public TObject {
    
  public:
    
    SubEvent();
    ~SubEvent();
    
    ClassDef( SubEvent, 1 );
    
  };

}

#endif
