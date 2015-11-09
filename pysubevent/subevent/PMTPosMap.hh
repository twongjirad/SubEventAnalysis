#ifndef __PMTPOSMAP__
#define __PMTPOSMAP__

#include <vector>

namespace subevent {

  class PMTPosMap {
    
  public:
    PMTPosMap();
    ~PMTPosMap();
    
    static const double FEMCH[36][3]; // sorry
    
    static bool GetPos( int femch, double pos[] );
    static bool GetPos( int femch, std::vector<double>& pos );
    
  
  };

}


#endif
