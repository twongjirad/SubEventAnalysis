import numpy as np

class ChannelSubEvent:
    """
    SubEvent Information on on channel. Instances will be grouped to form a subevent
    """
    def __init__( self, ch, tstart, tend, tmax, maxamp, expectation ):
        self.ch = ch
        self.tstart = tstart
        self.tend   = tend
        self.tmax   = tmax
        self.maxamp = maxamp
        self.expectation = expectation

class SubEvent:
    """
    SubEvent information
    """
    def __init__( self, chsubeventdict ):
        """
        inputs:
        ------
        chsubevents: list of ChannelSubEvent instances or None
        config: instance of subeventdiscConfig, containing configuration parameters
        """
        self.chsubeventdict = chsubeventdict
