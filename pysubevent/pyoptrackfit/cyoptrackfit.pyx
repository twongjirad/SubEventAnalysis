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
        double fprompt
        double sig_t
        double sig_promptpe
        double sig_totpe
        double detcenter[3]
        double detsigma[3]
        double Clar

cdef class pyOpTrackFitConfig:
    cdef OpTrackFitConfig* thisptr
    def __cinit__( self, configfile ):
        self.thisptr = new OpTrackFitConfig()
        f = open( configfile )
        jconfig = json.load( f )
        self.thisptr.gQE          = float(jconfig["gQE"])
        self.thisptr.LY           = float(jconfig["LY"])
        self.thisptr.dEdx         = float(jconfig["dEdx"])
        self.thisptr.NCHANS       = int(jconfig["NCHANS"])
        self.thisptr.NSPERTICK    = float(jconfig["NSPERTICK"])
        self.thisptr.fprompt      = float(jconfig["fprompt"])
        self.thisptr.sig_t        = float(jconfig["sig_t"])
        self.thisptr.sig_promptpe = float(jconfig["sig_promptpe"])
        self.thisptr.sig_totpe    = float(jconfig["sig_totpe"])
        self.thisptr.detcenter[0] = float(jconfig["detcenter"]["x"])
        self.thisptr.detcenter[1] = float(jconfig["detcenter"]["y"])
        self.thisptr.detcenter[2] = float(jconfig["detcenter"]["z"])
        self.thisptr.detsigma[0]  = float(jconfig["detsigma"]["x"])
        self.thisptr.detsigma[1]  = float(jconfig["detsigma"]["y"])
        self.thisptr.detsigma[2]  = float(jconfig["detsigma"]["z"])
        self.thisptr.Clar         = float(jconfig["Clar"])
        print "Loaded OpTrackFitConfig: QE=%.4f LY=%.1f"%(self.thisptr.gQE,self.thisptr.LY)


from pysubevent.pysubevent.subeventdata cimport SubEvent
from pysubevent.pyubphotonlib.photonlib cimport PhotonLibrary, PhotonVoxelDef

cdef extern from "OpTrackModule.hh" namespace "optrackfit":
    cdef void runOpTrackFit( SubEvent& subevent, OpTrackFitConfig& config, PhotonLibrary& photonlib )
    void extractFeatureVariables( SubEvent& subevent, vector[double]& featurevec, int NCHANS, double NSPERTICK, double TEMP_SPEAREA )

from pysubevent.pysubevent.cysubeventdisc cimport pySubEvent
from pysubevent.pysubevent.cysubeventdisc import pySubEvent
from pysubevent.pyubphotonlib.cyubphotonlib cimport PyPhotonLibrary
from pysubevent.pyubphotonlib.cyubphotonlib import PyPhotonLibrary

cpdef runpyOpTrackFit( pySubEvent subevent, pyOpTrackFitConfig config, PyPhotonLibrary photonlib ):
    runOpTrackFit( deref(subevent.thisptr), deref(config.thisptr), deref(photonlib.thisptr) )

cpdef pyExtractFeatureVariables(  pySubEvent subevent, int NCHANS, double NSPERTICK, double TEMP_SPEAREA ):
    cdef vector[double] featurevec
    extractFeatureVariables( deref(subevent.thisptr), featurevec, NCHANS, NSPERTICK, TEMP_SPEAREA )
    return np.asarray( featurevec )
