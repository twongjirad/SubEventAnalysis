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

def makeplots( inputfile, outdir, run ):
    os.system("mkdir -p %s"%(outdir))

    eventtree = TChain("eventtree")
    eventtree.Add( inputfile )
    eventtree.GetEntry(0)
    windowlen = (eventtree.samples-1)*15.625

    pulsetree = TChain("pulsetree")
    pulsetree.Add( inputfile )

    eventcut = "chmax<100"
    pulsecut = "chmaxamp<100 && amp>10"

    # 2D trigs per event vs. channel
    NBINSRATE = 25
    binwidth = 1.0/((eventtree.samples-1)*15.625e-6)
    MINRATE = -0.5*binwidth
    MAXRATE = (NBINSRATE+0.5)*binwidth

    c = TCanvas("c","c",800, 600)
    c.Draw()
    hrate2D = TH2D( "rate2d", ";FEM channel; rate (kHz)", NCHANS, 0, NCHANS, NBINSRATE+1, MINRATE, MAXRATE )
    hrates = {}
    for ich in range(0,NCHANS):
        hname = "ratech%d"%(ich)
        hrates[ich] = TH1D( hname, "", NBINSRATE+1, MINRATE, MAXRATE )
        eventtree.Draw("nfires[%d]/(%d*15.625e-6)>>%s"%(ich,eventtree.samples-1,hname),eventcut)
        c.Update()
        print hname, " mean=",hrates[ich].GetMean()
        #raw_input()
        for i in range(2,hrates[ich].GetNbinsX()+1):
            hrate2D.SetBinContent( ich+1, i, hrates[ich].GetBinContent( i ) )
    hrate_prof = hrate2D.ProfileX()
    hrate2D.Draw("COLZ")
    hrate_prof.Draw("same")

    c.SaveAs( "%s/run%d_rate_vs_ch.pdf"%(outdir,run) )
    c.Update()
    #raw_input()

    # pusles
    NBINSPULSES = NBINSRATE
    hpulses2D = TH2D( "pulses2d", ";FEM channel; pulses in readout window", NCHANS, 0, NCHANS, NBINSPULSES, 0, NBINSPULSES )
    hpulsess = {}
    for ich in range(0,NCHANS):
        hname = "pulsesch%d"%(ich)
        hpulsess[ich] = TH1D( hname, "", NBINSPULSES, 0, NBINSPULSES )
        eventtree.Draw("nfires[%d]>>%s"%(ich,hname),eventcut)
        c.Update()
        #raw_input()
        for i in range(2,hpulsess[ich].GetNbinsX()+1):
            hpulses2D.SetBinContent( ich+1, i, hpulsess[ich].GetBinContent( i ) )
    hpulses2D.Draw("COLZ")
    c.SaveAs( "%s/run%d_pulses_vs_ch.pdf"%(outdir,run) )
    c.Update()
    #raw_input()
    
    # 2D amp per pulse for each channel
    hamp2D = TH2D( "amp2d", ";FEM channel; amp (ADC counts)", NCHANS, 0, NCHANS, 60, 0, 60)
    hamps = {}
    for ich in range(0,NCHANS):
        hname = "ampch%d"%(ich)
        hamps[ich] = TH1D( hname, "", 60, 0, 60 )
        pulsetree.Draw("amp>>%s"%(hname),"(%s) && ch==%d"%(pulsecut,ich))
        c.Update()
        #raw_input()
        for i in range(1,hamps[ich].GetNbinsX()+1):
            hamp2D.SetBinContent( ich+1, i, hamps[ich].GetBinContent( i ) )
    hamp2D.Draw("COLZ")
    c.SaveAs( "%s/run%d_amp_vs_ch.pdf"%(outdir,run) )
    c.Update()
    #raw_input()

if __name__ == "__main__":

    input = "pmtratestudy/run1536.root"
    output = "pmtratestudy/figs/run1536"
    #if len(sys.argv)==4:
    #    input = sys.argv[1]
    #    output = sys.argv[2]
    #    run = int(sys.argv[3])

    folder = "../../data/pmtratedata/processed"
    files = os.listdir( folder )
    for f in files:
        if ".root" not in f.strip():
            continue
        if "filterreconnect" not in f.strip():
            continue
        #input = "pmtratestudy/"+f.strip()
        input = folder+"/"+f.strip()
        output = "pmtratestudy/filterreconnect_figs/"+f.strip()[:-len(".root")]
        try:
            run = int( f.strip().split("_")[0][len("run"):] )
        except:
           #print r.strip().split("_")
           #print r.strip().split("_")
            run = int( f.strip().split(".")[0][len("run"):] )
        print "PROCESS RUN ",run
        makeplots( input, output, run)

    makeplots( input, output, run)
    #makeplots( "test.root", "figs/test" )

