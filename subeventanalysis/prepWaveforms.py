import os,sys
import numpy as np
from pysubevent.utils.pedestal import getpedestal

def prepWaveforms( opdata, boundarysubevent=None ):
    RC = 80000.0 # ns
    fA = 5.0
    nsamples = opdata.getNBeamWinSamples()
    wfms = np.ones( (nsamples,32) )*2047.0
    qs   = np.zeros( (nsamples,32) )

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
            #print "channel ",ch," has a boundary correction of length ",len(qcorr)," starting from time=",t
            boundary_corrections[ch] = ( t, np.asarray( qcorr, dtype=np.float ) )

    # get waveforms, swap for low if needed, remove pedestal
    for ch in range(0,32):
        scale = 1.0
        if np.max( opdata.getData()[:,ch] )<4090:
            wfms[:,ch] = opdata.getData(slot=5)[:,ch]
        else:
            #print "swap HG ch",ch," with LG wfm"
            lgwfm = opdata.getData(slot=6)[:,ch]
            lgped = getpedestal( lgwfm, 20, 2.0 )
            if lgped is None:
                #print "ch ",ch," LG has bad ped"
                lgped = opdata.getData(slot=6)[0,ch]
            wfms[:,ch] = lgwfm-lgped
            #print "lg ped=",lgped," wfm[0-10]=",np.mean( wfms[0:10,ch] )
            wfms[:,ch] *= 10.0
            scale = 10.0
            #opdata.getData(slot=5)[:,ch] = wfms[:,ch] + lgped
            #opdata.getPedestal(slot=5)[ch] = lgped # since we removed the pedestal already
        # charge correction due to cosmic disc windows
        tlen = 1
        if ch in boundary_corrections.keys():
            # charge correction
            tstart = boundary_corrections[ch][0]
            qcorr = boundary_corrections[ch][1]
            t1 = -tstart
            tlen = np.minimum( len(qcorr)-t1, len(wfms[:,ch]) )
            #print "apply boundary correction to ch ",ch,": tstart=",tstart," covering=[0,",tlen,"]"
            wfms[:tlen,ch] += qcorr[t1:t1+tlen]
            # supress early subevent..
            if boundarysubevent.tend_sample>0 and boundarysubevent.tend_sample<len(wfms[:,ch]):
                ped = getpedestal( wfms[boundarysubevent.tend_sample:,ch], 20, 0.5 )
                tlen = np.minimum( boundarysubevent.tend_sample, len(wfms[:,ch]) )
                if ped is None:
                    ped = wfms[tlen,ch]

                #print "suppress using boundary flash on channel ",ch
                #flash = boundarysubevent.getFlash( ch )
                #expectation = flash.expectation
                opdata.suppressed_wfm[ch] = np.copy( wfms[:tlen-1,ch] )
                wfms[:tlen-1,ch] = ped
                #
                #for i in range(0,tlen-1):
                #    if -flash.tstart+i>=0 and -flash.tstart+i<len(expectation):
                #        expect = expectation[ -flash.tstart +i ]
                #        if wfms[i,ch] < expect + np.sqrt( expect )*3.0:
                #            wfms[i,ch] = ped

        ped = getpedestal( wfms[:,ch], 20, 2.0*scale )
        if ped is not None:
            #print "ch ",ch," ped=",ped
            wfms[:,ch] -= ped
            if boundarysubevent is not None and ch in opdata.suppressed_wfm:
                # subtract ped off of suppressed portion
                opdata.suppressed_wfm[ch] -= ped
        else:
            #print "ch ",ch," has bad ped"
            wfms[:,ch] -= 0.0
        # calc undershoot and correct
        for i in range(np.maximum(1,tlen),len(qs[:,ch])):
            #for j in range(i+1,np.minimum(i+1+200,len(qs[:,ch])) ):
            q = fA*wfms[i,ch]*(15.625/RC) + qs[i-1,ch]*np.exp(-1.0*15.625/RC) # 10 is fudge factor!
            qs[i,ch] = q
            wfms[i,ch] += q
        opdata.getData(slot=5)[:,ch] = wfms[:,ch]
        opdata.getPedestal(slot=5)[ch] = 0.0
            
    return wfms,qs

from pysubevent.pysubevent.cysubeventdisc import pyCosmicWindowHolder, formCosmicWindowSubEventsCPP
def prepCosmicSubEvents( opdata, config ):
    # stuff data into interface class
    cosmics = pyCosmicWindowHolder()
    for ch,timelist in opdata.cosmics.chtimes.items():
        if ch>=32:
            continue
        for t in timelist:
            cwd = opdata.cosmics.chwindows[ch][t]
            wfm = np.asarray( cwd.wfm, dtype=np.float )
            wfm -= 2048.0 # remove pedestal. no means to measure pedestal
            if cwd.slot==6:
                wfm *= 10.0 # high gain window
                #print "lg waveform: ",ch,t
                cosmics.addLGWaveform( ch, t, wfm)
            elif cwd.slot==5:
                #print "hg waveform: ",ch,t
                cosmics.addHGWaveform( ch, t, wfm )
        
    subevents = formCosmicWindowSubEventsCPP( cosmics, config )

    boundarysubevent = None
    largest = 0
    for subevent in subevents.getlist():
        #print "subevent: ",subevent.tstart_sample, subevent.tend_sample
        #if ( subevent.tstart_sample<0 and subevent.tend_sample>0 ):
        if subevent.tstart_sample<0 and subevent.tstart_sample*0.015625>=-40.0: # 20 us
            totalamp = 0.0
            for flash in subevent.getFlashList():
                totalamp += flash.maxamp
            print "boundary subevent candidate: start=",subevent.tstart_sample," end=",subevent.tend_sample," amp=",totalamp
            if totalamp > largest:
                boundarysubevent = subevent
                largest = totalamp
    print "[BOUNDARY SUBEVENT] start=",subevent.tstart_sample," end=",subevent.tend_sample, " amp=", subevent.maxamp
    return subevents,boundarysubevent
