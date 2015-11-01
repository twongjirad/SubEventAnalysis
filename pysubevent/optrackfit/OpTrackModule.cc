#include "OpTrackModule.hh"
#include "TVector3.h"
#include <cmath>

namespace optrackfit {

  void extractFeatureVariables( subevent::SubEvent& subevent, std::vector<double>& featurevec, int NCHANS, double NSPERTICK, double TEMP_SPEAREA )  {
    // Extract from a subevent, the relevant data we will be fitting against.
    featurevec.clear();
    featurevec.reserve(3*NCHANS);
    double tmin = 1.0e200;
    for ( subevent::FlashListIter iflash=subevent.flashes.begin(); iflash!=subevent.flashes.end(); iflash++ ) {
      subevent::Flash& aflash = *iflash;
      double tflash = aflash.tstart*NSPERTICK;
      if (tflash<tmin)
	tmin = tflash;
      featurevec.at( 3*aflash.ch + 0 ) = tflash;
      featurevec.at( 3*aflash.ch + 1 ) = aflash.area30/TEMP_SPEAREA;
      featurevec.at( 3*aflash.ch + 2 ) = aflash.area/TEMP_SPEAREA;
    }
    // subtract off leading time for non-zero elements
    for (int ichan=0; ichan<NCHANS; ichan++) {
      if (featurevec.at( 3*ichan + 1 )>0)
	featurevec.at( 3*ichan + 0 ) -= tmin;
    }
  }

  void makeVoxelList( TrackHypothesis& track, double LY, double dEdx, ubphotonlib::PhotonLibrary& photonlib ) {
    // calculate direction of track
    double dleft = 0.0; // distance to end of track
    for (unsigned int i=0;i<3;i++)
      dleft += ( track.start.at(i)-track.end.at(i) )*( track.start.at(i)-track.end.at(i) );
    dleft = sqrt(dleft);
    
    std::vector<double> dir;
    for ( int i=0; i<3; i++ )
      dir.at(i) = ( track.end.at(i)-track.start.at(i) )/dleft;

    //find first voxel bounds (photon library forced our hand to use ROOT)
    TVector3 start( track.start[0], track.start[1], track.start[2] );
    TVector3 end( track.start[0], track.start[1], track.start[2] );
    const TVector3& upper = photonlib.GetVoxelDef().GetContainingVoxel(start).GetLowerCorner();
    const TVector3& lower = photonlib.GetVoxelDef().GetContainingVoxel(start).GetUpperCorner();

    const TVector3& voxsize = photonlib.GetVoxelDef().GetVoxelSize();
    
  }


  void runOpTrackFit( subevent::SubEvent& subevent, OpTrackFitConfig& config, ubphotonlib::PhotonLibrary& photonlib ) {
    
  }
  
}
