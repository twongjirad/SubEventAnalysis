# cython: profile=True

import numpy as np
cimport numpy as np
import math

import pysubevent.pycfdiscriminator.cfdiscriminator as cfd
import pysubevent.utils.pedestal as ped
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
    cdef bint __isowner
    #cdef fromValues( cls,  int ch, int tstart, int tend, int tmax, float maxamp, np.ndarray[np.float_t,ndim=1] expectation ):
    #    obj = pyFlash()
    #    obj.fillValues( ch, tstart, tend, tmax, maxamp, expectation )
    #    return obj
    def __cinit__( self ):
        self.__isowner = True
    def fillValues( self, int ch, int tstart, int tend, int tmax, float maxamp, np.ndarray[np.float_t,ndim=1] expectation ):
        self.thisptr = new Flash()
        self.thisptr.ch = ch
        self.thisptr.tstart = tstart
        self.thisptr.tend   = tend
        self.thisptr.tmax   = tmax
        self.thisptr.maxamp = maxamp
        self.thisptr.expectation = expectation
    def __dealloc__( self ):
        if self.__isowner:
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
    property area:
        def __get__(self): return self.thisptr.area
    property area_prompt:
        def __get__(self): return self.thisptr.area30
    property isowner:
        def __get__(self): return self.__isowner
        def __set__(self,bint x): self.__isowner = x


# PyFlashList
# -----------
cdef class pyFlashList:
    cdef FlashList* thisptr
    cdef bint __isowner
    def __cint__(self):
        self.thisptr = NULL
        self.__isowner = True
    def __dealloc__( self ):
        if self.__isowner and self.thisptr!=NULL:
            del self.thisptr
    def getFlash( self, i ):
        apyflash = pyFlash()
        apyflash.thisptr = &(self.thisptr.get( i ))
        apyflash.isowner = False
        return apyflash
    def getFlashes( self ):
        flashes = []
        for iflash in range(0,self.thisptr.size()):
            aflash = self.getFlash( iflash )
            flashes.append( aflash )
        return flashes
    def addFlash( self, pyFlash flash ):
        flash.__isowner = False
        self.thisptr.transferFlash( deref( flash.thisptr ) )
    property size:
        def __get__(self): return self.thisptr.size()

#  pySubEvent
# ------------

cdef class pySubEvent:
    #cdef SubEvent* thisptr
    #cdef bint __isowner
    def __cinit__( self ):
        self.thisptr = NULL
        self.__isowner = True
    def __dealloc__( self ):
        if self.__isowner and self.thisptr!=NULL:
            del self.thisptr
    def getFlash( self, i ):
        if self.thisptr==NULL:
            print "pySubEvent pointer to c++ class is NULL! Cannot load any flashes"
            return
        apyflash = pyFlash()
        apyflash.thisptr = &(self.thisptr.flashes.get( i ))
        apyflash.isowner = False
        return apyflash
    def getFlashList( self ):
        flashlist = []
        for iflash in range(0,self.thisptr.flashes.size()):
            aflash = self.getFlash( iflash )
            aflash.isowner = False
            flashlist.append( aflash )
        return flashlist
    def getFlash2List( self ):
        flashlist = []
        for iflash in range(0,self.thisptr.flashes_pass2.size()):
            apyflash = pyFlash()
            apyflash.thisptr = &(self.thisptr.flashes_pass2.get(iflash))
            apyflash.isowner = False
            flashlist.append( apyflash )
        return flashlist
    def addFlashes( self, pyFlashList flashes ):
        self.thisptr.transferFlashes( deref( flashes.thisptr ) )
    property tstart_sample:
        def __get__(self): return self.thisptr.tstart_sample
        def __set__(self,x): self.thisptr.tstart_sample = x
    property tend_sample:
        def __get__(self): return self.thisptr.tend_sample
        def __set__(self,x): self.thisptr.tend_sample = x
    property totpe:
        def __get__(self): return self.thisptr.totpe
    property maxamp:
        def __get__(self): return self.thisptr.maxamp
    property isowner:
        def __get__(self): return self.__isowner
        def __set__(self,bint x): self.__isowner = x


            
cdef makePySubEventFromObject( SubEvent* subevent ):
    obj = pySubEvent()
    obj.thisptr = subevent
    return obj


cdef class pySubEventList:
    cdef SubEventList* thisptr
    def __cint__(self):
        self.thisptr = NULL
    def get( self, i ):
        apysubevent = makePySubEventFromObject( &(self.thisptr.get(i)) )
        apysubevent.isowner = False
        return apysubevent
    def getlist( self ):
        subevents = []
        for i in range(0,self.size):
            subevents.append( self.get(i) )
        return subevents
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
    def __cinit__(self):
        self.thisptr = new WaveformData()
    def storeWaveforms( self, np.ndarray[np.float_t,ndim=2] wfms ):
        for ch in range(0,wfms.shape[1]):
            self.thisptr.set( ch, wfms[:,ch], False )
    def __dealloc__(self):
        del self.thisptr
    def get( self, int ch ):
        return np.asarray( self.thisptr.get( ch ) )
    def calcBaselineInfo( self ):
        self.thisptr.calcBaselineInfo()
    def getbaseline( self, int ch ):
        return np.asarray( self.thisptr.getbaseline( ch ) )

