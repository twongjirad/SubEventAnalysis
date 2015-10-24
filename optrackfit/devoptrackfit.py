import os,sys
import emcee # the MCMC Hammer
import numpy as np
sys.path.append("/Users/twongjirad/working/uboone/SubEventAnalysis/subeventananlysis")
from pysubevent.utils.pedestal import getpedestal
from prepWaveforms import prepCosmicSubEvents, prepWaveforms
from pysubevent.pyubphotonlib import PhotonVisibility

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
    for flash in subevent.getFlashList():
        t[ flash.ch ] = flash.tstart*NSPERTICK
        prompt_pe[ flash.ch ] = flash.area_prompt/TEMP_SPEAREA
        tot_pe[ flash.ch ] = flash.area/TEMP_SPEAREA

    return OpFeatureVector( t, prompt_pe, tot_pe )


class TrackHypothesis:
    def __init__( self, start, end ):
        self.start = start
        self.end   = end
    def getTrackVector( self ):
        a = np.dstack( (self.start, self.end ) )
        return a.flatten()

def makeVoxelList( track ):
    """
    from a track hypothesis, make lists of:
    1) voxelid
    2) track length in voxel
    """
    

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

    return 
    
from pysubevent.pysubevent.cysubeventdisc import pyWaveformData, pySubEventIO, pySubEventList

def test_runSubEventFinder( opdata, seconfig, filename, opdisplay=None ):

    from pysubevent.pysubevent.cysubeventdisc import formSubEventsCPP
    import pysubevent.utils.pmtcalib as spe
    pmtspe = spe.getCalib( "../config/pmtcalib_20150930.json" )

    ok = True

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
        for subevent in subevents.getlist():
            print subevents, "t=",subevent.tstart_sample, " nflashes=",len(subevent.getFlashList())

        OpTrackFit( subevents )
        print "op track fit returned"
            
        if opdisplay is not None:
            opdisplay.clearUserWaveformItem()
            opdisplay.gotoEvent( opdata.current_event )
            subeventlist = subevents.getlist()
            if boundary_subevent is not None:
                subeventlist.append( boundary_subevent )
            for isubevent,subevent in enumerate( subeventlist ):
                for flash in subevent.getFlashList():
                    plot_flash = makeFlashPlotItem( flash, seconfig, color=colorlist[ isubevent%6 ] )
                    opdisplay.addUserWaveformItem( plot_flash, ch=flash.ch ) # main subevents
                    if subevent in [boundary_subevent]:
                        chsubevent = pg.PlotCurveItem()
                        x = np.linspace( seconfig.nspersample*flash.tstart, seconfig.nspersample*(flash.tstart+len(flash.waveform)), len(flash.waveform) )
                        y = flash.waveform
                        chsubevent.setData( x=x, y=y, pen=(255,255,255,255) )
                        opdisplay.addUserWaveformItem( chsubevent, ch=flash.ch ) # boundary subevent
                        if flash.ch in opdata.suppressed_wfm:
                            chsuppressed = pg.PlotCurveItem()
                            x = np.linspace( 0, len(opdata.suppressed_wfm[flash.ch])*seconfig.nspersample, len( opdata.suppressed_wfm[flash.ch]) )
                            y = opdata.suppressed_wfm[flash.ch]
                            chsuppressed.setData( x=x, y=y, pen=(255,255,255,255) )
                            opdisplay.addUserWaveformItem( chsuppressed, ch=flash.ch )

                for flash in subevent.getFlash2List():
                    plot_flash = makeFlashPlotItem( flash, seconfig, color=colorlist[ isubevent%6 ] )
                    opdisplay.addUserWaveformItem( plot_flash, ch=flash.ch ) # subevent low-thresh hits
            for flash in unclaimed_flashes.getFlashes():
                plot_flash = makeFlashPlotItem( flash, seconfig, color=(0,255,0,255) )
                #opdisplay.addUserWaveformItem( plot_flash, ch=flash.ch ) # unclaimed flashes
            for ch in range(0,32):
                plot_baseline = pg.PlotCurveItem()
                x = np.linspace( 0, len(baselines[:,ch])*seconfig.nspersample, len(baselines[:,ch]) )
                y = baselines[:,ch]
                plot_baseline.setData( x=x, y=y, pen=(255,153,51,255) )
                opdisplay.addUserWaveformItem( plot_baseline, ch=ch )

                plot_variance = pg.PlotCurveItem()
                x = np.linspace( 0, len(variances[:,ch])*seconfig.nspersample, len(variances[:,ch]) )
                y = variances[:,ch]
                plot_variance.setData( x=x, y=y, pen=(255,204,153,255) )
                opdisplay.addUserWaveformItem( plot_variance, ch=ch )

        #if subevents.size>0:
            raw_input()
        ok = opdata.getNextEvent()


if __name__ == "__main__":
    # Load config
    from pysubevent.pysubevent.cysubeventdisc import pySubEventModConfig
    config = pySubEventModConfig( "discr1", "subevent.cfg" )
    from pylard.pylardata.rawdigitsopdata import RawDigitsOpData
    fname = "../../data/pmtratedata/pmtrawdigits_recent_radon.root"
    opdata = RawDigitsOpData( fname )
    #ok = opdata.getNextEvent()
    ok = opdata.getEvent(5)
    if vis:
        app = QtGui.QApplication([])
        opdisplay = OpDetDisplay( opdata )
        opdisplay.show()
    else:
        opdisplay = None

    if ok:
        test_runSubEventFinder( opdata, config, "output_debug.root", opdisplay=opdisplay )
        
