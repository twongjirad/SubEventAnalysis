#ifndef __FlashTHitMap__
#define __FlashTHitMap__

/* 
   ------------------------------------------------------------
   This class provides a map we can refer to later to
   get time aligned hits
   ------------------------------------------------------------
*/
#include <vector>


namespace subevent {

  class Flash;

  class FlashTHitMap {

  public:
    FlashTHitMap( int nchans, int nticks, float t0 );
    ~FlashTHitMap();

    void addFlash( int tstart, int tend, Flash* ptrflash );
    void getFlashes( int tbin, std::vector<Flash*>& flashlist );

  protected:
    
    void init();
    Flash** thitmap;
    int* nhitmap;
    int NCHANS;
    int NTICKS;
    float T0;
    void addToMap( int tick, Flash* ptrflash );
    int getNhits( int tick );
    bool inRange( int tick );
    


  };


}


#endif