from subeventdata cimport CosmicWindowHolder
cdef class pyCosmicWindowHolder:
    cdef CosmicWindowHolder* thisptr
    cdef bint __isowner
    def __cinit__(self):
        self.thisptr = new CosmicWindowHolder()
        self.__isowner = True # default, wrapper owns the cpp object
    def addHGWaveform( self, int ch, int tsample, np.ndarray[np.float_t,ndim=1] wfm ):
        self.thisptr.addHG( ch, tsample, wfm )
    def addLGWaveform( self, int ch, int tsample, np.ndarray[np.float_t,ndim=1] wfm ):
        self.thisptr.addLG( ch, tsample, wfm )

# SubEventIO
# -----------
from subeventdata cimport SubEventIO

cdef class pySubEventIO:
   cdef SubEventIO* thisptr
   def __cinit__( self, str filename, str mode ):
       self.thisptr = new SubEventIO( filename, mode )
   def transferSubEventList( self, pySubEventList evlist ):
       if self.thisptr==NULL:
           print "wrapping around empty instance"
       self.thisptr.transferSubEventList( evlist.thisptr )
   def fill( self ):
       self.thisptr.fill()
   def write( self ):
       self.thisptr.write()
   def clearlist( self ):
       self.thisptr.clearlist()
   property eventid:
       def __get__(self): return self.thisptr.eventid
       def __set__(self,int x): self.thisptr.eventid = x
   property nsubevents:
       def __get__(self): return self.thisptr.nsubevents
       def __set__(self,int x): self.thisptr.nsubevents = x
   property chmaxamp:
       def __get__(self): return self.thisptr.chmaxamp
       def __set__(self,float x): self.thisptr.chmaxamp = x


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
        self.thisptr.cfdconfig_pass2.threshold = int(jconfig['config']["pass2"]['threshold'])  # threshold
        self.thisptr.cfdconfig_pass2.deadtime  = int(jconfig['config']["pass2"]['deadtime'])   # deadtme
        self.thisptr.cfdconfig_pass2.delay     = int(jconfig['config']["pass2"]['delay'])      # delay
        self.thisptr.cfdconfig_pass2.width     = int(jconfig['config']["pass2"]['width'])      # sample width to find max ADC
        self.thisptr.cfdconfig_pass2.gate      = int(jconfig['config']["pass2"]['gate'])       # coincidence gate
        self.thisptr.fastfraction = float(jconfig["fastfraction"])
        self.thisptr.slowfraction = float(jconfig["slowfraction"])
        self.thisptr.fastconst_ns    = float(jconfig["fastconst"])
        self.thisptr.slowconst_ns    = float(jconfig["slowconst"])
        self.thisptr.noslowthreshold = float(jconfig["noslowthreshold"])
        self.thisptr.pedsamples   = 100
        self.thisptr.npresamples   = 5
        self.thisptr.maxchflashes = 30
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
    property cfddelay:
      def __get__(self): return self.thisptr.cfdconfig.delay
    property flashgate:
      def __get__(self): return self.thisptr.flashgate


# ====================================================================================================
# SubEventModule Routines
# ====================================================================================================

# ------------------------------------------------------------------------------------------
# calcScintResponse
# ------------------------------------------------------------------------------------------

# NATIVE C+++
from libcpp.vector cimport vector
from libcpp.string cimport string

cdef extern from "scintresponse.hh" namespace "subevent":
   cdef void calcScintResponseCPP( vector[ double ]& fexpectation, int tstart, int tend, int maxt, float sig, float maxamp, float fastconst, float slowconst, float nspertick,
                                   float fastfrac, float slowfrac, float noslowthreshold )
                                   

cpdef pyCalcScintResponse( int tstart, int tend, int maxt, float sig, float maxamp, float fastconst, float slowconst, 
                           float nspertick, float fastfrac, float slowfrac, float noslowthreshold ):
    cdef vector[double] amp
    calcScintResponseCPP( amp, tstart, tend, maxt, sig, maxamp, fastconst, slowconst, nspertick, fastfrac, slowfrac, noslowthreshold )
    tdc = range(tstart,tend)
    return zip(tdc,amp)

# ------------------------------------------------------------------------------------------
# findOneSubEvent
# ------------------------------------------------------------------------------------------

# Native c++

cdef extern from "SubEventModule.hh" namespace "subevent":
    cdef int findChannelFlash( int channel, vector[double]& waveform, SubEventModConfig& config, string discrname, Flash& returned_flash )

