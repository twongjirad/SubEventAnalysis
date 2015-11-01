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

  // liklihood functions
  double lnProb( std::vector<double>& track_start_end, std::vector<double>& data_opfeatures,
                 ubphotonlib::PhotonLibrary& photonlib, OpTrackFitConfig& opconfig, std::vector< std::vector<double> >& chpos );
  double lnLL( std::vector<double>& datavec, std::vector<double> hypovec, double sig_t, double sig_promptpe, double sig_totpe );

  // module methods
  void extractFeatureVariables( subevent::SubEvent& subevent, std::vector<double>& featurevec, int NCHANS, double NSPERTICK, double TEMP_SPEAREA );
  void printFeatureVector( std::vector<double>& featurevec );
  void makeVoxelList( TrackHypothesis& track, ubphotonlib::PhotonLibrary& photonlib, double LY, double dEdx, int NCHANS, 
		      std::vector< std::vector<double> >& midpoints, std::vector< std::vector<float> >& chphotons );
  void makeFeatureHypothesis( TrackHypothesis& track,  ubphotonlib::PhotonLibrary& photonlib, OpTrackFitConfig& opconfig, std::vector< std::vector<double> >& chpos, 
			      std::vector<double>& featurehypo );
  

}

#endif
