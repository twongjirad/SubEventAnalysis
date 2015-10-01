# cython: profile=True

import numpy as np
cimport numpy as np
import math

import pysubevent.pycfdiscriminator.cfdiscriminator as cfd
import pysubevent.utils.pedestal as ped
from pysubevent.pysubevent.subevent import ChannelSubEvent, SubEvent
import pysubevent.pysubevent.cysubeventdisc as cyse

import json

import cython
cimport cython
from cython.operator cimport dereference as deref

DTYPEUINT16 = np.uint16
ctypedef np.uint16_t DTYPEUINT16_t
DTYPEINT16 = np.int16
ctypedef np.int16_t DTYPEINT16_t
DTYPEFLOAT32 = np.float32
ctypedef np.float32_t DTYPEFLOAT32_t
DTYPEFLOAT = np.float
ctypedef np.float_t DTYPEFLOAT_t


# ====================================================================================================
# calcScintResponse

# NATIVE C+++
from libcpp.vector cimport vector

cdef extern from "scintresponse.hh" namespace "subevent":
   cdef void calcScintResponseCPP( vector[ double ]& fexpectation, int tstart, int tend, int maxt, float sig, float maxamp, float fastconst, float slowconst, float nspertick )
                                   

cpdef pyCalcScintResponse( int tstart, int tend, int maxt, float sig, float maxamp, float fastconst, float slowconst, float nspertick ):
    cdef vector[double] amp
    calcScintResponseCPP( amp, tstart, tend, maxt, sig, maxamp, fastconst, slowconst, nspertick )
    tdc = range(tstart,tend)
    return zip(tdc,amp)

# compiled python

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

    return expect

# ====================================================================================================
# findOneSubEvent
# Native c++

cimport SubEventModConfig
from SubEventModConfig cimport SubEventModConfig
from pysubeventmodconfig import pySubEventModConfig
from subeventdata cimport Flash
from subeventdata import pyFlash

cdef extern from "SubEventModule.hh" namespace "subevent":
    cdef int findChannelFlash( int channel, vector[double]& waveform, SubEventModConfig& config, Flash& returned_flash )

# python wrapper to native c++
cpdef findOneSubEventCPP( int channel, np.ndarray[DTYPEFLOAT_t, ndim=1] waveform, pyconfig ):
    """
    channel: int
    waveform: numpy array
    config: pySubEventModConfig
    """
    cdef int nsubevents = 0
    cdef Flash opflash
    cdef SubEventModConfig* cppconfig = new SubEventModConfig()
    nsubevents = findChannelFlash( channel, waveform, deref(cppconfig), opflash )
    #ChannelSubEvent( ch, tstart, tend, tmax, maxamp, expectation )
    flash = pyFlash( opflash.ch, opflash.tstart, opflash.tend, opflash.tmax, opflash.maxamp, opflash.expectation )
    flash.waveform = opflash.waveform
    return flash

# compiled python
cpdef findOneSubEvent( np.ndarray[DTYPEFLOAT_t, ndim=1] waveform, cfdconf, config, ch ):
    """
    waveform: numpy array
    cfdconf: cfd.cfdiscConfig
    ch: int
    """

    # calculate expectation in first bin
    #pbin1_fast = config.fastfraction*prob_exp( 0, cfdconf.nspersample, 1.0/config.fastconst )
    #pbin1_slow = config.slowfraction*prob_exp( 0, cfdconf.nspersample, 1.0/config.slowconst )
    #pbin1 = pbin1_fast + pbin1_slow # expected fraction of combined slow-fast exponential in first bin
    
    # Find peaks
    cfdvec = cfd.runCFdiscriminator( waveform, cfdconf )
    peaks_sorted = cfdvec.getAmpOrderedList( reverse=True )

    # Sort by diff height, get biggest and make a subevent out of it
    if len(peaks_sorted)>0:
        tstart = peaks_sorted[0].tfire
        maxamp = peaks_sorted[0].maxamp
        tmax   = peaks_sorted[0].tmax
        #scale = waveform[tmax]/pbin1
        tend = tstart
        spe_sigma = 4.0*cfdconf.nspersample

        # python
        #expectation = calcExpectation()

        # cythonized!
        #expectation = cyse.calcScintResponse( np.maximum(0,tmax-20), len(waveform), tmax, spe_sigma, (maxamp-cfdconf.pedestal), config.fastconst, config.slowconst, cfdconf.nspersample )

        # native c++
        expectation = cyse.pyCalcScintResponse( np.maximum(0,tmax-20), len(waveform), tmax, spe_sigma, (maxamp-cfdconf.pedestal), config.fastconst, config.slowconst, cfdconf.nspersample )
        
        tend = tstart + len(expectation)

        #print expectation[:10]
        #print expectation_old[:10]
        #raw_input()

        return ChannelSubEvent( ch, tstart, tend, tmax, maxamp, expectation )
    return None


cpdef cyRunSubEventDiscChannel( np.ndarray[DTYPEFLOAT_t, ndim=1] waveform, config, ch, retpostwfm=False ):
    """
    Multiple pass strategy.
    (1) Find peaks using CFD
    (2) Pick biggest peak
    (3) Define expected signal using fast and slow fractions
    (4) Define start and end this way
    (5) Subtract off subevent
    (6) Repeat (1)-(5) until all disc. peaks are below threshold
    * Note this is time hog now *
    """
    subevents = []

    # build configuration
    config.fastconst = 20.0
    config.sigthresh = 3.0
    cdfthresh = config.threshold
    cfdconf = cfd.cfdiscConfig( config.discrname, threshold=cdfthresh, deadtime=config.deadtime, delay=config.delay, width=config.width )
    cfdconf.pedestal = ped.getpedestal( waveform, config.pedsamples, config.pedmaxvar )  # will have to calculate this at some point
    if cfdconf.pedestal is None:
        return subevents # empty -- bad baseline!
    cfdconf.nspersample = 15.625
    #print pbin1, config.fastconst, config.slowconst

    # make our working copy of the waveform
    wfm = np.copy( waveform )

    # find subevent
    cdef int maxsubevents = 20
    cdef int nsubevents = 0
    cdef int t = 0
    cdef float fx = 0.0
    cdef float sig = 0.0
    cdef float thresh = 0.0
    cdef float chped = cfdconf.pedestal
    
    while nsubevents<maxsubevents:
        # find subevent
        subevent = findOneSubEvent( wfm, cfdconf, config, ch )
        
        if subevent is not None:
            subevents.append(subevent)
        else:
            break
        # subtract waveform below subevent threshold
        for (t,fx) in subevent.expectation:
            
            sig = np.sqrt( fx/20.0 ) # units of pe
            thresh =  fx + 3.0*sig*20.0 # 3 sigma times pe variance

            #if fx*config.sigthresh > wfm[t]-config.pedestal:
            if wfm[t]-chped < thresh:
                wfm[t] = chped
        nsubevents += 1
        #break

    if retpostwfm:
        return subevents, wfm
    else:
        return subevents


