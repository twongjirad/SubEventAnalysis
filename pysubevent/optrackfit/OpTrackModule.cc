#include "OpTrackModule.hh"
#include "TVector3.h"
#include <cmath>
#include <iostream>

namespace optrackfit {

  void extractFeatureVariables( subevent::SubEvent& subevent, std::vector<double>& featurevec, int NCHANS, double NSPERTICK, double TEMP_SPEAREA )  {
    // Extract from a subevent, the relevant data we will be fitting against.
    featurevec.clear();
    featurevec.resize(3*NCHANS);
    double tmin = 1.0e200;
    for ( subevent::FlashListIter iflash=subevent.flashes.begin(); iflash!=subevent.flashes.end(); iflash++ ) {
      subevent::Flash& aflash = *iflash;
      if ( aflash.ch>=NCHANS )
	continue;
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

  void printFeatureVector( std::vector<double>& featurevec ) {
    std::cout << "[Feature Vector]" << std::endl;
    for ( int ichan=0; ichan<(int)(featurevec.size()/3); ichan++ ) {
      std::cout << "  ch=" << ichan 
		<< "  t=" << featurevec.at( 3*ichan )
		<< "  prompt=" << featurevec.at( 3*ichan+1 )
		<< "  total=" << featurevec.at( 3*ichan+2 )
		<< std::endl;
    }
  }

  void makeVoxelList( TrackHypothesis& track, ubphotonlib::PhotonLibrary& photonlib, double LY, double dEdx, int NCHANS, 
		      std::vector< std::vector<double> >& midpoints, std::vector< std::vector<float> >& chphotons ) {
    // calculate direction of track
    double dleft = 0.0; // distance to end of track
    for (unsigned int i=0;i<3;i++)
      dleft += ( track.start.at(i)-track.end.at(i) )*( track.start.at(i)-track.end.at(i) );
    dleft = sqrt(dleft);
    
    std::vector<double> dir(3,0.0);
    for ( int i=0; i<3; i++ )
      dir.at(i) = ( track.end.at(i)-track.start.at(i) )/dleft;

    //find first voxel bounds (photon library forced our hand to use ROOT)
    TVector3 start( track.start[0], track.start[1], track.start[2] );
    const TVector3& tupper = photonlib.GetVoxelDef().GetContainingVoxel(start).GetLowerCorner();
    const TVector3& tlower = photonlib.GetVoxelDef().GetContainingVoxel(start).GetUpperCorner();
    const TVector3& tvoxsize = photonlib.GetVoxelDef().GetVoxelSize();
    double upper[3] = { tupper.x(), tupper.y(), tupper.z() };
    double lower[3] = { tlower.x(), tlower.y(), tlower.z() };
    double voxsize[3] = { tvoxsize.x(), tvoxsize.y(), tvoxsize.z() };

    int nsteps = 0;
    double currentpos[3] = { start.x(), start.y(), start.z() };
    double next[3] = {0};

    while ( dleft>0 && nsteps<10000 ) {
      
      double s[3] = {0.0, 0.0, 0.0};
      for ( int i=0; i<3; i++ ) {
	if ( dir[i]!=0 ) {
	  double s1 = ( upper[i]-currentpos[i])/dir.at(i);
	  double s2 = ( lower[i]-currentpos[i])/dir.at(i);
	  if ( s1>0 )
	    s[i] = s1;
	  else
	    s[i] = s2;
	}
	else {
	  s[i] = -1;
	}
      }

      double shortest_s = -1;
      int shortest_i = -1;
      for (int i=0; i<3; i++) {
	if ( s[i]>0 && ( shortest_s<0 || s[i]<shortest_s ) ) {
	  shortest_s = s[i];
	  shortest_i = i;
	}
      }
      
      if ( shortest_i<0 ) {
	break;
      }

      // distance to end of the track
      dleft = 0.0;
      for (int i=0; i<3; i++)
	dleft += (track.end[i]-currentpos[i])*(track.end[i]-currentpos[i]);
      dleft = sqrt(dleft);

      // look for stopping conditions
      // (1) at end of track      
      if ( dleft<shortest_s ) {
	// yes, then move to end
	memcpy( next, track.end.data(), sizeof(double)*3 );
	dleft = 0.0;
      }
      else {
	// else move to edge of voxel
	for (int i=0; i<3; i++)
	  next[i] = currentpos[i] + shortest_s*dir.at(i);
      }
      
      // (2) outside of box
      if ( next[0]>photonlib.GetVoxelDef().GetRegionUpperCorner().x() || next[0]<photonlib.GetVoxelDef().GetRegionLowerCorner().x() )
	break;
      if ( next[1]>photonlib.GetVoxelDef().GetRegionUpperCorner().y() || next[1]<photonlib.GetVoxelDef().GetRegionLowerCorner().y() )
	break;
      if ( next[2]>photonlib.GetVoxelDef().GetRegionUpperCorner().z() || next[2]<photonlib.GetVoxelDef().GetRegionLowerCorner().z() )
	break;

      // update the voxels
      if ( shortest_s*dir.at(shortest_i)>0 ) {
	upper[shortest_i] += voxsize[shortest_i];
	lower[shortest_i] += voxsize[shortest_i];
      }
      else {
	upper[shortest_i] -= voxsize[shortest_i];
	lower[shortest_i] -= voxsize[shortest_i];
      }

      // calculate the number of photons that hit each channel for this step
      double stepdist = 0.0;
      for (int i=0; i<3; i++)
	stepdist += ( next[i]-currentpos[i])*(next[i]-currentpos[i]);
      stepdist = sqrt(stepdist);
      std::vector<double> midpt(3,0.0);
      for (int i=0; i<3; i++) {
	midpt.at(i) = currentpos[i] + 0.5*shortest_s*dir.at(i);
      }
      std::vector<float> chvis(NCHANS,0.0);
      photonlib.GetCounts( midpt.data(), chvis );
      for (int i=0; i<NCHANS; i++) {
	chvis.at(i) *= LY*dEdx*stepdist;
      }
      // store them
      midpoints.emplace_back( midpt );
      chphotons.emplace_back( chvis );

      // move to next step
      memcpy( currentpos, next, sizeof(double)*3 );

      // update distance to end of track again
      dleft = 0.0;
      for (int i=0; i<3; i++)
	dleft += ( track.end[i]-currentpos[i] )*(track.end[i]-currentpos[i]);
      dleft = sqrt(dleft);
      
      nsteps++;
    }//end of while loop
    
  }//end of make voxel list


  void makeFeatureHypothesis( TrackHypothesis& track, ubphotonlib::PhotonLibrary& photonlib, OpTrackFitConfig& opconfig, std::vector< std::vector<double> >& chpos,
			      std::vector<double>& featurevec ) {
    std::vector< std::vector<double> > midpoints; // position of each step
    std::vector< std::vector<float> > chphotons; // photons in each channel for each step
    
    makeVoxelList( track, photonlib, opconfig.LY, opconfig.dEdx, opconfig.NCHANS, midpoints, chphotons );

    // fill a feature vecto
    featurevec.clear();
    featurevec.resize( 3*opconfig.NCHANS );
      
    double tmin = -1.0;

    for (int ich=0; ich<opconfig.NCHANS; ich++) {
      double tearliest = 1e200;
      double peprompt = 0.0;
      double petotal = 0.0;
      for (int istep=0; istep<(int)midpoints.size(); istep++) {
	double dist = 0.0;
	for (int i=0; i<3; i++)
	  dist += ( chpos.at(ich).at(i)-midpoints[istep][i] )*( chpos.at(ich).at(i)-midpoints[istep][i] );
	dist = sqrt(dist);
	double dt =  dist/opconfig.Clar;
	if ( dt<tearliest )
	  tearliest = dt;
	peprompt += chphotons[istep][ich]*opconfig.gQE*opconfig.fprompt;
	petotal  += chphotons[istep][ich]*opconfig.gQE;
      }
      featurevec.at( 3*ich )   = tearliest;
      featurevec.at( 3*ich+1 ) = peprompt;
      featurevec.at( 3*ich+2 ) = petotal;
      if ( tmin<0 || tearliest<tmin )
	tmin = tearliest;
    }//end of channel loop

    // subtract off minimum
    for (int ich=0; ich<opconfig.NCHANS; ich++) {
      featurevec.at( 3*ich ) -= tmin;
    }
  }//end of makefeaturehypothesis


  double lnLL( std::vector<double>& datavec, std::vector<double> hypovec, double sig_t, double sig_promptpe, double sig_totpe ) {
    double ll = 0.0;
    double sigs[3] = { sig_t, sig_promptpe, sig_totpe };

    for (int i=0; i<(int)datavec.size(); i++) {
      double arg = (datavec[i]-hypovec[i])/sigs[i%3];
      ll += -0.5*arg*arg;
    }

    return ll;
  }

  double lnProb( std::vector<double>& track_start_end, std::vector<double>& data_opfeatures, 
		 ubphotonlib::PhotonLibrary& photonlib, OpTrackFitConfig& opconfig, std::vector< std::vector<double> >& chpos ) {
    // convert input values into track info
    std::vector<double> start(3,0.0);
    std::vector<double> end(3,0.0);
    for (int i=0; i<3; i++) {
      start[i] = track_start_end[i];
      end[i] = track_start_end[3+i];
    }
    TrackHypothesis track( start, end );
    // calculate likelihood
    std::vector<double> hypovec;
    makeFeatureHypothesis( track, photonlib, opconfig, chpos, hypovec );
    double ll = lnLL( data_opfeatures, hypovec, opconfig.sig_t, opconfig.sig_promptpe, opconfig.sig_totpe );
    // add weak priors to keep walkers around detector
    double llweakdet = 0.0;
    for (int i=0; i<3; i++) {
      double arg1 = (start[i]-opconfig.detcenter[i])/opconfig.detsigma[i];
      double arg2 = (end[i]-opconfig.detcenter[i])/opconfig.detsigma[i];
      llweakdet += -0.5*arg1*arg1;
      llweakdet += -0.5*arg2*arg2;
    }
    ll += llweakdet;
    return ll;
  }

  void runOpTrackFit( subevent::SubEvent& subevent, OpTrackFitConfig& config, ubphotonlib::PhotonLibrary& photonlib ) {

    std::cout << "[RunOpTrackFit] Start." << std::endl;

    // data variables we will be fitting to
    std::vector<double> datafeature;
    extractFeatureVariables( subevent, datafeature, config.NCHANS, config.NSPERTICK, 100.0 );

    

    
  }
  
}
