import os,sys
import emcee # the MCMC Hammer
import numpy as np
import ROOT
from pysubevent.utils.pedestal import getpedestal
from pysubevent.pysubevent.prepWaveforms import prepCosmicSubEvents, prepWaveforms
from pysubevent.pyubphotonlib.photonvisibility import PhotonVisibility
from pylard.config.pmtpos import getPosFromID
import matplotlib.pyplot as pl

vis = True
if vis:
    try:
        from pyqtgraph.Qt import QtGui, QtCore
        import pyqtgraph as pg
        from pylard.pylardisplay.opdetdisplay import OpDetDisplay
        PYQTGRAPH = True
    except:
        PYQTGRAPH = False

colorlist = [ ( 255, 0, 0, 255 ),
              ( 125, 125, 250, 255 ),
              ( 0, 0, 255, 255 ),
              ( 125, 125, 0, 255 ),
              ( 125, 0, 125, 255 ),
              ( 0, 125, 125, 255 ) ]


def makeFlashPlotItem( flash, seconfig, color=(255,0,0,255) ):
    chsubevent = pg.PlotCurveItem()
    x = np.linspace( seconfig.nspersample*flash.tstart, seconfig.nspersample*flash.tend, len(flash.expectation) )
    y = flash.expectation
    chsubevent.setData( x=x, y=y, pen=color )
    return chsubevent    
def makeFlashPlotArrays( flash, seconfig, color=(255,0,0,255) ):
    x = np.linspace( seconfig.nspersample*flash.tstart, seconfig.nspersample*flash.tend, len(flash.expectation) )
    y = flash.expectation
    return x,y

# =========================================================================================================
# Op Track Fit

NCHANS = 32 # fix this later
NSPERTICK = 15.625
TEMP_SPEAREA = 100.0
photonlib = PhotonVisibility( "photonlib.json" )

class OpFeatureVector:
    def __init__(self, pulse_tstart, prompt_pe, total_pe ):
        """
        human friendly container for data used to build the feature vector we will be fitting with
        
        inputs:
        times: np.array of pulse start times. one per channel
        prompt_pe: np.array of pe in prompt_pulse. one per channel
        total_pe: totalpe in pulse. one per channel
        """
        self.tstarts = pulse_tstart
        self.prompt_pe = prompt_pe
        self.total_pe = total_pe
        
    def getTstart( ch ):
        return self.tstarts[ch]
    def getPromptPE( ch ):
        return self.prompt_pe[ch]
    def getTotalPE( ch ):
        return self.prompt_pe[ch]
    def makeFeatureVector( self ):
        """
        take time and pe vectors, e.g. (t1, t2, t3 ), (p1,p2,p3), (tot1, tot2, tot3) 
        and unroll them into a flat array, e.g. (t1,p1,tot1,t2,p2,tot2,...)
        """
        a = np.dstack( (self.tstarts, self.prompt_pe, self.total_pe ) )
        return a.flatten()

def extractFeatureVariables( subevent ):
    """
    Extract from a subevent, the relevant data we will be fitting against."
    
    inputs
    ------
    subevent: pySubEvent instance

    outputs
    -------
    np.array: np.float vector with 3 entries
    """
    t = np.zeros( NCHANS, dtype=np.float )
    prompt_pe = np.zeros( NCHANS, dtype=np.float )
    tot_pe = np.zeros( NCHANS, dtype=np.float )
    tmin = 1e200
    for flash in subevent.getFlashList():
        tflash = flash.tstart*NSPERTICK
        if tflash<tmin:
            tmin = tflash
        t[ flash.ch ] = flash.tstart*NSPERTICK
        prompt_pe[ flash.ch ] = flash.area_prompt/TEMP_SPEAREA
        tot_pe[ flash.ch ] = flash.area/TEMP_SPEAREA
    # subtract off leading time for non-zero elements
    for i in range(0,len(t)):
        if prompt_pe[i]>0:
            t[i] -= tmin

    return OpFeatureVector( t, prompt_pe, tot_pe )


class TrackHypothesis:
    def __init__( self, start, end ):
        self.start = start
        self.end   = end
    def getTrackVector( self ):
        a = np.dstack( (self.start, self.end ) )
        return a.flatten()

