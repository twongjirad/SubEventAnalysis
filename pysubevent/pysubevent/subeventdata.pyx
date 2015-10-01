cimport subeventdata
cimport numpy as np
cimport numpy as np

cdef class pyFlash:
    cdef Flash* thisptr
    def __cinit__( self, int ch, int tstart, int tend, int tmax, float maxamp, np.ndarray[np.float_t,ndim=1] expectation ):
        self.thisptr = new Flash()
        self.thisptr.ch = ch
        self.thisptr.tstart = tstart
        self.thisptr.tend   = tend
        self.thisptr.tmax   = tmax
        self.thisptr.maxamp = maxamp
        self.thisptr.expectation = expectation
    def __dealloc__( self ):
        del self.thisptr
    def addWaveform( self, np.ndarray[np.float_t,ndim=1] waveform ):
        self.thisptr.waveform = waveform
        

