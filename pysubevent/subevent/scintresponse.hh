#include <vector>

namespace cpysubevent {

  void calcScintResponseCPP( std::vector< float >& fexpectation, 
			     int tstart, int tend, int maxt, float sig, float maxamp, float fastconst, float slowconst, float nspertick );
}
