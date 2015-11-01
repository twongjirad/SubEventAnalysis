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
    double fprompt;
    double sig_t;
    double sig_promptpe;
    double sig_totpe;
    double detcenter[3];
    double detsigma[3];
    double Clar;
    
  };
  
}


#endif
