#ifndef __FLASHCLUSTERMoD__
#define __FLASHCLUSTERMoD__

#include <vector>
#include "Flash.hh"

namespace subevent {

  int RemoveSmallestFurthest( std::vector< Flash* >& flashes, double& zmean, double& ymean, double& zvar, double& yvar, double& petot );
  int updateMeanVariance( std::vector< Flash* >& flashes, double& zmean, double& ymean, double& zvar, double& yvar, double& petot );

};


#endif
