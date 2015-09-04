import os,sys
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import ROOT as rt
import numpy as np
import array

# pylard
from pylard.pylardata.wfopdata import WFOpData

#sub-event code
from pysubevent.cfdiscriminator import cfdiscConfig, runCFdiscriminator
#from cfdiscriminator import cfdiscConfig, runCFdiscriminator
from pysubevent.femsim import FEMconfig, runFEMsim, runFEMsimChannel
from nntrigger import formnntrigger
from zotrigger import formzotrigger

def run_fem():
    #  expects 'raw_wf_tree'
    #fname='/Users/twongjirad/working/uboone/data/FlasherData_080715/wf_run004.root'
    fname='../wf_run001.root'

    femconfig = FEMconfig( os.environ["SUBEVENTDATA"]+"/fem.json" )
    opdata = WFOpData( fname )

    out = rt.TFile( "output_femsim_nnhits.root", "RECREATE" )
    eventid = array.array( 'i', [0] )  # event number
    winid   = array.array( 'i', [0] )  # window number (split total samples in 1.6 us chunks)
    maxhits = array.array( 'i', [0] )  # max hits from trigger analysis
    maxdiff   = array.array( 'i', [0] )    
    maxadc    = array.array( 'i', [0] )    
    nnmaxhits = array.array( 'i', [0]*6 )
    nnmaxdiff = array.array( 'i', [0]*6 )
    nnmaxadc  = array.array( 'i', [0]*6 )
    zomaxhits = array.array( 'i', [0]*6 )
    zomaxdiff = array.array( 'i', [0]*6 )
    zomaxadc  = array.array( 'i', [0]*6 )
    numchtrigs = array.array( 'i', [0]*36 )
    chmaxdiff = array.array( 'i', [0]*36 )
    chmaxadc = array.array( 'i', [0]*36 )


    tree = rt.TTree( "fem", "FEM simulation output" )

    tree.Branch( 'eventid', eventid, 'eventid/I' )
    tree.Branch( 'winid', winid, 'winid/I' )

    tree.Branch( 'maxhits', maxhits, 'maxhits/I' )    
    tree.Branch( 'maxdiff', maxdiff, 'maxdiff/I' )
    tree.Branch( 'maxadc', maxadc, 'maxadc/I' )

    tree.Branch( 'nnmaxhits', nnmaxhits, 'nnmaxhits[6]/I' )    
    tree.Branch( 'nnmaxdiff', nnmaxdiff, 'nnmaxdiff[6]/I' )
    tree.Branch( 'nnmaxadc', nnmaxadc, 'nnmaxadc[6]/I' )

    tree.Branch( 'zomaxhits', zomaxhits, 'zomaxhits[6]/I' )    
    tree.Branch( 'zomaxdiff', zomaxdiff, 'zomaxdiff[6]/I' )
    tree.Branch( 'zomaxadc', zomaxadc, 'zomaxadc[6]/I' )

    tree.Branch( 'numchtrigs', numchtrigs, 'numchtrigs[36]/I' )
    tree.Branch( 'chmaxdiff', chmaxdiff, 'chmaxdiff[36]/I' )
    tree.Branch( 'chmaxadc', chmaxadc, 'chmaxadc[36]/I' )

    beamwin = 1600.0  # 1.6 microseconds
    beamsamples = int(beamwin/15.625)

    eventid[0] = 0
    more = opdata.getEvent( eventid[0] )

    while more:
        trigs, maxadcs, femmaxdiff, femchtriggers, femchmaxadcs, femchdiffs  = runFEMsim( opdata.getData(slot=5), femconfig, maxch=32 )
        nwindows = len(trigs["discr1"])/(beamsamples+1)
        for iwin in xrange(0,nwindows):
            start = iwin*beamsamples
            end   = (iwin+1)*beamsamples

            # -- basic FEM trigger --
            maxhits[0] = np.max( trigs["discr1"][start:end] )
            maxdiff[0] = np.max( femmaxdiff["discr1"][start:end] )
            maxadc[0] = np.max( maxadcs["discr1"][start:end] )
            if maxdiff[0]>100000:
                print "event ",eventid[0]," maxdiff=",maxdiff[0]

            # -- discr fires in each channel -- 
            for ch in xrange(0,32):
                #print "CH ",ch,": ",femchtriggers["discr1"][start:end,ch]
                numchtrigs[ch] = np.max( femchtriggers["discr1"][start:end,ch] )
                chmaxdiff[ch] = np.max( femchdiffs["discr1"][start:end,ch] )
                chmaxadc[ch] = np.max( femchmaxadcs["discr1"][start:end,ch] )
            #print "------------------------------------------------------------"

            # --- local nearest neighbors triggers (skip paddles) ---
            nnresults = formnntrigger( femchtriggers, femchdiffs, femchmaxadcs, start, end, verbose=0 )
            for nn in xrange(1,6):
                nnmaxhits[nn] = nnresults["maxhits"][nn]
                nnmaxdiff[nn] = nnresults["maxdiff"][nn]
                nnmaxadc[nn]  = nnresults["maxadc"][nn]

            zoresults = formzotrigger( femchtriggers, femchdiffs, femchmaxadcs, start, end, verbose=0 )
            for zo in xrange(1,6):
                if zo in zoresults["maxhits"]:
                    zomaxhits[zo] = zoresults["maxhits"][zo]
                    zomaxdiff[zo] = zoresults["maxdiff"][zo]
                    zomaxadc[zo]  = zoresults["maxadc"][zo]

            # visualize window hits
            #imv.setImage( femchtriggers["discr1"][start:end,:] )
            #raw_input()
            # -- z order neighbors --
            tree.Fill()
            winid[0] = iwin

        eventid[0] += 1
        more = opdata.getEvent( eventid[0] )
        print "Event: ",eventid[0], more
        if eventid[0]>=100:
            break

    tree.Write()

if __name__ == "__main__":
    #import cProfile
    #cProfile.run( 'run_fem()', sort='cumulative' )
    run_fem()
