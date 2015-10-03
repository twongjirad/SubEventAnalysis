#ifndef __WAVEFORMDATA__
#define __WAVEFORMDATA__

#include <vector>
#include <map>

namespace subevent {
  class WaveformData {

  public:
    WaveformData();
    ~WaveformData();
    
    std::map< int, std::vector<double> > waveforms;
    std::vector< double >& get( int ch ) { return waveforms[ch]; };
    void set( int ch, std::vector<double>& wfm );
    
  };

}

#endif
