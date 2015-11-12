#include "FlashTHitMap.hh"
#include <cstring>

#include "Flash.hh"

namespace subevent {

  FlashTHitMap::FlashTHitMap( int nchans, int nticks, float t0 ) {
    NTICKS = nticks;
    NCHANS = nchans;
    T0 = t0;
    init();
  }

  FlashTHitMap::~FlashTHitMap() {
    delete [] thitmap;
    delete [] nhitmap;
  }


  void FlashTHitMap::init() {
    thitmap = new Flash*[NTICKS*NCHANS];
    nhitmap = new int[NTICKS];
    std::memset( nhitmap, 0, sizeof(int)*NTICKS );
  }

  bool FlashTHitMap::inRange( int tick ) {
    if ( tick>=NTICKS || tick < 0 )
      return false;
    return true;
  }

  int FlashTHitMap::getNhits( int tick ) {
    // tick is checked at public functions
    return *(nhitmap+tick);
  }

  void FlashTHitMap::addToMap( int tick, Flash* ptrflash ) {
    int nhits = getNhits( tick ); 
    if (nhits+1>=NTICKS)
      return; // vector is full. don't add hit from same channel twice
    *(thitmap + tick*NCHANS + nhits ) = ptrflash;
    nhitmap[tick]++;
  }

  void FlashTHitMap::getFlashes( int tick, std::vector<Flash*>& flashptrlist ) {
    if (!inRange(tick) )
      return;
    int nhits = getNhits( tick );
    for (int i=0; i<nhits; i++) {
      flashptrlist.push_back( *(thitmap + tick*NCHANS + i ) );
    }
  }

  void FlashTHitMap::addFlash( int tstart, int tend,  Flash* ptrflash ) {
    for (int t=tstart; t<=tend; t++) {
      if ( !inRange(t) ) continue;
      if ( t>=NTICKS ) 	break;
      addToMap( t, ptrflash );
    }
  }

}
