'''
Scripts to make the xsec.json and pmap.json files.

'''
import json


BR_THadronic = 0.665
BR_TLeptonic = 1 - BR_THadronic

BR_HBB = 0.5809

#Make the xsec.json file
# Cross sections in pb
xs = {}

# QCD
xs["QCD_HT50to100"] =  1.863e+08
xs["QCD_HT100to200"] = 2.361e+07
xs["QCD_HT200to300"] = 1.552e+06
xs["QCD_HT300to500"] = 3.245e+05
xs['QCD_HT500to700'] = 3.033e+04
xs['QCD_HT700to1000'] = 6.412e+03
xs['QCD_HT1000to1500'] = 1.118e+03
xs['QCD_HT1500to2000'] = 1.085e+02
xs['QCD_HT2000toInf'] = 2.194e+01

xs["QCD_bEnriched_HT50to100"] =  0
xs["QCD_bEnriched_HT100to200"] = 0
xs["QCD_bEnriched_HT200to300"] = 8.021e+04
xs["QCD_bEnriched_HT300to500"] = 1.674e+04
xs['QCD_bEnriched_HT500to700'] = 1.500e+03
xs['QCD_bEnriched_HT700to1000'] = 2.997e+02
xs['QCD_bEnriched_HT1000to1500'] = 4.761e+01
xs['QCD_bEnriched_HT1500to2000'] = 4.022e+00
xs['QCD_bEnriched_HT2000toInf'] = 6.973e-01

xs['QCD_Pt_120to170'] = 4.074e+05
xs['QCD_Pt_170to300'] = 1.035e+05
xs['QCD_Pt_300to470'] = 6.833e+03
xs['QCD_Pt_470to600'] = 5.495e+02
xs['QCD_Pt_600to800'] = 156.5
xs['QCD_Pt_800to1000'] = 2.622e+01
xs['QCD_Pt_1000to1400'] = 7.475e+00
xs['QCD_Pt_1400to1800'] = 6.482e-01
xs['QCD_Pt_1800to2400'] = 8.742e-02
xs['QCD_Pt_2400to3200'] = 5.237e-03
xs['QCD_Pt_3200toInf'] = 1.353e-04

# TTBar
# needs BRs
xs['TTJets'] = 0
xs['TTTo2L2Nu'] = 6.871e+02 * BR_TLeptonic**2
xs['TTToHadronic'] = 6.871e+02 * BR_THadronic**2
xs['TTToSemiLeptonic'] = 6.871e+02 * 2 * BR_TLeptonic * BR_THadronic
xs['TTToSemiLeptonic_ext1'] = xs['TTToSemiLeptonic']

xs['TT_MTT1000ToInf'] = 1.645e+01
xs['TT_MTT700To1000'] = 6.455e+01

# Single Top
# Needs BRs?
xs['ST_s-channel_4f_leptonDecays'] = 3.549e+00 * BR_TLeptonic
xs['ST_s-channel_4f_hadronicDecays'] = 3.549e+00 * BR_THadronic
xs['ST_t-channel_antitop_4f_InclusiveDecays'] = 6.793e+01
xs["ST_t-channel_antitop"] = 67.93
xs['ST_t-channel_antitop_5f_InclusiveDecays'] = 7.174e+01
xs['ST_t-channel_top_4f_InclusiveDecays'] = 1.134e+02
xs["ST_t-channel_top"] = 113.4
xs['ST_t-channel_top_5f_InclusiveDecays'] = 1.197e+02
xs['ST_tW_antitop_5f_inclusiveDecays'] = 3.251e+01
xs['ST_tW_antitop'] = 32.51
xs['ST_tW_antitop_5f_NoFullyHadronicDecays'] = 3.251e+01 * BR_TLeptonic
xs['ST_tW_top_5f_inclusiveDecays'] = 3.245e+01
xs["ST_tW_top"] = 32.45
xs['ST_tW_top_5f_NoFullyHadronicDecays'] = 3.245e+01 * BR_TLeptonic

# W+jets W(qq)
xs['WJetsToQQ_HT200to400'] = 2549.0
xs['WJetsToQQ_HT400to600'] = 2.770e+02 
xs['WJetsToQQ_HT600to800'] = 5.906e+01 
xs['WJetsToQQ_HT800toInf'] = 2.875e+01 
    
