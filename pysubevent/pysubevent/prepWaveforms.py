import os,sys
import numpy as np
from pysubevent.utils.pedestal import getpedestal

def prepWaveforms( opdata, RC, fA,hgslot, lgslot, boundarysubevent=None, doit=True ):
    """ prep beam windows. we do baseline and charge corrections. """
    #RC = 80000.0 # ns
    #fA = 5.0
    #hgslot = 5
    #lgslot = 6

    wfms = {} # will store waveforms for each channel
    qs   = {} # will store charge correction  for each channel

    nlargest = 0
    for ch in range(0,48):
        wins = opdata.getBeamWindows( hgslot, ch )
        if len(wins)>0 and len(wins[0].wfm)>0:
            if len(wins[0].wfm)>nlargest:
                nlargest = len(wins[0].wfm)
            wfms[ch] = np.ones( len(wins[0].wfm), dtype=np.float )
            qs[ch]   = np.zeros( len(wins[0].wfm), dtype=np.float )

    # if boundary subevent, we need to calculate corrections to the first part of the waveforms
    boundary_corrections = {}
    if boundarysubevent is not None:
        opdata.suppressed_wfm = {}
        for flash in boundarysubevent.getFlashList():
            ch = flash.ch
            t = flash.tstart
            wfm = flash.expectation
            qcorr = [0.0]
            for i in range(1,len(wfm)):
                q = fA*wfm[i]*(15.625/RC) + qcorr[i-1]*np.exp( -1.0*15.625/RC )
                qcorr.append( q )
            # keep going until q runs out
            while qcorr[-1]>1.0:
                q = qcorr[-1]*np.exp( -1.0*15.625/RC )
                qcorr.append( q )
            print "channel ",ch," has a boundary correction of length ",len(qcorr)," starting from time=",t
            boundary_corrections[ch] = ( t, np.asarray( qcorr, dtype=np.float ) )

    # get waveforms, swap for low if needed, remove pedestal
    for ch in range(0,32):
        scale = 1.0
        beamwfm = opdata.getBeamWindows( hgslot, ch )[0]
        if np.max( beamwfm.wfm )<4090:
            wfms[ch] = beamwfm.wfm
        else:
            lgwins = opdata.getBeamWindows( lgslot, ch )
            print "swap HG ch",ch," with LG wfm",lgwins
            lgwfm = lgwins[0].wfm
            
            lgped = getpedestal( lgwfm, 20, 10.0 )
            if lgped is None:
                #print "ch ",ch," LG has bad ped"
                lgped = lgwfm[0]
            opdata.getBeamWindows( lgslot, ch )[0].wfm -= lgped
            opdata.getBeamWindows( lgslot, ch )[0].wfm *= 10.0

            wfms[ch] = opdata.getBeamWindows( lgslot, ch )[0].wfm
            #print "lg ped=",lgped," wfm[0-10]=",np.mean( wfms[0:10,ch] )
            scale = 10.0
        # charge correction due to cosmic disc windows
        tlen = 1
        if ch in boundary_corrections.keys():
            # charge correction
            tstart = boundary_corrections[ch][0]
            qcorr = boundary_corrections[ch][1]
            t1 = -tstart
            tlen = np.minimum( len(qcorr)-t1, len(wfms[ch]) )
            #print "apply boundary correction to ch ",ch,": tstart=",tstart," covering=[0,",tlen,"]"
            if tlen>0:
                wfms[ch][:tlen] += qcorr[t1:t1+tlen] # boundary charge correction
            # supress early subevent..
            if boundarysubevent.tend_sample>0 and boundarysubevent.tend_sample<len(wfms[ch]):
                ped = getpedestal( wfms[ch][boundarysubevent.tend_sample:], 20, 0.5 )
                tlen = np.minimum( boundarysubevent.tend_sample, len(wfms[ch]) )
                if ped is None:
                    ped = wfms[ch][tlen]

                print "suppress using boundary flash on channel ",ch,". tlen=",tlen
                #flash = boundarysubevent.getFlash( ch )
                #expectation = flash.expectation
                opdata.suppressed_wfm[ch] = np.copy( wfms[ch][:tlen-1] )
                
                wfms[ch][:tlen-1] = ped
                #
                #for i in range(0,tlen-1):
                #    if -flash.tstart+i>=0 and -flash.tstart+i<len(expectation):
                #        expect = expectation[ -flash.tstart +i ]
                #        if wfms[i,ch] < expect + np.sqrt( expect )*3.0:
                #            wfms[i,ch] = ped

        ped = getpedestal( wfms[ch], 20, 2.0*scale )
        if ped is not None:
            #print "ch ",ch," ped=",ped
            wfms[ch] -= ped
            if boundarysubevent is not None and ch in opdata.suppressed_wfm:
                # subtract ped off of suppressed portion
                opdata.suppressed_wfm[ch] -= ped
        else:
            #print "ch ",ch," has bad ped"
            wfms[ch] -= 0.0
        # calc undershoot and correct
        for i in range(np.maximum(1,tlen),len(qs[ch])):
            #for j in range(i+1,np.minimum(i+1+200,len(qs[:,ch])) ):
            q = fA*wfms[ch][i]*(15.625/RC) + qs[ch][i-1]*np.exp(-1.0*15.625/RC) # 10 is fudge factor!
            qs[ch][i] = q
            if doit:
                wfms[ch][i] += q # in window charge correction
        opdata.getBeamWindows( hgslot, ch )[0].wfm = wfms[ch]
    
    npwfms = np.zeros( (nlargest,48), dtype=np.float )
    for ch,wfm in wfms.items():
        npwfms[:len(wfm),ch] = wfm[:]
    return npwfms,qs

from pysubevent.pysubevent.cysubeventdisc import pyCosmicWindowHolder, formCosmicWindowSubEventsCPP
def prepCosmicSubEvents( opdata, config ):
    
    print "prepCosmicSubEvents"

    # stuff data into interface class
    cosmics = pyCosmicWindowHolder()    
    for (slot,ch),timelist in opdata.cosmicwindows.chtimes.items():
        if ch>=32:
            continue
        for t in timelist:
            cwd = opdata.cosmicwindows.chwindows[(slot,ch)][t]
            cwd.wfm -= 2048.0 # remove pedestal. no means to measure pedestal
            #print cwd.wfm

            wfm = np.asarray( cwd.wfm, dtype=np.float )
            #print wfm
            tsample = int(t/config.nspersample)
            if cwd.slot==6:
                wfm *= 10.0 # high gain window
                #print "lg waveform: ",ch,t,tsample
                cosmics.addLGWaveform( ch, tsample, wfm)
            elif cwd.slot==5:
                #print "hg waveform: ",ch,t,tsample
                cosmics.addHGWaveform( ch, tsample, wfm )
        
    subevents = formCosmicWindowSubEventsCPP( cosmics, config )

    boundarysubevent = None
    largest = 0
    for subevent in subevents.getlist():
        if subevent.tstart_sample<0 and subevent.tstart_sample*0.015625>=-40.0: # 20 us
            totalamp = 0.0
            for flash in subevent.getFlashList():
                totalamp += flash.maxamp
            print "boundary subevent candidate: start=",subevent.tstart_sample," end=",subevent.tend_sample," amp=",totalamp
            if totalamp > largest:
                boundarysubevent = subevent
                largest = totalamp
    if boundarysubevent is not None:
        print "[BOUNDARY SUBEVENT] start=",boundarysubevent.tstart_sample," end=",boundarysubevent.tend_sample, " amp=", largest
    return subevents, boundarysubevent
