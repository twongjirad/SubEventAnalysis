import os,sys
import numpy as np
from pysubevent.utils.pedestal import getpedestal

def prepWaveforms( opdata ):
    RC = 50000.0 # ns
    nsamples = opdata.getNBeamWinSamples()
    wfms = np.ones( (nsamples,32) )*2047.0
    qs   = np.zeros( (nsamples,32) )
    for ch in range(0,32):
        scale = 1.0
        if np.max( opdata.getData()[:,ch] )<4090:
            wfms[:,ch] = opdata.getData(slot=5)[:,ch]
        else:
            print "swap HG ch",ch," with LG wfm"
            lgwfm = opdata.getData(slot=6)[:,ch]
            lgped = getpedestal( lgwfm, 20, 2.0 )
            if lgped is None:
                print "ch ",ch," LG has bad ped"
                lgped = opdata.getData(slot=6)[0,ch]
            wfms[:,ch] = lgwfm-lgped
            print "lg ped=",lgped," wfm[0-10]=",np.mean( wfms[0:10,ch] )
            wfms[:,ch] *= 10.0
            scale = 10.0
            #opdata.getData(slot=5)[:,ch] = wfms[:,ch] + lgped
            #opdata.getPedestal(slot=5)[ch] = lgped # since we removed the pedestal already
        ped = getpedestal( wfms[:,ch], 20, 2.0*scale )
        if ped is not None:
            print "ch ",ch," ped=",ped
            wfms[:,ch] -= ped
        else:
            print "ch ",ch," has bad ped"
            wfms[:,ch] -= 0.0
        # calc undershoot
        for i in range(1,len(qs[:,ch])):
            #for j in range(i+1,np.minimum(i+1+200,len(qs[:,ch])) ):
            q = 50.0*(wfms[i,ch]/RC) + qs[i-1,ch]*np.exp(-1.0*15.625/RC) # 10 is fudge factor!
            qs[i,ch] = q
            wfms[i,ch] += q
        opdata.getData(slot=5)[:,ch] = wfms[:,ch]
        opdata.getPedestal(slot=5)[ch] = 0.0
            
    return wfms


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
        wfms = prepWaveforms( opdata )   # extract numpy arrays
        pywfms = pyWaveformData( wfms )  # packages
        
        subevents = formSubEventsCPP( pywfms, config, pmtspe )

        subeventio.clearlist()
        subeventio.eventid = opdata.current_event
        subeventio.chmaxamp = np.max( wfms )
        print "chmaxamp: ",subeventio.chmaxamp-2047.0
        subeventio.transferSubEventList( subevents )
        subeventio.fill()
        nevents += 1
        #raw_input()
        #if nevents>=50:
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
