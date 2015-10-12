import os,sys
import numpy as np
from pysubevent.utils.pedestal import getpedestal

vis = True

if vis:
    try:
        from pyqtgraph.Qt import QtGui, QtCore
        import pyqtgraph as pg
        from pylard.pylardisplay.opdetdisplay import OpDetDisplay
        PYQTGRAPH = True
    except:
        PYQTGRAPH = False

def prepWaveforms( opdata ):
    RC = 50000.0 # ns
    nsamples = opdata.getNBeamWinSamples()
    wfms = np.ones( (nsamples,32) )*2047.0
    qs   = np.zeros( (nsamples,32) )
    for ch in range(0,32):
        scale = 1.0
        if np.max( opdata.getData()[:,ch] )<4090:
            wfms[:,ch] = opdata.getData(slot=5)[:,ch]
        else:
            print "swap HG ch",ch," with LG wfm"
            lgwfm = opdata.getData(slot=6)[:,ch]
            lgped = getpedestal( lgwfm, 20, 2.0 )
            if lgped is None:
                print "ch ",ch," LG has bad ped"
                lgped = opdata.getData(slot=6)[0,ch]
            wfms[:,ch] = lgwfm-lgped
            print "lg ped=",lgped," wfm[0-10]=",np.mean( wfms[0:10,ch] )
            wfms[:,ch] *= 10.0
            scale = 10.0
            #opdata.getData(slot=5)[:,ch] = wfms[:,ch] + lgped
            #opdata.getPedestal(slot=5)[ch] = lgped # since we removed the pedestal already
        ped = getpedestal( wfms[:,ch], 20, 2.0*scale )
        if ped is not None:
            print "ch ",ch," ped=",ped
            wfms[:,ch] -= ped
        else:
            print "ch ",ch," has bad ped"
            wfms[:,ch] -= 0.0
        # calc undershoot
        for i in range(1,len(qs[:,ch])):
            #for j in range(i+1,np.minimum(i+1+200,len(qs[:,ch])) ):
            q = 50.0*(wfms[i,ch]/RC) + qs[i-1,ch]*np.exp(-1.0*15.625/RC) # 10 is fudge factor!
            qs[i,ch] = q
            wfms[i,ch] += q
        opdata.getData(slot=5)[:,ch] = wfms[:,ch]
        opdata.getPedestal(slot=5)[ch] = 0.0
            
    return wfms,qs
            

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
    wfms,qs = prepWaveforms( opdata )   # extract numpy arrays
    pywfms = pyWaveformData( wfms )  # package
    
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

    wfms,qs = prepWaveforms( opdata )   # extract numpy arrays
    pywfms = pyWaveformData( wfms )  # package
    for i in range(0,wfms.shape[1]):
        print "ch ",i,": max=",np.max(wfms[:,i])

    subeventio = pySubEventIO( filename, 'w' )
    
    from pysubevent.pysubevent.cysubeventdisc import formSubEventsCPP
    import pysubevent.utils.pmtcalib as spe
    pmtspe = spe.getCalib( "../config/pmtcalib_20150930.json" )
    subevents = formSubEventsCPP( pywfms, seconfig, pmtspe )
    for subevent in subevents.getlist():
        print subevents, "t=",subevent.tstart_sample, " nflashes=",len(subevent.getFlashList())
    subeventio.transferSubEventList( subevents )
    subeventio.fill()
    subeventio.write()
    if opdisplay is not None:
        opdisplay.gotoEvent( opdata.current_event )
    

if __name__ == "__main__":


    # Load config
    from pysubevent.pysubevent.cysubeventdisc import pySubEventModConfig
    config = pySubEventModConfig( "discr1", "subevent.cfg" )
    print config.cfd_threshold,config.fastconst
    
    # Load data
    from pylard.pylardata.rawdigitsopdata import RawDigitsOpData
    fname = "../../data/pmtratedata/run2668_filterreconnect_rerun.root"
    opdata = RawDigitsOpData( fname )
    #ok = opdata.getNextEvent()
    ok = opdata.getEvent(8)
    if vis:
        app = QtGui.QApplication([])
        opdisplay = OpDetDisplay( opdata )
        opdisplay.show()
    else:
        opdisplay = None


    if ok:
        #test_findonesubevent( 0, opdata, config, opdisplay=opdisplay )
        #test_getChannelFlashes( 0, opdata, config, opdisplay=opdisplay )
        #test_runSubEventFinder( opdata, config, "output_debug.root", opdisplay=opdisplay )
        test_secondPassFlashes( opdata, config, opdisplay )


    if vis and ( (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION')):
        print "exec called ..."
        QtGui.QApplication.instance().exec_()
