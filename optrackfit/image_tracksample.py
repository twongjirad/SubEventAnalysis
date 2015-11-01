import os,sys
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from pylard.pylardisplay.detectordisplay import DetectorDisplay
from devoptrackfit import TrackHypothesis, makeVoxelList, photonlib
from ROOT import *


app = QtGui.QApplication([])

detdisplay = DetectorDisplay()
detdisplay.load_geometry( "../../pylard/microboone_32pmts_nowires_cryostat.dae" )
detdisplay.show()

if __name__ == "__main__":

    QE = 0.0093
    LY = 29000
    dEdx = 2.0
    fprompt = 0.3

    data = np.load( "tracksamples.npz" )

    chain = data['arr_0']

    denom = float(len( chain ))

    print len(chain)," samples"
    pnts = []

    for n,pos in enumerate(chain):
        if np.random.rand()>0.1:
            continue
        print "plotting event ",n
        track = TrackHypothesis( pos[:3], pos[3:] )
        steps, photons = makeVoxelList( track, LY, dEdx )
        np_steps = np.asarray( steps )
        np_steps[:,2] -= 500.0
        np_steps[:,0] -= 125.0
        np_steps[:,1] -= 125.0
        np_steps *= 10.0
        strack = gl.GLScatterPlotItem(pos=np_steps, color=(1,1,1,1), size=1.0)
        detdisplay.addItem( strack )
            

    raw_input()
        
        
