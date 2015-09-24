import os,sys

# these use FEM channel number
pmt_nearest_neighbors = {
    0:[1,2,3,4,5,6],
    1:[0,2,3,4,5,6],
    2:[0,4,1,3,5,6],
    3:[9,1,6,32,0,5],
    4:[5,2,6,0,3,1],
    5:[6,4,2,3,0,1],
    6:[5,4,3,2,1,0],
    7:[8,9,10,32,11,12],
    8:[7,10,9,32,12,11],
    9:[3,32,11,7,8,12],
    10:[15,12,8,33,7,11],
    11:[12,32,9,10,7,8],
    12:[11,10,32,9,8,7],
    13:[14,15,16,33,34,17,18],
    14:[13,16,15,34,33,18,17],
    15:[10,33,13,17,14,18],
    16:[21,14,18,34,13,17],
    17:[18,15,33,34,16,13,14],
    18:[17,16,34,33,15,14,13],
    19:[20,21,22,23,24,35],
    20:[19,22,21,24,23,35],
    21:[16,19,23,20,24,22],
    22:[28,35,20,24,19,23],
    23:[24,21,35,22,19,20],
    24:[23,22,35,21,20,19],
    25:[26,27,28,29,30,31],
    26:[25,27,28,29,30,31],
    27:[26,29,25,31,30,28],
    28:[22,25,30,35,26,31],
    29:[31,27,30,26,25,28],
    30:[31,29,28,25,26,27],
    31:[30,29,28,27,26,25] }

femchzorder = [2,4,0,5,1,6,3,9,7,11,8,12,10,15,13,17,14,18,16,21,19,23,20,24,22,28,25,30,26,31,27,29]
femchzorder_wpaddles = [2,4,0,5,1,6,3,9,32,7,11,8,12,10,15,33,13,17,14,18,34,16,21,19,23,20,24,35,22,28,25,30,26,31,27,29]
femch_zorder_dict = {}
for n,femch in enumerate( femchzorder ):
    femch_zorder_dict[femch] = n

def getNthNeighbor( femch, nth ):
    if femch in pmt_nearest_neighbors.keys():
        if nth<len(pmt_nearest_neighbors[femch]):
            return pmt_nearest_neighbors[femch][nth]
        else:
            return None
    return None

def getZorderPos( femch ):
    return femch_zorder_dict[ femch ]

def getZorderNeighbors( femch, nneighbors ):
    zpos = getZorderPos( femch )
    neighbors = []
    for i in xrange(1,nneighbors+1):
        # low
        if zpos-i>=0:
            neighbors.append( femchzorder[zpos-i] )
        if zpos+i<len(femchzorder):
            neighbors.append( femchzorder[zpos+i] )
    return neighbors

    
