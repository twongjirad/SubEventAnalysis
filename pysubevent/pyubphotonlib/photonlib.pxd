from libcpp.vector cimport vector
from libcpp.string cimport string

cdef extern from "TVector3.h":
  cdef cppclass TVector3:
    TVector3( double x, double y, double z ) except +
    double x() const
    double y() const
    double z() const

cdef extern from "PhotonVoxels.h" namespace "ubphotonlib":
  cdef cppclass PhotonVoxels:
    PhotonVoxels( double xMin, double xMax, double yMin, double yMax, double zMin, double zMax, int N=0 ) except +

  cdef cppclass PhotonVoxel:
    PhotonVoxel() except+
    TVector3 GetCenter() const
    TVector3 GetLowerCorner() const
    TVector3 GetUpperCorner() const

  cdef cppclass PhotonVoxelDef:
    PhotonVoxelDef( double xMin, double xMax, int xN, double yMin, double yMax, int yN, double zMin, double zMax, int zN) except +
    int GetVoxelID( double* pos ) const
    vector[int] GetVoxelCoords( int id )
    PhotonVoxel GetContainingVoxel( TVector3 ) const
    TVector3 GetSteps() const


cdef extern from "PhotonLibrary.h" namespace "ubphotonlib":
  cdef cppclass PhotonLibrary:
    PhotonLibrary() except +
    float GetCount( size_t voxel, int opchannel )
    void GetCounts( size_t voxel, vector[ float ]& opchan_counts )
    float GetCounts( double* pos, int opchannel )
    void GetCounts( double* pos, vector[ float ]& opchan_counts )
    void LoadLibraryFile( string libfile, PhotonVoxelDef* voxeldef, int NOpChannels )
    int NOpChannels() const
    size_t NVoxels() const

