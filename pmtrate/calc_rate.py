import os,sys
import ROOT as rt
import numpy as np
from array import array


# pylard
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
from pylard.pylardata.wfopdata import WFOpData
from pylard.pylardata.rawdigitsopdata import RawDigitsOpData
from pysubevent.pedestal import getpedestal
from pysubevent.cfdiscriminator import cfdiscConfig, runCFdiscriminator
from pylard.pylardisplay.opdetdisplay import OpDetDisplay

NCHANS = 32

# config
cfdsettings = cfdiscConfig("disc1","cfdconfig.json")


def calc_rates( inputfile, nevents, outfile, wffile=False, rawdigitfile=False, VISUALIZE=False ):
    # check that the data file type was selected
    if wffile==False and rawdigitfile==False:
        print "Select either wffile or rawdigitfile"
        return
    # load data
    if wffile==True:
        opdata = WFOpData( inputfile )
    elif rawdigitfile==True:
        opdata = RawDigitsOpData( inputfile )

    out = rt.TFile( outfile, "RECREATE" )
    # Event tree
    eventtree = rt.TTree("eventtree","PMT Rates")
    event = array('i',[0])
    samples = array('i',[0])
    nfires = array('i',[0]*NCHANS)
    echmax = array('f',[0])
    eventtree.Branch( 'event', event,'event/I' )
    eventtree.Branch( 'samples', samples, 'samples/I' )
    eventtree.Branch( 'nfires', nfires, 'nfires[%d]/I'%(NCHANS) )
    eventtree.Branch( 'chmax', echmax, 'chmax/F' )

    # Pulse Tree
    pulsetree = rt.TTree("pulsetree","PMT Rates")
    pch = array('i',[0])
    pt = array( 'f',[0] )
    pwindt = array( 'f',[0] )
    pchdt = array( 'f',[0] )
    pmaxamp = array('f',[0])
    ped = array('f',[0])
    pchmaxamp = array('f',[0])
    parea = array('f',[0])
    pulsetree.Branch( 'event', event, 'event/I' )
    pulsetree.Branch( 'ch',pch,'ch/I' )
    pulsetree.Branch( 't',pt,'t/F' )
    pulsetree.Branch( 'windt',pwindt,'windt/F' )
    pulsetree.Branch( 'chdt',pchdt,'chdt/F' )
    pulsetree.Branch( 'amp',pmaxamp,'amp/F' )
    pulsetree.Branch( 'area',parea,'area/F' )
    pulsetree.Branch( "ped",ped,"ped/F")
    pulsetree.Branch( 'chmaxamp',pchmaxamp,'chmaxamp/F' )

    first_event = opdata.first_event
    if VISUALIZE:
        opdisplay = OpDetDisplay( opdata )
        opdisplay.show()

    for ievent in range(first_event,first_event+nevents+1):
        if ievent%50==0:
            print "Event: ",ievent
        event[0] = ievent

        if VISUALIZE:
            more = opdisplay.gotoEvent( ievent )
        else:
            more = opdata.getEvent( ievent )
        if not more:
            print "not more"
            break

        # for each event gather disc fires and sort by time
        event_times = []
        event_discs = {}
        echmax[0] = 0
        chpedestals = {}
        chmaxamps = {}
        for femch in range(0,NCHANS):
            wfm = opdata.getData(slot=5)[:,femch]            
            discs = runCFdiscriminator( wfm, cfdsettings )
            ped[0] = getpedestal( wfm, 10, 2 )
            chpedestals[femch] = ped[0]

            nfires[femch]  = len(discs)
            pch[0] = femch
            pchmaxamp[0] = np.max( wfm - ped[0] )
            chmaxamps[femch] = pchmaxamp[0]
            if echmax[0]<pchmaxamp[0]:
                echmax[0] = pchmaxamp[0]
            samples[0] = len(wfm)

            pchdt[0] = -1
            pmaxamp[0] = 0
            
            if len(discs)==0:
                print "Discriminator found zero pusles in channel=",femch," event=",event[0]
            
            for idisc,disc in enumerate(discs):
                disc.ch = femch
                t = disc.tfire + 0.01*disc.ch # the channel number is just to keep a unique tag
                event_times.append( t )
                event_discs[t] = disc

                tdisc = disc.tfire
                disc.pmaxamp = np.max( wfm[tdisc:tdisc+cfdsettings.deadtime]-ped[0] )
                pped = getpedestal( wfm[ np.maximum(0,tdisc-20):tdisc ] , 5, 2 )
                if pped is None:
                    pped = ped[0]
                disc.parea = np.sum( wfm[tdisc:tdisc+cfdsettings.deadtime] ) - cfdsettings.deadtime*pped

                if idisc>0:
                    disc.pchdt = tdisc - discs[idisc-1].tfire
                else:
                    disc.pchdt = -1
                if VISUALIZE:
                    discfire = pg.PlotCurveItem()
                    x = np.linspace( 15.625*(tdisc-5), 15.625*(tdisc+5+cfdsettings.deadtime), cfdsettings.deadtime+10 )
                    y = np.ones( cfdsettings.deadtime+10 )*femch
                    y[5:5+cfdsettings.deadtime] += 2
                    discfire.setData( x=x, y=y, pen=(255,0,0,255) )
                    opdisplay.addUserWaveformItem( discfire, femch )
        event_times.sort()
        for idisc,t in enumerate(event_times):
            disc = event_discs[t]
            pch[0] = disc.ch
            pt[0] = disc.tfire
            pmaxamp[0] = disc.pmaxamp
            pchdt[0] = disc.pchdt
            ped[0] = chpedestals[disc.ch]
            pchmaxamp[0] = chmaxamps[disc.ch]
            parea[0] = disc.parea
            
            if idisc==0:
                pwindt[0] = -1
            else:
                pwindt[0] = disc.tfire-event_discs[ event_times[idisc-1] ].tfire
            
            pulsetree.Fill()
            
        if VISUALIZE:
            print "please enjoy plot"
            raw_input()
        eventtree.Fill()
    eventtree.Write()
    pulsetree.Write()


def runloop():
    for f in os.listdir( "../../data/pmtratedata/" ):
        if ".root" not in f:
            continue
        if "filter" not in f:
            continue
        #print f
        input = "../../data/pmtratedata/"+f.strip()
        output = "pmtratestudy/"+f.strip()
        calc_rates( input, 10000, output, rawdigitfile=True, wffile=False )
        print output
    
        
if __name__ == "__main__":
    app = QtGui.QApplication([])
    #input = "../../data/pmtbglight/run2228_pmtrawdigits_subrun0.root"
    #input = "../../data/pmttriggerdata/run2290_subrun0.root"
    #input = "../../data/pmtratedata/run1536_pmtrawdigits.root"
    #output = "test.root"
    #output = "pmtratestudy/run1536.root"
    runloop()

    #if len(sys.argv)==3:
    #    input = sys.argv[1]
    #    output = sys.argv[2]

    #calc_rates( input, 500, output, rawdigitfile=True, wffile=False )

    #import cProfile
    #cProfile.run("calc_rates(\"%s\",200,\"%s\",rawdigitfile=True,wffile=False)"%(input,output))
