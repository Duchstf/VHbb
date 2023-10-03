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
xs['ST_t-channel_antitop_5f_InclusiveDecays'] = 7.174e+01
xs['ST_t-channel_top_4f_InclusiveDecays'] = 1.134e+02
xs['ST_t-channel_top_5f_InclusiveDecays'] = 1.197e+02
xs['ST_tW_antitop_5f_inclusiveDecays'] = 3.251e+01
xs['ST_tW_antitop_5f_NoFullyHadronicDecays'] = 3.251e+01 * BR_TLeptonic
xs['ST_tW_top_5f_inclusiveDecays'] = 3.245e+01
xs['ST_tW_top_5f_NoFullyHadronicDecays'] = 3.245e+01 * BR_TLeptonic

# W+jets W(qq)
xs['WJetsToQQ_HT-200to400'] = 2549.0
xs['WJetsToQQ_HT-400to600'] = 2.770e+02 
xs['WJetsToQQ_HT-600to800'] = 5.906e+01 
xs['WJetsToQQ_HT-800toInf'] = 2.875e+01 
    
# W+jets W(lv)
xs['WJetsToLNu_HT-70To100'] = 1.270e+03
xs['WJetsToLNu_HT-100To200'] = 1.252e+03 
xs['WJetsToLNu_HT-200To400'] = 3.365e+02 
xs['WJetsToLNu_HT-400To600'] = 4.512e+01 
xs['WJetsToLNu_HT-600To800'] = 1.099e+01 
xs['WJetsToLNu_HT-800To1200'] = 4.938e+00 
xs['WJetsToLNu_HT-1200To2500'] = 1.155e+00 
xs['WJetsToLNu_HT-2500ToInf'] = 2.625e-02 

# Z+jets Z(qq)
xs['ZJetsToQQ_HT-200to400'] = 1012.0
xs['ZJetsToQQ_HT-400to600'] = 1.145e+02
xs['ZJetsToQQ_HT-600to800'] = 2.541e+01
xs['ZJetsToQQ_HT-800toInf'] = 1.291e+01
        
# DY+jets
xs['DYJetsToLL_M-50_HT-70to100'] = 1.399e+02
xs['DYJetsToLL_M-50_HT-100to200'] = 1.401e+02
xs['DYJetsToLL_M-50_HT-200to400'] = 3.835e+01
xs['DYJetsToLL_M-50_HT-400to600'] = 5.217e+00
xs['DYJetsToLL_M-50_HT-600to800'] = 1.267e+00
xs['DYJetsToLL_M-50_HT-800to1200'] = 5.682e-01
xs['DYJetsToLL_M-50_HT-1200to2500'] = 1.332e-01
xs['DYJetsToLL_M-50_HT-2500toInf'] = 2.978e-03

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

xs['WWTo1L1Nu2Q_NLO'] = 5.090e+01
xs['WWTo4Q_NLO'] = 5.157e+01
xs['WZTo1L1Nu2Q_NLO'] = 9.152e+00
xs['WZTo2Q2L_NLO'] = 6.422e+00
xs['ZZTo2Q2L_NLO'] = 3.705e+00
xs['ZZTo2Q2Nu_NLO'] = 4.498e+00
xs['ZZTo4Q_NLO'] = 3.295e+00

# Higgs
xs['GluGluHToBB'] = 4.716e-01 * BR_HBB
xs['VBFHToBB'] = 3.873e+00 * BR_HBB
xs['VBFHToBBDipoleRecoilOn'] = xs['VBFHToBB']

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

with open('../xsec.json', 'w') as outfile:
    json.dump(xs, outfile, indent=4)
    

#Make the pmap.json file
pmap = {}
    
pmap['QCD'] = ['QCD_Pt_120to170',                 
               'QCD_Pt_170to300', 
               'QCD_Pt_300to470', 
               'QCD_Pt_470to600', 
               'QCD_Pt_600to800', 
               'QCD_Pt_800to1000',
               'QCD_Pt_1000to1400',
               'QCD_Pt_1400to1800',
               'QCD_Pt_1800to2400',
               'QCD_Pt_2400to3200', 
               'QCD_Pt_3200toInf']

pmap['QCDHT'] = ['QCD_HT500to700',
                 'QCD_HT700to1000',
                 'QCD_HT1000to1500',
                 'QCD_HT1500to2000',
                 'QCD_HT2000toInf']

pmap['ttbar'] = ['TTTo2L2Nu', 
                 'TTToHadronic', 
#                 'TTToSemiLeptonic',
                 'TTToSemiLeptonic_ext1'
                ]

pmap['ttbarBoosted'] = ['TT_MTT700To1000',
                        'TT_MTT1000ToInf']

pmap['singlet'] = ['ST_t-channel_antitop_4f_InclusiveDecays', 
                   'ST_t-channel_top_4f_InclusiveDecays', 
                   'ST_tW_antitop_5f_inclusiveDecays', 
                   'ST_tW_top_5f_inclusiveDecays']

