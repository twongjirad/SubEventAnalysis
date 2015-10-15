import os,sys
import numpy as np
from pysubevent.utils.pedestal import getpedestal
from prepWaveforms import prepWaveforms, prepCosmicSubEvents

def runSubEventFinder( config, input, outfilename ):
    print "Opening ... ", input

    # Load Data
    from pylard.pylardata.rawdigitsopdata import RawDigitsOpData
    opdata = RawDigitsOpData( input )
    ok = opdata.getNextEvent()
    
    # Load Calibration
    from pysubevent.pysubevent.cysubeventdisc import formSubEventsCPP
    import pysubevent.utils.pmtcalib as spe
    pmtspe = spe.getCalib( "../config/pmtcalib_20150930.json" )

    # Setup Output
    from pysubevent.pysubevent.cysubeventdisc import pyWaveformData, pySubEventIO, pySubEventList

    subeventio = pySubEventIO( outfilename, 'w' )

    nevents = 0
    while ok:

        # first we get cosmic discriminator windows and make them into subevents
        cosmic_subevents,boundarysubevent = prepCosmicSubEvents( opdata, config )
        wfms,qs = prepWaveforms( opdata, boundarysubevent )   # extract numpy arrays, undershoot correct, pedestal correct
        pywfms = pyWaveformData()  # packages
        pywfms.storeWaveforms( wfms )
        
        # beam window subevents
        subevents, unclaimedflashes = formSubEventsCPP( pywfms, config, pmtspe )
        nsubevents = subevents.size

        subeventio.clearlist()
        subeventio.eventid = opdata.current_event
        subeventio.chmaxamp = np.max( wfms )
        print "chmaxamp: ",subeventio.chmaxamp
        subeventio.transferSubEventList( subevents )
        subeventio.transferSubEventList( cosmic_subevents )
        subeventio.fill()
        nevents += 1
        #if nsubevents>0:
        #raw_input()
        #if nevents>=200:
        #    break
        if opdata.current_event>=1405:
            break
        ok = opdata.getNextEvent()


    subeventio.write()


if __name__ == "__main__":

    # Load config
    from pysubevent.pysubevent.cysubeventdisc import pySubEventModConfig
    config = pySubEventModConfig( "discr1", "subevent.cfg" )

    inputfile = sys.argv[1]
    outfile   = sys.argv[2]
    
    print inputfile, outfile
    
    runSubEventFinder( config, inputfile, outfile )
