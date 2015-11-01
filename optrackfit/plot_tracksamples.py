import os,sys
import numpy as np
from ROOT import *
from devoptrackfit import TrackHypothesis, makeVoxelList, photonlib

if __name__ == "__main__":

    QE = 0.0093
    LY = 29000
    dEdx = 2.0
    fprompt = 0.3

    data = np.load( "tracksamples.npz" )

    chain = data['arr_0']

    f = TFile("test.root", "RECREATE")
    
    hzy = TH2D("hzy", ";z;y", photonlib.Nz, photonlib.zmin, photonlib.zmax, photonlib.Ny, photonlib.ymin, photonlib.ymax )
    hxy = TH2D("hxy", ";x;y", photonlib.Nx, photonlib.xmin, photonlib.xmax, photonlib.Ny, photonlib.ymin, photonlib.ymax )
    hzx = TH2D("hzx", ";z;x", photonlib.Nz, photonlib.zmin, photonlib.zmax, photonlib.Nx, photonlib.xmin, photonlib.xmax )
               
    denom = float(len( chain ))

    print len(chain)," samples"
    for pos in chain:
        
        track = TrackHypothesis( pos[:3], pos[3:] )
        
        steps, photons = makeVoxelList( track, LY, dEdx )
        for step in steps:
            hzy.Fill( step[2], step[1], 1.0/denom )
            hxy.Fill( step[0], step[1], 1.0/denom )
            hzx.Fill( step[2], step[0], 1.0/denom )
    
    print "fill done"
    hzy.Write()
    hxy.Write()
    hzx.Write()

    c = TCanvas("c","",1200, 400 )
    c.Divide(3,1)
    c.cd(1)
    hzy.Draw("COLZ")
    c.cd(2)
    hxy.Draw("COLZ")
    c.cd(3)
    hzx.Draw("COLZ")

    c.Draw()
    c.Update()
    print "well?"
    raw_input()
        
        