def makeVoxelList( track, LY, dEdx ):
    """
    from a track hypothesis, make lists of:
    1) voxelid
    2) track length in voxel
    """
    diff = track.end-track.start
    dleft = 0.0
    for i in range(0,3):
        dleft += diff[i]*diff[i];
    dleft = np.sqrt(dleft)

    dvec = diff/dleft
    
    # find first voxel bounds
    upper = photonlib.voxeldef.getVoxelLowerCorner( track.start )
    lower = photonlib.voxeldef.getVoxelUpperCorner( track.start )

    voxsize = np.asarray( [ (photonlib.xmax-photonlib.xmin)/photonlib.Nx, (photonlib.ymax-photonlib.ymin)/photonlib.Ny, (photonlib.zmax-photonlib.zmin)/photonlib.Nz ] )

    nsteps = 0
    currentpos = np.asarray( track.start )
    #print "Start"
    #print "  pos: ",currentpos
    #print "  dir: ",dvec
    #print "  voxels: ", upper,lower
    #print "  voxsize: ",voxsize

    step_photons = []
    steps = []

    while dleft>0.0:
    
        # first intersection test
        # x
        s = np.zeros( 3 )
        for i in range(0,3):
            if dvec[i]!=0:
                s1 = (upper[i]-currentpos[i])/dvec[i]
                s2 = (lower[i]-currentpos[i])/dvec[i]
                if s1>0:
                    s[i] = s1
                else:
                    s[i] = s2
            else:
                s[i] = -1.0 # we can use as sentinel since we always go forward
        shortest_s = -1
        shortest_i = -1
        for i in range(0,3):
            if s[i]>0 and ( shortest_s<0 or s[i]<shortest_s ):
                shortest_s = s[i]
                shortest_i = i
        if shortest_i<0:
            break # we've gone past

        # distance to end of track
        dleft = 0.0
        for i in range(0,3):
            dleft += ( track.end[i]-currentpos[i] )*( track.end[i]-currentpos[i] )
        dleft = np.sqrt( dleft )

        # look for stopping condition 
        # (1) at end of track
        if dleft < shortest_s:
            next = track.end
            dleft = 0.0
        else:
            # move to next intersection
            next = currentpos + shortest_s*dvec
        # (2) outside of box
        if next[0] > photonlib.xmax or next[0]<photonlib.xmin:
            break
        if next[1] > photonlib.ymax or next[1]<photonlib.ymin:
            break
        if next[2] > photonlib.zmax or next[2]<photonlib.zmin:
            break


        # we update the voxels
        # we move in the dimension hit
        if shortest_s*dvec[shortest_i]>0:
            upper[shortest_i] += voxsize[shortest_i]
            lower[shortest_i] += voxsize[shortest_i]
        else:
            upper[shortest_i] -= voxsize[shortest_i]
            lower[shortest_i] -= voxsize[shortest_i]
            
        # get the photons from this step
        stepdist = 0.0
        for i in range(0,3):
            stepdist += ( next[i]-currentpos[i])*( next[i]-currentpos[i])
        stepdist = np.sqrt(stepdist)

        midpoint = currentpos + 0.5*shortest_s*dvec
        chvis = []
        for ch in range(0,32):
            vis = photonlib.getCounts( midpoint, ch )
            chvis.append( vis*(LY*dEdx*stepdist) )
        step_photons.append( chvis )
        steps.append( midpoint )

        # move to next step
        currentpos = next

        # distance to end of track again
        dleft = 0.0
        for i in range(0,3):
            dleft += ( track.end[i]-currentpos[i] )*( track.end[i]-currentpos[i] )
        dleft = np.sqrt( dleft )

        #print "step %d update"%(nsteps)
        #print "  pos: ",currentpos
        #print "  voxels: ",upper,lower
        #print "  dist remaining: ",dleft
        #print "  shortest_s: ",shortest_s
        nsteps += 1
        #raw_input()
    # print "made it"
    np_photons = np.asarray( step_photons )

    return steps, np_photons

