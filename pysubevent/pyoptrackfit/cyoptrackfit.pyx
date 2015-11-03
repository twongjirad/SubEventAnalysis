import cython
cimport cython
from cython.operator cimport dereference as deref
from libcpp.vector cimport vector
from libcpp.string cimport string
from pysubevent.utils.pmtpos import getPosFromID,getDetectorCenter


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
        self.thisptr.nwalkers     = int(jconfig["nwalkers"])
        self.thisptr.nburn        = int(jconfig["nburn"])
        self.thisptr.nsamples     = int(jconfig["nsamples"])
        print "Loaded OpTrackFitConfig: QE=%.4f LY=%.1f"%(self.thisptr.gQE,self.thisptr.LY)
    property NCHANS:
       def __get__(self): return self.thisptr.NCHANS
    property NSPERTICK:
       def __get__(self): return self.thisptr.NSPERTICK
    property nwalkers:
       def __get__(self): return self.thisptr.nwalkers
    property nburn:
       def __get__(self): return self.thisptr.nburn
    property nsamples:
       def __get__(self): return self.thisptr.nsamples

cdef extern from "TrackHypothesis.hh" namespace "optrackfit":
    cdef cppclass TrackHypothesis:
         TrackHypothesis( vector[double]& start, vector[double]& end ) except +

from pysubevent.pysubevent.subeventdata cimport SubEvent
from pysubevent.pyubphotonlib.photonlib cimport PhotonLibrary, PhotonVoxelDef

cdef extern from "OpTrackModule.hh" namespace "optrackfit":
    cdef void runOpTrackFit( SubEvent& subevent, OpTrackFitConfig& config, PhotonLibrary& photonlib )
    void extractFeatureVariables( SubEvent& subevent, vector[double]& featurevec, int NCHANS, double NSPERTICK, double TEMP_SPEAREA )
    void printFeatureVector( vector[double]& featurevec )
    void makeVoxelList( TrackHypothesis& track, PhotonLibrary& photonlib, double LY, double dEdx, int NCHANS,
                        vector[ vector[double] ]& midpoints, vector[ vector[float] ]& chphotons )
    double lnProb( vector[double]& track_start_end, vector[double]& data_opfeatures,
                   PhotonLibrary& photonlib, OpTrackFitConfig& opconfig, vector[ vector[double] ]& chpos )

from pysubevent.pysubevent.cysubeventdisc cimport pySubEvent
from pysubevent.pysubevent.cysubeventdisc import pySubEvent
from pysubevent.pyubphotonlib.cyubphotonlib cimport PyPhotonLibrary, PyPhotonVoxelDef
from pysubevent.pyubphotonlib.cyubphotonlib import PyPhotonLibrary, PyPhotonVoxelDef
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
    cdef list chpos
    def __cinit__(self, pyOpTrackFitConfig opconfig, PyPhotonLibrary photonlib):
        self.opconfig = opconfig    # pyOpTrackFitConfig
        self.photonlib = photonlib  # PyPhotonLibrary
        self.chpos = self.makeChannelMap()
    cpdef lnProb(self, x, opfeatures):
        return lnProb( x, opfeatures, deref(self.photonlib.thisptr), deref(self.opconfig.thisptr), self.chpos )
    def makeChannelMap(self):
        chpos = []
        for ich in range(0,self.opconfig.NCHANS):
            chpos.append( getPosFromID( ich ) )
        return chpos

cpdef pyExtractFeatureVariables(  pySubEvent subevent, int NCHANS, double NSPERTICK, double TEMP_SPEAREA ):
    cdef vector[double] featurevec
    extractFeatureVariables( deref(subevent.thisptr), featurevec, NCHANS, NSPERTICK, TEMP_SPEAREA )
    return np.asarray( featurevec )

cpdef runpyOpTrackFit( pySubEvent subevent, pyOpTrackFitConfig config, PyPhotonLibrary photonlib ):
    print "[Run pyOpTrackFit] initializing"
    cdef int ndims = 6
    # generate seeds
    model = pyOpTrackModel( config, photonlib )
    print "[Run pyOpTrackFit] gen seed"
    p0 = genSeedTracks( config )
    # make feature vector to fit to
    print "[Run pyOpTrackFit] gen seed"
    opfeatures = pyExtractFeatureVariables( subevent, config.NCHANS, config.NSPERTICK, 100.0 )
    printFeatureVector( opfeatures )
    # make the MCMC sampler
    print "[Run pyOpTrackFit] load ensemble sampler"
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

    
# Plotting
from ROOT import TH2D,  TH3D

cpdef makeHistograms(  np.ndarray[np.float_t, ndim=2] samplechain, photonvis, PyPhotonLibrary photonlib, pyOpTrackFitConfig opconfig, stemname="optrackemcee" ):
    hzy = TH2D( "h%s_zy"%(stemname),";z;y", photonvis.Nz, photonvis.zmin, photonvis.zmax, photonvis.Ny, photonvis.ymin, photonvis.ymax )
    hxy = TH2D("h%s_xy"%(stemname), ";x;y", photonvis.Nx, photonvis.xmin, photonvis.xmax, photonvis.Ny, photonvis.ymin, photonvis.ymax )
    hzx = TH2D("h%s_zx"%(stemname), ";z;x", photonvis.Nz, photonvis.zmin, photonvis.zmax, photonvis.Nx, photonvis.xmin, photonvis.xmax )
    h3d = TH3D("h%s_3d"%(stemname), ";z;x;y", photonvis.Nz, photonvis.zmin, photonvis.zmax, photonvis.Nx, photonvis.xmin, photonvis.xmax, photonvis.Ny, photonvis.ymin, photonvis.ymax )
    
    cdef int nsamples = samplechain.shape[0]
    cdef float denom = float(nsamples)
    cdef int n, i
    cdef int ndims = 6
    cdef vector[ vector[double] ] steps
    cdef vector[ vector[float] ] photons
    cdef float LY = opconfig.thisptr.LY
    cdef float dEdx = opconfig.thisptr.dEdx
    cdef int NCHANS = opconfig.NCHANS
    cdef int nsteps = 0
    cdef int istep = 0
    cdef np.ndarray[np.float_t, ndim=1] start
    cdef np.ndarray[np.float_t, ndim=1] end
    cdef TrackHypothesis* track = NULL

    print "[optrack makeHistograms] total ",nsamples," samples"
    for n in range(nsamples):
        start = samplechain[n,:3]
        end   = samplechain[n,3:]
        if n%10000==0:
            print "sample: ",n
        
        track = new TrackHypothesis( start, end )
        steps.clear()
        photons.clear()
        makeVoxelList( deref(track), deref(photonlib.thisptr), LY, dEdx, NCHANS, steps, photons )
        nsteps = steps.size()
        istep = 0
        for istep in range(nsteps):
            hzy.Fill( steps.at(istep).at(2), steps.at(istep).at(1), 1.0/denom )
            hxy.Fill( steps.at(istep).at(0), steps.at(istep).at(1), 1.0/denom )
            hzx.Fill( steps.at(istep).at(2), steps.at(istep).at(0), 1.0/denom )

        del track
        track = NULL


    return hzy, hxy, hzx
