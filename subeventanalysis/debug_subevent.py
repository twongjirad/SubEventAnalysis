import os,sys
import numpy as np
from pysubevent.utils.pedestal import getpedestal
from prepWaveforms import prepWaveforms, prepCosmicSubEvents

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

def test_findonesubevent( ch, opdata, seconfig, opdisplay=None ):
    """ tests findonesubevent routines: python, cython, cpp """
    from pysubevent.pysubevent.cysubeventdisc import findOneSubEventCPP
    wfm = opdata.getData()[:,ch]
    flash = findOneSubEventCPP( ch, wfm, seconfig )
    print "returned flash: ",flash.ch, flash.tstart, flash.tend
    print "flash waveform: ",len(flash.waveform)
    print "flash expectation: ",len(flash.expectation)
    if opdisplay is not None:
        print "Visualize!"
        opdisplay.clearUserWaveformItem()
        chsubevent = makeFlashPlotItem( flash, seconfig )
        opdisplay.addUserWaveformItem( chsubevent, ch=ch)

def test_getChannelFlashes( ch, opdata, seconfig, opdisplay=None ):
    """tests getChannelFlashesCPP"""
    from pysubevent.pysubevent.cysubeventdisc import getChannelFlashesCPP
    if opdisplay is not None:
        opdisplay.gotoEvent( opdata.current_event )
        opdisplay.clearUserWaveformItem()
    wfms,qs = prepWaveforms( opdata )

    for ch in range(0,32):
        wfm = wfms[:,ch]
        flashes, postwfm = getChannelFlashesCPP( ch, wfm, seconfig, ret_postwfm=True )
        print "channel=",ch,":  number of flashes=",len(flashes)
        if opdisplay is not None:
            print "visualize! ",flashes
            #postwfm -= postwfm[0]
            for flash in flashes:
                chsubevent = makeFlashPlotItem( flash, seconfig )
                opdisplay.addUserWaveformItem( chsubevent, ch=ch)
            # plot postwfm
            plot_postwfm = pg.PlotCurveItem()
            x = np.linspace( 0,  seconfig.nspersample*len(postwfm), len(postwfm) )
            plot_postwfm.setData( x=x, y=postwfm, pen=(0,255,0,100) )
            opdisplay.addUserWaveformItem( plot_postwfm, ch=ch )
            # plot diff waveform
            diffwfm = np.zeros( len(wfm),  dtype=np.float )
            for i in range( seconfig.cfddelay, len(wfm) ):
                diffwfm[i] = wfm[i]-wfm[i-seconfig.cfddelay]
            
            plot_diffwfm = pg.PlotCurveItem()
            x = np.linspace( 0,  seconfig.nspersample*len(diffwfm), len(diffwfm) )
            plot_diffwfm.setData( x=x, y=diffwfm, pen=(0,100,255,100) )
            opdisplay.addUserWaveformItem( plot_diffwfm, ch=ch )
        plot_qs = pg.PlotCurveItem()
        x = np.linspace( 0, seconfig.nspersample*len(qs[:,ch]), len(qs[:,ch]) )
        y = qs[:,ch]
        plot_qs.setData( x=x, y=y, pen=(100,100,0,100) )
        opdisplay.addUserWaveformItem( plot_qs, ch=ch )
            
    print flashes

from pysubevent.pysubevent.cysubeventdisc import pyWaveformData, pyFlashList, formFlashesCPP

def test_secondPassFlashes( opdata, seconfig, opdisplay=None ):
    # extract numpy arrays
    wfms,qs = prepWaveforms( opdata )   
    # package waveforms
    pywfms = pyWaveformData()
    pyqwfms.storeWaveforms( wfms )  
    
    # pass 1
    flashes1, postwfms = formFlashesCPP( pywfms, seconfig, "pass1" )

    # pass 2
    flashes2, postpostwfms = formFlashesCPP( postwfms, seconfig, "pass2" )

    # DRAW
    if opdisplay is not None:
        for flash1 in flashes1.getFlashes():
            plot_flash = makeFlashPlotItem( flash1, seconfig )
            opdisplay.addUserWaveformItem( plot_flash, ch=flash1.ch )

        for flash2 in flashes2.getFlashes():
            plot_flash = makeFlashPlotItem( flash2, seconfig, color=(0,255,0,255) )
            opdisplay.addUserWaveformItem( plot_flash, ch=flash2.ch )
            
    

from pysubevent.pysubevent.cysubeventdisc import pyWaveformData, pySubEventIO, pySubEventList

