#ifndef __CFDFire__

#include "TObject.h"

namespace cfd {

  class CFDFire : public TObject {

  public:

    CFDFire();
    ~CFDFire();
    
    int tfire;
    int maxamp;
    int tmax;
    int maxdiff;
    
    ClassDef( CFDFire, 1 );

  };

}

#endif
