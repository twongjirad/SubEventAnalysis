#include <iostream>
#include <fstream>
#include <sstream>

#include "TCanvas.h"
#include "TPaveStats.h"
#include "TFile.h"
#include "TH1F.h"
#include "TH2F.h"

using namespace std;

void compare() {
  
  ifstream fin;
  fin.open("runlist.txt");

  string currentRun = "";
  int runCounter = 0;  

  TCanvas* c1 = new TCanvas("c1", "c1", 0, 0, 1600, 800);
  c1->Divide(2,2);

  while (getline(fin, currentRun)) {
    runCounter++;
    stringstream path;
    path << "../run" << currentRun << "_plots.root";
    
    TFile* f = new TFile(path.str().c_str());
    TH2F* h = (TH2F *)f->Get("h3");

    h->SetTitle(currentRun.c_str());

    c1->cd(runCounter);
    h->Draw("COLZ");
    h->GetXaxis()->SetRangeUser(0, 8);
    h->GetYaxis()->SetRangeUser(0, 100);
  }

}
