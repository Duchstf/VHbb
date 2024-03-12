from __future__ import print_function, division
import sys, os
import json
import numpy as np
from scipy.interpolate import interp1d
import scipy.stats
import pickle
import ROOT

import rhalphalib as rl
from rhalphalib import AffineMorphTemplate, MorphHistW2

rl.util.install_roofit_helpers()

eps=0.0000001
do_muon_CR = False

'''
python make_cards.py [year]

Example: 

python make_cards.py 2017
'''

# Tell me if my sample is too small to care about
def badtemp_ma(hvalues, mask=None):
    # Need minimum size & more than 1 non-zero bins                                                                                                                                   
    tot = np.sum(hvalues[mask])

    count_nonzeros = np.sum(hvalues[mask] > 0)
    if (tot < eps) or (count_nonzeros < 2):
        return True
    else:
        return False

# Turn an msd distribution into a single bin (for muon CR)
def one_bin(template):
    try:
        h_vals, h_edges, h_key, h_variances = template
        return (np.array([np.sum(h_vals)]), np.array([0., 1.]), "onebin", np.array([np.sum(h_variances)]))
    except:
        h_vals, h_edges, h_key = template
        return (np.array([np.sum(h_vals)]), np.array([0., 1.]), "onebin")

# Read the histogram
def get_template(sName, passed, ptbin, cat, obs, syst, muon=False):
    """
    Read msd template from root file
    """

    f = ROOT.TFile.Open('{}/signalregion.root'.format(year))

    if muon:
        f = ROOT.TFile.Open('{}/muonCR.root'.format(year))

    #Jet 1 b pass/failing region
    name = 'pass_' if passed else 'fail_' 
    name = '{}_'.format(cat) + name #Charm/Light Category
    name += sName+'_'+syst #sytematic name

    print("Extracting ... ", name)
    h = f.Get(name)

    sumw = []
    sumw2 = []

    for i in range(1,h.GetNbinsX()+1):
        sumw += [h.GetBinContent(i)]
        sumw2 += [h.GetBinError(i)*h.GetBinError(i)]

    return (np.array(sumw), obs.binning, obs.name, np.array(sumw2))

