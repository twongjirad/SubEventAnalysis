#include "SubEventModule.hh"
#include "Flash.hh"
#include "FlashList.hh"
#include "SubEventList.hh"
#include "WaveformData.hh"
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

    opflash.tend = std::min( opflash.tstart+expectation.size(), waveform.size()-1 );
    
    std::vector< double > subwfm( waveform.begin()+opflash.tstart, waveform.begin()+opflash.tend );
    opflash.storeWaveform( subwfm );
    std::vector< double > subexp( expectation.begin(), expectation.begin()+subwfm.size() );
    opflash.storeExpectation(  subexp );

    // for debug
    //std::cout << "return opflash: " << opflash.ch << " " << opflash.tstart << " " << opflash.tend << " " << opflash.tmax << " " << opflash.maxamp << std::endl;
    //for ( int i=0; i<expectation.size(); i++)
    //std::cout << expectation.at(i) << " ";
    //std::cout << std::endl;

    return 1;
  };

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
    double chped = waveform.at(0);
    
    //flashes.clear();

    while ( nsubevents<maxsubevents ) {
      // find one subevent (finds the largest flash of light)
      Flash opflash;
      int found = findChannelFlash( channel, postwfm, config, opflash );
      if ( found==0 )
	break;
      
      // subtract waveform below subevent threshold
      //double amp_start = waveform.at( opflash.tstart );
      //double amp_end   = waveform.at( opflash.tend );
      //double slope = (amp_end-amp_start)/( opflash.tend-opflash.tstart );

      for (int tdc=0; tdc<opflash.expectation.size(); tdc++) {
	fx = opflash.expectation.at(tdc);
	sig = sqrt( fx/20.0 );
	thresh = fx + 3.0*sig*20.0; // 3 sigma variance
	if ( postwfm.at( opflash.tstart )-chped < thresh ) {
	  //postwfm.at( opflash.tstart + tdc ) = slope*( tdc ) + amp_start;
	  postwfm.at( opflash.tstart + tdc ) = chped;
	}
      }
      nsubevents += 1;
      flashes.add( std::move(opflash) );
    }//end of subflash search
      
    return nsubevents;

  };

  void formFlashes( WaveformData& wfms, SubEventModConfig& config, FlashList& flashes ) {

    for ( ChannelSetIter it=wfms.chbegin(); it!=wfms.chend(); it++ ) {
      int ch = *it;
      std::vector< double > postwfm;
      getChannelFlashes( ch, wfms.get( ch ), config, flashes, postwfm );
    }
  };

  void fillFlashAccumulators( FlashList& flashes, std::map< int, double >& pmtspemap, SubEventModConfig& config, std::vector< double >& peacc, std::vector< double >& hitacc ) {

    for ( FlashListIter iflash=flashes.begin(); iflash!=flashes.end(); iflash++ ) {
      if ( (*iflash).claimed )
	continue;

      for ( int t=(*iflash).tstart-0.5*config.flashgate; t<(*iflash).tstart+0.5*config.flashgate; t++ ) {
	peacc[t] += ((*iflash).maxamp-2047.0)/pmtspemap[(*iflash).ch];
	hitacc[t] += 1.0;
      }
      
    }

  };

  void formSubEvents( WaveformData& wfms, SubEventModConfig& config, std::map< int, double >& pmtspemap, SubEventList& subevents ) {

    std::cout << "FormSubEvents" << std::endl;

    FlashList flashes;
    formFlashes( wfms, config, flashes );

    std::cout << "  total flashes: " << flashes.size() << std::endl;

    int nloops = 0;
    while ( nloops < config.maxsubeventloops ) {


      // accumulators: the summed pulse height and the number of hits
      std::vector< double > peacc( wfms.get(0).size(), 0.0 );
      std::vector< double > hitacc( wfms.get(0).size(), 0.0 );
      
      fillFlashAccumulators( flashes, pmtspemap, config, peacc, hitacc );

      // find maximums
      double  hit_tmax = 0;
      double pe_tmax = 0;
      double pemax = 0;
      double hitmax = 0;
      for ( int tick=0; tick<peacc.size(); tick++ ) {
	if ( peacc.at(tick)>pemax ) {
	  pemax = peacc.at(tick);
	  pe_tmax = tick;
	}
	if ( hitacc.at(tick)>hitmax ) {
	  hitmax = hitacc.at(tick);
	  hit_tmax = tick;
	}
      }
      std::cout << "  accumulator max: t=" << pe_tmax << " amp=" << pemax << " hits=" << hitmax << std::endl;

      // organize flashes within maxima
      if ( pemax>config.ampthresh || hitmax>config.hitthresh ) {
	// passed! 
	std::cout << "  subevent formed. loop #" << nloops << std::endl;

	SubEvent newsubevent;
	
	//if ( !flashes.sortedByTime()  ) flashes.sortByTime();
	//std::cout << "   sorted flashes by time" << std::endl;
	
	// form subevent by grouping flashes around tmax
	int nclaimed = 0;
	for ( FlashListIter iflash=flashes.begin(); iflash!=flashes.end(); iflash++ ) {
	  
	  if ( (*iflash).claimed ) continue;
	  
	  if ( abs( (*iflash).tstart - pe_tmax )< config.flashgate ) {

	    newsubevent.tstart_sample = (int)pe_tmax;
	    if ( newsubevent.tend_sample < (int)(*iflash).tend )
	      newsubevent.tend_sample = (int)(*iflash).tend;
	    newsubevent.maxamp = pemax;
	    newsubevent.totpe += (*iflash).area/pmtspemap[ (*iflash).ch ];
	    Flash copyflash( (*iflash ) );
	    copyflash.claimed = true;
	    (*iflash).claimed = true;
	    newsubevent.flashes.add( std::move(copyflash) ); 
	    nclaimed++;
	  }

	} //end of flash loop
	
	// store new subevent
	std::cout << "  subevent " << subevents.size() << ": tstart=" << newsubevent.tstart_sample << "  tend=" << newsubevent.tend_sample << " nflashes=" << newsubevent.flashes.size() << std::endl;
	subevents.add( std::move( newsubevent ) );
	
      }
      else {
	std::cout << "  did not find additional subevent" << std::endl;
	break;
      }

      nloops += 1;
    }//end of while loop

  };

}
