#include "Flash.hh"
#include <iostream>
#include <algorithm>

ClassImp( subevent::Flash );

namespace subevent {

  Flash::Flash() {}

  Flash::Flash( int ch_, int tstart_, int tend_, int tmax_, float maxamp_, std::vector< double >& expectation_, std::vector< double >& waveform_ ) :
    ch (ch_), tstart( tstart_ ), tend( tend_ ), tmax( tmax_ ), maxamp( maxamp_) {

    storeWaveform( waveform_ );
    storeExpectation( expectation_ );
  
  }

  Flash::~Flash() {}

  void Flash::storeWaveform( std::vector< double >& waveform_ ) {
    waveform.clear();
    waveform.reserve( waveform_.size() );

    for ( std::vector< double >::iterator it=waveform_.begin(); it!=waveform_.end(); it++ ) {
      waveform.push_back( (double)*it );
    }
  }

  void Flash::storeExpectation( std::vector< double >& expectation_ ) {
    expectation.clear();
    expectation.reserve( expectation_.size() );    
    for ( std::vector< double >::iterator it=expectation_.begin(); it!=expectation_.end(); it++ ) {
      //std::cout << *it << " ";
      expectation.push_back( *it );
    }    
    //std::cout << std::endl;
  }
  
}
