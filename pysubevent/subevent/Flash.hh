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
    
    void storeWaveform( std::vector< double >& waveform );
    void storeExpectation( std::vector< double >& expectation );

    int ch;
    int tstart;
    int tend;
    int tmax;
    double maxamp;
    double area;
    std::vector< double > expectation;
    std::vector< double > waveform;

    ClassDef( Flash, 1 );
  };

}

#endif
