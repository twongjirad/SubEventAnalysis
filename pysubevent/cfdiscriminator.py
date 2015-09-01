import os,sys
import json
import numpy as np

# cythonized function
import cycfdiscriminator as cycfd

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
        #s = f.readlines()
        jconfig = json.load( f )
        self.threshold = int(jconfig['config'][self.discrname]['threshold'])  # threshold
        self.deadtime  = int(jconfig['config'][self.discrname]['deadtime'])   # deadtme
        self.delay     = int(jconfig['config'][self.discrname]['delay'])      # delay
        self.width     = int(jconfig['config'][self.discrname]['width'])      # sample width to find max ADC
        self.gate      = int(jconfig['config'][self.discrname]['gate'])       # coincidence gate
        f.close()

def runCFdiscriminator( waveform, config ):
    """
    inputs
    ------
    waveform: numpy array
    config: cfdiscConfig instance
    """

#     diff = np.zeros( len(waveform), dtype=np.float )
#     t_fire = []
#     amp_fire = []
#     maxt_fire = []
#     last_fire = -1
#     for tdc in xrange( int(config.delay), len(waveform)-int(config.delay) ):
#         diff[tdc] = waveform[tdc]-waveform[tdc+int(config.delay)]

#     # determine time
#     for t in xrange(0,len(waveform)):
#         if diff[t]>config.threshold and ( len(t_fire)==0 or (len(t_fire)>0 and t_fire[-1]+config.deadtime<t) ):
#             t_fire.append( t-config.delay )
#     # determine max amp
#     for trig in t_fire:
#         amp_fire.append( np.max( waveform[trig:np.minimum( len(waveform), trig+config.width )] )  )
#         maxt_fire.append( trig+np.argmax( waveform[trig:np.minimum( len(waveform), trig+config.width )] ) )

#     out_old = zip( t_fire, amp_fire, maxt_fire )

    out = cycfd.runCFdiscriminator( waveform, config.delay, config.threshold, config.deadtime, config.width )

    return out
        
