import os,sys

from pysubevent.pycfdiscriminator.cfdiscriminator import cfdiscConfig
import calcRate

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

    # discriminator config
    cfdsettings = cfdiscConfig("disc1","cfdconfig.json")

    vis = False
    if vis==True:
        from pyqtgraph.Qt import QtGui, QtCore
        app = QtGui.QApplication([])
    #input = "../../data/pmtbglight/run2228_pmtrawdigits_subrun0.root"
    #input = "../../data/pmttriggerdata/run2290_subrun0.root"
    #input = "../../data/pmtratedata/run1536_pmtrawdigits.root"
    #output = "test.root"
    #output = "pmtratestudy/run1536.root"
    #runloop()
    # sys.exit()

    if len(sys.argv)==3:
        input = sys.argv[1]
        output = sys.argv[2]

    calcRate.calcEventRates( cfdsettings, input, 500, output, rawdigitfile=True, wffile=False, VISUALIZE=vis )

    #import cProfile
    #cProfile.run("calc_rates(\"%s\",200,\"%s\",rawdigitfile=True,wffile=False)"%(input,output))

