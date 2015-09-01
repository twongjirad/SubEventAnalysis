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

    femconfig = FEMconfig( os.environ["SUBEVENTDATA"]+"/fem.cfg" )
    opdata = WFOpData( fname )

    out = rt.TFile( "output_femsim_nnhits.root", "RECREATE" )
    eventid = array.array( 'i', [0] )  # event number
    maxhits = array.array( 'i', [0] )  # max hits from trigger analysis
    winid   = array.array( 'i', [0] )  # window number (split total samples in 1.6 us chunks)
    maxpe   = array.array( 'i', [0] )    
    nnmaxhits = array.array( 'i', [0]*6 )
    zomaxhits = array.array( 'i', [0]*6 )
    chtrig = array.array( 'i', [0]*36 )

    tree = rt.TTree( "fem", "FEM simulation output" )
    tree.Branch( 'eventid', eventid, 'eventid/I' )
    tree.Branch( 'maxhits', maxhits, 'maxhits/I' )
    tree.Branch( 'winid', winid, 'winid/I' )
    tree.Branch( 'maxpe', maxpe, 'maxpe/I' )
    tree.Branch( 'chtrig', chtrig, 'chtrig[32]/I' )
    tree.Branch( 'nnmaxhits', nnmaxhits, 'nnmaxhits[6]/I' )
    tree.Branch( 'zomaxhits', zomaxhits, 'zomaxhits[6]/I' )

    beamwin = 1600.0  # 1.6 microseconds
    beamsamples = int(beamwin/15.625)

    eventid[0] = 0
    more = opdata.getEvent( eventid[0] )

    while more:
        trigs, pes, femchtriggers = runFEMsim( opdata.getData(slot=5), femconfig, maxch=32 )
        nwindows = len(trigs["discr1"])/(beamsamples+1)
        for iwin in xrange(0,nwindows):
            start = iwin*beamsamples
            end   = (iwin+1)*beamsamples

            # -- basic FEM trigger --
            maxhits[0] = np.max( trigs["discr1"][start:end] )
            maxpe[0] = np.max( pes["discr1"][start:end] )

            # -- discr fires in each channel -- 
            for ch in xrange(0,32):
                #print "CH ",ch,": ",femchtriggers["discr1"][start:end,ch]
                chtrig[ch] = np.max( femchtriggers["discr1"][start:end,ch] )
            #print "------------------------------------------------------------"

            # --- local nearest neighbors triggers (skip paddles) ---
            nnresults = formnntrigger( femchtriggers, start, end, verbose=0 )
            for nn in xrange(1,6):
                nnmaxhits[nn] = nnresults[nn]

            zoresults = formzotrigger( femchtriggers, start, end, verbose=0 )
            for nn in xrange(1,6):
                if nn in zoresults:
                    zomaxhits[nn] = zoresults[nn]
                else:
                    zomaxhits[nn] = 0

            # visualize window hits
            #imv.setImage( femchtriggers["discr1"][start:end,:] )
            #raw_input()
            # -- z order neighbors --
            tree.Fill()
            winid[0] = iwin

        eventid[0] += 1
        more = opdata.getEvent( eventid[0] )
        print "Event: ",eventid[0], more
        if eventid[0]>=500:
            break

    tree.Write()

if __name__ == "__main__":
    #import cProfile
    #cProfile.run( 'run_fem()', sort='cumulative' )
    run_fem()
