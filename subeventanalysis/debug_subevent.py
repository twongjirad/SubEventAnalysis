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

colorlist = [ ( 255, 0, 0, 255 ),
              ( 125, 125, 250, 255 ),
              ( 0, 0, 255, 255 ),
              ( 125, 125, 0, 255 ),
              ( 125, 0, 125, 255 ),
              ( 0, 125, 125, 255 ) ]

def prepWaveforms( opdata, boundarysubevent=None ):
    RC = 60000.0 # ns
    nsamples = opdata.getNBeamWinSamples()
    wfms = np.ones( (nsamples,32) )*2047.0
    qs   = np.zeros( (nsamples,32) )

    # if boundary subevent, we need to calculate corrections to the first part of the waveforms
    boundary_corrections = {}
    if boundarysubevent is not None:
        opdata.suppressed_wfm = {}
        for flash in boundarysubevent.getFlashList():
            ch = flash.ch
            t = flash.tstart
            wfm = flash.expectation
            qcorr = [0.0]
            for i in range(1,len(wfm)):
                q = 3.0*wfm[i]*(15.625/RC) + qcorr[i-1]*np.exp( -1.0*15.625/RC )
                qcorr.append( q )
            # keep going until q runs out
            while qcorr[-1]>1.0:
                q = qcorr[-1]*np.exp( -1.0*15.625/RC )
                qcorr.append( q )
            print "channel ",ch," has a boundary correction of length ",len(qcorr)," starting from time=",t
            boundary_corrections[ch] = ( t, np.asarray( qcorr, dtype=np.float ) )

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
        tlen = 1
        if ch in boundary_corrections.keys():
            print "apply boundary correction to waveform"
            tstart = boundary_corrections[ch][0]
            qcorr = boundary_corrections[ch][1]
            t1 = -tstart
            tlen = np.minimum( len(qcorr)-t1, len(wfms[:,ch]) )
            wfms[:,ch] += qcorr[t1:t1+tlen]
            ped = getpedestal( wfms[boundarysubevent.tend_sample:,ch], 10, 1.0 )
            # supress early subevent..
            opdata.suppressed_wfm[ch] = np.copy( wfms[:boundarysubevent.tend_sample-1,ch] )
            wfms[:boundarysubevent.tend_sample-1,ch] = ped


        ped = getpedestal( wfms[:,ch], 20, 2.0*scale )
        if ped is not None:
            print "ch ",ch," ped=",ped
            wfms[:,ch] -= ped
            if boundarysubevent is not None and ch in opdata.suppressed_wfm:
                # subtract ped off of suppressed portion
                opdata.suppressed_wfm[ch] -= ped
        else:
            print "ch ",ch," has bad ped"
            wfms[:,ch] -= 0.0
        # calc undershoot and correct
        for i in range(np.maximum(1,tlen),len(qs[:,ch])):
            #for j in range(i+1,np.minimum(i+1+200,len(qs[:,ch])) ):
            q = wfms[i,ch]*(15.625/RC) + qs[i-1,ch]*np.exp(-1.0*15.625/RC) # 10 is fudge factor!
            qs[i,ch] = q
            wfms[i,ch] += q
        opdata.getData(slot=5)[:,ch] = wfms[:,ch]
        opdata.getPedestal(slot=5)[ch] = 0.0
            
    return wfms,qs

from pysubevent.pysubevent.cysubeventdisc import pyCosmicWindowHolder, formCosmicWindowSubEventsCPP
def prepCosmicSubEvents( opdata ):
    # stuff data into interface class
    cosmics = pyCosmicWindowHolder()
    for ch,timelist in opdata.cosmics.chtimes.items():
        if ch>=32:
            continue
        for t in timelist:
            cwd = opdata.cosmics.chwindows[ch][t]
            wfm = np.asarray( cwd.wfm, dtype=np.float )
            wfm -= 2048.0 # remove pedestal. no means to measure pedestal
            if cwd.slot==6:
                wfm *= 10.0 # high gain window
                print "lg waveform: ",ch,t
                cosmics.addLGWaveform( ch, t, wfm)
            elif cwd.slot==5:
                cosmics.addHGWaveform( ch, t, wfm )
        
    subevents = formCosmicWindowSubEventsCPP( cosmics, config )
    boundarysubevent = None
    for subevent in subevents.getlist():
        #print "subevent: ",subevent.tstart_sample, subevent.tend_sample
        if ( subevent.tstart_sample<0 and subevent.tend_sample>0 ):
            print "BOUNDARY SUBEVENT"
            boundarysubevent = subevent
    return subevents,boundarysubevent


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

        cosmic_subevents, boundary_subevent = prepCosmicSubEvents( opdata )
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
    #ok = opdata.getNextEvent()
    ok = opdata.getEvent(43)
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
