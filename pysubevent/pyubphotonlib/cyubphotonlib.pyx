import numpy as np
cimport numpy as np

import cython
cimport cython

from libcpp.vector cimport vector
from libcpp.string cimport string

cdef extern from "PhotonVoxels.h" namespace "ubphotonlib":
  cdef cppclass PhotonVoxels:
    PhotonVoxels( double xMin, double xMax, double yMin, double yMax, double zMin, double zMax, int N=0 ) except +
    
  cdef cppclass PhotonVoxelDef:
    PhotonVoxelDef( double xMin, double xMax, int xN, double yMin, double yMax, int yN, double zMin, double zMax, int zN) except +
    int GetVoxelID( double* pos ) const                             

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
    

cdef class  PyPhotonVoxelDef:
  cdef PhotonVoxelDef *thisptr  # hold a C++ instance which we're wrapping
  def __init__( self, double xMin, double xMax, int xN, double yMin, double yMax, int yN, double zMin, double zMax, int zN ):
      self.thisptr = new PhotonVoxelDef( xMin, xMax, xN, yMin, yMax, yN, zMin, zMax, zN )
  def __delloc__(self):
      del self.thisptr
  def getVoxelID( self, np.ndarray[np.float, ndim=1] pos ):
      cdef int voxid = self.thisptr.GetVoxelID( <double*>pos.data )
      return voxid

cdef class PyPhotonLibrary:
  cdef PhotonLibrary *thisptr # hold a C++ instance which we're wrapping
  def __init__( self, str libfile, PyPhotonVoxelDef voxeldef, int NOpChannels ):
      self.thisptr = new PhotonLibrary()
      cdef string sfile = libfile
      self.thisptr.LoadLibraryFile( sfile, voxeldef.thisptr, NOpChannels )
  def getCounts( self, np.ndarray[np.float_t, ndim=1] pos, int opchannel ):
      return self.thisptr.GetCounts( <double*>pos.data, opchannel )
  def getOpChannelCounts( self, np.ndarray[np.float_t, ndim=1] pos ):
      cdef vector[float] opchcounts
      self.thisptr.GetCounts( <double*>pos.data, opchcounts )
      return opchcounts
