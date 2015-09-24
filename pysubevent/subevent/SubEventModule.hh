#ifndef __SubEventModule__
#define __SubEventModule__

#include <vector>
#include "SubEvent.hh"
#include "Flash.hh"
#include "SubEventModConfig.hh"

namespace subevent {

  int findChannelFlash( int ch, std::vector<double>& waveform, SubEventModConfig& config, Flash& returned_flash );

}

#endif
