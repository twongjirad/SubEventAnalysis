import cython
cimport cython
from cython.operator cimport dereference as deref
from libcpp.vector cimport vector
from libcpp.string cimport string

cimport numpy as np
import numpy as np
import json
import time


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
        int nwalkers
        int nburn
        int nsamples

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
    double lnProb( vector[double]& track_start_end, vector[double]& data_opfeatures,
                   PhotonLibrary& photonlib, OpTrackFitConfig& opconfig, vector[ vector[double] ]& chpos )

from pysubevent.pysubevent.cysubeventdisc cimport pySubEvent
from pysubevent.pysubevent.cysubeventdisc import pySubEvent
from pysubevent.pyubphotonlib.cyubphotonlib cimport PyPhotonLibrary
from pysubevent.pyubphotonlib.cyubphotonlib import PyPhotonLibrary
import emcee # the MCMC hammer

cdef genSeedTracks( pyOpTrackFitConfig config ):
    s = np.asarray( [ 150.0, 150.0, 500.0 ], dtype=np.float )
    e = np.asarray( [ 150.0, -150.0, 500.0 ], dtype=np.float )
    p0 = []
    for i in range(0,config.nwalkers):
        p1 = []
        for x in range(0,3):
            p1.append( np.random.normal( s[x], 10.0 ) )
        for x in range(0,3):
            p1.append( np.random.normal( e[x], 10.0 ) )
        p0.append( p1 )
    return p0

# this class holds the function that the sampler will run
cdef class pyOpTrackModel:
    cdef pyOpTrackFitConfig opconfig
    cdef PyPhotonLibrary photonlib
    def __cinit__(self, pyOpTrackFitConfig opconfig, PyPhotonLibrary photonlib):
        self.opconfig = opconfig    # pyOpTrackFitConfig
        self.photonlib = photonlib  # PyPhotonLibrary
        self.chpos = self.makeChannelMap()
    cpdef lnProb(self, x, opfeatures):
        return lnProb( x, opfeatures, deref(self.photonlib.thisptr), deref(self.opconfig.thisptr), self.chpos )
    def makeChannelMap(self):
        return

cpdef pyExtractFeatureVariables(  pySubEvent subevent, int NCHANS, double NSPERTICK, double TEMP_SPEAREA ):
    cdef vector[double] featurevec
    extractFeatureVariables( deref(subevent.thisptr), featurevec, NCHANS, NSPERTICK, TEMP_SPEAREA )
    return np.asarray( featurevec )

cpdef runpyOpTrackFit( pySubEvent subevent, pyOpTrackFitConfig config, PyPhotonLibrary photonlib ):
    print "[Run pyOpTrackFit] initializing"
    cdef int ndims = 6
    # generate seeds
    model = pyOpTrackModel( config, photonlib )
    p0 = genSeedTracks( config )
    # make feature vector to fit to
    opfeatures = pyExtractFeatureVariables( subevent, config.NCHANS, config.NSPERTICK, 100.0 )
    # make the MCMC sampler
    sampler = emcee.EnsembleSampler( config.nwalkers, ndims, model.lnProb, args=[opfeatures])
    print "[Run pyOpTrackFit] begin burn-in"
    burntime = time.time()
    fitpos, prob, state  = sampler.run_mcmc( p0, config.nburn )
    print "[Run pyOpTrackFit] burn-in finished: ",time.time()-burntime," secs"
    print "[Run pyOpTrackFit] begin production sampling"
    sampler.reset()
    sampletime = time.time()
    pos = sampler.run_mcmc( fitpos, config.nsamples)
    print "[Run pyOpTrackFit] samping finished: ",time.time()-sampletime," secs"
    print "[Run pyOpTrackFit] returning ensemble"
    return sampler

    



