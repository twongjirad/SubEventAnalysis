#include "SubEventModule.hh"
#include "FlashList.hh"
#include "cfdiscriminator.hh"
#include "scintresponse.hh"
#include <algorithm>
#include <iostream>
#include <cmath>

namespace subevent {

  int findChannelFlash( int channel, std::vector< double >& waveform, SubEventModConfig& config, Flash& opflash ) {
    // ---------------------------------------
    // input
    // int channel: channel id
    // waveform: ADCs
    // config: SubEventModule configuration
    // output
    // opflash: Flash object
    // ---------------------------------------

    std::vector< int > t_fire;
    std::vector< int > amp_fire;
    std::vector< int > maxt_fire;
    std::vector< int > diff_fire;

    cpysubevent::runCFdiscriminatorCPP( t_fire, amp_fire, maxt_fire, diff_fire, waveform.data(), 
					config.cfdconfig.delay, config.cfdconfig.threshold, config.cfdconfig.deadtime, config.cfdconfig.width, waveform.size() );

    // find largest
    int largestCFD = -1;
    double maxamp = 0;
    for (int n=0; n<t_fire.size(); n++) {
      if ( amp_fire.at(n) > maxamp ) {
	maxamp = amp_fire.at(n);
	largestCFD = n;
      }
    }

    if ( largestCFD==-1 )
      return 0;

    // store info from discriminator
    opflash.ch = channel;
    opflash.tstart = std::max(t_fire.at( largestCFD )-config.npresamples, 0);
    opflash.tmax = maxt_fire.at( largestCFD );
    opflash.maxamp = amp_fire.at( largestCFD );

    // calc scint response
    std::vector< double > expectation;
    expectation.reserve( 200 );
    subevent::calcScintResponseCPP( expectation, 
				    opflash.tstart, waveform.size(), opflash.tmax, 
				    config.spe_sigma, maxamp-waveform.at( opflash.tstart ), config.fastconst_ns, config.slowconst_ns, config.nspersample );

    opflash.tend = opflash.tstart+expectation.size();
    std::vector< double > subwfm( waveform.begin()+opflash.tstart, waveform.begin()+opflash.tend );
    opflash.storeWaveform( subwfm );
    opflash.storeExpectation( expectation );

    // for debug
    //std::cout << "return opflash: " << opflash.ch << " " << opflash.tstart << " " << opflash.tend << " " << opflash.tmax << " " << opflash.maxamp << std::endl;
    //for ( int i=0; i<expectation.size(); i++)
    //std::cout << expectation.at(i) << " ";
    //std::cout << std::endl;

    return 1;
  };



// cpdef cyRunSubEventDiscChannel( np.ndarray[DTYPEFLOAT_t, ndim=1] waveform, config, ch, retpostwfm=False ):
//     """
//     Multiple pass strategy.
//     (1) Find peaks using CFD
//     (2) Pick biggest peak
//     (3) Define expected signal using fast and slow fractions
//     (4) Define start and end this way
//     (5) Subtract off subevent
//     (6) Repeat (1)-(5) until all disc. peaks are below threshold
//     * Note this is time hog now *
//     """
//     subevents = []

//     # build configuration
//     config.fastconst = 20.0
//     config.sigthresh = 3.0
//     cdfthresh = config.threshold
//     cfdconf = cfd.cfdiscConfig( config.discrname, threshold=cdfthresh, deadtime=config.deadtime, delay=config.delay, width=config.width )
//     cfdconf.pedestal = ped.getpedestal( waveform, config.pedsamples, config.pedmaxvar )  # will have to calculate this at some point
//     if cfdconf.pedestal is None:
//         return subevents # empty -- bad baseline!
//     cfdconf.nspersample = 15.625
//     #print pbin1, config.fastconst, config.slowconst

//     # make our working copy of the waveform
//     wfm = np.copy( waveform )

//     # find subevent
//     cdef int maxsubevents = 20
//     cdef int nsubevents = 0
//     cdef int t = 0
//     cdef float fx = 0.0
//     cdef float sig = 0.0
//     cdef float thresh = 0.0
//     cdef float chped = cfdconf.pedestal
    
//     while nsubevents<maxsubevents:
//         # find subevent
//         subevent = findOneSubEvent( wfm, cfdconf, config, ch )
        
//         if subevent is not None:
//             subevents.append(subevent)
//         else:
//             break
//         # subtract waveform below subevent threshold
//         for (t,fx) in subevent.expectation:
            
//             sig = np.sqrt( fx/20.0 ) # units of pe
//             thresh =  fx + 3.0*sig*20.0 # 3 sigma times pe variance

//             #if fx*config.sigthresh > wfm[t]-config.pedestal:
//             if wfm[t]-chped < thresh:
//                 wfm[t] = chped
//         nsubevents += 1
//         #break

//     if retpostwfm:
//         return subevents, wfm
//     else:
//         return subevents

  int getChannelFlashes( int channel, std::vector< double >& waveform, SubEventModConfig& config, FlashList& flashes, std::vector<double>& postwfm ) {
    // corresponds to cyRunSubEventDiscChannel
    // input
    // channel: FEMCH number
    // waveform: ADCs
    // config
    // output

    // make our working copy of the waveform
    postwfm.clear();
    postwfm.reserve( waveform.size() );
    std::copy( waveform.begin(), waveform.end(), back_inserter(postwfm) );

    //  find subevent
    int maxsubevents = config.maxchflashes;
    int nsubevents = 0;
    int t = 0;
    double fx = 0.0;
    double sig = 0.0;
    double thresh = 0.0;
    double chped = 2048.0;
    
    flashes.clear();

    while ( nsubevents<maxsubevents ) {
      // find one subevent (finds the largest flash of light)
      Flash opflash;
      int found = findChannelFlash( channel, postwfm, config, opflash );
      if ( found==0 )
	break;
      
      // subtract waveform below subevent threshold
      double amp_start = waveform.at( opflash.tstart );
      double amp_end   = waveform.at( opflash.tend );
      double slope = (amp_end-amp_start)/( opflash.tend-opflash.tstart );

      for (int tdc=0; tdc<opflash.expectation.size(); tdc++) {
	fx = opflash.expectation.at(tdc);
	sig = sqrt( fx/20.0 );
	thresh = fx + 3.0*sig*20.0; // 3 sigma variance
	if ( postwfm.at( opflash.tstart )-2048.0 < thresh ) {
	  postwfm.at( opflash.tstart + tdc ) = slope*( tdc ) + amp_start;
	}
      }
      nsubevents += 1;
      flashes.add( std::move(opflash) );
    }//end of subflash search
      
    return nsubevents;

  };
}
