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
# SubEvent Data Types
# ====================================================================================================

from subeventdata cimport Flash, FlashList, SubEvent, SubEventList, WaveformData
cimport numpy as np
import numpy as np

# PyFlash
# -------

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


#  pySubEvent
# ------------

cdef class pySubEvent:
    cdef SubEvent* thisptr
    def __cinit__( self ):
        self.thisptr = NULL
    def __dealloc__( self ):
        del self.thisptr
    def getFlash( self, i ):
        if self.thisptr==NULL:
            print "pySubEvent pointer to c++ class is NULL! Cannot load any flashes"
            return
        apyflash = pyFlash()
        apyflash.thisptr = &(self.thisptr.flashes.get( i ))
        return apyflash
    def getFlashList( self ):
        flashlist = []
        for iflash in range(0,self.thisptr.flashes.size()):
            flashlist.append( self.getFlash( iflash ) )
        return flashlist
    property tstart_sample:
        def __get__(self): return self.thisptr.tstart_sample
    property tstart_end:
        def __get__(self): return self.thisptr.tend_sample
    property totpe:
        def __get__(self): return self.thisptr.totpe
    property maxamp:
        def __get__(self): return self.thisptr.maxamp
            

cdef makePySubEventFromObject( SubEvent* subevent ):
    obj = pySubEvent()
    obj.thisptr = subevent
    return obj


cdef class pySubEventList:
    cdef SubEventList* thisptr
    def __cint__(self):
        self.thisptr = NULL
    def get( self, i ):
        return makePySubEventFromObject( &(self.thisptr.get(i)) )
    def sortByTime(self):
        self.thisptr.sortByTime()
    def sortByCharge(self):
        self.thisptr.sortByCharge()
    def sortByAmp(self):
        self.thisptr.sortByAmp()
    property size:
        def __get__(self): return self.thisptr.size()
    property sortedbytime:
        def __get__(self): return self.thisptr.sortedByTime()
    property sortedbycharge:
        def __get__(self): return self.thisptr.sortedByCharge()
    property sortedbyamp:
        def __get__(self): return self.thisptr.sortedByAmp()


# pyWaveformData
# ---------------

cdef class pyWaveformData:
    cdef WaveformData* thisptr
    def __cinit__(self, np.ndarray[np.float_t,ndim=2] wfms ):
        self.thisptr = new WaveformData()
        for ch in range(0,wfms.shape[1]):
            self.thisptr.set( ch, wfms[:,ch] )
    def __dealloc__(self):
        del self.thisptr
    def get( self, int ch ):
        return np.asarray( self.thisptr.get( ch ) )


# SubEventModConfig c++ wrapper
# ------------------------------

from SubEventModConfig cimport SubEventModConfig

cdef class pySubEventModConfig:
    cdef SubEventModConfig* thisptr
    cdef str discrname
    def __cinit__( self, discrname, configfile ):
        self.thisptr = new SubEventModConfig()
        self.discrname = discrname
        self.loadFromFile( configfile )
    def __dealloc__( self ):
        del self.thisptr
    def loadFromFile( self, configfile ):
        f = open( configfile )
        jconfig = json.load( f )
        self.thisptr.cfdconfig.threshold = int(jconfig['config'][self.discrname]['threshold'])  # threshold
        self.thisptr.cfdconfig.deadtime  = int(jconfig['config'][self.discrname]['deadtime'])   # deadtme
        self.thisptr.cfdconfig.delay     = int(jconfig['config'][self.discrname]['delay'])      # delay
        self.thisptr.cfdconfig.width     = int(jconfig['config'][self.discrname]['width'])      # sample width to find max ADC
        self.thisptr.cfdconfig.gate      = int(jconfig['config'][self.discrname]['gate'])       # coincidence gate
        self.thisptr.fastfraction = float(jconfig["fastfraction"])
        self.thisptr.slowfraction = float(jconfig["slowfraction"])
        self.thisptr.fastconst_ns    = float(jconfig["fastconst"])
        self.thisptr.slowconst_ns    = float(jconfig["slowconst"])
        self.thisptr.pedsamples   = 100
        self.thisptr.npresamples   = 5
        self.thisptr.pedmaxvar    = 1.0
        self.thisptr.spe_sigma = 4.0*15.625
        self.thisptr.nspersample = 15.625
        self.thisptr.hgslot = 5
        self.thisptr.lgslot = 6
        self.thisptr.flashgate = int(jconfig["flashgate"])
        self.thisptr.maxsubeventloops = 50
        self.thisptr.ampthresh = float(jconfig["ampthresh"])
        self.thisptr.hitthresh = int(jconfig["hitthresh"])
        f.close()
    property cfd_threshold:
      def __get__(self): return self.thisptr.cfdconfig.threshold
      def __set__(self, x0): self.thisptr.cfdconfig.threshold = x0
    property fastconst:
      def __get__(self): return self.thisptr.fastconst_ns
      def __set__(self, x0): self.thisptr.fastconst_ns = x0
    property nspersample:
      def __get__(self): return self.thisptr.nspersample
    property npresamples:
      def __get__(self): return self.thisptr.npresamples


