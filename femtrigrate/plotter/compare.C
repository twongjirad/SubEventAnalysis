#include <iostream>
#include <sstream>

#include "TCanvas.h"
#include "TFile.h"
#include "TH1F.h"
#include "TH2F.h"

using namespace std;

void compare() {
  
  TFile* f1 = new TFile("../run1571_plots.root");
  TFile* f2 = new TFile("../run1578_plots.root");

  TH2F* h1 = (TH2F *)f1->Get("h3");
  TH2F* h2 = (TH2F *)f2->Get("h3");

  //TH2F* h_sum = new TH2F("hminus","difference", 25,0,25,10000,0,10000);
  h1->Add(h2, -1);

  h1->SetTitle("run1571");
  h2->SetTitle("run1578");

  TCanvas* c1 = new TCanvas("c1", "c1", 0, 0, 1600, 800);
  c1->Divide(2,2);

  c1->cd(1);
  h1->Draw("COLZ");
  c1->cd(2);
  h2->Draw("COLZ");
  c1->cd(3);
  //-------------h_sum->Draw("COLZ");

}
