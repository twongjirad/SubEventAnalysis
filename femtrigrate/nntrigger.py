import os,sys
import numpy as np
from pysubevent.pmtnn import getNthNeighbor, femchzorder

# Nearest neighbor trigger formation

def formnntrigger( femchtriggers, femchdiffs, femchadc, startwin, endwin, verbose=0 ):
    """
    inputs
    ------
    femchtriggers: dict of (str discr name) --> ( numpy 2D array, (t,ch) )
    startwin: start of sample window
    endwin: end of sample window
    
    return
    ------
    nnmaxhits: dict of (int nearest neighbors considered) --> (max coincident triggers in window)
    """
    beamsamples = endwin-startwin
    nnmaxhits = {}
    nnmaxdiff = {}
    nnmaxadc  = {}

    # --- local nearest neighbors triggers (skip paddles) ---
    for nneighbors in xrange(1,6):
        # nneighbors is max neighors matched
        nnmaxhits[nneighbors] = 0
        nnmaxdiff[nneighbors] = 0
        nnmaxadc[nneighbors] = 0
        triglist = []
        nnmultiplicity = {}
        nngatesum = {}
        nndiffsum = {}
        nnadcsum = {}
        for femch in xrange(0,32):
            if np.max(femchtriggers["discr1"][startwin:endwin,femch])==0:
                continue # no triggers on this channel, move on
            ith_pos = 0
            neighbor = getNthNeighbor( femch, ith_pos )
            ith_neighbor = 1
            coinset = [femch]
            gatesum = np.zeros( beamsamples, dtype=np.int )
            adcsum = np.zeros( beamsamples, dtype=np.int )
            diffsum = np.zeros( beamsamples, dtype=np.int )
            gatesum[:] += femchtriggers["discr1"][startwin:endwin,femch]
            adcsum[:] += femchadc["discr1"][startwin:endwin,femch]
            diffsum[:] += femchdiffs["discr1"][startwin:endwin,femch]
            while neighbor is not None and ith_neighbor<=nneighbors:
                # loop through neighbor list
                if neighbor>=32:
                    # skip paddles
                    ith_pos += 1
                    neighbor = getNthNeighbor( femch, ith_pos )
                    continue
                gatesum[:] += femchtriggers["discr1"][startwin:endwin,neighbor]
                adcsum[:] += femchadc["discr1"][startwin:endwin,neighbor]
                diffsum[:] += femchdiffs["discr1"][startwin:endwin,neighbor]
                coinset.append(neighbor)
                ith_pos += 1
                neighbor = getNthNeighbor( femch, ith_pos )
                ith_neighbor += 1
            coinset.sort()
            # look for coincidence in neighbor set
            #print "COINSET: ",coinset, "gatesum=",gatesum
            if np.max( gatesum ) >=2:
                triglist.append( coinset )
                nnmultiplicity[ tuple(coinset) ] = np.max( gatesum )
                nngatesum[ tuple(coinset) ] = gatesum
                nndiffsum[ tuple(coinset) ] = np.max(diffsum)
                nnadcsum[ tuple(coinset) ] = np.max(adcsum)
        finallist = []
        final_nnmulti = {}
        final_nngatesum = {}
        final_nndiffsum = {}
        final_nnadcsum = {}
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
                final_nnmulti[ tuple(set) ] = nnmultiplicity[tuple(set)]
                final_nngatesum[ tuple(set) ] = nngatesum[  tuple(set) ]
                final_nndiffsum[ tuple(set) ] = nndiffsum[  tuple(set) ]
                final_nnadcsum[ tuple(set) ] = nnadcsum[  tuple(set) ]
        maxcoin = 0
        maxdiff = 0
        maxadc  = 0
        for set in finallist:
            if maxcoin < final_nnmulti[ tuple(set) ]:
                maxcoin = final_nnmulti[ tuple(set) ]
            if maxdiff < final_nndiffsum[ tuple(set) ]:
                maxdiff = final_nndiffsum[ tuple(set) ]
            if maxcoin < final_nnadcsum[ tuple(set) ]:
                maxadc = final_nnadcsum[ tuple(set) ]
        nnmaxhits[nneighbors] = maxcoin
        nnmaxdiff[nneighbors] = maxdiff
        nnmaxadc[nneighbors] = maxadc
        if verbose>0:
            print "NN=",nneighbors,": maxcoin=",maxcoin,"finallist=",finallist, "(",triglist,")"
            if len(finallist)>0 and tuple(finallist[0]) in final_nngatesum:
                print "  gatesum=",final_nngatesum[ tuple(finallist[0]) ]

    return {"maxhits":nnmaxhits, "maxdiff":nnmaxdiff, "maxadc":nnmaxadc}
