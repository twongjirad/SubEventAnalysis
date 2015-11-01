from photonlib cimport *

cdef class  PyPhotonVoxelDef:
  cdef PhotonVoxelDef *thisptr  # hold a C++ instance which we're wrapping

cdef class PyPhotonLibrary:
  cdef PhotonLibrary *thisptr # hold a C++ instance which we're wrapping

