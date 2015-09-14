import os,sys
from ROOT import *

"""
******************************************************************************
*Tree    :pulsetree : PMT Rates                                              *
*Entries :   143649 : Total =         2883640 bytes  File  Size =     648147 *
*        :          : Tree compression factor =   4.45                       *
******************************************************************************
*Br    0 :event     : event/I                                                *
*Entries :   143649 : Total  Size=     576733 bytes  File Size  =       7142 *
*Baskets :       19 : Basket Size=      32000 bytes  Compression=  80.66     *
*............................................................................*
*Br    1 :ch        : ch/I                                                   *
*Entries :   143649 : Total  Size=     576570 bytes  File Size  =      47550 *
*Baskets :       18 : Basket Size=      32000 bytes  Compression=  12.11     *
*............................................................................*
*Br    2 :dt        : dt/F                                                   *
*Entries :   143649 : Total  Size=     576570 bytes  File Size  =     268895 *
*Baskets :       18 : Basket Size=      32000 bytes  Compression=   2.14     *
*............................................................................*
*Br    3 :amp       : amp/F                                                  *
*Entries :   143649 : Total  Size=     576592 bytes  File Size  =     252061 *
*Baskets :       18 : Basket Size=      32000 bytes  Compression=   2.28     *
*............................................................................*
*Br    4 :chmaxamp  : chmaxamp/F                                             *
*Entries :   143649 : Total  Size=     576802 bytes  File Size  =      70958 *
*Baskets :       19 : Basket Size=      32000 bytes  Compression=   8.12     *
*............................................................................*
"""

gStyle.SetOptStat(0)
NCHANS = 32

def makeplots( inputfile, outdir ):
    os.system("mkdir -p %s"%(outdir))

    eventtree = TChain("eventtree")
    eventtree.Add( inputfile )
    eventtree.GetEntry(0)
    windowlen = (eventtree.samples-1)*15.625

    pulsetree = TChain("pulsetree")
    pulsetree.Add( inputfile )


    # 2D trigs per event vs. channel
    c = TCanvas("c","c",800, 600)
    c.Draw()
    hrate2D = TH2D( "rate2d", ";FEM channel; rate (kHz)", NCHANS, 0, NCHANS, 20, 0, 800 )
    hrates = {}
    for ich in range(0,NCHANS):
        hname = "ratech%d"%(ich)
        hrates[ich] = TH1D( hname, "", 20, 0, 800 )
        eventtree.Draw("nfires[%d]/(1500.0*15.625e-6)>>%s"%(ich,hname),"chmax<100")
        c.Update()
        #raw_input()
        for i in range(2,hrates[ich].GetNbinsX()+1):
            hrate2D.SetBinContent( ich+1, i, hrates[ich].GetBinContent( i ) )
    hrate2D.Draw("COLZ")
    c.SaveAs( "%s/rate_vs_ch.pdf"%(outdir) )
    c.Update()
    raw_input()
    
    # 2D amp per pulse for each channel
    hamp2D = TH2D( "amp2d", ";FEM channel; amp (ADC counts)", NCHANS, 0, NCHANS, 60, 0, 60)
    hamps = {}
    for ich in range(0,NCHANS):
        hname = "ampch%d"%(ich)
        hamps[ich] = TH1D( hname, "", 60, 0, 60 )
        pulsetree.Draw("amp>>%s"%(hname),"chmaxamp<100 && ch==%d"%(ich))
        c.Update()
        #raw_input()
        for i in range(1,hamps[ich].GetNbinsX()+1):
            hamp2D.SetBinContent( ich+1, i, hamps[ich].GetBinContent( i ) )
    hamp2D.Draw("COLZ")
    c.SaveAs( "%s/amp_vs_ch.pdf"%(outdir) )
    c.Update()
    raw_input()

if __name__ == "__main__":
    makeplots( "run1574_lightsoff.root", "figs/run1574_lightsoff" )
