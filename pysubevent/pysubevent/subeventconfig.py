import os,sys
from pysubevent.pycfdiscriminator.cfdiscriminator import cfdiscConfig


# Single discriminator
class subeventdiscConfig:
    def __init__( self, discrname, configfile):
        self.discrname = discrname
        self.loadFromFile( configfile )
            
    def loadFromFile( self, configfile ):
        f = open( configfile )
        #s = f.readlines()
        jconfig = json.load( f )
        self.threshold = int(jconfig['config'][self.discrname]['threshold'])  # threshold
        self.deadtime  = int(jconfig['config'][self.discrname]['deadtime'])   # deadtme
        self.delay     = int(jconfig['config'][self.discrname]['delay'])      # delay
        self.width     = int(jconfig['config'][self.discrname]['width'])      # sample width to find max ADC
        self.gate      = int(jconfig['config'][self.discrname]['gate'])       # coincidence gate
        self.fastfraction = float(jconfig["fastfraction"])
        self.slowfraction = float(jconfig["slowfraction"])
        self.fastconst    = float(jconfig["fastconst"])
        self.slowconst    = float(jconfig["slowconst"])
        self.pedsamples   = 100
        self.pedmaxvar    = 1.0
        self.nspersample = 15.625
        f.close()

