import os,sys
import numpy as np

vis = True

if vis:
    try:
        from pyqtgraph.Qt import QtGui, QtCore
        import pyqtgraph as pg
        from pylard.pylardisplay.opdetdisplay import OpDetDisplay
        PYQTGRAPH = True
    except:
        PYQTGRAPH = False

def makeFlashPlotItem( flash, seconfig ):
    chsubevent = pg.PlotCurveItem()
    x = np.linspace( seconfig.nspersample*flash.tstart, seconfig.nspersample*flash.tend, len(flash.expectation) )
    y = flash.expectation
    chsubevent.setData( x=x, y=y, pen=(255,0,0,255) )
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
    wfm = opdata.getData()[:,ch]
    flashes, postwfm = getChannelFlashesCPP( ch, wfm, seconfig, ret_postwfm=True )
    postwfm -= 2048.0
    if opdisplay is not None:
        print "visualize!"
        opdisplay.clearUserWaveformItem()
        for flash in flashes:
            chsubevent = makeFlashPlotItem( flash, seconfig )
            opdisplay.addUserWaveformItem( chsubevent, ch=ch)
        # plot postwfm
        plot_postwfm = pg.PlotCurveItem()
        x = np.linspace( 0,  seconfig.nspersample*len(postwfm), len(postwfm) )
        plot_postwfm.setData( x=x, y=postwfm, pen=(0,255,0,255) )
        opdisplay.addUserWaveformItem( plot_postwfm )
            
    print flashes

if __name__ == "__main__":


    # Load config
    from pysubevent.pysubevent.cysubeventdisc import pySubEventModConfig
    config = pySubEventModConfig( "discr1", "subevent.cfg" )
    print config.cfd_threshold,config.fastconst
    
    # Load data
    from pylard.pylardata.rawdigitsopdata import RawDigitsOpData
    fname = "../../data/pmtratedata/run2668_filterreconnect_rerun.root"
    opdata = RawDigitsOpData( fname )
    ok = opdata.getNextEvent()

    if vis:
        app = QtGui.QApplication([])
        opdisplay = OpDetDisplay( opdata )
        opdisplay.show()
    else:
        opdisplay = None


    if ok:
        #test_findonesubevent( 0, opdata, config, opdisplay=opdisplay )
        test_getChannelFlashes( 0, opdata, config, opdisplay=opdisplay )


    if vis and ( (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION')):
        print "exec called ..."
        QtGui.QApplication.instance().exec_()
