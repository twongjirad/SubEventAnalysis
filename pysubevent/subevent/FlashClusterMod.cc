#include "FlashClusterMod.hh"
#include "PMTPosMap.hh"
#include <cmath>

namespace subevent {

  int updateMeanVariance( std::vector< Flash* >& flashes, double& zmean, double& ymean, double& zvar, double& yvar, double& petot ) {
    // updates means and variances

    zmean = 0.0;
    ymean = 0.0;
    zvar  = 0.0;
    yvar  = 0.0;
    petot = 0.0;

    int nflashes = 0;

    for ( int i=0; i<(int)flashes.size(); i++ ) {
      if ( flashes.at(i)==NULL )
	continue;
      double chpos[3];
      PMTPosMap::GetPos( (*flashes.at(i)).ch, chpos );
      double zold = zmean;
      double yold = ymean;
      double pe = (*flashes.at(i)).maxamp;
      if ( pe>0 ) {
	petot += pe;
	ymean += (pe/petot)*(chpos[1]-yold);
	zmean += (pe/petot)*(chpos[2]-zold);
	yvar += pe*( chpos[1] - yold )*(chpos[1]-ymean);
	zvar += pe*( chpos[2] - zold )*(chpos[2]-zmean);
	nflashes++;
      }
    }

    if ( petot>0 ) {
      zvar /= petot;
      zvar = sqrt(zvar);
      yvar /= petot;
      yvar = sqrt(yvar);
    }
    else {
      zmean = 0.;
      ymean = 0.;
      zvar = 0.0;
      yvar = 0.0;
      nflashes = 0;
    }

    return nflashes;
  }

  int RemoveSmallestFurthest( std::vector< Flash* >& flashes, double& zmean, double& ymean, double& zvar, double& yvar, double& petot ) {
    // sets the smallest, furthest from current mean to NULL
    // then updates means and variances
    // returns the number of goood flashes remaining

    int smallest = -1;
    double minamp = 0;
    double mindist = 0;
    int nflashes = 0;
    
    for ( int i=0; i<(int)flashes.size(); i++ ) {
      if ( flashes.at(i)==NULL )
	continue;

      if ( smallest<0 || minamp>(*flashes.at(i)).maxamp ) {
	minamp = (*flashes.at(i)).maxamp;
	smallest = i;
      }
      else if ( smallest>=0 && minamp==(*flashes.at(i)).maxamp ) {
	double chpos[3];
	PMTPosMap::GetPos( (*flashes.at(i)).ch, chpos );

	double dist = sqrt( (zmean-chpos[2])*(zmean-chpos[2]) + (ymean-chpos[1])*(ymean-chpos[1]) );
	if ( dist > mindist ) {
	  mindist = dist;
	  smallest = i;
	}
      }
      nflashes++;
    }//end of flash loop


    zmean = ymean = zvar = yvar = petot = 0.0;
    if ( smallest<0 )
      return 0;

    // remove smallest
    flashes.at(smallest) = NULL;
    nflashes--;

    if (nflashes<=0)
      return 0;

    // update
    return updateMeanVariance( flashes,  zmean, ymean, zvar, yvar, petot );

  }
}
