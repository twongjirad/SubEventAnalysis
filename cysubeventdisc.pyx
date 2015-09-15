# cython: profile=True

import numpy as np
cimport numpy as np
import math

import cython
cimport cython

DTYPEUINT16 = np.uint16
ctypedef np.uint16_t DTYPEUINT16_t
DTYPEINT16 = np.int16
ctypedef np.int16_t DTYPEINT16_t
DTYPEFLOAT32 = np.float32
ctypedef np.float32_t DTYPEFLOAT32_t

cpdef calcScintResponse( int tstart, int tend, int maxt, float sig, float maxamp, float fastconst, float slowconst, float nspertick ):
    """
    t=0 is assumed to be max of distribution
    """
    # slow component shape: expo convolved with gaus
    t_smax = 95.0 # peak of only slow component. numerically solved for det. smearing=3.5*15.625 ns, decay time const= 1500 ns
    t_fmax = 105.0 # numerically solved for det. smearing=3.5*15.625 ns, decay time const= 6 ns
    #dt_smax = -10.0 # expect slow comp peak to be 10 ns earlier than fast component peak
    smax = np.exp( sig*sig/(2*slowconst*slowconst) - t_fmax/slowconst )*(1 - math.erf( (sig*sig - slowconst*t_fmax )/(np.sqrt(2)*sig*slowconst ) ) )
    # normalize max at fast component peak
    As = 0.3*maxamp/smax
    #s = np.exp( sig*sig/(2*slowconst*slowconst))*(1-math.erf( (sig*sig)/(np.sqrt(2)*sig*slowconst ) ) )
    #s = maxamp*np.exp( sig*sig/(2*slowconst*slowconst) - t/slowconst )*(1 - math.erf( (sig*sig - slowconst*t )/(np.sqrt(2)*sig*slowconst ) ) )

    # fast component: since time const is smaller than spe response, we model as simple gaussian
    #
    #fmax = np.exp( -0.5*farg*farg )
    Af = 0.8*maxamp
    #f = Af*np.exp( -0.5*farg*farg )

    #farg = t/sig
    #s = As*np.exp( sig*sig/(2*slowconst*slowconst) - t/slowconst )*(1 - math.erf( (sig*sig - slowconst*t )/(np.sqrt(2)*sig*slowconst ) ) )

    cdef int arrlen = tend-tstart
    cdef bint rising = True
    cdef float t = 0.0
    cdef float tmax_ns = maxt*nspertick
    cdef float tstart_ns = tstart*nspertick
    #cdef np.ndarray expectation_out = np.zeros(arrlen, dtype=DTYPEFLOAT32)
    expect = []

    for tdc in range( 0, arrlen):
        # convert to time
        t = (tstart_ns + float(tdc*nspertick)) - tmax_ns
        farg = (t)/sig
        f = Af*np.exp( -0.5*farg*farg )
        s = As*np.exp( sig*sig/(2*slowconst*slowconst) - (t)/slowconst )*(1 - math.erf( (sig*sig - slowconst*(t) )/(np.sqrt(2)*sig*slowconst ) ) )
        amp = f+s
        expect.append( (tstart+tdc,amp) ) # amp vs tdc
        if rising and amp>20:
            rising = False
        elif not rising and amp<0.1:
            break

    #return fastfraction*f + slowfraction*s
    #print t, f, s
    return expect

# NATIVE C+++
from libcpp.vector cimport vector

cdef extern from "pysubevent/scintresponse.hh" namespace "cpysubevent":
   cdef void calcScintResponseCPP( vector[ float ]& fexpectation, int tstart, int tend, int maxt, float sig, float maxamp, float fastconst, float slowconst, float nspertick )
                                   

cpdef pyCalcScintResponse( int tstart, int tend, int maxt, float sig, float maxamp, float fastconst, float slowconst, float nspertick ):
    cdef vector[float] amp
    calcScintResponseCPP( amp, tstart, tend, maxt, sig, maxamp, fastconst, slowconst, nspertick )
    tdc = range(tstart,tend)
    return zip(tdc,amp)
