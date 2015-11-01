#ifndef __OPTRACKMODULE__
#define __OPTRACKMODULE__

#include <vector>
#include "SubEvent.hh"
#include "TrackHypothesis.hh"
#include "OpTrackFitConfig.hh"
#include "PhotonLibrary.h"

namespace optrackfit {

  // Main routine
  void runOpTrackFit( subevent::SubEvent& subevent, OpTrackFitConfig& config, ubphotonlib::PhotonLibrary& photonlib ); 

  // module methods
  void extractFeatureVariables( subevent::SubEvent& subevent, std::vector<double>& featurevec, int NCHANS, double NSPERTICK, double TEMP_SPEAREA );
  void makeVoxelList( TrackHypothesis& track, double LY, double dEdx );
  

}

#endif
