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
#include"TChain.h"
#include"TCanvas.h"
#include"TMultiGraph.h"
#include"TGraphErrors.h"

using namespace std;

vector<double> parse(string s);

void rateStudy() {
  const int NRUNS = 25;
  const int NCH = 32;
  const int NBINS = 32;

  TCanvas* c1 = new TCanvas("c1", "c1", 800, 600);

  TMultiGraph *mg = new TMultiGraph();

  TLegend *legend=new TLegend(0.65,0.15,0.88,0.55);
  legend->SetNColumns(4);
  legend->SetFillColor(0);

  TH1F* hRate = new TH1F("hRate", "hist", 32.0, 0, 8.0);

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
  TH1F* h = new TH1F("h","hist", NBINS, 0, NBINS);
  TF1* pois = new TF1("pois","[0]*TMath::Poisson(x,[1])",0,50);
  TF1* ppp = new TF1("ppp","[0]*TMath::Power(0.5,x*[1])",0.01,1.0);


  for (int ch = 0; ch < NCH; ++ch) {

    if ( ch==26 || ch==27 )
      continue;

    //Graph points and errors
    Double_t x[NRUNS];
    Double_t y[NRUNS];
    Double_t errX[NRUNS] = {0};
    Double_t errY[NRUNS] = {0};

    int fileCounter = 0;
    while(getline(fin, line)) {
      vector<double> data = parse(line);
      stringstream filePath;
      filePath << "pmtratestudy/run" << data[0] << "*.root";
      cout << "opening file at " << filePath.str() << endl;
      cout << "file counter: " << fileCounter << " channel=" << ch << endl;
      //TFile* f = new TFile(filePath.str().c_str());
      //TTree* t = (TTree *)f->Get("eventtree");
      TChain* t = new TChain("eventtree");
      t->Add( filePath.str().c_str() );
      out->cd();

      x[fileCounter] = data[1];

      int nfires[NCH] = {0};
      int samples = 0;
      float chmax = 0.0;
      t->SetBranchAddress("nfires", &nfires);
      t->SetBranchAddress("samples", &samples);
      t->SetBranchAddress("chmax", &chmax);
      
      h->Reset();
      
      int nentries = t->GetEntries();
      for (int entry = 0; entry < nentries; ++entry) {
        t->GetEntry(entry);
        if (chmax < 100.0) {
          h->Fill(nfires[ch]);
        }
      }


      
      pois->SetParameter(0,1);
      pois->SetParameter(1, h->GetMean());

      h->Fit(pois,"RQ","",0,50);
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
      delete t;
      //f->Close();
      fileCounter++;
    } 

    ppp->SetParameter(0,1);
    ppp->SetParameter(1,0.4);
     
    TGraphErrors* gr = new TGraphErrors(NRUNS, x, y, errX, errY);
    gr->SetLineColor(color[ch % NCOLORS]);
    cout << "color: " << color[ch % NCOLORS] << endl;
    gr->SetLineWidth(2);
    gr->SetMarkerStyle(7);
    gr->Fit("ppp","R0","Q0",0.045,2.0);
    TF1 *afit = (TF1 *)gr->GetFunction("ppp");
    Double_t aRate = 1/afit->GetParameter(1);  
    if (aRate > 0) {
      hRate->Fill(aRate);
    }
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
  } // loop over channel
  hRate->Draw();
  hRate->Fit("gaus");
  c1->SaveAs("hrate.pdf");
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