def makeFeatureHypothesis( track ):
    # -70 kV
    QE = 0.0093
    LY = 29000.0
    # MCC 6.1 
    #QE = 0.01
    #LY = 24000.0
    dEdx = 2.3
    fprompt = 0.3
    clar = (3.0e8*100.0*1.0e-9)/1.2
    pmtplane = -14.7 # cm
    
    # get track photons and step points
    midpoints, stepphotons = makeVoxelList( track, LY, dEdx )
    # turn this into a feature vector
    track_t        = np.zeros( 32 )
    track_peprompt = np.zeros( 32 )
    track_petot    = np.zeros( 32 )
    for ipmt in range(0,32):
        apmtpos = getPosFromID( ipmt ) # change from mm to cm
        pmtpos = np.asarray( [pmtplane,apmtpos[1],apmtpos[2]+500.0] )

        tearliest = 1e200
        peprompt = 0.0
        petotal = 0.0
        for n in range(0,len(midpoints)):
            dist = 0.0
            for i in range(0,3):
                dist += (pmtpos[i]-midpoints[n][i])*(pmtpos[i]-midpoints[n][i])
            dist = np.sqrt(dist)
            dt = dist/clar
            if dt<tearliest:
                tearliest = dt
            peprompt += stepphotons[n][ipmt]*QE*fprompt
            petotal += stepphotons[n][ipmt]*QE*(1.0-fprompt)
        track_t[ipmt] = tearliest
        track_peprompt[ipmt] = peprompt
        track_petot[ipmt] = petotal
    # subtract off min
    tmin = np.min(track_t)
    track_t -= tmin
    hypo = OpFeatureVector( track_t, track_peprompt, track_petot )
    return hypo

def likelihood( data, hypo ):
    sig = np.asarray( [50.0, 10.0, 10.0 ] )
    ll = 0.0
    for i in range(0,len(data)):
        ll -= 0.5*np.power( (data[i]-hypo[i])/sig[i%3], 2 )
    return ll

def lnProb( x, opfeatures ):
    # ivar: track start,end
    # datavec
    s = x[:3]
    e = x[3:]
    trackhypo = TrackHypothesis( s, e )
    hypovec = makeFeatureHypothesis( trackhypo )
    ll = likelihood( opfeatures.makeFeatureVector(), hypovec.makeFeatureVector() )

    # 1 side-gaussian when outside of detector
#     out1 = [0,0,0]
#     if s[0]<photonlib.xmin:
#         out1[0] = (s[0]-photonlib.xmin)/10.0
#     elif s[0]>photonlib.xmax:
#         out1[0] = (s[0]-photonlib.xmax)/10.0
#     if s[1]<photonlib.ymin:
#         out1[1] = (s[1]-photonlib.ymin)/10.0
#     elif s[1]>photonlib.ymax:
#         out1[1] = (s[1]-photonlib.ymax)/10.0
#     if s[2]<photonlib.zmin:
#         out1[2] = (s[2]-photonlib.zmin)/10.0
#     elif s[2]>photonlib.zmax:
#         out1[2] = (s[2]-photonlib.zmax)/10.0

#     out2 = [0,0,0]
#     if e[0]<photonlib.xmin:
#         out2[0] = (e[0]-photonlib.xmin)/10.0
#     elif e[0]>photonlib.xmax:
#         out2[0] = (e[0]-photonlib.xmax)/10.0
#     if e[1]<photonlib.ymin:
#         out2[1] = (e[1]-photonlib.ymin)/10.0
#     elif e[1]>photonlib.ymax:
#         out2[1] = (e[1]-photonlib.ymax)/10.0
#     if e[2]<photonlib.zmin:
#         out2[2] = (e[2]-photonlib.zmin)/10.0
#     elif e[2]>photonlib.zmax:
#         out2[2] = (e[2]-photonlib.zmax)/10.0
    
    # add weak priors on track position
    llweakpos = 0.0
    detcenter = np.asarray( [125.0, 0.0, 500.0 ] )
    detsig     = np.asarray( [ 500.0, 500.0, 2000.0 ] )
    for i in range(0,3):
        llweakpos += -0.5*np.power( (s[i]-detcenter[i])/detsig[i], 2 )
        llweakpos += -0.5*np.power( (e[i]-detcenter[i])/detsig[i], 2 )
        #llweakpos += -0.5*np.power( out1[i], 2 ) - 0.5*np.power( out2[i], 2 ) # edge penalties
    ll += llweakpos
    return ll

