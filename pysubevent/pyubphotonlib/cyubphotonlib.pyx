import numpy as np
cimport numpy as np

import cython
cimport cython

from libcpp.vector cimport vector
from libcpp.string cimport string

from photonlib cimport *

cdef class  PyPhotonVoxelDef:
  #cdef PhotonVoxelDef *thisptr  # hold a C++ instance which we're wrapping
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
  #cdef PhotonLibrary *thisptr # hold a C++ instance which we're wrapping
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
