#ifndef __OPTRACKFITCONFIG__
#define __OPTRACKFITCONFIG__

namespace optrackfit {
  
  class OpTrackFitConfig {
    
  public:
    
    OpTrackFitConfig();
    ~OpTrackFitConfig();
    
    double gQE; // global quantum efficiency
    double LY;  // light yield (nphotons/MeV for MIP, e.g. muon)
    double dEdx; // dEdx for MIP (muon
    int NCHANS; // number of channels
    double NSPERTICK; // time per tick
    
  };
  
}


#endif
