#ifndef PHOTON_LIBRARY_H
#define PHOTON_LIBRARY_H

#include <vector>
#include <string>
#include "PhotonVoxels.h"

class TChain;

namespace ubphotonlib {

  class PhotonLibrary {

  public:
    PhotonLibrary();
    ~PhotonLibrary();

    float GetCounts( size_t voxel, int opchannel );
    void GetCounts( size_t voxel,  std::vector<float>& opchan_counts );
    float GetCounts( double* pos, int opchannel );
    void GetCounts( double* pos, std::vector<float>& opchan_counts );
    void LoadLibraryFile( std::string libfile, PhotonVoxelDef* voxeldef, int NOpChannels );
    
    int NOpChannels() const {return fNOpChannels; };
    size_t NVoxels() const { return fNVoxels; };
    
  private:

    std::vector< std::vector<float> > fLookupTable; // [VoxelID,NOpChannels]
    Int_t fNOpChannels;
    Int_t fNVoxels;
    Float_t fVisibility;
    Int_t fOpChannel;
    Int_t fVoxel;
    TChain* tLib;
    PhotonVoxelDef* fVoxelDef;
    

  };
}

#endif
