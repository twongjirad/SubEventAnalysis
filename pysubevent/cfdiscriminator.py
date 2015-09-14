import os,sys
import json
import numpy as np

# cythonized function
import pysubevent.cycfdiscriminator as cycfd

# Single discriminator

class cfdiscConfig:
    def __init__( self, discrname, configfile=None, threshold=None, deadtime=None, delay=None, width=None ):
        self.discrname = discrname
        if configfile is not None:
            self.loadFromFile( configfile )
        else:
            self.threshold = threshold
            self.deadtime = deadtime
            self.delay = delay
            self.width = width
            
    def loadFromFile( self, configfile ):
        f = open( configfile )
        jconfig = json.load( f )
        self.threshold   = int(jconfig['config'][self.discrname]['threshold'])  # threshold
        self.thresholdpe = float(jconfig['config'][self.discrname]['thresholdpe'])  # threshold in pe
        self.deadtime    = int(jconfig['config'][self.discrname]['deadtime'])   # deadtme
        self.delay       = int(jconfig['config'][self.discrname]['delay'])      # delay for calculating diff
        self.width       = int(jconfig['config'][self.discrname]['width'])      # sample width to find max ADC
        self.gate        = int(jconfig['config'][self.discrname]['gate'])       # coincidence gate
        f.close()

def runCFdiscriminator( waveform, config ):
    """
    inputs
    ------
    waveform: numpy array
    config: cfdiscConfig instance
    """

    # confirmed that cythonized code produces same output (2015/08/30)
    # cythonized
    outcy = cycfd.runCFdiscriminator( waveform, config.delay, config.threshold, config.deadtime, config.width )
    #outnative = cycfd.pyRunCFdiscriminatorCPP( waveform, config.delay, config.threshold, config.deadtime, config.width )
    #print "cythonized: ",outcy
    #print "native: ",outnative
    #out = outnative
    out = outcy
    #raw_input()

    return out
        
