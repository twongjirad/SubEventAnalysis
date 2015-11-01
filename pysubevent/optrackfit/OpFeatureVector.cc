#include "OpFeatureVector.hh"

namespace optrackfit {

  OpFeatureVector::OpFeatureVector() {}

  OpFeatureVector::OpFeatureVector( std::vector<double>& pulse_tstart, std::vector<double>& pulse_promptpe, std::vector<double>& pulse_totpe ) {
    setData( pulse_tstart, pulse_promptpe, pulse_totpe );
  }

  OpFeatureVector::~OpFeatureVector() {}

  void OpFeatureVector::setData( std::vector<double>& pulse_tstart_, std::vector<double>& pulse_promptpe_, std::vector<double>& pulse_totpe_ ) {
    pulse_tstart = pulse_tstart_;
    pulse_promptpe = pulse_promptpe_;
    pulse_totpe = pulse_totpe_;
  }

  void OpFeatureVector::makeFeatureVector( std::vector<double>& featurevec ) {
    // take time and pe vectors, e.g. (t1, t2, t3 ), (p1,p2,p3), (tot1, tot2, tot3) 
    // and unroll them into a flat array, e.g. (t1,p1,tot1,t2,p2,tot2,...)
    featurevec.clear();
    featurevec.reserve( pulse_tstart.size()*3 );
    for ( unsigned int i=0; i<pulse_tstart.size(); i++ ) {
      featurevec.push_back( pulse_tstart.at(i) );
      featurevec.push_back( pulse_promptpe.at(i) );
      featurevec.push_back( pulse_totpe.at(i) );
    }

  }

}
