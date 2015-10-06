#ifndef __SubEventList__
#define __SubEventList__

#include "SubEvent.hh"
#include <vector>

namespace subevent {

  typedef std::vector< SubEvent >::iterator SubEventListIter;

  class SubEventList { 

  public:
    SubEventList();
    ~SubEventList();
    
    int add( SubEvent&& opflash );
    SubEvent& get( int i );
    SubEventListIter begin();
    SubEventListIter end();
    void sortByTime();
    void sortByCharge();
    void sortByAmp();
    int size() { return fSubEventes.size(); };
    void clear() { fSubEventes.clear(); fSubEventes.reserve(20); };
    bool sortedByTime() { if (sortMethod==kByTime) return true; else return false; }; 
    bool sortedByCharge() { if (sortMethod==kByCharge) return true; else return false; }; 
    bool sortedByAmp() { if (sortMethod==kByAmp) return true; else return false; }; 

  protected:
    std::vector< SubEvent > fSubEventes;

    typedef enum { kUnsorted=-1, kByTime, kByCharge, kByAmp } SortMethod_t;
    SortMethod_t sortMethod;

    static bool compareTime( SubEvent& t1, SubEvent& t2 ) {
      if (t1.tstart_ns<t2.tstart_ns )
	return true;
      else
	return false;
    };
    static bool compareArea( SubEvent& q1, SubEvent& q2 ) {
      if ( q1.totpe<q2.totpe ) return true;
      else return false;
    };
    static bool compareAmp( SubEvent& amp1, SubEvent& amp2 ) {
      if ( amp1.maxamp<amp2.maxamp ) return true;
      else return false;
    };


  };

}




#endif
