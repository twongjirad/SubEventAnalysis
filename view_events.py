import os,sys
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np

# pylard
from pylard.pylardisplay.opdetdisplay import OpDetDisplay
from pylard.pylardata.wfopdata import WFOpData
from pylard.pylardata.rawdigitsopdata import RawDigitsOpData

#sub-event code
#from pysubevent.pysubevent.subeventdisc import subeventdiscConfig, runSubEventDisc, runSubEventDiscChannel
#import pysubevent.utils.pedestal as ped

#  expects 'raw_wf_tree'
#fname='/Users/twongjirad/working/uboone/data/FlasherData_080115/wf_run001.root'
#fname='/Users/twongjirad/working/uboone/data/FlasherData_080715/wf_run004.root'
#fname='/Users/twongjirad/working/uboone/data/FlasherData_080115/wf_run005.root'
#fname='/Users/twongjirad/working/uboone/data/FlasherData_082715/wf_run000.root'
#fname='/Users/twongjirad/working/uboone/data/FlasherData_080115/wf_run001.root'
#fname='/Users/twongjirad/working/uboone/data/pmtratedata/run2617_filterreconnect_subrun2.root'
fname="../data/pmttriggerdata/run3090_pmtrawdigits.root"
#fname='/Users/twongjirad/working/uboone/mc/low_energy_protons.root'
#fname="/Users/twongjirad/working/uboone/data/pmttriggerdata/run2213_pmtrawdigits.root"

#fname='wf_run001.root'
#fname = "/Users/twongjirad/working/uboone/data/splittermodtest/run2083_pmtonly_rawdigits.root"
#fname='wf_test123_pt_trig.root'
#fname="/Users/twongjirad/working/uboone/data/20150909_CosmicDiscTuning/wf_run007.root"
#opdata = WFOpData( fname )

#fname='/Users/twongjirad/working/uboone/data/DAQTest_081315/raw_digits_1387.root'
#fname='/Users/twongjirad/working/uboone/data/LightLeakData/20150818/rawdigits.pmtonly.noiserun.1573.0000.root'
#fname='/Users/twongjirad/working/uboone/data/LightLeakData/20150818/rawdigits.pmtonly.noiserun.1574.0000.root'
#fname="../data/pmttriggerdata/run1807_pmtrawdigits.root"
#fname="/Users/twongjirad/working/uboone/data/pmtbglight/run2228_pmtrawdigits_subrun0.root"
opdata = RawDigitsOpData( fname )

app = QtGui.QApplication([])
opdisplay = OpDetDisplay( opdata )
opdisplay.show()

