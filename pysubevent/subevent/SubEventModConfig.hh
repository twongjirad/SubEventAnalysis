#ifndef __SubEventModConfig__
#define __SubEventModConfig__

#include "CFDiscConfig.hh"

namespace subevent {


  class SubEventModConfig {

  public:
    SubEventModConfig();
    ~SubEventModConfig();

    double spe_sigma;
    double fastfraction;
    double slowfraction;
    double fastconst_ns;
    double slowconst_ns;

    int npresamples;    
    int pedsamples;
    double pedmaxvar;
    double nspersample;
    int maxchflashes;

    cpysubevent::CFDiscConfig cfdconfig;

  };

}

#endif