# W+jets W(lv)
xs['WJetsToLNu_HT70to100'] = 1.270e+03
xs['WJetsToLNu_HT100to200'] = 1.252e+03 
xs['WJetsToLNu_HT200to400'] = 3.365e+02 
xs['WJetsToLNu_HT400to600'] = 4.512e+01 
xs['WJetsToLNu_HT600to800'] = 1.099e+01 
xs['WJetsToLNu_HT800to1200'] = 4.938e+00 
xs['WJetsToLNu_HT1200to2500'] = 1.155e+00 
xs['WJetsToLNu_HT2500toInf'] = 2.625e-02 

# Z+jets Z(qq)
xs['ZJetsToQQ_HT200to400'] = 1012.0
xs['ZJetsToQQ_HT400to600'] = 1.145e+02
xs['ZJetsToQQ_HT600to800'] = 2.541e+01
xs['ZJetsToQQ_HT800toInf'] = 1.291e+01
        
# DY+jets
xs['DYJetsToLL_HT70to100'] = 1.399e+02
xs['DYJetsToLL_HT100to200'] = 1.401e+02
xs['DYJetsToLL_HT200to400'] = 3.835e+01
xs['DYJetsToLL_HT400to600'] = 5.217e+00
xs['DYJetsToLL_HT600to800'] = 1.267e+00
xs['DYJetsToLL_HT800to1200'] = 5.682e-01
xs['DYJetsToLL_HT1200to2500'] = 1.332e-01
xs['DYJetsToLL_HT2500toInf'] = 2.978e-03

xs['DYJetsToLL_Pt-50To100'] = 3.941e+02
xs['DYJetsToLL_Pt-100To250'] = 9.442e+01
xs['DYJetsToLL_Pt-250To400'] = 3.651e+00
xs['DYJetsToLL_Pt-400To650'] = 4.986e-01
xs['DYJetsToLL_Pt-650ToInf'] = 4.678e-02

# EWK Z
xs['EWKZ_ZToQQ'] = 9.791e+00
xs['EWKZ_ZToLL'] = 6.207e+00
xs['EWKZ_ZToNuNu'] = 1.065e+01

# EWK W
xs['EWKWminus_WToQQ'] = 1.917e+01
xs['EWKWplus_WToQQ'] = 2.874e+01
xs['EWKWminus_WToLNu'] = 3.208e+01
xs['EWKWplus_WToLNu'] = 3.909e+01

# VV 
xs['WW'] = 7.583e+01
xs['WZ'] = 2.756e+01
xs['ZZ'] = 1.214e+01

#VV NLO
xs['WWTo1L1Nu2Q_NLO'] = 5.090e+01
xs['WWTo4Q_NLO'] = 5.157e+01

xs['WZTo4Q_NLO'] = 1.595e+01
xs['WZToLNu2B_NLO'] = 2.638e+01
xs['WZTo1L1Nu2Q_NLO'] = 9.152e+00
xs['WZTo2Q2L_NLO'] = 6.422e+00

xs['ZZTo2Q2L_NLO'] = 3.705e+00
xs['ZZTo2Nu2Q_NLO'] = 4.498e+00
xs['ZZTo4Q_NLO'] = 3.295e+00

# Higgs
xs['GluGluHToBB'] = 4.716e-01 * BR_HBB
xs['VBFHToBB'] = 3.873e+00 * BR_HBB
xs['VBFHToBB_DipoleRecoilOn'] = xs['VBFHToBB']

xs['WminusH_HToBB_WToQQ'] = 3.675e-01 * BR_HBB
xs['WplusH_HToBB_WToQQ'] = 5.890e-01 * BR_HBB
xs['WminusH_HToBB_WToLNu'] = 1.770e-01 * BR_HBB
xs['WplusH_HToBB_WToLNu'] = 2.832e-01 * BR_HBB

xs['ZH_HToBB_ZToQQ'] = 5.612e-01 * BR_HBB
xs['ZH_HToBB_ZToLL'] = 7.977e-02 * BR_HBB
xs['ZH_HToBB_ZToNuNu'] = 1.573e-01 * BR_HBB

xs['ggZH_HToBB_ZToNuNu'] = 1.222e-02 * BR_HBB
xs['ggZH_HToBB_ZToQQ'] = 4.319e-02 * BR_HBB
xs['ggZH_HToBB_ZToLL'] = 6.185e-03 * BR_HBB
    
xs['ttHToBB'] = 5.013e-01 * BR_HBB

xs['HHTo4B'] = 31.05e-3*5.824e-01*5.824e-01

with open('../xsec.json', 'w') as outfile: json.dump(xs, outfile, indent=4)