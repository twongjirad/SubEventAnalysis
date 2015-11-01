#ifndef __OpFeatureVector__
#define __OpFeatureVector__

#include <vector>

namespace optrackfit {

  class OpFeatureVector {

  public:

    OpFeatureVector();
    OpFeatureVector( std::vector<double>& pulse_tstart, std::vector<double>& pulse_promptpe, std::vector<double>& pulse_totpe );
    ~OpFeatureVector();

    void setData( std::vector<double>& pulse_tstart, std::vector<double>& pulse_promptpe, std::vector<double>& pulse_totpe );
    double getTstart( int ch ) { return pulse_tstart.at(ch); };
    double getPromptPE( int ch ) { return pulse_promptpe.at(ch); };
    double getTotalPE( int ch ) { return pulse_totpe.at(ch); };
    void makeFeatureVector( std::vector<double>& featurevec );

    // entry value is channel
    std::vector<double> pulse_tstart;
    std::vector<double> pulse_promptpe;
    std::vector<double> pulse_totpe;

  };
  
}

#endif
