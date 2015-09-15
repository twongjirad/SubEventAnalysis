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

  for (int ch = 0; ch < 32; ++ch) {
    Double_t x[13];
    Double_t y[13];
    Double_t errX[13] = {0};
    Double_t errY[13];

    int fileCounter = 0;
    while(getline(fin, runNumber)) {
      x[fileCounter] = fileCounter;
      stringstream filePath;
      filePath << "pmtratestudy/run" << runNumber << ".root";

      TFile* f = new TFile(filePath.str().c_str());
      TTree* t = (TTree *)f->Get("eventtree");

      int nfires[32] = {0};
      t->SetBranchAddress("nfires", &nfires);

      TH1F* h = new TH1F("h","hist",32, 0, 32);
      
      int nentries = t->GetEntries();
      for (int entry = 0; entry < nentries; ++entry) {
        t->GetEntry(entry);
        //for (int i = 0; i < 32; ++i) {
          h->Fill(nfires[ch]);
        //}
      }
      y[fileCounter] = h->GetMean();
      errY[fileCounter] = h->GetMeanError();
      cout << x[fileCounter] << ", " << y[fileCounter] << endl;
      f->Close();
      fileCounter++;
    } 
    
    TGraphErrors* gr = new TGraphErrors(13, x, y, errX, errY);
    gr->SetLineColor(color[ch % NCOLORS]);
    cout << "color: " << color[ch % NCOLORS] << endl;
    gr->SetLineWidth(2);
    gr->GetXaxis()->SetTitle("Run #");
    gr->GetYaxis()->SetTitle("Rate");
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
  mg->GetYaxis()->SetTitle("Rate");

  legend->Draw();
}