def OpTrackFit( subevents ):
    
    subevents.sortByAmp()

    for subevent in subevents.getlist():
        print subevent.maxamp
    
    if subevents.size>0:
        subevent = subevents.getlist()[0]
    else:
        return None

    opfeatures = extractFeatureVariables( subevent )

    print opfeatures.makeFeatureVector()

    s = np.asarray( [ 150.0, 150.0, 500.0 ], dtype=np.float )
    e = np.asarray( [ 150.0, -150.0, 500.0 ], dtype=np.float )
    print "seed. start,end=",s,e
    seedtrack = TrackHypothesis( s, e )

    nwalkers = 40
    ndims = 6
    p0 = []
    for i in range(0,nwalkers):
        p1 = []
        for x in range(0,3):
            p1.append( np.random.normal( s[x], 2.0 ) )
        for x in range(0,3):
            p1.append( np.random.normal( e[x], 2.0 ) )
        p0.append( p1 )
            
    sampler = emcee.EnsembleSampler(nwalkers, ndims, lnProb, args=[opfeatures])
    fitpos, prob, state  = sampler.run_mcmc( p0, 1000)
    sampler.reset()
    print "Sample burn-in finished."
    pos = sampler.run_mcmc( fitpos, 1000)
    print "Sample run finished."
    np.savez( "tracksamples.npz", sampler.flatchain )
    for i in range(ndims):
        pl.figure()
        pl.hist(sampler.flatchain[:,i], 100, color="k", histtype="step")
        pl.title("Dimension {0:d}".format(i))
    pl.show()
    print "samples saved"

    raw_input()
    return 
    
from pysubevent.pysubevent.cysubeventdisc import pyWaveformData, pySubEventIO, pySubEventList

