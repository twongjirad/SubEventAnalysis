import os,sys
import json
import numpy as np
import cfdiscriminator as cfd
import pedestal as ped
import math 
import cysubeventdisc as cyse

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
        f.close()

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
            

def prob_exp( a, b, alpha ):
    return np.exp( -1.0*alpha*a) - np.exp( -1.0*alpha*b )

def response( t, sig, maxamp, maxt, fastconst, slowconst ):
    """
    t=0 is assumed to be max of distribution
    """
    # simplistic
    #farg = t/sig
    #f = 0.5*maxamp*np.exp( -0.5*farg*farg )#/sig/np.sqrt(2*3.14159)
    #if t<0:
    #    s = 0.0
    #else:
    #    s = 0.5*maxamp*np.exp( -t/config.slowconst )

    # slow component shape: expo convolved with gaus
    t_smax = 95.0 # peak of only slow component. numerically solved for det. smearing=3.5*15.625 ns, decay time const= 1500 ns
    t_fmax = 105.0 # numerically solved for det. smearing=3.5*15.625 ns, decay time const= 6 ns
    #dt_smax = -10.0 # expect slow comp peak to be 10 ns earlier than fast component peak
    smax = np.exp( sig*sig/(2*slowconst*slowconst) - t_fmax/slowconst )*(1 - math.erf( (sig*sig - slowconst*t_fmax )/(np.sqrt(2)*sig*slowconst ) ) )
    # normalize max at fast component peak
    As = 0.3*maxamp/smax
    s = As*np.exp( sig*sig/(2*slowconst*slowconst) - t/slowconst )*(1 - math.erf( (sig*sig - slowconst*t )/(np.sqrt(2)*sig*slowconst ) ) )
    #s = np.exp( sig*sig/(2*slowconst*slowconst))*(1-math.erf( (sig*sig)/(np.sqrt(2)*sig*slowconst ) ) )
    #s = maxamp*np.exp( sig*sig/(2*slowconst*slowconst) - t/slowconst )*(1 - math.erf( (sig*sig - slowconst*t )/(np.sqrt(2)*sig*slowconst ) ) )

    # fast component: since time const is smaller than spe response, we model as simple gaussian
    #
    farg = t/sig
    fmax = np.exp( -0.5*farg*farg )
    Af = 0.8*maxamp
    f = Af*np.exp( -0.5*farg*farg )

    #return fastfraction*f + slowfraction*s
    #print t, f, s
    return f+s

def findOneSubEvent( waveform, cfdconf, config, ch ):
    """
    waveform: numpy array
    cfdconf: cfd.cfdiscConfig
    ch: int
    """

    # calculate expectation in first bin
    #pbin1_fast = config.fastfraction*prob_exp( 0, cfdconf.nspersample, 1.0/config.fastconst )
    #pbin1_slow = config.slowfraction*prob_exp( 0, cfdconf.nspersample, 1.0/config.slowconst )
    #pbin1 = pbin1_fast + pbin1_slow # expected fraction of combined slow-fast exponential in first bin
    
    # Find peaks
    peaks = cfd.runCFdiscriminator( waveform, cfdconf )

    # Sort by diff height, get biggest
    peaks_sorted = sorted( peaks, key=lambda tup: tup[1], reverse=True )
    if len(peaks_sorted)>0:
        tstart = peaks_sorted[0][0]
        maxamp = peaks_sorted[0][1]
        tmax   = peaks_sorted[0][2]
        #scale = waveform[tmax]/pbin1
        tend = tstart
        spe_sigma = 4.0*cfdconf.nspersample

#         # old response code
#         rising = True
#         expectation_old = []
#         for t in xrange(np.maximum(0,tmax-20), len(waveform)):
#            n = (t-tmax)
#            fx = response( n*cfdconf.nspersample, spe_sigma, (maxamp-cfdconf.pedestal), tmax, config.fastconst, config.slowconst )
#            tend = t
#            if rising and fx>20:
#                rising = False
#            elif not rising and ( fx<0.1 ): # this should be config
#                break
#            #elif t-tmax>200:
#            #    break
               
#            expectation_old.append( (t,fx) )
#            #print "t=",t,": n=",n," exp=",expectation[-1]

        # cythonized!
        expectation = cyse.calcScintResponse( np.maximum(0,tmax-20), len(waveform), tmax, spe_sigma, (maxamp-cfdconf.pedestal), config.fastconst, config.slowconst, cfdconf.nspersample )
        tend = tstart + len(expectation)

        #print expectation[:10]
        #print expectation_old[:10]
        #raw_input()

        return ChannelSubEvent( ch, tstart, tend, tmax, maxamp, expectation )
    return None


