/************************************************
 * Jennet Dickinson 
 * Nov 19, 2020
 * Draw Roofit plots
 ************************************************/
#include <iostream>

using namespace RooFit;
using namespace RooStats;

bool blind = true;

void draw(int Vmass_bin, bool bb_pass,  bool log=true){

  // Get the year and prefit/postfit/obs from the running directory
  string thisdir = gSystem->pwd();

  string year = "";
  string year_string = "137/fb, Run 2";

  if(thisdir.find("2016APV") != std::string::npos){
    year = "2016APV";
    year_string = "19.5/fb, 2016 APV";
  }
  else if(thisdir.find("2016") != std::string::npos){
    year = "2016";
    year_string = "16.8/fb, 2016";
  }
  else if(thisdir.find("2017") != std::string::npos){
    year = "2017";
    year_string = "41.5/fb, 2017";
  }
  else if(thisdir.find("2018") != std::string::npos){
    year = "2018";
    year_string = "59.2/fb, 2018";
  }

  //Fit root file
  string filename = "fitDiagnostics.root";

  string bb_region = (bb_pass) ? "pass" : "fail";

  // branch name (only one pT bin)
  string name = "VBin" + to_string(Vmass_bin) + bb_region + year;

  // Fit directory
  string hist_dir = "shapes_prefit/" + name+ "/";
  cout << hist_dir << endl;

  // Dummy variable to select the data branch
  TFile *f = new TFile(filename.c_str()); // Can use dataf and read all the distributions from there

  // Root specific stuff (can copy these for later use)
  gStyle->SetOptTitle(0);
  gStyle->SetOptStat(0);

  TCanvas* c = new TCanvas(name.c_str(),name.c_str(),600,600);
  TPad *pad1 = new TPad("pad1","pad1",0,.33,1,1);
  TPad *pad2 = new TPad("pad2","pad2",0,0,1,.33);

  pad1->SetBottomMargin(0.00001);
  pad1->SetTopMargin(0.1);
  pad1->SetBorderMode(0);
  pad2->SetTopMargin(0.00001);
  pad2->SetBottomMargin(0.3);
  pad2->SetBorderMode(0);

  pad1->SetLeftMargin(0.15);
  pad2->SetLeftMargin(0.15);
  pad1->Draw();
  pad2->Draw();

  float textsize1 = 16/(pad1->GetWh()*pad1->GetAbsHNDC());
  float textsize2 = 16/(pad2->GetWh()*pad2->GetAbsHNDC());

  pad1->cd();
  if( log ) pad1->SetLogy();

  /*DATA*/
  // Dummy variable to select the data branch
  string data_file = "signalregion.root";

  string data_bb_region  = (bb_pass) ? "_pass_": "_fail_";
  string leading_name = "Vmass_" + to_string(Vmass_bin) + data_bb_region;

  TFile *dataf = new TFile(data_file.c_str());
  TH1D* data_obs = (TH1D*)dataf->Get((leading_name+"data_nominal").c_str());

  // Check if the histogram is retrieved successfully
  if (!data_obs) {
    std::cerr << "Error: Histogram not found in the ROOT file." << std::endl;
    dataf->Close(); // Close the file
    return;
  }

  cout << data_obs->Integral() << endl;

  // blind data!
  if( blind && bb_pass ){                                                                                        
    for(int i=10; i<15; i++){
      data_obs->SetBinContent(i,0);
      data_obs->SetBinError(i,0);
    }                            
  } 

  // Plot data
  data_obs->SetLineColor(kBlack);
  data_obs->SetMarkerColor(kBlack);
  data_obs->SetMarkerStyle(20);    

  float mc_scale = 7.0; //FitDiagnostics scale every MC by the bin width
  // >>>>>>>>>>>Signal<<<<<<<<<<<<
  /* WH */
  TH1D* WH = (TH1D*)f->Get((hist_dir+"WH").c_str()); // Reformat to get from the right file.
  WH->Scale(mc_scale);
  WH->SetLineColor(kGreen+1);
  WH->SetMarkerColor(kGreen+1);
  WH->SetLineWidth(3);

  /* ZH */
  TH1D* ZH = (TH1D*)WH->Clone("ZH"); // Copy WH and give it ZH name and empty it. 
  ZH->Reset();
  ZH->Add((TH1D*)f->Get((hist_dir+"ZH").c_str()));
  ZH->Scale(mc_scale);
  ZH->SetLineColor(kRed+1);
  ZH->SetMarkerColor(kRed+1);
  ZH->SetLineStyle(2);
  ZH->SetLineWidth(3);

  // >>>>>>>>>>> Back ground <<<<<<<<<
  /* bkg Higgs */
  TH1D* bkgHiggs = (TH1D*)WH->Clone("bkgHiggs");
  bkgHiggs->Reset();
  bkgHiggs->Add((TH1D*)f->Get((hist_dir+"ggF").c_str())); // Is this right?
  bkgHiggs->Add((TH1D*)f->Get((hist_dir+"VBF").c_str()));
  bkgHiggs->Add((TH1D*)f->Get((hist_dir+"ttH").c_str()));
  bkgHiggs->Scale(mc_scale);
  bkgHiggs->SetLineWidth(1);
  bkgHiggs->SetLineColor(kBlack);
  bkgHiggs->SetFillColor(kOrange);

  THStack *bkg = new THStack("bkg",""); //Histogram stack, order add -> stack

  /* VV */
  TH1D* VV = (TH1D*)WH->Clone("VV");
  VV->Reset();
  VV->Add((TH1D*)f->Get((hist_dir+"VV").c_str())); 
  VV->Scale(mc_scale);
  VV->SetLineWidth(1);
  VV->SetLineColor(kBlack);
  VV->SetFillColor(kOrange-3);

  /* single t */
  TH1D* singlet = (TH1D*)WH->Clone("singlet");
  singlet->Reset();
  singlet->Add((TH1D*)f->Get((hist_dir+"singlet").c_str()));
  singlet->Scale(mc_scale);
  singlet->SetLineWidth(1);
  singlet->SetLineColor(kBlack);
  singlet->SetFillColor(kPink+6);

  /* Z + jets */
  TH1D* Zjets = (TH1D*)f->Get((hist_dir+"Zjets").c_str());
  Zjets->Scale(mc_scale);
  Zjets->SetLineColor(kBlack);
  Zjets->SetFillColor(kAzure+8);

  /* Z + jets bb*/
  // TH1D* Zjetsbb = (TH1D*)f->Get((hist_dir+"Zjetsbb").c_str());
  // Zjetsbb->Scale(mc_scale);
  // Zjetsbb->SetLineColor(kBlack);
  // Zjetsbb->SetFillColor(kBlue-9);

  /* W + jets */
  TH1D* Wjets = (TH1D*)f->Get((hist_dir+"Wjets").c_str());
  Wjets->Scale(mc_scale);
  Wjets->SetLineColor(kBlack);
  Wjets->SetFillColor(kRed+1);

  /* ttbar */
  TH1D* ttbar = (TH1D*)f->Get((hist_dir+"ttbar").c_str());
  ttbar->Scale(mc_scale);
  ttbar->SetLineColor(kBlack);
  ttbar->SetFillColor(kViolet-5);
  
  /* QCD */
  TH1D* qcd = (TH1D*)f->Get((hist_dir+"qcd").c_str());
  qcd->Scale(mc_scale);
  qcd->SetLineColor(kBlack);
  qcd->SetFillColor(kGray);

  /* total background */
  TH1D* TotalBkg = (TH1D*)f->Get((hist_dir+"/total_background").c_str());
  TotalBkg->Scale(mc_scale);
  TotalBkg->SetMarkerColor(kGray+3);
  TotalBkg->SetLineColor(kGray+3);
  TotalBkg->SetFillColor(kGray+3);
  TotalBkg->SetFillStyle(3004);

  double max = TotalBkg->GetMaximum();
  TotalBkg->GetYaxis()->SetRangeUser(0.1,1000*max);
  if( !log ) TotalBkg->GetYaxis()->SetRangeUser(0,1.3*max);
  TotalBkg->GetYaxis()->SetTitle("Events / 7 GeV");
  TotalBkg->GetXaxis()->SetTitle("m_{sd} [GeV]");
  TotalBkg->GetYaxis()->SetTitleSize(textsize1);
  TotalBkg->GetYaxis()->SetLabelSize(textsize1);

  if( log ){
    bkg->Add(bkgHiggs);
    bkg->Add(VV);
    bkg->Add(singlet);
    bkg->Add(Zjets);
    // bkg->Add(Zjetsbb);
    bkg->Add(ttbar);
    bkg->Add(Wjets);
    bkg->Add(qcd);
  }
  else{
    bkg->Add(qcd);
    bkg->Add(ttbar);
    bkg->Add(VV);
    bkg->Add(Wjets);
    bkg->Add(Zjets);
    // bkg->Add(Zjetsbb);
    bkg->Add(singlet);
    bkg->Add(bkgHiggs);
  }

  cout << "QCD: "     << qcd->Integral()     << endl;
  cout << "Wjets: "   << Wjets->Integral()   << endl;
  cout << "Zjets: "   << Zjets->Integral()   << endl;
  // cout << "Zjetsbb: "   << Zjetsbb->Integral()   << endl;
  cout << "ttbar: "   << ttbar->Integral()   << endl;
  cout << "singlet: " << singlet->Integral() << endl;
  cout << "VV: "      << VV->Integral()      << endl;
  cout << "bkgHiggs: " << bkgHiggs->Integral() << endl;

  // PLot the fitted MC
  TotalBkg->Draw("e2");
  bkg->Draw("histsame");
  TotalBkg->Draw("e2same");
  WH->Draw("histsame");
  ZH->Draw("histsame");
  bkg->GetYaxis()->SetTitle("Events / 7 GeV");
  bkg->GetXaxis()->SetTitle("m_{sd} [GeV]");
  bkg->GetYaxis()->SetTitleSize(textsize1);
  bkg->GetYaxis()->SetLabelSize(textsize1);

  data_obs->Draw("pesame");
  data_obs->Draw("axissame");
  
  double x1=.6, y1=.88;
  TLegend* leg = new TLegend(x1,y1,x1+.3,y1-.3);
  leg->SetBorderSize(0);
  leg->SetFillStyle(0);
  leg->SetNColumns(2);
  leg->SetTextSize(textsize1);

  leg->AddEntry(data_obs,"Data","p");
  leg->AddEntry(TotalBkg,"Bkg. Unc.","f");
  leg->AddEntry(qcd,"QCD","f");
  leg->AddEntry(Wjets,"W","f");
  leg->AddEntry(ttbar,"t#bar{t}","f");
  leg->AddEntry(Zjets,"Z(qq)","f");
  // leg->AddEntry(Zjetsbb,"Z(bb)","f");
  leg->AddEntry(singlet,"Single t","f");
  leg->AddEntry(VV,"VV","f");
  leg->AddEntry(bkgHiggs,"Bkg. H","f");
  leg->AddEntry(ZH,"ZH","l");
  leg->AddEntry(WH,"WH","l");

  leg->Draw();

  TLatex l1;
  l1.SetNDC();
  l1.SetTextFont(42);
  l1.SetTextSize(textsize1);
  l1.DrawLatex(0.2,.92,"CMS Preliminary");

  TLatex l2;
  l2.SetNDC();
  l2.SetTextFont(42);
  l2.SetTextSize(textsize1);
  l2.DrawLatex(0.7,.92,year_string.c_str());

  TLatex l3;
  l3.SetNDC();
  l3.SetTextFont(42);
  l3.SetTextSize(textsize1);

  string region_text = "VBin " + to_string(Vmass_bin) + "; ";

  if( bb_pass )
    region_text += "Jet 1 B Pass";
  else
    region_text += "Jet 1 B Fail";

  l3.DrawLatex(0.2,.82,region_text.c_str());

  // Draw data - obs ratio
  pad2->cd();

  TH1D* TotalBkg_sub = (TH1D*)TotalBkg->Clone("TotalBkg_sub");
  TotalBkg_sub->Reset();
  TH1D* data_obs_sub = (TH1D*)data_obs->Clone("data_obs_ratio");
  data_obs_sub->Reset();

  TH1D* WH_sub = (TH1D*)WH->Clone("WH_sub");
  WH_sub->Reset();
  TH1D* ZH_sub = (TH1D*)ZH->Clone("ZH_sub");
  ZH_sub->Reset();

  for(int i=1; i<TotalBkg_sub->GetNbinsX()+1; i++){
    TotalBkg_sub->SetBinError(i,TotalBkg->GetBinError(i)/data_obs->GetBinError(i));


    data_obs_sub->SetBinContent(i,(data_obs->GetBinContent(i)-TotalBkg->GetBinContent(i))/data_obs->GetBinError(i));
    data_obs_sub->SetBinError(i,data_obs->GetBinError(i)/data_obs->GetBinError(i));

    WH_sub->SetBinContent(i,WH->GetBinContent(i)/data_obs->GetBinError(i));
    ZH_sub->SetBinContent(i,ZH->GetBinContent(i)/data_obs->GetBinError(i));
  }

  TotalBkg_sub->GetYaxis()->SetTitleSize(textsize2);
  TotalBkg_sub->GetYaxis()->SetLabelSize(textsize2);
  TotalBkg_sub->GetXaxis()->SetTitleSize(textsize2);
  TotalBkg_sub->GetXaxis()->SetLabelSize(textsize2);
  TotalBkg_sub->GetYaxis()->SetTitleOffset(2*pad2->GetAbsHNDC());
  TotalBkg_sub->GetYaxis()->SetTitle("(Data - Bkg)/#sigma_{Data}");
  TotalBkg_sub->SetMarkerSize(0);

  // blind data!                                                                                                                                                              
  if( blind  ){
    for(int i=10; i<15; i++){
      TotalBkg_sub->SetBinError(i,0);
      data_obs_sub->SetBinContent(i,0);
      data_obs_sub->SetBinError(i,0);
    }
  }

  double min2 = data_obs_sub->GetMinimum();
  double max2 = data_obs_sub->GetMaximum();
  if( !bb_pass ){
    max2 += 1;
    min2 -= 1;
  }
  TotalBkg_sub->GetYaxis()->SetRangeUser(1.3*min2,1.3*max2);

  TotalBkg_sub->Draw("e2");
  WH_sub->Draw("histsame");                                                                                                                                              
  ZH_sub->Draw("histsame");                                                                                                                                              
  data_obs_sub->Draw("pesame");                                                                                    

  c->SaveAs(("plots/"+ name + "_DataFit"+ ".png").c_str());
  c->SaveAs(("plots/"+ name + "_DataFit"+ ".pdf").c_str());

  return;

}

void draw_DataFit(){

  //Loop over V mass bins
  for(int i=0; i<3; i++){
    draw(i,1,0); //bb pass
    draw(i,0,0); //bb fail
  }

  return 0;

}
