import os,sys
import numpy as np
from pysubevent.utils.pedestal import getpedestal
from pysubevent.pysubevent.prepWaveforms import prepWaveforms, prepCosmicSubEvents

vis = True

if vis:
    try:
        from pyqtgraph.Qt import QtGui, QtCore
        import pyqtgraph as pg
        from pylard.pylardisplay.opdetdisplay import OpDetDisplay
        app = QtGui.QApplication([])
        PYQTGRAPH = True
    except:
        print "no opdetdisplay"
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

    wfms,qs = prepWaveforms( opdata )
    pywfms = pyWaveformData()
    pywfms.storeWaveforms( wfms )  # package
    pywfms.calcBaselineInfo()
    baselines = np.zeros( wfms.shape, dtype=np.float )
    for ch in range(0, wfms.shape[1] ):
        baselines[:,ch] = pywfms.getbaseline( ch )

    if opdisplay is not None:
        opdisplay.gotoEvent( opdata.event )

    hgslot = 5
    for ch in range(0,32):
        wfm = wfms[:,ch]
        baseline = baselines[:,ch]
        flashes, postwfm = getChannelFlashesCPP( ch, wfm, baseline, seconfig, "discr1", ret_postwfm=True )
        print "channel=",ch,":  number of flashes=",len(flashes)
        if opdisplay is not None:
            print "visualize flashes! ",flashes
            beamchoffset = opdata.getBeamWindows( hgslot, ch )[0].getTimestamp()

            for flash in flashes:
                x,y = makeFlashPlotArrays( flash, seconfig, color=(255,0,0,255) )
                opdata.userwindows.makeWindow( y, x, 5, flash.ch, default_color=(255,0,0,255) )
    
            # plot postwfm
            x = np.linspace( 0,  seconfig.nspersample*len(postwfm), len(postwfm) )
            opdata.userwindows.makeWindow( postwfm, x, 5, None, default_color=(0,0,255) )
            # plot diff waveform
            diffwfm = np.zeros( len(wfm),  dtype=np.float )
            for i in range( seconfig.cfddelay, len(wfm) ):
                diffwfm[i] = wfm[i]-wfm[i-seconfig.cfddelay]
            
            plot_diffwfm = pg.PlotCurveItem()
            x = np.linspace( 0,  seconfig.nspersample*len(diffwfm), len(diffwfm) )
            plot_diffwfm.setData( x=x, y=diffwfm, pen=(0,100,255,100) )
            opdisplay.addUserWaveformItem( plot_diffwfm, ch=ch )

            x = np.linspace( 0, len(baselines[:,ch])*seconfig.nspersample, len(baselines[:,ch]) ) + beamchoffset
            y = baselines[:,ch]
            opdata.userwindows.makeWindow( y, x, 5, ch, default_color=(255,128,0,255), highlighted_color=(255,128,0,255) ) 
    opdisplay.plotData()

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
    opdisplay.gotoEvent( opdata.event )

    while ok:
        cosmic_subevents, boundary_subevent = prepCosmicSubEvents( opdata, seconfig )

        #boundary_subevent = None
        wfms,qs = prepWaveforms( opdata, seconfig.RC, seconfig.fA, seconfig.hgslot, seconfig.lgslot, boundary_subevent, doit=False )   # extract numpy arrays
        pywfms = pyWaveformData()
        pywfms.storeWaveforms( wfms )  # package
        pywfms.calcBaselineInfo()
        #for i in range(0,wfms.shape[1]):
        #    print "ch ",i,": max=",np.max(wfms[:,i])
        print "BEAM WINS: ",opdata.beamwindows.getNumWindows()
        print "COSMIC WINS: ",opdata.cosmicwindows.getNumWindows()

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
        subeventio.transferSubEventList( subevents )
        subeventio.fill()
        subeventio.write()
        
        hgslot = 5
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
                    #opdata.userwindows.makeWindow( y, x+beamchoffset, 5, flash.ch, default_color=colorlist[ isubevent%6 ], highlighted_color=colorlist[ isubevent%6 ] )

            #for flash in unclaimed_flashes.getFlashes():
            #    beamchoffset = opdata.getBeamWindows( hgslot, flash.ch )[0].getTimestamp()
            #    x,y = makeFlashPlotArrays( flash, seconfig )
            #    opdata.userwindows.makeWindow( y, x+beamchoffset, 5, flash.ch, default_color=(0,255,0,255), highlighted_color=(0,255,0,255)  )

            for ch in range(0,32):
                beamchoffset = opdata.getBeamWindows( hgslot, ch )[0].getTimestamp()
                x = np.linspace( 0, len(baselines[:,ch])*seconfig.nspersample, len(baselines[:,ch]) ) + beamchoffset
                y = baselines[:,ch]
                #opdata.userwindows.makeWindow( y, x, 5, ch, default_color=(255,128,0,255), highlighted_color=(255,128,0,255) )
                
                qcorr = qs[ch]
                x = np.linspace( beamchoffset, beamchoffset+len(qcorr)*seconfig.nspersample, len(qcorr) )
                y = qcorr
                opdata.userwindows.makeWindow( y, x, 5, ch, default_color=(255,128,0,50), highlighted_color=(255,128,0,50) )

                #plot_variance = pg.PlotCurveItem()
                #x = np.linspace( 0, len(variances[:,ch])*seconfig.nspersample, len(variances[:,ch]) )
                #y = variances[:,ch]
                #plot_variance.setData( x=x, y=y, pen=(255,204,153,255) )
                #opdisplay.addUserWaveformItem( plot_variance, ch=ch )

        #if subevents.size>0:
            opdisplay.plotData()
            #opdisplay.gotoEvent( opdata.event )
            raw_input()
        ok = opdata.getNextEntry()

def test_cosmicsubeventfinder( opdata, config, opdisplay=None ):
    # stuff data into interface class
    cosmic_subevents, boundarysubevent = prepCosmicSubEvents( opdata )
    boundarysubevent = None # way to hack it to not make corrections
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
    from pylard.larlite_interface.larliteopdata import LArLiteOpticalData

    #fname = "../../data/pmtratedata/run2668_filterreconnect_rerun.root"
    #fname = "../../data/pmtratedata/run2597_filterreconnect.root"
    #fname = "../../data/pmtratedata/pmtrawdigits_recent_radon.root"
    #fname = "raw_digits.root"
    #fname = "../mc_piminus_rawdigits_nodark.root"
    #opdata = RawDigitsOpData( fname )
    opdata = LArLiteOpticalData( "../../mc/mcc6.1samples/mcc6.1sample_3_2493461_0.root" )
    #opdata = LArLiteOpticalData( "../../pylard/test_opflash.root" )
    #opdata = LArLiteOpticalData( "../../pylard/larlite_mergedopdata_run2382.root" )
    #ok = opdata.getNextEntry()
    ok = opdata.gotoEvent(102)
    if vis:
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