def runSubEventDiscChannel( waveform, config, ch, retpostwfm=False ):
    """
    Multiple pass strategy.
    (1) Find peaks using CFD
    (2) Pick biggest peak
    (3) Define expected signal using fast and slow fractions
    (4) Define start and end this way
    (5) Subtract off subevent
    (6) Repeat (1)-(5) until all disc. peaks are below threshold
    """


    subevents = []

    # build configuration
    config.fastconst = 20.0
    config.sigthresh = 3.0
    cdfthresh = config.threshold
    cfdconf = cfd.cfdiscConfig( config.discrname, threshold=cdfthresh, deadtime=config.deadtime, delay=config.delay, width=config.width )
    cfdconf.pedestal = ped.getpedestal( waveform, config.pedsamples, config.pedmaxvar )  # will have to calculate this at some point
    if cfdconf.pedestal is None:
        return subevents # empty -- bad baseline!
    cfdconf.nspersample = 15.625
    #print pbin1, config.fastconst, config.slowconst

    # make our working copy of the waveform
    wfm = np.copy( waveform )

    # find subevent
    maxsubevents = 20
    nsubevents = 0
    while nsubevents<maxsubevents:
        # find subevent
        subevent = findOneSubEvent( wfm, cfdconf, config, ch )
        if subevent is not None:
            subevents.append(subevent)
        else:
            break
        # subtract waveform below subevent threshold
        for (t,fx) in subevent.expectation:
            
            sig = np.sqrt( fx/20.0 ) # units of pe
            thresh =  fx + 3.0*sig*20.0 # 3 sigma times pe variance

            #if fx*config.sigthresh > wfm[t]-config.pedestal:
            if wfm[t]-cfdconf.pedestal < thresh:
                wfm[t] = cfdconf.pedestal
        nsubevents += 1
        #break

    if retpostwfm:
        return subevents, wfm
    else:
        return subevents
        
def runSubEventDisc( opdata, config, retpostwfm=False, hgslot=5, lgslot=6, maxch=None ):
    hgwfm = opdata.getData(slot=hgslot)
    lgwfm = opdata.getData(slot=lgslot)
    if maxch is None:
        chs = hgwfm.shape[1]
    else:
        chs = maxch

    chsubevents = {}
    chpostwfms = {}

    for ch in xrange(0,chs):
        wf = hgwfm[:,ch]
        use_hg = True
        if np.max(wf)>=4094:
            wf = lgwfm[:,ch] # switch to low-gain waveform
            use_hg = False
        if retpostwfm:
            subevents,postwfm =  runSubEventDiscChannel( wf, config, ch, retpostwfm=retpostwfm )
            chpostwfms[ch] = postwfm
        else:
            subevents =  runSubEventDiscChannel( wf, config, ch, retpostwfm=retpostwfm )
        # add waveforms for subevents
        for subevent in subevents:
            subevent.hgwfm = hgwfm[subevent.tstart:subevent.tend,ch]
            subevent.lgwfm = lgwfm[subevent.tstart:subevent.tend,ch]
            if not use_hg:
                subevent.gainfactor = 10.0
            else:
                subevent.gainfactor = 1.0
            
        chsubevents[ch] = subevents
        #print "Running subevent finder on Ch=",ch,". Found ",len(subevents),". hgmax=",np.max( hgwfm[:,ch] ),
        #if use_hg:
        #    print " Used high gain."
        #else:
        #    print " Used low gain."

    if retpostwfm:
        return chsubevents, chpostwfms
    else:
        return chsubevents
            
