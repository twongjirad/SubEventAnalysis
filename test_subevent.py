import os,sys
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np

# pylard
from pylard.pylardisplay.opdetdisplay import OpDetDisplay
from pylard.pylardata.wfopdata import WFOpData
from pylard.pylardata.rawdigitsopdata import RawDigitsOpData

#sub-event code
from subeventdisc import subeventdiscConfig, runSubEventDisc, runSubEventDiscChannel, SubEvent, makeSubEventAccumulators, formSubEvents
import pysubevent.pedestal as ped
import pysubevent.pmtcalib as spe

from ROOT import *

app = QtGui.QApplication([])

HIGHFEM = 5
LOWFEM  = 6
pmtspe = spe.getCalib( "config/pmtcalib_20150807.json" )

#  expects 'raw_wf_tree'
#fname='/Users/twongjirad/working/uboone/data/FlasherData_080115/wf_run001.root'
fname='/Users/twongjirad/working/uboone/data/FlasherData_080715/wf_run004.root'
#fname='/Users/twongjirad/working/uboone/data/FlasherData_080115/wf_run005.root'
opdata = WFOpData( fname )

#fname='/Users/twongjirad/working/uboone/data/DAQTest_081315/raw_digits_1387.root'
#fname='/Users/twongjirad/working/uboone/data/LightLeakData/20150818/rawdigits.pmtonly.noiserun.1573.0000.root'
#opdata = RawDigitsOpData( fname )

opdisplay = OpDetDisplay( opdata )
opdisplay.show()

femch = 9

#opdisplay.gotoEvent( 21 )

#wf = opdata.getData( slot=5)[:,femch]
#print "MAX: ",np.max(wf)
#if np.max(wf)>=4094:
#    print "switch to low gain!"
#    wf = opdata.getData( slot=6)[:,femch]
#    opdisplay.gotoEvent( 21, slot=6 )

chbych = False
drawchsubevents = True
config = subeventdiscConfig( "discr0", "subevent.cfg" )

def makeChSubEventPlot( chsubevent, chspe,displayslot ):
    tx = []
    ty = []
    thresh = []
    for (x,y) in chsubevent.expectation:
        if displayslot==LOWFEM:
            gy = (chsubevent.gainfactor/10.0)*y
        else:
            gy = (chsubevent.gainfactor)*y
        tx.append( x )
        ty.append( gy )
        sig = np.sqrt( gy/20.0 )
        thresh.append( gy + 3.0*sig*20.0 )
    y = np.array( ty, dtype=np.float )
    x = np.array( tx, dtype=np.float )
    th = np.array( thresh, dtype=np.float )
    pexp = pg.PlotCurveItem()
    pexp.setData( x=x, y=y, pen=(255,0,0,255) )
    pthresh = pg.PlotCurveItem()
    pthresh.setData( x=x, y=th, pen=(0,255,0,255) )
    return pexp, pthresh

def runChSubEventTest( opdata, opdisplay ):
    ch_subevents = {}
    products = []
    if not chbych:
        chsubevtdict, chpostwfms = runSubEventDisc( opdata, config, retpostwfm=True, maxch=32 )
        ch_subevents = chsubevtdict
        for ch,subevents in chsubevtdict.items():
            for subevent in subevents:
                tx = []
                ty = []
                thresh = []
                for (x,y) in subevent.expectation:
                    gy = subevent.gainfactor*y
                    tx.append( x )
                    ty.append( gy )
                    sig = np.sqrt( gy/20.0 )
                    thresh.append( gy + 3.0*sig*20.0 )
                y = np.array( ty, dtype=np.float )
                x = np.array( tx, dtype=np.float )
                th = np.array( thresh, dtype=np.float )

                if drawchsubevents:
                    pexp = pg.PlotCurveItem()
                    pexp.setData( x=x, y=y, pen=(255,0,0,255) )

                    pthresh = pg.PlotCurveItem()
                    pthresh.setData( x=x, y=th, pen=(0,255,0,255) )

                    #opdisplay.addUserWaveformItem( pexp, ch=ch )  
                    #opdisplay.addUserWaveformItem( pthresh, ch=ch )  
                    products.append( { "plotitem":pexp,"femch":ch,"screen":"waveform"} )
                    products.append( { "plotitem":pthresh,"femch":ch,"screen":"waveform"} )

                    pwfm = pg.PlotCurveItem()
                    postwfm = chpostwfms[ch]
                    pwfm.setData( x=range(0,len(postwfm)), y=postwfm-ped.getpedestal(postwfm, 10, 10), pen=(255,255,0,255) )
                    #opdisplay.addUserWaveformItem( pwfm, ch=ch )
                    products.append( { "plotitem":pwfm, "femch":ch, "screen":"waveform"} )
    else:
        print "runChSubEventTest Event-by-Event!"
        opdisplay.setOverlayMode( True )

        for ch in xrange(0,32):
            print "CHANNEL ",ch
            opdisplay.selectChannels( [ch] )
            chwfm = opdata.getData(slot=5)[:,ch]
            if np.max(chwfm)>=4094:
                print "channel ",ch," switch to low gain!"
                chwfm = opdata.getData(slot=6)[:,ch]
            subevents,wfm =  runSubEventDiscChannel( chwfm, config, femch, retpostwfm=True )
            ch_subevents[ ch ] = subevents
            for subevent in subevents:
                tx = []
                ty = []
                thresh = []
                for (x,y) in subevent.expectation:
                    tx.append( x )
                    ty.append( y )
                    sig = np.sqrt( y/20.0 )
                    thresh.append( y + 3.0*sig*20.0 )
                y = np.array( ty, dtype=np.float )
                x = np.array( tx, dtype=np.float )
                th = np.array( thresh, dtype=np.float )

                if drawchsubevents:
                    pexp = pg.PlotCurveItem()
                    pexp.setData( x=x, y=y, pen=(255,0,0,255) )

                    pthresh = pg.PlotCurveItem()
                    pthresh.setData( x=x, y=th, pen=(0,255,0,255) )

                    opdisplay.addUserWaveformItem( pexp, ch=ch )
                    opdisplay.addUserWaveformItem( pthresh, ch=ch )

                    print subevent.expectation
                    products.append( { "plotitem":pexp,"femch":ch,"screen":"waveform"} )
                    products.append( { "plotitem":pthresh,"femch":ch,"screen":"waveform"} )

                    pwfm = pg.PlotCurveItem()
                    postwfm = wfm
                    pwfm.setData( x=range(0,len(postwfm)), y=postwfm-ped.getpedestal(postwfm, 10, 10), pen=(255,255,0,255) )
                    opdisplay.addUserWaveformItem( pwfm, ch=ch )
                    opdisplay.plotData()
                    #raw_input()
                    opdisplay.clearUserWaveformItem()
                    products.append( { "plotitem":pwfm,"femch":ch,"screen":"waveform"} )

    # merger of events
    merger_gatehalfwidth = 1
    pethresh = 5.0
    nchthresh = 3.0
    hitacc, peacc = makeSubEventAccumulators( ch_subevents, merger_gatehalfwidth, opdata, pmtspe )

    # defining subevents
    print np.argmax(hitacc),hitacc
    print np.argmax(peacc),peacc
    phitacc = pg.PlotCurveItem()
    phitacc.setData( x=range(0,len(hitacc)), y=hitacc, pen=(255,255,0,255) )
    ppeacc = pg.PlotCurveItem()
    ppeacc.setData( x=range(0,len(peacc)), y=peacc, pen=(0,125,255,255) )

    products.append( { "plotitem":phitacc,"femch":None,"screen":"waveform"} )
    products.append( { "plotitem":ppeacc,"femch":None,"screen":"waveform"} )

    return products

