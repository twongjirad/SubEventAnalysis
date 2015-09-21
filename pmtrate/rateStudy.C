#include<iostream>
#include<fstream>
#include<vector>
#include<sstream>

#include"TH1F.h"
#include"TMath.h"
#include"TF1.h"
#include"TFile.h"
#include"TLegend.h"
#include"TTree.h"
#include"TCanvas.h"
#include"TMultiGraph.h"
#include"TGraphErrors.h"

using namespace std;

vector<double> parse(string s);

void rateStudy() {
  const int NRUNS = 21;
  const int NCH = 32;

  TCanvas* c1 = new TCanvas("c1", "c1", 800, 600);

  TMultiGraph *mg = new TMultiGraph();

  TLegend *legend=new TLegend(0.75,0.65,0.88,0.85);
  legend->SetNColumns(4);
  legend->SetFillColor(0);

  //Color buffer
  const int NCOLORS = 32;
  int color[NCOLORS] = {73, 2, 3, 4, 99, 6, 7, 8, 9, 12, 28, 32, 34,
                        28, 50, 51, 56, 58, 88, 99, 1, 208, 209,
                        218, 212, 210, 221, 224, 225, 226, 227, 228 };

  ifstream fin;
  //fin.open("runlist.txt");
  fin.open("filter_runlist.txt");

  string line = "";

  TFile* out = new TFile("outtemp.root", "REACREATE");
  
  for (int ch = 0; ch < NCH; ++ch) {
    //Graph points and errors
    Double_t x[NRUNS];
    Double_t y[NRUNS];
    Double_t errX[NRUNS] = {0};
    Double_t errY[NRUNS];

    int fileCounter = 0;
    while(getline(fin, line)) {
      vector<double> data = parse(line);
      stringstream filePath;
      filePath << "pmtratestudy/run" << data[0] << "*.root";
      cout << "opening file at " << filePath.str() << endl;
      //TFile* f = new TFile(filePath.str().c_str());
      //TTree* t = (TTree *)f->Get("eventtree");
      TChain* t = new TChain("eventtree");
      t->Add( filePath.str().c_str() );
      out->cd();

      x[fileCounter] = data[1];

      int nfires[NCH] = {0};
      int samples = 0;
      t->SetBranchAddress("nfires", &nfires);
      t->SetBranchAddress("samples", &samples);
      TH1F* h = new TH1F("h","hist", NCH, 0, NCH);
      
      int nentries = t->GetEntries();
      for (int entry = 0; entry < nentries; ++entry) {
        t->GetEntry(entry);
        h->Fill(nfires[ch]);
      }

      TF1* pois = new TF1("pois","[0]*TMath::Poisson(x,[1])",0,50);
      pois->SetParameter(0,1);
      pois->SetParameter(1, h->GetMean());

      h->Fit(pois,"R","",0,50);
      //TF1 *myfit = (TF1 *)h->GetFunction("pois");
      TF1 *myfit = (TF1 *)pois;
      Double_t lambda = myfit->GetParameter(1);  
      h->Draw();
      stringstream histFileName;
      histFileName << "hist/h" << data[0] << "_ch" << ch << ".png";
      c1->SaveAs(histFileName.str().c_str());
      //Graph with poisson method
#if 1
      y[fileCounter] = lambda / ((samples - 1) * 15.625E-6);
      errY[fileCounter] = myfit->GetParError(1) / ((samples - 1) * 15.625E-6);
#endif
      //Graph with mean method
#if 0
      y[fileCounter] = h->GetMean() / ((samples - 1) * 15.625E-6);
      errY[fileCounter] = h->GetMeanError() / ((samples - 1) * 15.625E-6);
#endif
      cout << x[fileCounter] << ", " << y[fileCounter] 
           << " | " << (samples - 1) << endl;
      //f->Close();
      fileCounter++;
    } 
    
    TGraphErrors* gr = new TGraphErrors(NRUNS, x, y, errX, errY);
    gr->SetLineColor(color[ch % NCOLORS]);
    cout << "color: " << color[ch % NCOLORS] << endl;
    gr->SetLineWidth(2);
    gr->SetMarkerStyle(7);
    gr->GetXaxis()->SetTitle("Run Date");
    gr->GetYaxis()->SetTitle("Rate [kHz]");

    stringstream entryName, fileName;
    entryName << "Channel" << ch;
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
  mg->GetXaxis()->SetTitle("Days since first run");
  mg->GetYaxis()->SetTitle("Rate [kHz]");
  mg->SetTitle("All channels: Rate vs. Days since first Run");

  legend->Draw();
  c1->SaveAs("mg.pdf");
}

//Splits input string and returns a vector of doubles
vector<double> parse(string s) {
    string str = s;
    vector<double> vect;

    stringstream ss(str);

    double d;

    while (ss >> d) {
        vect.push_back(d);

        if (ss.peek() == ',') {
            ss.ignore();
        }
    }
    return vect;
}

