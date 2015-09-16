#include<iostream>
#include<fstream>
#include<sstream>

#include"TH1F.h"
#include"TFile.h"
#include"TLegend.h"
#include"TTree.h"
#include"TCanvas.h"
#include"TMultiGraph.h"
#include"TGraphErrors.h"

using namespace std;

void rateStudy() {
  const int NRUNS = 13;
  const int NCH = 32;

  TCanvas* c1 = new TCanvas("c1", "c1", 800, 600);

  ifstream fin;
  fin.open("runlist.txt");

  string runNumber = "";

  TMultiGraph *mg = new TMultiGraph();

  TLegend *legend=new TLegend(0.75,0.65,0.88,0.85);
  legend->SetNColumns(4);
  legend->SetFillColor(0);

  //Color buffer
  const int NCOLORS = 32;
  int color[NCOLORS] = {73, 2, 3, 4, 5, 6, 7, 8, 9, 12, 28, 32, 34,
                        28, 50, 51, 56, 58, 88, 99, 1, 208, 209,
                        218, 212, 210, 221, 224, 225, 226, 227, 228 };

  for (int ch = 0; ch < NCH; ++ch) {
    Double_t x[NRUNS];
    Double_t y[NRUNS];
    Double_t errX[NRUNS] = {0};
    Double_t errY[NRUNS];

    int fileCounter = 0;
    while(getline(fin, runNumber)) {
      x[fileCounter] = fileCounter;
      stringstream filePath;
      filePath << "pmtratestudy/run" << runNumber << ".root";

      TFile* f = new TFile(filePath.str().c_str());
      TTree* t = (TTree *)f->Get("eventtree");

      int nfires[NCH] = {0};
      t->SetBranchAddress("nfires", &nfires);

      TH1F* h = new TH1F("h","hist", NCH, 0, NCH);
      
      int nentries = t->GetEntries();
      for (int entry = 0; entry < nentries; ++entry) {
        t->GetEntry(entry);
        h->Fill(nfires[ch]);
      }
      y[fileCounter] = h->GetMean() / (1500 * 15.625E-6);
      errY[fileCounter] = h->GetMeanError() / (1500 * 15.625E-6);
      cout << x[fileCounter] << ", " << y[fileCounter] << endl;
      f->Close();
      fileCounter++;
    } 
    
    TGraphErrors* gr = new TGraphErrors(NRUNS, x, y, errX, errY);
    gr->SetLineColor(color[ch % NCOLORS]);
    cout << "color: " << color[ch % NCOLORS] << endl;
    gr->SetLineWidth(2);
    gr->GetXaxis()->SetTitle("Run Date");
    gr->GetYaxis()->SetTitle("Rate [kHz]");

    ifstream din;
    din.open("runinfo.txt");
    string date;
    int runCounter = 0;
    while(getline(din, date)) {
      int bin_index = gr->GetXaxis()->FindBin(x[runCounter]);
      gr->GetXaxis()->SetBinLabel(bin_index, date.c_str());
      runCounter++;
    }
    din.close();

    stringstream entryName, fileName;
    entryName << ch;
    gr->SetTitle(entryName.str().c_str());
    fileName << "plots/" << ch << ".png";
    legend->AddEntry(gr, entryName.str().c_str());
    gr->Draw("alp");
    c1->SaveAs(fileName.str().c_str());
    mg->Add(gr);
    cout << "added plot to mg\n";
    fin.clear();
    fin.seekg(0, ios::beg);
  }
  mg->Draw("alp");
  mg->GetXaxis()->SetTitle("Run #");
  mg->GetYaxis()->SetTitle("Rate [kHz]");

  legend->Draw();

  c1->SaveAs("mg.pdf");
}

