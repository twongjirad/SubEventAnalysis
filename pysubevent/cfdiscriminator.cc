
#include "cfdiscriminator.hh"
#include <iostream>

namespace cpysubevent {
  void runCFdiscriminatorCPP( std::vector< int >& t_fire, std::vector< int >& amp_fire, std::vector< int >& maxt_fire, std::vector< int >& diff_fire,
			      double* waveform, int delay, int threshold, int deadtime, int width, int arrlen ) {
    
    // fill diff vector
    //std::cout << "Waveform: ";
    std::vector<float> diff( arrlen, 0.0);
    for ( int tdc=delay; tdc<arrlen-delay; tdc++ ) {
      //std::cout << waveform[tdc] << ", ";
      diff.at( tdc ) = waveform[tdc]-waveform[tdc-delay];
    }
    //std::cout << std::endl;

    // reset vectors
    t_fire.clear();
    t_fire.reserve(20);
    diff_fire.clear();
    diff_fire.reserve(20);
    amp_fire.clear();
    amp_fire.reserve(20);
    maxt_fire.clear();
    maxt_fire.reserve(20);

    // determine time
    //std::cout << "Diff: ";
    for ( int t=0; t<arrlen; t++ ) {
      //std::cout << diff.at(t) << ", ";
      if ( diff.at(t)>threshold && 
	   ( t_fire.size()==0 || ( t_fire.at( t_fire.size()-1 )+deadtime<t ) ) ) {
	t_fire.push_back( t-delay );
	diff_fire.push_back( int(diff.at(t)) );
      }
    }
    //std::cout << std::endl;

    // determine max amp
    for ( std::vector< int >::iterator it=t_fire.begin(); it!=t_fire.end(); it++ ) {
      int trig = *it;
      int end = trig+width;
      if ( end>arrlen )
	end = arrlen;
      int maxamp = waveform[trig];
      int maxt = trig;
      for ( int t=trig; t<end; t++ ) {
	if ( maxamp < waveform[t] ) {
	  maxamp = waveform[t];
	  maxt = t;
	}
      }

      amp_fire.push_back( maxamp );
      maxt_fire.push_back( maxt );
    }
  }
}

/*
cpdef runCFdiscriminator( np.ndarray[DTYPE_t, ndim=1] waveform, int delay, int threshold, int deadtime, int width ):
  """
  inputs:
  -------
  waveform: raw adc waveform
  delay: subtraction time delay in ticks
  threshold: to form disc. fire
  deadtime: ticks to wait before new disc. can form
  width: length of tick window to find max adc counts
  """

  cdef np.ndarray[DTYPE_t, ndim=1] diff = np.zeros( len(waveform), dtype=DTYPE )
  t_fire = []
  amp_fire = []
  maxt_fire = []
  last_fire = -1
  for tdc in range( delay, len(waveform)-delay ):
      diff[tdc] = waveform[tdc]-waveform[tdc+delay]
      
  # determine time
  for t in range(0,len(waveform)):
      if diff[t]>threshold and ( len(t_fire)==0 or (len(t_fire)>0 and t_fire[-1]+deadtime<t) ):
          t_fire.append( t-delay )
  # determine max amp
  for trig in t_fire:
      amp_fire.append( np.max( waveform[trig:np.minimum( len(waveform), trig+width )] )  )
      maxt_fire.append( trig+np.argmax( waveform[trig:np.minimum( len(waveform), trig+width )] ) )

  return zip( t_fire, amp_fire, maxt_fire )

*/