# python wrapper to native c++
cpdef findOneSubEventCPP( int channel, np.ndarray[DTYPEFLOAT_t, ndim=1] waveform, pySubEventModConfig pyconfig, str discrname ):
    """
    channel: int
    waveform: numpy array
    config: pySubEventModConfig
    """
    cdef int nsubevents = 0
    cdef Flash opflash
    cdef SubEventModConfig* cppconfig = pyconfig.thisptr
    nsubevents = findChannelFlash( channel, waveform, deref(cppconfig), discrname, opflash )
    #flash = pyFlash( opflash.ch, opflash.tstart, opflash.tend, opflash.tmax, opflash.maxamp, np.asarray( opflash.expectation ) )
    #print opflash.ch, opflash.tstart, opflash.tend, opflash.tmax, opflash.maxamp
    flash = pyFlash.fromValues( opflash.ch, opflash.tstart, opflash.tend, opflash.tmax, opflash.maxamp, np.asarray( opflash.expectation ) ) 
    flash.addWaveform( waveform[opflash.tstart:np.minimum(len(waveform), opflash.tend)] )
    #flash = pyFlash()
    #<Flash*>(flash.thisptr) = opflash
    return flash


# ------------------------------------------------------------------------------------------
# getChannelFlashes: Find flashes in a channel
# ------------------------------------------------------------------------------------------

# native c++
from subeventdata cimport FlashList

cdef extern from "SubEventModule.hh" namespace "subevent":
     cdef int getChannelFlashes( int channel, vector[double]& waveform, vector[double]& baseline, SubEventModConfig& config, string discrname, FlashList& flashes, vector[double]& postwfm )

# python wrapper to native cpp
cpdef getChannelFlashesCPP( int channel,  np.ndarray[DTYPEFLOAT_t, ndim=1] waveform, np.ndarray[DTYPEFLOAT_t, ndim=1] baseline, pySubEventModConfig pyconfig, str discrname, ret_postwfm=False ):
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
    numflashes = getChannelFlashes( channel, waveform, baseline, deref(pyconfig.thisptr), discrname, cpp_flashes, postwfm )
    print "ch=",channel," numflashes=",numflashes," max(waveform)=",np.max( waveform )
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
# formFlashes
# ------------------------------------------------------------------------------------------

# native c++
from libcpp.map cimport map

cdef extern from "SubEventModule.cc" namespace "subevent":
    void formFlashes( WaveformData& wfms, SubEventModConfig& config, string discrname, FlashList& flashes, WaveformData& postwfms )

cpdef formFlashesCPP( pyWaveformData pywfms, pySubEventModConfig pyconfig, str discrname ):
   cdef FlashList* flashes = new FlashList()
   cdef WaveformData* postwfms = new WaveformData()

   formFlashes( deref( pywfms.thisptr ), deref( pyconfig.thisptr ), discrname, deref( flashes ), deref( postwfms ) )
   
   pyflashes = pyFlashList()
   pyflashes.thisptr = flashes
   
   pywfmdata = pyWaveformData()
   del pywfmdata.thisptr
   pywfmdata.thisptr = postwfms
   
   return pyflashes, pywfmdata

# ------------------------------------------------------------------------------------------
# formSubEvents
# ------------------------------------------------------------------------------------------

cdef extern from "SubEventModule.cc" namespace "subevent":
    void formSubEvents( WaveformData& wfms, SubEventModConfig& config, map[ int, double ]& pmtspemap, SubEventList& subevents, FlashList& unclaimed_flashes )

cpdef formSubEventsCPP( pyWaveformData pywfms, pySubEventModConfig pyconfig, pmtspedict ):
    cdef map[int,double] pmtspemap = pmtspedict # why not
    subevents = pySubEventList()
    subevents.thisptr = new SubEventList()

    pyflashlist = pyFlashList()
    pyflashlist.thisptr = new FlashList()

    formSubEvents( deref(pywfms.thisptr), deref(pyconfig.thisptr), pmtspemap, deref(subevents.thisptr), deref(pyflashlist.thisptr) )

    for subevent in subevents.getlist():
        print subevents, "t=",subevent.tstart_sample,"-",subevent.tend_sample," (",subevent.tstart_sample*pyconfig.nspersample,"-",subevent.tend_sample*pyconfig.nspersample," ns) nflashes=",len(subevent.getFlashList())

    return subevents, pyflashlist

# ------------------------------------------------------------------------------------------
# formCosmicWindowSubEvents
# ------------------------------------------------------------------------------------------

cdef extern from "CosmicWindowSubEvents.hh" namespace "subevent":
   cdef void formCosmicWindowSubEvents( CosmicWindowHolder& cosmics, SubEventModConfig& config, SubEventList& subevents )    

cpdef formCosmicWindowSubEventsCPP( pyCosmicWindowHolder cosmicwindows, pySubEventModConfig pyconfig ):
    cdef pySubEventList pysubevents = pySubEventList()
    pysubevents.thisptr = new SubEventList()
    formCosmicWindowSubEvents( deref( cosmicwindows.thisptr ), deref( pyconfig.thisptr ), deref( pysubevents.thisptr ) )
    return pysubevents