pmap['Wjets'] = ['WJetsToQQ_HT-400to600', 
                 'WJetsToQQ_HT-600to800', 
                 'WJetsToQQ_HT-800toInf',
                 'WJetsToLNu_HT-70To100',
                 'WJetsToLNu_HT-100To200', 
                 'WJetsToLNu_HT-200To400', 
                 'WJetsToLNu_HT-400To600', 
                 'WJetsToLNu_HT-600To800', 
                 'WJetsToLNu_HT-800To1200'
                 'WJetsToLNu_HT-1200To2500', 
                 'WJetsToLNu_HT-2500ToInf']

pmap['Zjets'] = ['ZJetsToQQ_HT-400to600', 
                 'ZJetsToQQ_HT-600to800', 
                 'ZJetsToQQ_HT-800toInf',
                 'DYJetsToLL_Pt-50To100',
                 'DYJetsToLL_Pt-100To250',
                 'DYJetsToLL_Pt-250To400',
                 'DYJetsToLL_Pt-400To650',
                 'DYJetsToLL_Pt-650ToInf']

pmap['ZjetsHT'] = ['ZJetsToQQ_HT-400to600', 
                   'ZJetsToQQ_HT-600to800', 
                   'ZJetsToQQ_HT-800toInf',
                   'DYJetsToLL_M-50_HT-70to100',
                   'DYJetsToLL_M-50_HT-100to200',
                   'DYJetsToLL_M-50_HT-200to400',
                   'DYJetsToLL_M-50_HT-400to600',
                   'DYJetsToLL_M-50_HT-600to800',
                   'DYJetsToLL_M-50_HT-800to1200',
                   'DYJetsToLL_M-50_HT-1200to2500',
                   'DYJetsToLL_M-50_HT-2500toInf']

pmap['WW'] = ['WW']
pmap['ZZ'] = ['ZZ']
pmap['WZ'] = ['WZ']

pmap['WW_NLO'] = ['WWTo1L1Nu2Q_NLO',
                  'WWTo4Q_NLO']

pmap['WZ_NLO'] =  ['WZTo1L1Nu2Q_4f_TuneCP5_13TeV-amcatnloFXFX-pythia8',
                   'WZTo2Q2L_mllmin4p0_TuneCP5_13TeV-amcatnloFXFX-pythia8']

pmap['ZZ_NLO'] = ['ZZTo2Q2L_NLO',
                  'ZZTo2Q2Nu_NLO',
                  'ZZTo4Q_NLO']

pmap['EWKZ'] = ['EWKZ_ZToQQ', 'EWKZ_ZToLL', 'EWKZ_ZtoNuNu']

pmap['EWKW'] = ['EWKWminus_WToQQ','EWKWplus_WToQQ', 'EWKWminus_WToLNu', 'EWKWplus_WToLNu']

pmap['ggF'] = ['GluGluHToBB']

pmap['VBFDipoleRecoilOff'] = ['VBFHToBB']

pmap['WH'] = ['WminusH_HToBB_WToQQ',
              'WplusH_HToBB_WToQQ',
              'WminusH_HToBB_WToLNu',
              'WplusH_HToBB_WToLNu']

pmap['ZH'] = ['ZH_HToBB_ZToQQ',
              'ZH_HToBB_ZToLL',
              'ZH_HToBB_ZToNuNu',
              'ggZH_HToBB_ZToQQ',
              'ggZH_HToBB_ZToLL',
              'ggZH_HToBB_ZToNuNu']
    
pmap['ttH'] = ['ttHToBB']

pmap['data'] = [
   'JetHT_Run2016B_ver2_HIPM',
    'JetHT_Run2016C_HIPM',
    'JetHT_Run2016D_HIPM',
    'JetHT_Run2016E_HIPM',
    'JetHT_Run2016F_HIPM',
    'JetHT_Run2016F',
    'JetHT_Run2016G',
    'JetHT_Run2016H',
    'JetHT_Run2017B',
    'JetHT_Run2017C',
    'JetHT_Run2017D',
    'JetHT_Run2017E',
    'JetHT_Run2017F',
    'JetHT_Run2018A', 
    'JetHT_Run2018B', 
    'JetHT_Run2018C', 
    'JetHT_Run2018D'
]

pmap['muondata'] = [
    'SingleMuon_Run2016B_ver2_HIPM',
    'SingleMuon_Run2016C_HIPM',
    'SingleMuon_Run2016D_HIPM',
    'SingleMuon_Run2016E_HIPM',
    'SingleMuon_Run2016F_HIPM',
    'SingleMuon_Run2016F',
    'SingleMuon_Run2016G',
    'SingleMuon_Run2016H',
    'SingleMuon_Run2017B',
    'SingleMuon_Run2017C',
    'SingleMuon_Run2017D',
    'SingleMuon_Run2017E',
    'SingleMuon_Run2017F',
    'SingleMuon_Run2018A', 
    'SingleMuon_Run2018B', 
    'SingleMuon_Run2018C', 
    'SingleMuon_Run2018D'
]

with open('../pmap.json', 'w') as outfile:
    json.dump(pmap, outfile, indent=4)