def vh_rhalphabet(tmpdir):
    """ 
    Create the data cards!

    1. Fit QCD MC Only
    2. Fill in actual fit model to every thing except for QCD
    3. Fill QCD in the actual fit model
    """
    
    with open('files/lumi.json') as f:
        lumi = json.load(f)
    
    with open("files/samples.json", "r") as f:   # Unpickling
        samples = json.load(f)
        
    with open("files/Vmass_cat.json", "r") as f:   # Unpickling
        mass_catergories = json.load(f)
        
    ptbins = np.array([450, 500, 550, 600, 675, 800, 1200])
    npt = len(ptbins) - 1
    msdbins = np.linspace(40, 201, 24)
    msd = rl.Observable("msd", msdbins)

    # here we derive these all at once with 2D array
    ptpts, msdpts = np.meshgrid(ptbins[:-1] + 0.3 * np.diff(ptbins), msdbins[:-1] + 0.5 * np.diff(msdbins), indexing="ij")
    rhopts = 2 * np.log(msdpts / ptpts)
    ptscaled = (ptpts - 450.0) / (1200.0 - 450.0)
    rhoscaled = (rhopts - (-6)) / ((-2.1) - (-6))
    validbins = (rhoscaled >= 0) & (rhoscaled <= 1)
    rhoscaled[~validbins] = 1  # we will mask these out later

    # Define the bins
    msdbins = np.linspace(40, 201, 24)
    msd = rl.Observable('msd', msdbins)

    validbins = {}
    
    exp_systs = ['pileup_weight', 'JES','JER','UES', 'jet_trigger']

    # TT params: scale factor from the muon control region, allowed to float, not signal strength: nuisance parameter. 
    tqqeffSF = rl.IndependentParameter('tqqeffSF_{}'.format(year), 1., 0, 2) 
    tqqnormSF = rl.IndependentParameter('tqqnormSF_{}'.format(year), 1., 0, 2) 

    #! SYSTEMATICS
    # Simple lumi systematics, changes event yields, onstraints applied to overall likelihood                                                                                                                                                        
    sys_lumi_uncor = rl.NuisanceParameter('CMS_lumi_13TeV_{}'.format(year), 'lnN') #lnN: Log Normal
    sys_lumi_cor_161718 = rl.NuisanceParameter('CMS_lumi_13TeV_correlated_', 'lnN')
    sys_lumi_cor_1718 = rl.NuisanceParameter('CMS_lumi_13TeV_correlated_20172018', 'lnN')
    
    # Lepton vetoes
    sys_eleveto = rl.NuisanceParameter('CMS_hbb_e_veto_{}'.format(year), 'lnN')                                    
    sys_muveto = rl.NuisanceParameter('CMS_hbb_mu_veto_{}'.format(year), 'lnN')  
    sys_tauveto = rl.NuisanceParameter('CMS_hbb_tau_veto_{}'.format(year), 'lnN')

    sys_dict = {}
    yearstr = year
    if 'APV' in year:
        yearstr = '2016preVFP'
    elif year == '2016':
        yearstr = '2016postVFP'
    
    # Muon control region only
    sys_dict['muon_ID_{}_value'.format(yearstr)] = rl.NuisanceParameter('CMS_mu_id_{}'.format(year), 'lnN')
    sys_dict['muon_ISO_{}_value'.format(yearstr)] = rl.NuisanceParameter('CMS_mu_iso_{}'.format(year), 'lnN')
    sys_dict['muon_TRIGNOISO_{}_value'.format(yearstr)] = rl.NuisanceParameter('CMS_hbb_mu_trigger_{}'.format(year), 'lnN')

    #All experimental systematics
    sys_dict['JES'] = rl.NuisanceParameter('CMS_scale_j_{}'.format(year), 'lnN')
    sys_dict['JER'] = rl.NuisanceParameter('CMS_res_j_{}'.format(year), 'lnN')
    sys_dict['UES'] = rl.NuisanceParameter('CMS_ues_j_{}'.format(year), 'lnN')
    sys_dict['jet_trigger'] = rl.NuisanceParameter('CMS_hbb_jet_trigger_{}'.format(year), 'lnN')
    sys_dict['pileup_weight'] = rl.NuisanceParameter('CMS_hbb_PU_{}'.format(year), 'lnN')

    #Pre firing for 2018
    if '2018' not in year: exp_systs += ['L1Prefiring']
    sys_dict['L1Prefiring'] = rl.NuisanceParameter('CMS_L1Prefiring_{}'.format(year),'lnN')
    
    #No jet trigger in muon control region systematics
    mu_exp_systs = [x for x in exp_systs if x is not 'jet_trigger']
    mu_exp_systs += ['muon_ID_{}_value'.format(yearstr), 'muon_ISO_{}_value'.format(yearstr), 'muon_TRIGNOISO_{}_value'.format(yearstr)]
    
    print("Experimental systematics: ",  exp_systs) 
    print("Muon CR systematics: ", mu_exp_systs)
    
    #Particle Net BB systematics
    #TODO: Put the scale factor and uncertainty into a json file and read it afterwards
    sys_ParticleNetEffBB = rl.NuisanceParameter('CMS_eff_bb_{}'.format(year), 'lnN')
    
    #n2 uncertainty, derived
    sys_veff = rl.NuisanceParameter('CMS_hbb_veff_{}'.format(year), 'lnN')
    
    #All derived from muon control region, shape systematics in all the masses.
    sys_smear = rl.NuisanceParameter('CMS_hbb_smear_{}'.format(year), 'shape')
    sys_scale = rl.NuisanceParameter('CMS_hbb_scale_{}'.format(year), 'shape')
    
    #lnN up and down, shape varies the shape
    
    # Theory systematics are correlated across years
    # V + jets, not year in name and correlated accross year
    for sys in ['d1kappa_EW', 'Z_d2kappa_EW', 'Z_d3kappa_EW', 'W_d2kappa_EW', 'W_d3kappa_EW', 'd1K_NLO', 'd2K_NLO', 'd3K_NLO']:
        sys_dict[sys] = rl.NuisanceParameter('CMS_hbb_{}'.format(sys), 'lnN')
        
    Zjets_thsysts = ['d1kappa_EW', 'Z_d2kappa_EW', 'Z_d3kappa_EW', 'd1K_NLO', 'd2K_NLO']
    Wjets_thsysts = ['d1kappa_EW', 'W_d2kappa_EW', 'W_d3kappa_EW', 'd1K_NLO', 'd2K_NLO', 'd3K_NLO']
    
    #TODO: Likely add VV for these theory systematics
    pdf_Higgs_ggF = rl.NuisanceParameter('pdf_Higgs_ggF','lnN')
    pdf_Higgs_VBF = rl.NuisanceParameter('pdf_Higgs_VBF','lnN')
    pdf_Higgs_VH  = rl.NuisanceParameter('pdf_Higgs_VH','lnN')
    pdf_Higgs_ttH = rl.NuisanceParameter('pdf_Higgs_ttH','lnN')

    scale_ggF = rl.NuisanceParameter('QCDscale_ggF', 'lnN')
    scale_VBF = rl.NuisanceParameter('QCDscale_VBF', 'lnN')
    scale_VH = rl.NuisanceParameter('QCDscale_VH', 'lnN')
    scale_ttH = rl.NuisanceParameter('QCDscale_ttH', 'lnN')

    isr_ggF = rl.NuisanceParameter('UEPS_ISR_ggF', 'lnN')
    isr_VBF = rl.NuisanceParameter('UEPS_ISR_VBF', 'lnN')
    isr_VH = rl.NuisanceParameter('UEPS_ISR_VH', 'lnN')
    isr_ttH = rl.NuisanceParameter('UEPS_ISR_ttH', 'lnN')

    fsr_ggF = rl.NuisanceParameter('UEPS_FSR_ggF', 'lnN')
    fsr_VBF = rl.NuisanceParameter('UEPS_FSR_VBF', 'lnN')
    fsr_VH = rl.NuisanceParameter('UEPS_FSR_VH', 'lnN')
    fsr_ttH = rl.NuisanceParameter('UEPS_FSR_ttH', 'lnN')
    
    
    
    return

   
    with open(os.path.join(str(tmpdir), 'testModel_'+year+'.pkl'), 'wb') as fout:
        pickle.dump(model, fout)

    model.renderCombine(os.path.join(str(tmpdir), 'testModel_'+year))


def main():

    #Setting different years depending on 
    if len(sys.argv) < 2:
        print("Enter year")
        return

    global year
    year = sys.argv[1]

    print("Running for " + year)

    outdir = '{}/output'.format(year)
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    vh_rhalphabet(outdir)

if __name__ == '__main__':

    year = ""

    main()