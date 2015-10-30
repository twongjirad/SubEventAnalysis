import numpy as np
cimport numpy as np

import cython
cimport cython

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
    

cdef class  PyPhotonVoxelDef:
  cdef PhotonVoxelDef *thisptr  # hold a C++ instance which we're wrapping
  def __init__( self, double xMin, double xMax, int xN, double yMin, double yMax, int yN, double zMin, double zMax, int zN ):
      self.thisptr = new PhotonVoxelDef( xMin, xMax, xN, yMin, yMax, yN, zMin, zMax, zN )
  def __delloc__(self):
      del self.thisptr
  def getVoxelID( self, np.ndarray[np.float_t, ndim=1] pos ):
      cdef int voxid = self.thisptr.GetVoxelID( <double*>pos.data )
      return voxid
  def getVoxelCenter( self, np.ndarray[np.float_t, ndim=1] pos ):
      cdef PhotonVoxel voxel = self.thisptr.GetContainingVoxel( TVector3( pos[0], pos[1], pos[2] ) )
      return np.asarray( [ voxel.GetCenter().x(), voxel.GetCenter().y(), voxel.GetCenter().z() ] )
  def getVoxelLowerCorner( self, np.ndarray[np.float_t, ndim=1] pos ):
      cdef PhotonVoxel voxel = self.thisptr.GetContainingVoxel( TVector3( pos[0], pos[1], pos[2] ) )
      return np.asarray( [ voxel.GetLowerCorner().x(), voxel.GetLowerCorner().y(), voxel.GetLowerCorner().z() ] )
  def getVoxelUpperCorner( self, np.ndarray[np.float_t, ndim=1] pos ):
      cdef PhotonVoxel voxel = self.thisptr.GetContainingVoxel( TVector3( pos[0], pos[1], pos[2] ) )
      return np.asarray( [ voxel.GetUpperCorner().x(), voxel.GetUpperCorner().y(), voxel.GetUpperCorner().z() ] )
  def getSteps( self ):
      return np.asarray( [ self.thisptr.GetSteps().x(), self.thisptr.GetSteps().y(), self.thisptr.GetSteps().z() ] )

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
