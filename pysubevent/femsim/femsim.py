import os
import numpy as np
import json
from cfdiscriminator import cfdiscConfig
from pmtcalib import getCalib

# FEM simulation
class FEMconfig:
    def __init__( self, configfile ):
        self.configs = {}
        for disc in [0,1,3]:
            self.configs["discr%d"%(disc)] = cfdiscConfig( "discr%d"%(disc), configfile )
        f = open( configfile )
        jconfig = json.load( f )
        self.discr0precount = int(jconfig["precount"])
        self.discr0win = int(jconfig["discr0win"])
        self.spe = getCalib( os.environ["SUBEVENTDATA"]+"/"+jconfig["spe"] )
        

def runFEMsimChannel( waveform, femconfig, femch, spe, use_spe=False ):
    """
    runs discriminitor sim on channel waveform.
    """
    
    configs = femconfig.configs

    diffs = { "discr0":np.zeros( len(waveform), np.int ),
              "discr1":np.zeros( len(waveform), np.int ),
              "discr3":np.zeros( len(waveform), np.int ) }

    # calc diff vectors
    for id in [0,1,3]:
        disc = "discr%d"%(id)
        for tdc in xrange( int(configs[disc].delay), len(waveform)-int(configs[disc].delay) ):
            diffs[disc][tdc] = waveform[tdc]-waveform[tdc-int(configs[disc].delay)]
            
    # find triggers
    trigs = { "discr0":[],
              "discr1":[],
              "discr3":[] }
    maxadcs = { "discr1":[],
                "discr3":[] }
    maxdiffs = { "discr1":[],
                 "discr3":[] }

    for t in xrange( 0, len(waveform) ):
        # discr 0 must fire first: acts as pre-trigger. won't fire again until all discs are not active
        if diffs["discr0"][t]>=configs["discr0"].threshold:
            if ( ( len(trigs["discr0"])==0 or trigs["discr0"][-1] + femconfig.discr0precount < t ) and
                 ( len(trigs["discr1"])==0 or trigs["discr1"][-1] + configs["discr1"].deadtime < t ) and
                 ( len(trigs["discr3"])==0 or trigs["discr3"][-1] + configs["discr3"].deadtime < t ) ):
                trigs["discr0"].append( t )

        # discr1 and discr3 firing condition
        for disc in ["discr1","discr3"]:
            if ( not use_spe and diffs[disc][t]>=configs[disc].threshold) or (use_spe and diffs[disc][t]>=int(spe[femch]*configs[disc].thresholdpe)):
                if ( (len(trigs["discr0"])>0 and t-trigs["discr0"][-1]<femconfig.discr0win) and 
                     ( len(trigs[disc])==0 or trigs[disc][-1] + configs[disc].deadtime < t ) ): # within last disc0 fire and not in last disc deadtime
                    # store discriminator window quantities
                    trigs[disc].append( t )
                    maxadcs[disc].append( np.max( waveform[t:np.minimum(t+configs[disc].width,len(waveform))] ) )
                    maxdiffs[disc].append( np.max( diffs[disc][t:np.minimum(t+configs[disc].width,len(diffs[disc]))] ) )

    return trigs, maxadcs, maxdiffs
        
                
def runFEMsim( waveforms, femconfig, maxch=None, use_spe=False ):
    if maxch is None:
        chs = waveforms.shape[1]
    else:
        chs = maxch

    chtriglists = {}
    chmaxadcs = {}
    chmaxdiff = {}
    for ch in xrange(0,chs):
        chtriglists[ch], chmaxadcs[ch], chmaxdiff[ch] = runFEMsimChannel( waveforms[:,ch], femconfig, ch, femconfig.spe, use_spe=use_spe )

    # allocate memory for accumulators. will sum up disc. quantities across channels
    multis    = {"discr1": np.zeros( waveforms.shape[0], np.int ) } # number of channels hit
    maxadcs   = {"discr1": np.zeros( waveforms.shape[0], np.int ) } # max ADCS
    maxdiffs  = {"discr1": np.zeros( waveforms.shape[0], np.int ) } # max Diffs
    # accumulators for only 1 channel only
    chtrigs   = {"discr1": np.zeros( waveforms.shape, np.int ) }
    chdiffs   = {"discr1": np.zeros( waveforms.shape, np.int ) }
    chmaxadc  = {"discr1": np.zeros( waveforms.shape, np.int ) }

    for ch in xrange(0,chs):
        for n,t in enumerate(chtriglists[ch]["discr1"]): # loop over list of times of triggers
            for i in xrange(0, femconfig.configs["discr1"].gate ): # loop over time of gate
                if t+i<waveforms.shape[0]:
                    # accumulators
                    multis["discr1"][t+i] += 1
                    maxadcs["discr1"][t+i] += chmaxadcs[ch]["discr1"][n]
                    maxdiffs["discr1"][t+i] += chmaxdiff[ch]["discr1"][n]
                    # channel disc values array
                    chtrigs["discr1"][t+i,ch] += 1
                    chdiffs["discr1"][t+i,ch] += chmaxdiff[ch]["discr1"][n]
                    chmaxadc["discr1"][t+i,ch] += chmaxadcs[ch]["discr1"][n]
                else:
                    break

    return multis, maxadcs, maxdiffs, chtrigs, chmaxadc, chdiffs
    
    
