/////////////////////////////////////////
// Thomas Wester, September 2015       //
// plotCut.C                           //
//                                     //
// ROOT macro for creating histograms  //
// from processed MicroBooNE files.    //
// Histograms show efficiency at diff- //
// erent trigger thresholds (photoele- //
// ctrons & hits).                     //
//                                     //
// Processed file for this script      //
// comes from running run_fem.py on    // 
// desired uBooNE data file.           //
/////////////////////////////////////////

#include <iostream>
#include <sstream>   //stringstream

#include "TFile.h"
#include "TTree.h"
#include "TCanvas.h"
#include "TPad.h"
#include "TStyle.h"
#include "TH1F.h"
#include "TH2F.h"

using namespace std;

void plotter() {
  
  //Grab the tree from the file
  TFile* f = TFile::Open("../output_femsim_nnhits.root");
  TTree* t = (TTree *)f->Get("fem");

  //Set the branches
  int id, maxhits, maxdiff;
  //nn & zo branches contain arrays, 6 elements per entry
  int nnmaxhits[6], nnmaxdiff[6];
  int zomaxhits[6], zomaxdiff[6];
 
  t->SetBranchAddress("eventid", &id);
  t->SetBranchAddress("maxhits", &maxhits);
  t->SetBranchAddress("maxdiff", &maxdiff);
  t->SetBranchAddress("nnmaxhits", &nnmaxhits);
  t->SetBranchAddress("nnmaxdiff", &nnmaxdiff);
  t->SetBranchAddress("zomaxhits", &zomaxhits);
  t->SetBranchAddress("zomaxdiff", &zomaxdiff);

  //Create a file to write histograms to
  TFile* f1 = TFile::Open("plots.root", "RECREATE");
  
  Int_t nentries = (Int_t)t->GetEntries();

  //3 modes: all, (n)earest(n)eighbor and (z)-(o)rdered
  //To disable a mode, change #if 1 to #if 0
  //"All" requires only one loop, nn & zo have 6 elements per entry, 
  //so have to loop over each entry 6 times for those modes
  //Histograms from "all" mode are drawn to a canvas as well as saved.

#if 1
  //all mode
  int total = 0; //Used to normalize histograms.
  TH1F* h1 = new TH1F("h1", "maxhits all", 25, 0, 25);
  TH1F* h2 = new TH1F("h2", "maxdiff all", 60000, 0, 60000);
  TH2F* h3 = new TH2F("h3", "2d all", 25, 0, 25, 20000, 0, 20000);

  //Set up drawing
  TCanvas* c1 = new TCanvas("c", "c", 0, 0, 1600, 800);
  TPad *pad1 = new TPad("pad2", "ch1", 0.01, 0.01, 0.64, 0.99);
  TPad *pad2 = new TPad("pad1", "ch0", 0.65, 0.51, 0.99, 0.99);
  TPad *pad3 = new TPad("pad3", "ch1", 0.65, 0.01, 0.99, 0.49);

  pad1->SetFillColor(18);
  pad2->SetFillColor(18);
  pad3->SetFillColor(18);

  c1->cd();

  pad1->Draw();
  pad2->Draw();
  pad3->Draw();

  for (Int_t i = 0; i < nentries; i++) {
    t->GetEntry(i);
    total++;
    for (int j = 0; j < maxhits + 1; j++) {
      h1->Fill(j);
    }
    for (int j = 0; j < maxdiff + 1; j++) {
      h2->Fill(j);
    }
    for (int j = 0; j < maxhits + 1; j++) {
      for (int k = 0; k < maxdiff + 1; k++) {
        h3->Fill(j, k);
      }
    }
  }

  //Draw histograms from "all" setting
  gStyle->SetPalette(1);
  pad2->cd();
  h1->Scale(1./(float)total);
  h1->Draw("colz");
  h1->GetXaxis()->SetTitle("Max Hits");
  h1->GetYaxis()->SetTitle("Fraction of Total");

  pad3->cd();
  h2->Scale(1./(float)total);
  h2->SetLineColor(2);
  h2->Draw("colz");
  h2->GetXaxis()->SetTitle("Max Diff");
  h2->GetYaxis()->SetTitle("Fraction of Total");

  pad1->cd();
  h3->Scale(1./(float)total);
  h3->Draw("colz");
  h3->GetXaxis()->SetTitle("Max Hits");
  h3->GetYaxis()->SetTitle("Max Diff");

  h1->Write();
  h2->Write();
  h3->Write();
#endif

  //Loop over groups
  for (Int_t group = 1; group < 6; group++) {
#if 1
    //nn mode
    int totalnn = 0;
    stringstream nnHitName, nnDiffName, nnAllName;
    stringstream nnHist1, nnHist2, nnHist3;
    nnHitName << "maxhits nn " << group;
    nnDiffName << "maxDiff nn " << group;
    nnAllName << "2d nn " << group;
    nnHist1 << "nnHits" << group;
    nnHist2 << "nnDiff" << group;
    nnHist3 << "nn2D" << group;

    TH1F* h4 = new TH1F(nnHist1.str().c_str(), nnHitName.str().c_str(), 25, 0, 25);
    TH1F* h5 = new TH1F(nnHist2.str().c_str(), nnDiffName.str().c_str(), 60000, 0, 60000);
    TH2F* h6 = new TH2F(nnHist3.str().c_str(), nnAllName.str().c_str(), 25, 0, 25, 20000, 0, 20000);

    for (Int_t i = 0; i < nentries; i++) {
      t->GetEntry(i);
      totalnn++;
      for (int j = 0; j < nnmaxhits[group] + 1; j++) {
        h4->Fill(j);
      }
      for (int j = 0; j < nnmaxdiff[group] + 1; j++) {
        h5->Fill(j);
      }
      for (int j = 0; j < nnmaxhits[group] + 1; j++) {
        for (int k = 0; k < nnmaxdiff[group] + 1; k++) {
          h6->Fill(j, k);
        }
      }
    }

    h4->Scale(1./(float)totalnn);
    h4->GetXaxis()->SetTitle("Max Hits");
    h4->GetYaxis()->SetTitle("Fraction of Total");

    h5->Scale(1./(float)totalnn);
    h5->SetLineColor(2);
    h5->GetXaxis()->SetTitle("Max Diff");
    h5->GetYaxis()->SetTitle("Fraction of Total");

    h6->Scale(1./(float)totalnn);
    h6->GetXaxis()->SetTitle("Max Hits");
    h6->GetYaxis()->SetTitle("Max Diff");

    h4->Write();
    h5->Write();
    h6->Write();
#endif

#if 1
    //zo mode
    int totalzo = 0;
    stringstream zoHitName, zoDiffName, zoAllName;
    stringstream zoHist1, zoHist2, zoHist3;
    zoHitName << "maxhits zo " << group;
    zoDiffName << "maxDiff zo " << group;
    zoAllName << "2d zo " << group;
    zoHist1 << "zoHits" << group;
    zoHist2 << "zoDiff" << group;
    zoHist3 << "zo2D" << group;

    TH1F* h7 = new TH1F(zoHist1.str().c_str(), zoHitName.str().c_str(), 25, 0, 25);
    TH1F* h8 = new TH1F(zoHist2.str().c_str(), zoDiffName.str().c_str(), 60000, 0, 60000);
    TH2F* h9 = new TH2F(zoHist3.str().c_str(), zoAllName.str().c_str(), 25, 0, 25, 20000, 0, 20000);

    for (Int_t i = 0; i < nentries; i++) {
      t->GetEntry(i);
      totalzo++;
      for (int j = 0; j < zomaxhits[group] + 1; j++) {
        h7->Fill(j);
      }
      for (int j = 0; j < zomaxdiff[group] + 1; j++) {
        h8->Fill(j);
      }
      for (int j = 0; j < zomaxhits[group] + 1; j++) {
        for (int k = 0; k < zomaxdiff[group] + 1; k++) {
          h9->Fill(j, k);
        }
      }
    }

    h7->Scale(1./(float)totalzo);
    h7->GetXaxis()->SetTitle("Max Hits");
    h7->GetYaxis()->SetTitle("Fraction of Total");

    h8->Scale(1./(float)totalzo);
    h8->SetLineColor(2);
    h8->GetXaxis()->SetTitle("Max Diff");
    h8->GetYaxis()->SetTitle("Fraction of Total");

    h9->Scale(1./(float)totalzo);
    h9->GetXaxis()->SetTitle("Max Hits");
    h9->GetYaxis()->SetTitle("Max Diff");

    h7->Write();
    h8->Write();
    h9->Write();
#endif
  }
  
}

