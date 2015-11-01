#include "TrackHypothesis.hh"

namespace optrackfit {

  TrackHypothesis::TrackHypothesis() {}

  TrackHypothesis::TrackHypothesis( std::vector<double>& start_, std::vector<double>& end_ ) {
    start = start_;
    end = end_;
  }

  TrackHypothesis::~TrackHypothesis() {}

  void TrackHypothesis::getTrackVector( std::vector<double>& vec ) {
    vec.clear();
    vec.reserve(6);
    for (int i=0; i<3; i++)
      vec.push_back( start.at(i) );
    for (int i=0; i<3; i++)
      vec.push_back( end.at(i) );
  }
  
}