def test_runSubEventFinder( opdata, seconfig, filename, opdisplay=None ):

    subeventio = pySubEventIO( filename, 'w' )
    
    from pysubevent.pysubevent.cysubeventdisc import formSubEventsCPP
    import pysubevent.utils.pmtcalib as spe
    pmtspe = spe.getCalib( "../config/pmtcalib_20150930.json" )

    ok = True

    while ok:

        cosmic_subevents, boundary_subevent = prepCosmicSubEvents( opdata, seconfig )
        wfms,qs = prepWaveforms( opdata, boundary_subevent )   # extract numpy arrays
        pywfms = pyWaveformData()
        pywfms.storeWaveforms( wfms )  # package
        for i in range(0,wfms.shape[1]):
            print "ch ",i,": max=",np.max(wfms[:,i])

        subevents, unclaimed_flashes = formSubEventsCPP( pywfms, seconfig, pmtspe )
        if boundary_subevent is None:
            print "[NUMBER OF SUBEVENT: ",subevents.size,"]"
        else:
            print "[NUMBER OF SUBEVENT: ",subevents.size,"] + [BOUNDARY SUBEVENT]"
        for subevent in subevents.getlist():
            print subevents, "t=",subevent.tstart_sample, " nflashes=",len(subevent.getFlashList())
        subeventio.transferSubEventList( subevents )
        subeventio.fill()
        subeventio.write()

        if opdisplay is not None:
            opdisplay.clearUserWaveformItem()
            opdisplay.gotoEvent( opdata.current_event )
            subeventlist = subevents.getlist()
            if boundary_subevent is not None:
                subeventlist.append( boundary_subevent )
            for isubevent,subevent in enumerate( subeventlist ):
                for flash in subevent.getFlashList():
                    plot_flash = makeFlashPlotItem( flash, seconfig, color=colorlist[ isubevent%6 ] )
                    opdisplay.addUserWaveformItem( plot_flash, ch=flash.ch )
                    if subevent in [boundary_subevent]:
                        chsubevent = pg.PlotCurveItem()
                        x = np.linspace( seconfig.nspersample*flash.tstart, seconfig.nspersample*len(flash.waveform), len(flash.waveform) )
                        y = flash.waveform
                        chsubevent.setData( x=x, y=y, pen=(255,255,255,255) )
                        opdisplay.addUserWaveformItem( chsubevent, ch=flash.ch )
                        chsuppressed = pg.PlotCurveItem()
                        x = np.linspace( 0, len(opdata.suppressed_wfm[flash.ch])*seconfig.nspersample, len( opdata.suppressed_wfm[flash.ch]) )
                        y = opdata.suppressed_wfm[flash.ch]
                        chsuppressed.setData( x=x, y=y, pen=(255,255,255,255) )
                        opdisplay.addUserWaveformItem( chsuppressed, ch=flash.ch )

                #for flash in subevent.getFlash2List():
                #    plot_flash = makeFlashPlotItem( flash, seconfig, color=colorlist[ isubevent%6 ] )
                #    opdisplay.addUserWaveformItem( plot_flash, ch=flash.ch )                    
            for flash in unclaimed_flashes.getFlashes():
                plot_flash = makeFlashPlotItem( flash, seconfig, color=(0,255,0,255) )
                opdisplay.addUserWaveformItem( plot_flash, ch=flash.ch )

        raw_input()
        ok = opdata.getNextEvent()

def test_cosmicsubeventfinder( opdata, config, opdisplay=None ):
    # stuff data into interface class
    cosmic_subevents, boundarysubevent = prepCosmicSubEvents( opdata )
    wfms,qs = prepWaveforms( opdata, boundarysubevent )
    
    if opdisplay is not None:
        opdisplay.clearUserWaveformItem()
        opdisplay.gotoEvent( opdata.current_event )
        #for isubevent,subevent in enumerate( cosmic_subevents.getlist() ):
        if boundarysubevent is not None:
            for isubevent,subevent in enumerate([boundarysubevent]):
                for flash in subevent.getFlashList():
                    plot_flash = makeFlashPlotItem( flash, config, color=colorlist[ isubevent%6 ] )
                    opdisplay.addUserWaveformItem( plot_flash, ch=flash.ch )
        

if __name__ == "__main__":


    # Load config
    from pysubevent.pysubevent.cysubeventdisc import pySubEventModConfig
    config = pySubEventModConfig( "discr1", "subevent.cfg" )
    print config.cfd_threshold,config.fastconst
    
    # Load data
    from pylard.pylardata.rawdigitsopdata import RawDigitsOpData
    #fname = "../../data/pmtratedata/run2668_filterreconnect_rerun.root"
    #fname = "../../data/pmtratedata/run2597_filterreconnect.root"
    fname = "../../data/pmtratedata/pmtrawdigits_recent_radon.root"
    opdata = RawDigitsOpData( fname )
    ok = opdata.getNextEvent()
    #ok = opdata.getEvent(1)
    if vis:
        app = QtGui.QApplication([])
        opdisplay = OpDetDisplay( opdata )
        opdisplay.show()
    else:
        opdisplay = None


    if ok:
        #test_findonesubevent( 0, opdata, config, opdisplay=opdisplay )
        #test_getChannelFlashes( 0, opdata, config, opdisplay=opdisplay )
        test_runSubEventFinder( opdata, config, "output_debug.root", opdisplay=opdisplay )
        #test_secondPassFlashes( opdata, config, opdisplay )
        #test_cosmicsubeventfinder( opdata, config, opdisplay=opdisplay )
        


    if vis and ( (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION')):
        print "exec called ..."
        QtGui.QApplication.instance().exec_()
