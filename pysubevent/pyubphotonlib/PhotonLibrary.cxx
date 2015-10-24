#include "PhotonLibrary.h"
#include "TChain.h"
#include <iostream>

namespace ubphotonlib {

  PhotonLibrary::PhotonLibrary()
  {
    fLookupTable.clear();
  }

  PhotonLibrary::~PhotonLibrary()
  {
    fLookupTable.clear();
  }

  void PhotonLibrary::LoadLibraryFile( std::string libfile, PhotonVoxelDef* voxdef, int NOpChannels ) {
    // weird that file doesn't carry these critical pieces of meta data
    fNOpChannels = NOpChannels;
    fNVoxels = voxdef->GetNVoxels();
    fVoxelDef = voxdef;
    
    tLib = new TChain("pmtresponse/PhotonLibraryData");
    tLib->Add( libfile.c_str() );
    tLib->SetBranchAddress("Voxel",      &fVoxel);
    tLib->SetBranchAddress("OpChannel",  &fOpChannel);
    tLib->SetBranchAddress("Visibility", &fVisibility);

    fLookupTable.resize( fNVoxels );

    for(size_t ivox=0; ivox!=fLookupTable.size(); ++ivox)
      fLookupTable[ivox].resize( fNOpChannels, 0 );

    size_t entry = 0;
    size_t bytes = tLib->GetEntry(entry);
    while ( bytes!=0 ) {
      fLookupTable[ fVoxel ][ fOpChannel ] = fVisibility;
      entry++;
      bytes = tLib->GetEntry(entry);
    }
    std::cout << "Loaded Photon Library (number entries=" << entry << ")" << std::endl;
  }

  float PhotonLibrary::GetCounts( size_t voxel, int opchannel ) {
    return fLookupTable[ voxel ][opchannel];
  }

  void PhotonLibrary::GetCounts( size_t voxel, std::vector<float>& opchan_counts ) {
    opchan_counts.clear();
    opchan_counts.reserve( fNOpChannels );
    for ( size_t opchan=0; opchan<fLookupTable.at(voxel).size(); opchan++ ) {
      opchan_counts.push_back( fLookupTable.at(voxel).at( opchan ) ) ;
    }
  }
  
  float PhotonLibrary::GetCounts( double* pos, int opchannel ) {
    int voxid = fVoxelDef->GetVoxelID( pos );
    return GetCounts( voxid, opchannel );
  }

  void PhotonLibrary::GetCounts( double* pos, std::vector<float>& opchan_counts ) {
    size_t voxid =(size_t)fVoxelDef->GetVoxelID( pos );
    GetCounts( voxid, opchan_counts );
  }

}