# ====================================================================================================
# SubEventModule Routines
# ====================================================================================================

# ------------------------------------------------------------------------------------------
# calcScintResponse
# ------------------------------------------------------------------------------------------

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

      

# ------------------------------------------------------------------------------------------
# findOneSubEvent
# ------------------------------------------------------------------------------------------

# Native c++

cdef extern from "SubEventModule.hh" namespace "subevent":
    cdef int findChannelFlash( int channel, vector[double]& waveform, SubEventModConfig& config, Flash& returned_flash )

# python wrapper to native c++
cpdef findOneSubEventCPP( int channel, np.ndarray[DTYPEFLOAT_t, ndim=1] waveform, pySubEventModConfig pyconfig ):
    """
    channel: int
    waveform: numpy array
    config: pySubEventModConfig
    """
    cdef int nsubevents = 0
    cdef Flash opflash
    cdef SubEventModConfig* cppconfig = pyconfig.thisptr
    nsubevents = findChannelFlash( channel, waveform, deref(cppconfig), opflash )
    #flash = pyFlash( opflash.ch, opflash.tstart, opflash.tend, opflash.tmax, opflash.maxamp, np.asarray( opflash.expectation ) )
    #print opflash.ch, opflash.tstart, opflash.tend, opflash.tmax, opflash.maxamp
    flash = pyFlash.fromValues( opflash.ch, opflash.tstart, opflash.tend, opflash.tmax, opflash.maxamp, np.asarray( opflash.expectation ) ) 
    flash.addWaveform( waveform[opflash.tstart:np.minimum(len(waveform), opflash.tend)] )
    #flash = pyFlash()
    #<Flash*>(flash.thisptr) = opflash
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


# ------------------------------------------------------------------------------------------
# RunSubEventDiscChannel: Find subevents in a given beam window
# ------------------------------------------------------------------------------------------

# compiled python
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


# native c++
from subeventdata cimport FlashList

cdef extern from "SubEventModule.hh" namespace "subevent":
     cdef int getChannelFlashes( int channel, vector[double]& waveform, SubEventModConfig& config, FlashList& flashes, vector[double]& postwfm )

# python wrapper to native cpp
cpdef getChannelFlashesCPP( int channel,  np.ndarray[DTYPEFLOAT_t, ndim=1] waveform, pySubEventModConfig pyconfig, ret_postwfm=False ):
    """
    returns flashes in the waveform

    inputs
    ------
    channel
    waveform
    config
    ret_postwfm: function returns the waveform left over after subevent processing (algorithm subtracts regions with pulses)
    output
    ------
    list of pyFlash objects
    ndarray, if ret_postwfm==True
    """
    cdef vector[double] postwfm
    cdef FlashList cpp_flashes
    numflashes = getChannelFlashes( channel, waveform, deref(pyconfig.thisptr), cpp_flashes, postwfm )
    print "ch=",channel," numflashes=",numflashes
    cdef np.ndarray[DTYPEFLOAT_t, ndim=1] postarr = np.asarray( postwfm )
    if numflashes==0:
        if ret_postwfm:
            return [],postarr
        else:
            return []
    
    # package flashes
    flashes = []
    cpp_flashes.sortByTime()
    for i in range(0,cpp_flashes.size()):
        flash = pyFlash.fromValues( cpp_flashes.get(i).ch, cpp_flashes.get(i).tstart, cpp_flashes.get(i).tend, cpp_flashes.get(i).tmax, cpp_flashes.get(i).maxamp, np.asarray( cpp_flashes.get(i).expectation ) )
        flash.addWaveform( waveform[ cpp_flashes.get(i).tstart: np.minimum( len(waveform), cpp_flashes.get(i).tend ) ] )
        flashes.append( flash )
    
    if ret_postwfm:
        return flashes,postarr
    else:
        return flashes

# ------------------------------------------------------------------------------------------
# formSubEvents
# ------------------------------------------------------------------------------------------

# native c++
from libcpp.map cimport map
        
cdef extern from "SubEventModule.cc" namespace "subevent":
    void formSubEvents( WaveformData& wfms, SubEventModConfig& config, map[ int, double ]& pmtspemap, SubEventList& subevents )

cpdef formSubEventsCPP( pyWaveformData pywfms, pySubEventModConfig pyconfig, pmtspedict ):
    cdef map[int,double] pmtspemap = pmtspedict # why not
    subevents = pySubEventList()
    subevents.thisptr = new SubEventList()
    formSubEvents( deref(pywfms.thisptr), deref(pyconfig.thisptr), pmtspemap, deref(subevents.thisptr) )

    cdef SubEvent* asubevent = NULL
    subevents.sortByTime()
    subeventlist = []
    for isubevent in range(0,subevents.size):
        subeventlist.append( subevents.get(isubevent) )
        
    return subeventlist
