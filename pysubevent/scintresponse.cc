#include <iostream>
#include <math.h>

#include "scintresponse.hh"

namespace cpysubevent {

  void calcScintResponseCPP( std::vector< float >& fexpectation, int tstart, int tend, int maxt, float sig, float maxamp, float fastconst, float slowconst, float nspertick ) {
    
    //slow component shape: expo convolved with gaus
    float t_smax = 95.0;    // peak of only slow component. numerically solved for det. smearing=3.5*15.625 ns, decay time const= 1500 ns
    float t_fmax = 105.0;   // numerically solved for det. smearing=3.5*15.625 ns, decay time const= 6 ns
    float smax = exp( sig*sig/(2*slowconst*slowconst) - t_fmax/slowconst )*(1 - erf( (sig*sig - slowconst*t_fmax )/(sqrt(2.0)*sig*slowconst ) ) );
    // normalize max at fast component peak
    float As = 0.3*maxamp/smax;
  
    // fast component: since time const is smaller than spe response, we model as simple gaussian
    float Af = 0.8*maxamp;

    int arrlen = tend-tstart;
    bool rising = true;
    float t = 0.0;
    float tmax_ns = maxt*nspertick;
    float tstart_ns = tstart*nspertick;

    //texpectation.clear();
    //texpectation.reserve( arrlen );
    fexpectation.clear();
    fexpectation.reserve( arrlen );

    for ( int tdc=0; tdc<arrlen; tdc++ ) {
      // convert to time
      t = (tstart_ns + float(tdc*nspertick)) - tmax_ns;
      float farg = (t)/sig;
      float f = Af*exp( -0.5*farg*farg );
      float s = As*exp( sig*sig/(2*slowconst*slowconst) - (t)/slowconst )*(1 - erf( (sig*sig - slowconst*(t) )/(sqrt(2.0)*sig*slowconst ) ) );
      float amp = f+s;
      //texpectation.push_back( tstart+tdc ); // amp vs tdc
      fexpectation.push_back( amp ); // amp vs tdc
      if ( rising && amp>20 )
	rising = false;
      else if ( !rising && amp<0.1 )
	break;
    }
  }

}