def test_runSubEventFinder( opdata, seconfig, filename, opdisplay=None ):

    from pysubevent.pysubevent.cysubeventdisc import formSubEventsCPP
    import pysubevent.utils.pmtcalib as spe
    pmtspe = spe.getCalib( "../config/pmtcalib_20150930.json" )

    from pysubevent.pyoptrackfit.cyoptrackfit import runpyOpTrackFit, pyOpTrackFitConfig, makeHistograms

    tf = ROOT.TFile("test_optrack.root","recreate")
    opconfig = pyOpTrackFitConfig( "optrackfit.json" )

    ok = True
    hgslot = 5
    lgslot = 6

    while ok:

        cosmic_subevents, boundary_subevent = prepCosmicSubEvents( opdata, seconfig )
        #boundary_subevent = None
        wfms,qs = prepWaveforms( opdata, boundary_subevent )   # extract numpy arrays
        pywfms = pyWaveformData()
        pywfms.storeWaveforms( wfms )  # package
        pywfms.calcBaselineInfo()
        #for i in range(0,wfms.shape[1]):
        #    print "ch ",i,": max=",np.max(wfms[:,i])

        baselines = np.zeros( wfms.shape, dtype=np.float )
        variances = np.zeros( wfms.shape, dtype=np.float )
        print "baslines: ",baselines.shape
        for ch in range(0, wfms.shape[1] ):
            baselines[:,ch] = pywfms.getbaseline( ch )

        subevents, unclaimed_flashes = formSubEventsCPP( pywfms, seconfig, pmtspe )
        if boundary_subevent is None:
            print "[NUMBER OF SUBEVENT: ",subevents.size,"]"
        else:
            print "[NUMBER OF SUBEVENT: ",subevents.size,"] + [BOUNDARY SUBEVENT]"

        subevents.sortByAmp()
        for subevent in subevents.getlist():
            print subevents, "t=",subevent.tstart_sample, " nflashes=",len(subevent.getFlashList())

        print "Run OpTrackFin"
        #OpTrackFit( subevents ) # pythonthin

        ndims = 6
        sampler = runpyOpTrackFit( subevents.getlist()[0], opconfig, photonlib.photonlib ) # native c++
        print "op track fit returned"
        np.savez( "tracksamples.npz", sampler.flatchain )
        print "samples saved"
        hzy, hxy, hzx = makeHistograms( sampler.flatchain, photonlib, photonlib.photonlib, opconfig, "event%d"%(opdata.event) )
        print "made histograms"
        hzy.Write()
        hxy.Write()
        hzx.Write()
        #for i in range(ndims):
        #    pl.figure()
        #    pl.hist(sampler.flatchain[:,i], 100, color="k", histtype="step")
        #    pl.title("Dimension {0:d}".format(i))
        #pl.show()
            
        if opdisplay is not None:
            # add subevent drawings
            #opdisplay.clearUserWaveformItem()
            subeventlist = subevents.getlist()
            if boundary_subevent is not None:
                subeventlist.append( boundary_subevent )
            for isubevent,subevent in enumerate( subeventlist ):
                for flash in subevent.getFlashList():
                    beamchoffset = opdata.getBeamWindows( hgslot, flash.ch )[0].getTimestamp()
                    x,y = makeFlashPlotArrays( flash, seconfig, color=colorlist[ isubevent%6 ] )
                    opdata.userwindows.makeWindow( y, x+beamchoffset, 5, flash.ch, default_color=colorlist[ isubevent%6 ], highlighted_color=colorlist[ isubevent%6 ] )
                    if subevent in [boundary_subevent]:
                        x = np.linspace( seconfig.nspersample*flash.tstart, seconfig.nspersample*(flash.tstart+len(flash.waveform)), len(flash.waveform) )
                        y = flash.waveform
                        opdata.userwindows.makeWindow( y, x, 5, flash.ch, default_color=colorlist[ isubevent%6 ], highlighted_color=colorlist[ isubevent%6 ] )
                        if flash.ch in opdata.suppressed_wfm:
                            beamchoffset2 = opdata.getBeamWindows( hgslot, flash.ch )[0].getTimestamp()
                            x = np.linspace( 0, len(opdata.suppressed_wfm[flash.ch])*seconfig.nspersample, len( opdata.suppressed_wfm[flash.ch]) ) + beamchoffset2
                            y = opdata.suppressed_wfm[flash.ch]
                            opdata.userwindows.makeWindow( y, x, 5, flash.ch )

                for flash in subevent.getFlash2List():
                    beamchoffset = opdata.getBeamWindows( hgslot, flash.ch )[0].getTimestamp()
                    x,y = makeFlashPlotArrays( flash, seconfig, color=colorlist[ isubevent%6 ] )
                    opdata.userwindows.makeWindow( y, x+beamchoffset, 5, flash.ch, default_color=colorlist[ isubevent%6 ], highlighted_color=colorlist[ isubevent%6 ] )

            for flash in unclaimed_flashes.getFlashes():
                beamchoffset = opdata.getBeamWindows( hgslot, flash.ch )[0].getTimestamp()
                x,y = makeFlashPlotArrays( flash, seconfig )
                opdata.userwindows.makeWindow( y, x+beamchoffset, 5, flash.ch, default_color=(0,255,0,255), highlighted_color=(0,255,0,255)  )

            for ch in range(0,32):
                plot_baseline = pg.PlotCurveItem()
                beamchoffset = opdata.getBeamWindows( hgslot, ch )[0].getTimestamp()
                x = np.linspace( 0, len(baselines[:,ch])*seconfig.nspersample, len(baselines[:,ch]) ) + beamchoffset
                y = baselines[:,ch]
                #opdata.userwindows.makeWindow( y, x, 5, ch, default_color=(255,128,0,255), highlighted_color=(255,128,0,255) )
                
                #plot_variance = pg.PlotCurveItem()
                #x = np.linspace( 0, len(variances[:,ch])*seconfig.nspersample, len(variances[:,ch]) )
                #y = variances[:,ch]
                #plot_variance.setData( x=x, y=y, pen=(255,204,153,255) )
                #opdisplay.addUserWaveformItem( plot_variance, ch=ch )

        #if subevents.size>0:
            #opdisplay.plotData()
            opdisplay.gotoEvent( opdata.event )
  
        #if subevents.size>0:
            raw_input()
        ok = opdata.getNextEntry()


if __name__ == "__main__":
    # Load config
    from pysubevent.pysubevent.cysubeventdisc import pySubEventModConfig
    config = pySubEventModConfig( "discr1", "subevent.cfg" )
    from pylard.pylardata.rawdigitsopdata import RawDigitsOpData
    from pylard.larlite_interface.larliteopdata import LArLiteOpticalData
    fname = "../../data/pmtratedata/pmtrawdigits_recent_radon.root"
    #opdata = RawDigitsOpData( fname )
    #ok = opdata.gotoEvent(5)
    opdata = LArLiteOpticalData( "../../mc/mcc6.1samples/mcc6.1sample_3_2493461_0.root" )
    ok = opdata.gotoEvent(112)
    #ok = opdata.getNextEntry(
    if vis:
        app = QtGui.QApplication([])
        opdisplay = OpDetDisplay( opdata )
        opdisplay.show()
    else:
        opdisplay = None

    if ok:
        test_runSubEventFinder( opdata, config, "output_debug.root", opdisplay=opdisplay )
        
