#ifndef __FLASH_HH__
#define __FLASH_HH__

#include "TObject.h"
#include <vector>

namespace subevent {
  class Flash : public TObject {

  public:
    
    Flash();
    Flash( int ch, int tstart, int tend, int tmax, float maxamp, std::vector< double >& expectation, std::vector< double >& waveform );
    ~Flash();
    
    template< typename T >
    void storeWaveform( std::vector< T >& waveform );
    void storeExpectation( std::vector< double >& expectation );

    int ch;
    int tstart;
    int tend;
    int tmax;
    float maxamp;
    std::vector< double > expectation;
    std::vector< double > waveform;

    ClassDef( Flash, 1 );
  };

}

#endif