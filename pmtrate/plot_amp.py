import os,sys
import json
from ROOT import *
from datetime import datetime

gStyle.SetOptStat(0)

folder = "../../data/pmtratedata/processed"
filelist = "../../data/pmtratedata/README_v2.json"
f = open( filelist, 'r' )
j = json.load( f )

runs = j.keys()
runs.sort()

tstart_liquidflow = datetime.strptime( "09/18/2015 15:00:00", "%m/%d/%Y %H:%M:%S" )
print "Liquid flow: ",tstart_liquidflow


tf = TFile( "temp.root", "RECREATE" )

hamp = TH1D( "hamp", "", 50, 0, 50 )
hcharge = TH1D( "hcharge", "", 200, 0, 200 )
NCHANS = 32

maxamp = {}
charge = {}
for ch in range(0,NCHANS):
    maxamp[ch] = {}
    charge[ch] = {}

for strrun in runs:
    run = int(strrun)
    if "condition" not in j[strrun] or "filter reconnect" not in j[strrun]["condition"]:
        continue

    trun = datetime.strptime( j[strrun]["date"], "%m/%d/%Y %H:%M" )
    diff = trun-tstart_liquidflow
    secs = diff.days*(3600.0*24.0) + diff.seconds
    print run, trun, secs/3600.0,"hours"

    pfiles = os.popen( "ls "+folder+"/run%d_filterreconnect*.root"%(run) )
    files = pfiles.readlines()

    for file in files:
        input = file.strip()

        if "subrun" in input:
            subrun = int( input.split("_")[-1].split(".")[0][len("subrun"):] )
        else:
            subrun = -1

        subrunsecs = 0
        if subrun>0:
            subrunsecs = subrun*1000.0*0.1
        t = secs + subrunsecs
        print input, "subrun=",subrun," t=",t

        tevent = TChain("eventtree")
        tpulse = TChain("pulsetree")
        tevent.Add( input )
        tpulse.Add( input )
        tevent.GetEntry(0)
        nsamples = tevent.samples

        for ch in range(0,NCHANS):
            hamp.Reset()
            hcharge.Reset()
            tpulse.Draw("amp>>hamp","ch==%d && abs(ped-2048.0)<10 && amp<50 && amp>0 && area>0"%(ch))
            tpulse.Draw("area>>hcharge","ch==%d && abs(ped-2048.0)<10 && amp<50 && amp>0 && area>0"%(ch))
            fitptr = hamp.Fit( "gaus", "RQS0", "", 6, 30 )
            fitmean = fitptr.Get().Parameter(1)
            maxamp[ch][t] = fitmean
            fitptr = hcharge.Fit("gaus", "RQS0","",10, 200 )
            fitmean = fitptr.Get().Parameter(1)
            charge[ch][t] = fitmean
            #print ch,fitmean, maxamp[ch][t]
    #if len(maxamp[0])>=10:
    #    break

# make graph
camp = TCanvas("camp","Amp", 1200,600)
ccharge = TCanvas("ccharge","Charge", 1200,600)
camp.Draw()
ccharge.Draw()
haxis = TH2D("haxis",";hours;pulse amp (ADCs)",100,-2.0, 260.0, 100, 0, 50.0 )
haxis2 = TH2D("haxis2",";hours;pulse charge (ADC*ticks)",100,-2.0, 260.0, 100, 0, 200.0 )
camp.cd()
haxis.Draw()
ccharge.cd()
haxis2.Draw()
amp_tgraphs = {}
charge_tgraphs = {}
amp_centroid = {}
amp_trend = {}
amp_var = {}
for ch in range(0,NCHANS):
    npts = len(maxamp[ch])
    amp_tgraphs[ch] = TGraph( npts )
    charge_tgraphs[ch] = TGraph( npts )
    amp_tgraphs[ch].SetLineColor( 2+ch )
    charge_tgraphs[ch].SetLineColor( 2+ch )
    tvalues = maxamp[ch].keys()
    tvalues.sort()
    amp_x = 0
    amp_xx = 0
    charge_x = 0
    charge_xx = 0
    for pt in range(0,npts):
        y = maxamp[ch][ tvalues[pt] ]
        amp_tgraphs[ch].SetPoint( pt, tvalues[pt]/3600.0, y )
        amp_x += maxamp[ch][ tvalues[pt] ]
        amp_xx += maxamp[ch][ tvalues[pt] ]*maxamp[ch][ tvalues[pt] ]
        charge_tgraphs[ch].SetPoint( pt, tvalues[pt]/3600.0, charge[ch][ tvalues[pt] ] )
        charge_x = charge[ch][ tvalues[pt] ]
        charge_xx += charge[ch][ tvalues[pt] ]*charge[ch][ tvalues[pt] ]
    amp_x /= float(npts)
    amp_xx /= float(npts)
    charge_x /= float(npts)
    charge_xx /= float(npts)

    camp.cd()
    haxis.Draw()
    amp_tgraphs[ch].Draw("PL")
    camp.SaveAs("figs/filterreconnect/ch%d_spe_amp.pdf"%(ch))
    ccharge.cd()
    haxis2.Draw()
    charge_tgraphs[ch].Draw("PL")
    ccharge.SaveAs("figs/filterreconnect/ch%d_spe_charge.pdf"%(ch))
    camp.Update()
    ccharge.Update()


    # fit graphs
    print "CH %d AMP FIT" % (ch)
    print "  mean:",amp_x
    print "  stddev: ",sqrt( amp_xx - amp_x*amp_x )
    amp_fitptr = amp_tgraphs[ch].Fit( "pol1", "S0" )
    amp_var[ch] = sqrt( amp_xx - amp_x*amp_x )
    amp_centroid[ch] = (amp_fitptr.Get().Parameter(0),amp_fitptr.Get().Error(0))
    amp_trend[ch] = (amp_fitptr.Get().Parameter(1),amp_fitptr.Get().Error(1))
    
    print "CH %d CHARGE FIT"  % (ch)
    print "  mean: ",charge_x
    print "  stddev: ",sqrt( charge_xx - charge_x*charge_x )
    charge_fitptr = charge_tgraphs[ch].Fit( "pol1", "S0" )

# combined
camp.cd()
haxis.Draw()
for ch in range(0,NCHANS):
    amp_tgraphs[ch].Draw("PL")
camp.Update()
camp.SaveAs( "figs/filterreconnect/spe_amp_filterreconnect.pdf" )

ccharge.cd()
haxis2.Draw()
for ch in range(0,NCHANS):
    charge_tgraphs[ch].Draw("PL")
ccharge.Update()
ccharge.SaveAs( "figs/filterreconnect/spe_charge_filterreconnect.pdf" )

# print table
for ch in range(0,32):
    print ch," & %.2f\\pm%.2f"%(amp_centroid[ch][0],amp_centroid[ch][1])," & %.02f"%(amp_var[ch])," & %.04f\\pm%.04f"%amp_trend[ch]