def runSubEventTest( opdata, opdisplay ):
    subevents = formSubEvents( opdata, config, pmtspe )
    print "Number of Subevents: ",len(subevents)
    products = []
    displayslot = int(opdisplay.slot.text())
    for subevent in subevents:
        for ch,subeventlist in subevent.chsubeventdict.items():
            chspe = pmtspe[ch]
            if len(subeventlist)>0:
                print "FEMCH ",ch," has subevent: spe=",chspe," gainfactor=",subeventlist[0].gainfactor
            
            # draw chsubevents
            for chsubevent in subeventlist:
                pexp,pthresh = makeChSubEventPlot( chsubevent, chspe, displayslot )
                products.append( { "plotitem":pexp,"femch":ch,"screen":"waveform"} )
                products.append( { "plotitem":pthresh,"femch":ch,"screen":"waveform"} )
        
        phitacc = pg.PlotCurveItem()
        phitacc.setData( x=range(0,len(subevent.hitacc)), y=subevent.hitacc, pen=(255,255,102,255) )
        products.append( { "plotitem":phitacc,"femch":None,"screen":"waveform"} )

        ppeacc = pg.PlotCurveItem()
        ppeacc.setData( x=range(0,len(subevent.peacc)), y=subevent.peacc, pen=(255,0,255,255) )
        products.append( { "plotitem":ppeacc,"femch":None,"screen":"waveform"} )

        print "Subevent: ",np.argmax( subevent.hitacc )

    
    return products

def run_subevent_finder():
    global opdata


    f = TFile("output_test_subeventfinder.root", "RECREATE" )
    t = TTree( "subevent", "Subevent info" )
    # variables
    eventid = array.array('i',[0])
    nsubevents = array.array('i',[0])
    tpeak = array.array('i',[0]*20)
    hitmax = array.array('i',[0]*20)
    pemax = array.array('f',[0]*20)

    ievent = 0
    ok = opdata.getEntry( ievent )
    
    while ok:

        eventid[0] = ievent
        subevents = formSubEvents( opdata, config, pmtspe )
        nsubevents[0] = len(subevents)

        if len(subevents)>0:
            print "found ",len(subevents)," subevents in event ",ievent
            for n,subevent in enumerate(subevents):
                if n>=20:
                    break
                tpeak[n] = subevent.tpeak
                hitmax[n] = subevent.hitmax
                pemax[n] = subevent.pemax
            #opdisplay.run_user_analysis.setChecked(True)
            #opdisplay.gotoEvent( ievent, slot=5 )
            #opdisplay.plotData() 
            #opdisplay.run_user_analysis.setChecked(False)
            #raw_input()
        else:
            for n in range(0,20):
                tpeak[n] = 0
                hitmax[n] = 0
                pemax[n] = 0
        t.Fill()
        ok = opdata.getEvent( ievent, slot=5 )
    t.Write()

if __name__ == "__main__":
    print "batch mode"
    import cProfile
    #cProfile.run('run_subevent_finder()')
    run_subevent_finder()
else:
    print "interactive mode"
    opdisplay.addUserAnalysis( runSubEventTest )
    #opdisplay.addUserAnalysis( runChSubEventTest )
    opdisplay.gotoEvent( 21, slot=5 )
    opdisplay.plotData()

