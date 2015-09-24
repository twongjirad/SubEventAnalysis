#ifndef __SubEventModConfig__
#define __SubEventModConfig__

#include "CFDiscConfig.hh"

namespace subevent {


  class SubEventModConfig {

  public:
    SubEventModConfig();
    ~SubEventModConfig();

    double spe_sigma;
    double fastconst_ns;
    double slowconst_ns;
    double nspersample;
    cpysubevent::CFDiscConfig cfdconfig;

  };

}

#endif
