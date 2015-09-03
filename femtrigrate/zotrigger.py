import os,sys
import numpy as np
from pysubevent.pmtnn import getNthNeighbor, getZorderNeighbors

# Nearest neighbor trigger formation

def formzotrigger( femchtriggers, femchdiffs, femchadc, startwin, endwin, verbose=0 ):
    """
    inputs
    ------
    femchtriggers: dict of (str discr name) --> ( numpy 2D array, (t,ch) )
    startwin: start of sample window
    endwin: end of sample window
    
    return
    ------
    zomaxhits: dict of (int nearest neighbors considered) --> (max coincident triggers in window)
    """
    beamsamples = endwin-startwin
    zomaxhits = {}
    zomaxdiff = {}
    zomaxadc  = {}

    # --- local nearest neighbors triggers (skip paddles) ---
    for zneighbors in xrange(1,3):
        # nneighbors is max neighors matched
        nneighbors = 1 + 2*zneighbors
        zomaxhits[nneighbors] = 0
        zomaxdiff[nneighbors] = 0
        zomaxadc[nneighbors] = 0
        triglist = []
        zomultiplicity = {}
        zogatesum = {}
        zoadcsum = {}
        zodiffsum = {}
        for femch in xrange(0,32):
            if np.max(femchtriggers["discr1"][startwin:endwin,femch])==0:
                continue # no triggers on this channel, move on
            ith_pos = 0
            neighbors = getZorderNeighbors( femch, zneighbors )
            #print "FEMCH=",femch," NEIGHBOORS(",zneighbors,")=",neighbors
            coinset = [femch]
            gatesum = np.zeros( beamsamples, dtype=np.int )
            adcsum = np.zeros( beamsamples, dtype=np.int )
            diffsum = np.zeros( beamsamples, dtype=np.int )
            gatesum[:] += femchtriggers["discr1"][startwin:endwin,femch]
            adcsum[:] += femchadc["discr1"][startwin:endwin,femch]
            diffsum[:] += femchdiffs["discr1"][startwin:endwin,femch]
            for neighbor in neighbors:
                # loop through neighbor list
                if neighbor>=32:
                    # skip paddles
                    continue
                gatesum[:] += femchtriggers["discr1"][startwin:endwin,neighbor]
                adcsum[:] += femchadc["discr1"][startwin:endwin,neighbor]
                diffsum[:] += femchdiffs["discr1"][startwin:endwin,neighbor]                
                coinset.append(neighbor)
            coinset.sort()
            # look for coincidence in neighbor set
            if verbose>1:
                print "COINSET: ",coinset, "gatesum=",gatesum
            if np.max( gatesum ) >=2:
                triglist.append( coinset )
                zomultiplicity[ tuple(coinset) ] = np.max( gatesum )
                zodiffsum[ tuple(coinset) ] = np.max(diffsum)
                zoadcsum[ tuple(coinset) ] = np.max(adcsum)                
                zogatesum[ tuple(coinset) ] = gatesum
        finallist = []
        final_zomulti = {}
        final_zogatesum = {}
        final_zodiffsum = {}
        final_zoadcsum = {}

        # check if a trig set is a subset before putting into final list
        for set in triglist:
            addme = True
            for setb in triglist:
                if set==setb:
                    continue
                if len(set)<len(setb):
                    subset = True
                    for item in set:
                        if item not in setb:
                            subset = False
                            break
                    if subset:
                        addme = False
                        break
            if addme and set not in finallist:
                finallist.append(set)
                final_zomulti[ tuple(set) ] = zomultiplicity[tuple(set)]
                final_zogatesum[ tuple(set) ] = zogatesum[  tuple(set) ]
                final_zodiffsum[ tuple(set) ] = zodiffsum[  tuple(set) ]
                final_zoadcsum[ tuple(set) ] = zoadcsum[  tuple(set) ]

        maxcoin = 0
        maxdiff = 0
        maxadc  = 0        
        for set in finallist:
            if maxcoin < final_zomulti[ tuple(set) ]:
                maxcoin = final_zomulti[ tuple(set) ]
            if maxdiff < final_zodiffsum[ tuple(set) ]:
                maxdiff = final_zodiffsum[ tuple(set) ]
            if maxcoin < final_zoadcsum[ tuple(set) ]:
                maxadc = final_zoadcsum[ tuple(set) ]                
        zomaxhits[nneighbors] = maxcoin
        zomaxdiff[nneighbors] = maxdiff
        zomaxadc[nneighbors] = maxadc
        if verbose>0:
            print "ZO=",nneighbors,": maxcoin=",maxcoin,"finallist=",finallist, "(",triglist,")"
            for set in finallist:
                print "  set=",set,": gatesum=",final_zogatesum[ tuple(set) ]

    return {"maxhits":zomaxhits,"maxdiff":zomaxdiff,"maxadc":zomaxadc}