def makeSubEventAccumulators( chsubevents, gatehalfwidth, opdata, pmtspe, HGSLOT=5, LGSLOT=6 ):
    """
    inputs
    ------
    chsubevents: dict of {int:list of ChannelSubEvent} for {FEM CH:subevent list}
    gatehalfwidth: int
    opdata: concrete instance of pylard.opdataplottable
    pmtspe: dict of {int:float} for {FEM CH:spe max amp mean}

    outputs
    -------
    nch_acc: numpy array
    npe_acc: numpy array
    """
    
    nch_acc = np.zeros( opdata.getSampleLength(), dtype=np.int ) # for number of hits
    npe_acc = np.zeros( opdata.getSampleLength(), dtype=np.float ) # for number of pe
    hgwfms = opdata.getData( slot=HGSLOT )
    lgwfms = opdata.getData( slot=LGSLOT )
    for ch,chsubevent in chsubevents.items():
        hgped = ped.getpedestal(hgwfms[:,ch], 10, 10)
        lgped = ped.getpedestal(lgwfms[:,ch], 10, 10)
        if ch in pmtspe:
            chspe = pmtspe[ch]
        else:
            chspe = 1.0

        gainfactor = 1.0
        chped = hgped
        #print  hgwfms[:,ch]
        if np.max( hgwfms[:,ch] )>=4094:
            gainfactor = 10.0
            chped = lgped
        if chped is None:
            chped = 2048.0

        # fill accumulator
        for subevent in chsubevent:
            pe = gainfactor*float( subevent.maxamp - chped )/float(chspe)
            nch_acc[ np.maximum(0,subevent.tstart-gatehalfwidth) : np.minimum( opdata.getSampleLength(), subevent.tstart+gatehalfwidth ) ] += 1
            npe_acc[ np.maximum(0,subevent.tstart-gatehalfwidth) : np.minimum( opdata.getSampleLength(), subevent.tstart+gatehalfwidth ) ] += pe
    return nch_acc, npe_acc


def formSubEvents( opdata, config, pmtspe, retpostwfm=False, hgslot=5, lgslot=6, maxch=None ):
    # search for channel subevents
    chsubevtdict = runSubEventDisc( opdata, config, retpostwfm=False, maxch=32 )
    gatehalfwidth = 15
    pethresh  = 2.5
    nchthresh = 7.0

    subevents = []
    nloops = 0
    maxloops = 20

    loopchsubevtdict = { nloops:chsubevtdict }

    while nloops<maxloops:
        # form accumulator with leftover subevents
        hitacc,peacc = makeSubEventAccumulators( loopchsubevtdict[nloops], gatehalfwidth, opdata, pmtspe, HGSLOT=hgslot, LGSLOT=lgslot )
        
        # storage for unused subevents
        unused_chsubevtdict = {}

        # use accumulators to form a subevent
        tpeak = np.argmax( peacc )
        pepeak = peacc[tpeak]
        nhits = np.max( hitacc[ np.maximum(0,tpeak-2) : np.minimum( len(hitacc),  tpeak+2) ] )
        nchsubevents = 0

        if pepeak/nhits > pethresh or nhits > nchthresh:    
            # collect subevents within time of accumulator peak
            ncollected = 0
            primarysubeventdict = {}
            for ch,chsubeventlist in loopchsubevtdict[nloops].items():
                unused_chsubevtdict[ch] = []
                primarysubeventdict[ch] = []
                for chsubevent in chsubeventlist:
                    nchsubevents += 1
                    #if chsubevent.maxamp/pmtspe[ch] > pepeak:
                        #print "ch=",ch,": ",chsubevent.maxamp/pmtspe[ch],"tstart=",chsubevent.tstart
                    if np.abs( chsubevent.tstart-tpeak ) < gatehalfwidth:
                        ncollected += 1
                        primarysubeventdict[ch].append( chsubevent )
                    else:
                        unused_chsubevtdict[ch].append( chsubevent )
            # form subevent
            se = SubEvent( primarysubeventdict )
            se.peacc = np.zeros( peacc.shape[0] )
            se.hitacc = np.zeros( hitacc.shape[0] )
            if nhits > nchthresh:
                se.hitacc[ np.maximum(0,tpeak-2) : np.minimum( len(hitacc),  tpeak+2) ] =  hitacc[ np.maximum(0,tpeak-2) : np.minimum( len(hitacc),  tpeak+2) ]
            if pepeak > pethresh:
                se.peacc[ np.maximum(0,tpeak-2) : np.minimum( len(peacc),  tpeak+2) ] =  peacc[ np.maximum(0,tpeak-2) : np.minimum( len(peacc),  tpeak+2) ]
            print "number collected in new subevent: ",ncollected," pepeak=",pepeak," nhits=",nhits," tpeak=",tpeak
            if ncollected==0:
                break
            else:
                subevents.append( se )
        else:
            break

        print "form subevent loop ",nloops,": ",nchsubevents
        nloops += 1
        loopchsubevtdict[nloops] = unused_chsubevtdict


        # collect all peaks within 4 samples as primary subevent
        # in primary subevent, find earliest tstart and latest tend as subevent bounds
        # collect all chsubevents in previous 200 samples as pre-activity
        # collect all chsubevents within [tstart,tend] as subsubevents

        # recursive:
        # inside subsubevents, build accumulator
    return subevents

