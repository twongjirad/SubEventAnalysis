#ifndef __FLASH_HH__

#include "TObject.h"
#include <vector>

class Flash : public TObject {

public:

  Flash();
  ~Flash();

  int ch;
  int tstart;
  int tend;
  int tmax;
  float maxamp;
  std::vector< double > expectation;
  std::vector< double > waveform;

  ClassDef( Flash, 1 );

};

#endif
