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
c = TCanvas("c","c", 1200,600)
cch = TCanvas("cch","",800,500)
csinglerate = TCanvas("csinglerate","c", 1200,600)
h = TH1D( "h", "", 20, 0, 20 )
NCHANS = 32

eventrate = {}
for ch in range(0,NCHANS):
    eventrate[ch] = {}

runpts = {}

pois = TF1("pois","[0]*TMath::Poisson(x,[1])",0,50)


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
            figsfolder = "figs/filterreconnect/run%d_subrun%d"%(run,subrun)
        else:
            subrun = -1
            figsfolder = "figs/filterreconnect/run%d"%(run)
        os.popen( "mkdir -p %s"%(figsfolder) )

        subrunsecs = 0
        if subrun>0:
            subrunsecs = subrun*1000.0*0.1
        t = secs + subrunsecs

        tevent = TChain("eventtree")
        tpulse = TChain("pulsetree")
        tevent.Add( input )
        tpulse.Add( input )
        ientry = 0
        bytes = tevent.GetEntry(0)
        while bytes!=0:
            if tevent.samples>=1000:
                nsamples = tevent.samples - tevent.samples%100
                break
            bytes = tevent.GetEntry(ientry)
            ientry += 1


        cch.cd()

        exrate = 0
        for ch in range(0,NCHANS):
            h.Reset()
            tevent.Draw("nfires[%d]>>h"%(ch),"chmax<100 && samples>=950")
            mean = h.GetMean()
            hmax = h.GetMaximum()
            pois.SetParameter(0,hmax)
            pois.SetParameter(1,mean)
            h.Fit( pois, "RQ", "", 0, 20 )
            fitmean = pois.GetParameter(1)
            eventrate[ch][t] = (fitmean/float(15.625e-9*nsamples))*1.0e-3
            if ch==0:
                runpts[t] = (run,subrun)
            if ch==5:
                exrate = fitmean
            #print ch,fitmean, eventrate[ch][t]
            #cch.SaveAs( figsfolder+"/nfires_ch%d.png"%(ch))

        print input, "subrun=",subrun," t=",t," samples=",nsamples," mean npulses=",exrate," rate=",(exrate/float(15.625e-9*nsamples))*1.0e-3,"kHz"
            
# make graph
c.cd()
c.Draw()
haxis = TH2D("haxis",";hours;rate (kHz)",100,-2.0, 12*24.0, 100, 0, 400.0 )
haxis.Draw()
tgraphs = {}

runmarkerypos = {}

for ch in range(0,NCHANS):
    npts = len(eventrate[ch])
    tgraphs[ch] = TGraph( npts )
    tgraphs[ch].SetLineColor( 2+ch )
    tvalues = eventrate[ch].keys()
    tvalues.sort()

    for pt in range(0,npts):
        y = eventrate[ch][ tvalues[pt] ]
        tgraphs[ch].SetPoint( pt, tvalues[pt]/3600.0, y )

        if pt not in runmarkerypos:
            runmarkerypos[pt] = -1.0
        if runmarkerypos[pt]<0 or runmarkerypos[pt]>y:
            runmarkerypos[pt] = y
    c.cd()
    tgraphs[ch].Draw("PL")
    c.Update()
    csinglerate.Clear()
    csinglerate.cd()
    tgraphs[ch].Draw("APL")
    csinglerate.Update()
    csinglerate.SaveAs( "figs/filterreconnect/rate_ch%d.png"%(ch) )

# save combined graph
c.SaveAs( "figs/filterreconnect/filterreconnect.pdf" )
# annotate it
pts = runmarkerypos.keys()
pts.sort()

labels = []
lastt = -1000
for pt in pts:
    t = tvalues[pt]/3600.0
    y = (runmarkerypos[pt]-50.0)
    if runpts[ tvalues[pt] ][1]<0:
        label = TText( t, y, "%d"%( runpts[ tvalues[pt] ][0] ) )
    else:
        label = TText( t, y, "%d.%d"%runpts[ tvalues[pt] ] )    
    #print t, y, runpts[ tvalues[pt] ]
    if  t-lastt>1.0 or runpts[ tvalues[pt] ][0] in [2648,2659,2661,2663,2668]:
        if runpts[ tvalues[pt] ][1]<0:
            print runpts[tvalues[pt] ][0]," & N/A & %.2f"%(t)," & %.0f"%(runmarkerypos[pt]),"\\\\"
        else:
            print runpts[tvalues[pt] ][0]," & ", runpts[tvalues[pt] ][1]," & %.2f"%(t)," & %.0f"%(runmarkerypos[pt]),"\\\\"
        lastt = t
    label.SetNDC()
    label.SetTextSize(1)
    label.SetTextColor(1)
    label.Draw("same")
    labels.append( label )
c.SaveAs( "figs/filterreconnect/filterreconnect_annotated.pdf" )

# plot rate over tubes

from pyqtgraph.Qt import QtGui, QtCore
app = QtGui.QApplication([])

import pyqtgraph as pg
from pylard.pylardisplay.opdetdisplay import OpDetDisplay
opdisplay = OpDetDisplay( None )
opdisplay.show()

channeldata = {}
for ch in range(0,32):
    rate = eventrate[ch][ tvalues[-1] ]
    y = (rate-150.0)/150.0
    channeldata[ch] = y
    print ch,rate
opdisplay.setPMTdiagramValues( channeldata )

raw_input()

