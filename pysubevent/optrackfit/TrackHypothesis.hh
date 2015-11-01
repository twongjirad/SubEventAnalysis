#ifndef __TrackHypothesis__
#define __TrackHypothesis__

#include <vector>

namespace optrackfit {

  class TrackHypothesis {

  public:
    
    TrackHypothesis();
    TrackHypothesis( std::vector<double>& start, std::vector<double>& end );
    ~TrackHypothesis();
    
    std::vector<double> start;
    std::vector<double> end;
    
    void getTrackVector( std::vector<double>& vec );
  };

}

#endif
