import os,sys
import json
import numpy as np
from collections import Sequence
import operator

# cythonized function
import pysubevent.pycfdiscriminator.cycfdiscriminator as cycfd

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

class CFDFire:
    def __init__( self, t_fire=None, maxaxmp_fire=None, maxt_fire=None, diff_fire=None ):
        self.setData( t_fire, maxaxmp_fire, maxt_fire, diff_fire )
    def setData( self, t_fire=None, maxamp_fire=None, maxt_fire=None, diff_fire=None ):
        if t_fire is not None:
            self.tfire = t_fire
        if maxamp_fire is not None:
            self.maxamp = maxamp_fire
        if maxt_fire is not None:
            self.tmax = maxt_fire
        if diff_fire is not None:
            self.diff = diff_fire

class CFDFireVector(Sequence):
    def __init__(self):
        self.fires = []

    @classmethod
    def from_vectors( cls, vec_tfire, vec_maxamp, vec_tmax, vec_diff ):
        newvec = cls()
        for (tfire,maxamp, tmax, diff) in zip( vec_tfire, vec_maxamp, vec_tmax, vec_diff ):
            newvec.fires.append( CFDFire( tfire,maxamp, tmax, diff ) )
        return newvec
    @classmethod
    def from_vector_tuple( cls, data ):
        newvec = cls()
        for (tfire,maxamp, tmax, diff) in data:
            newvec.fires.append( CFDFire( tfire,maxamp, tmax, diff ) )
        return newvec

    def getNumFires(self):
        return len(self.fires)
    def __getitem__(self,index):
        return self.fires[index]
    def __len__(self):
        return self.getNumFires()
    def getAmpOrderedList( self, reverse=False ):
        return sorted( self.fires, key=operator.attrgetter('maxamp'), reverse=reverse )
    def getTimeOrderedList( self, reverse=False ):
        return sorted( self.fires, key=operator.attrgetter('tfire'), reverse=reverse )

def runCFdiscriminator( waveform, config ):
    """
    inputs
    ------
    waveform: numpy array
    config: cfdiscConfig instance
    """

    # confirmed that cythonized code produces same output (2015/08/30)
    # cythonized
    #outcy = cycfd.runCFdiscriminator( waveform, config.delay, config.threshold, config.deadtime, config.width )
    outnative = cycfd.pyRunCFdiscriminatorCPP( waveform.astype(np.float), config.delay, config.threshold, config.deadtime, config.width )
    #print "cythonized: ",outcy
    #print "native: ",outnative
    #out = CFDFireVector.from_vector_tuple( outcy )
    out = CFDFireVector.from_vector_tuple( outnative )
    #raw_input()
    return out
        
