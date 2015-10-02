cimport subeventdata
cimport numpy as np
cimport numpy as np

def makePyFlashFromValues( cls, int ch, int tstart, int tend, int tmax, float maxamp, np.ndarray[np.float_t,ndim=1] expectation ):
    obj = cls()
    obj.fillValues( ch, tstart, tend, tmax, maxamp, expectation )
    return obj

cdef class pyFlash:
    cdef Flash* thisptr
    fromValues = classmethod( makePyFlashFromValues )
    #cdef fromValues( cls,  int ch, int tstart, int tend, int tmax, float maxamp, np.ndarray[np.float_t,ndim=1] expectation ):
    #    obj = pyFlash()
    #    obj.fillValues( ch, tstart, tend, tmax, maxamp, expectation )
    #    return obj
    def __cinit__( self ):
        pass
    def fillValues( self, int ch, int tstart, int tend, int tmax, float maxamp, np.ndarray[np.float_t,ndim=1] expectation ):
        self.thisptr = new Flash()
        self.thisptr.ch = ch
        self.thisptr.tstart = tstart
        self.thisptr.tend   = tend
        self.thisptr.tmax   = tmax
        self.thisptr.maxamp = maxamp
        self.thisptr.expectation = expectation
        print "filled flash"
    def __dealloc__( self ):
        del self.thisptr
    def addWaveform( self, np.ndarray[np.float_t,ndim=1] waveform ):
        self.thisptr.waveform = waveform
    property waveform:
        def __get__( self ): return self.thisptr.waveform
        def __set__( self, wfm ): self.addWaveform( wfm )
    property expectation:
        def __get__(self): return self.thisptr.expectation
        def __set__(self, np.ndarray[np.float_t,ndim=1] wfm): self.thisptr.expectation = wfm
    property ch:
        def __get__(self): return self.thisptr.ch
        def __set__(self, int x): self.thisptr.ch = x
    property tstart:
        def __get__(self): return self.thisptr.tstart
        def __set__(self,x): self.thisptr.tstart = x
    property tend:
        def __get__(self): return self.thisptr.tend
        def __set__(self,x): self.thisptr.tend = x
    property maxamp:
        def __get__(self): return self.thisptr.maxamp
        def __set__(self,x): self.thisptr.maxamp = x
    property tmax:
        def __get__(self): return self.thisptr.tmax
        def __set__(self,x): self.thisptr.tmax = x

