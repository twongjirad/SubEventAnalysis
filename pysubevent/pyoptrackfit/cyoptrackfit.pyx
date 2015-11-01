import cython
cimport cython
from cython.operator cimport dereference as deref
from libcpp.vector cimport vector
from libcpp.string cimport string

cimport numpy as np
import numpy as np
import json


cdef extern from "OpTrackFitConfig.hh" namespace "optrackfit":
    cdef cppclass OpTrackFitConfig:
        OpTrackFitConfig() except +
        double gQE
        double LY
        double dEdx
        int NCHANS
        double NSPERTICK

cdef class pyOpTrackFitConfig:
    cdef OpTrackFitConfig* thisptr
    def __cint__( self, configfile ):
        self.thisptr = new OpTrackFitConfig()
        f = open( configfile )
        jconfig = json.load( f )
        self.thisptr.gQE = float(jconfig["gQE"])
        self.thisptr.LY  = float(jconfig["LY"])
        self.thisptr.dEdx = float(jconfig["dEdx"])
        self.thisptr.NCHANS = int(jconfig["NCHANS"])
        self.thisptr.NSPERTICK = int(jconfig["NSPERTICK"])

from pysubevent.pysubevent.subeventdata cimport SubEvent
from pysubevent.pyubphotonlib.photonlib cimport PhotonLibrary, PhotonVoxelDef

cdef extern from "OpTrackModule.hh" namespace "optrackfit":
    cdef void runOpTrackFit( SubEvent& subevent, OpTrackFitConfig& config, PhotonLibrary& photonlib )

from pysubevent.pysubevent.cysubeventdisc cimport pySubEvent
from pysubevent.pysubevent.cysubeventdisc import pySubEvent
from pysubevent.pyubphotonlib.cyubphotonlib cimport PyPhotonLibrary
from pysubevent.pyubphotonlib.cyubphotonlib import PyPhotonLibrary

cpdef runpyOpTrackFit( pySubEvent subevent, pyOpTrackFitConfig config, PyPhotonLibrary photonlib ):
    runOpTrackFit( deref(subevent.thisptr), deref(config.thisptr), deref(photonlib.thisptr) )
