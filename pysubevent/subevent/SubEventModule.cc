#include "SubEventModule.hh"
#include "cfdiscriminator.hh"
#include "scintresponse.hh"
#include <algorithm>

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
    opflash.tstart = t_fire.at( largestCFD );
    opflash.tmax = maxt_fire.at( largestCFD );
    opflash.maxamp = amp_fire.at( largestCFD );

    // calc scint response
    std::vector< double > expectation;
    expectation.reserve( 200 );
    subevent::calcScintResponseCPP( expectation, 
				    std::max( 0, opflash.tstart-20), waveform.size(), opflash.tmax, 
				    config.spe_sigma, maxamp-waveform.at( opflash.tstart ), config.fastconst_ns, config.slowconst_ns, config.nspersample );

    opflash.tend = opflash.tstart+expectation.size();
    std::vector< double > subwfm( waveform.begin()+opflash.tstart, waveform.begin()+opflash.tend );
    opflash.storeWaveform( subwfm );
    
    opflash.storeExpectation( expectation );
    
  };


  void getChannelFlashes( int channel, std::vector< double >& waveform, SubEventModConfig& config, std::vector<double>& postwfm ) {
    // corresponds to cyRunSubEventDiscChannel
    // input
    // channel: FEMCH number
    // waveform: ADCs
    // config
    // output
  };
}
