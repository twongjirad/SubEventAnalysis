import os, sys
from ROOT import *

gStyle.SetOptStat(0)

"""
******************************************************************************
*Tree    :fem       : FEM simulation output                                  *
*Entries :     9500 : Total =         1832962 bytes  File  Size =     172032 *
*        :          : Tree compression factor =  10.72                       *
******************************************************************************
*Br    0 :eventid   : eventid/I                                              *
*Entries :     9500 : Total  Size=      38628 bytes  File Size  =       1811 *
*Baskets :        2 : Basket Size=      32000 bytes  Compression=  21.06     *
*............................................................................*
*Br    1 :maxhits   : maxhits/I                                              *
*Entries :     9500 : Total  Size=      38628 bytes  File Size  =       5561 *
*Baskets :        2 : Basket Size=      32000 bytes  Compression=   6.86     *
*............................................................................*
*Br    2 :winid     : winid/I                                                *
*Entries :     9500 : Total  Size=      38616 bytes  File Size  =        570 *
*Baskets :        2 : Basket Size=      32000 bytes  Compression=  66.92     *
*............................................................................*
*Br    3 :maxpe     : maxpe/I                                                *
*Entries :     9500 : Total  Size=      38616 bytes  File Size  =      16525 *
*Baskets :        2 : Basket Size=      32000 bytes  Compression=   2.31     *
*............................................................................*
*Br    4 :chtrig    : chtrig[32]/I                                           *
*Entries :     9500 : Total  Size=    1219894 bytes  File Size  =     116363 *
*Baskets :       39 : Basket Size=      32000 bytes  Compression=  10.47     *
*............................................................................*
*Br    5 :nnmaxhits : nnmaxhits[6]/I                                         *
*Entries :     9500 : Total  Size=     229096 bytes  File Size  =      17014 *
*Baskets :        8 : Basket Size=      32000 bytes  Compression=  13.44     *
*............................................................................*
*Br    6 :zomaxhits : zomaxhits[6]/I                                         *
*Entries :     9500 : Total  Size=     229096 bytes  File Size  =      12764 *
*Baskets :        8 : Basket Size=      32000 bytes  Compression=  17.91     *
*............................................................................*
"""

infile = TFile( "output_femsim_nnhits.root" )
tree = infile.Get( "fem" )
nentries = tree.GetEntries()

ofile = TFile( "output_plots.root", "RECREATE" )

c = TCanvas("c","c",800,600)
c.Draw()

# CHANNEL TRIGGER RATE
hchrate = TH1D( "hchrate", ";FEM CH;frac. with triggers", 32, 0, 32 )
for femch in xrange(0,32):
    ntrigs = float( tree.GetEntries( "chtrig[%d]>0"%(femch) ) )
    frac = ntrigs/float(nentries)
    hchrate.SetBinContent( femch+1, frac )

hchrate.Draw()
c.Update()

raw_input()
