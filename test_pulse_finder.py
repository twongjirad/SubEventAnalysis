import os,sys
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg

# pylard
from pylard.pylardisplay.opdetdisplay import OpDetDisplay
from pylard.pylardata.wfopdata import WFOpData
from pylard.pylardata.rawdigitsopdata import WFOpData

#sub-event code
from cfdiscriminator import cfdiscConfig, runCFdiscriminator
from femsim import FEMconfig, runFEMsim, runFEMsimChannel

app = QtGui.QApplication([])

#  expects 'raw_wf_tree'
#fname='/Users/twongjirad/working/uboone/data/FlasherData_080115/wf_run001.root'
#fname='/Users/twongjirad/working/uboone/data/FlasherData_080715/wf_run004.root'
fname='/Users/twongjirad/working/uboone/data/FlasherData_080115/wf_run005.root'

opdata = WFOpData( fname )

opdisplay = OpDetDisplay( opdata )
opdisplay.show()

#opdisplay.setOverlayMode( True )
#opdisplay.selectChannels( [3] )
#opdisplay.gotoEvent( 0 )

#wf = opdata.opdetdigi[:,3]
#print wf

#discr0 = cfdiscConfig( configfile="discr0.cfg" )
#triggers = runCFdiscriminator( wf, discr0 )
#print triggers

#femconfig = FEMconfig( "config/fem.cfg" )
#femtriggers, femmaxadc = runFEMsimChannel( wf, femconfig, 3, femconfig.spe )
#print femtriggers
#print femmaxadc

#for t in femtriggers["discr1"]:
#    trigmark = pg.InfiniteLine( pos=t, movable=False, angle=90, pen=(255,0,0,255) )
#    opdisplay.addUserWaveformItem( trigmark )

opdisplay.plotData()
