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
def get_template(sName, bb_pass, V_bin, obs, syst, muon=False):
    """
    Read msd template from root file
    """

    f = ROOT.TFile.Open('{}/signalregion.root'.format(year))

    if muon:
        f = ROOT.TFile.Open('{}/muonCR.root'.format(year))

    #Jet 1 ParticleNet bb pass/failing region
    name_bb = 'pass' if bb_pass else 'fail'
    name='{}_{}_{}_{}'.format(V_bin, name_bb, sName, syst)
    print("Extracting ... ", name)
    h = f.Get(name)
    
    
    print(h)
    print(dir(h))

    sumw = []
    sumw2 = []
    
    for i in range(1, h.GetNbinsX()+1):
        sumw += [h.GetBinContent(i)]
        sumw2 += [h.GetBinError(i)*h.GetBinError(i)]

    return (np.array(sumw), obs.binning, obs.name, np.array(sumw2))

def vh_rhalphabet(tmpdir):
    """ 
    Create the data cards!

    - Set up the systematics variable.
    - Start setting up the fit.
    
    Then,
    1. Fit QCD TF in fail -> pass
    2. Fit Data/MC TF. 
    """
    
    #! SYSTEMATICS
    exp_systs = ['pileup_weight', 'JES','JER','UES', 'jet_trigger']

    # TT params: scale factor from the muon control region, allowed to float, not signal strength: nuisance parameter. 
    tqqeffSF = rl.IndependentParameter('tqqeffSF_{}'.format(year), 1., 0, 2) 
    tqqnormSF = rl.IndependentParameter('tqqnormSF_{}'.format(year), 1., 0, 2) 

    
    # Simple lumi systematics, changes event yields, onstraints applied to overall likelihood                                                                                                                                                        
    sys_lumi_uncor = rl.NuisanceParameter('CMS_lumi_13TeV_{}'.format(year), 'lnN') #lnN: Log Normal
    sys_lumi_cor_161718 = rl.NuisanceParameter('CMS_lumi_13TeV_correlated', 'lnN')
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
    mu_exp_systs = [x for x in exp_systs if x != 'jet_trigger']
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
    
    #Now start setting up the fit
    with open('files/lumi.json') as f:
        lumi = json.load(f)
    
    with open("files/samples.json", "r") as f:   # Unpickling
        samples = json.load(f)
        # samples += ['Zjetsbb', 'Wjetsbb']
        
    with open("files/Vmass.json", "r") as f:   # Unpickling
        VmassBins = np.asarray(json.load(f))
    
    print("Current mass bins: ", VmassBins)
    nVmass = len(VmassBins) - 1
    msdbins = np.linspace(40, 201, 24)
    msd = rl.Observable("msd", msdbins)

    # Run qcd fit for 5 times
    fitfailed_qcd = 0
    fitfailed_limit = 5 
    
    # Here we derive these all at once with 2D array
    Vmass_pts, Hmass_pts = np.meshgrid(VmassBins[:-1] + 0.5 * np.diff(VmassBins), msdbins[:-1] + 0.5 * np.diff(msdbins), indexing="ij")
    Vmass_scaled = (Vmass_pts - 40.0) / (201.0 - 40.0)
    Hmass_scaled = (Hmass_pts - 40.0) / (201.0 - 40.0)

    validbins = Hmass_scaled < 3000 #All True (3 by 23)
    
    while fitfailed_qcd < 5: #Fail if choose bad initial values, start from where the fits fail. 
   
        # Build qcd MC pass+fail model and fit to polynomial
        qcdmodel = rl.Model("qcdmodel")
        qcdpass, qcdfail = 0.0, 0.0
        for iBin in range(nVmass):
            Vmass_bin = 'Vmass_{}'.format(iBin)
            
            failCh = rl.Channel("VBin%d%s%s" % (iBin, "fail", year)) #Naming convention prevents using "_"
            passCh = rl.Channel("VBin%d%s%s" % (iBin, "pass", year)) #Naming convention prevents using "_" 
            qcdmodel.addChannel(failCh)
            qcdmodel.addChannel(passCh)
            
            failTempl = get_template(sName='QCD', bb_pass=0, V_bin=Vmass_bin, obs=msd, syst='nominal')
            passTempl = get_template(sName='QCD', bb_pass=1, V_bin=Vmass_bin, obs=msd, syst='nominal')
            
            failCh.setObservation(failTempl, read_sumw2=True)
            passCh.setObservation(passTempl, read_sumw2=True)
            
            qcdfail += sum([val for val in failCh.getObservation()[0]])
            qcdpass += sum([val for val in passCh.getObservation()[0]])
            
        
        qcdeff = qcdpass / qcdfail
        print('Inclusive P/F from Monte Carlo: ', str(qcdeff))
        
        # Initial values
        # {"initial_vals":[[1,1]]} in json file (1st Vmass and 1st in Hmass)                                                               
        print('Initial fit values read from file initial_vals*')
        with open('files/initial_vals.json') as f: initial_vals = np.array(json.load(f)['initial_vals'])
        print("Initial fit values: ", initial_vals)
        print("Poly Shape: ", (initial_vals.shape[0]-1,initial_vals.shape[1]-1))
        
        tf_MCtempl = rl.BasisPoly("tf_MCtempl_{}".format(year),
                                (initial_vals.shape[0]-1,initial_vals.shape[1]-1), #shape
                                ["Vmass", "Hmass"], #variable names
                                basis='Bernstein', #type of polys
                                init_params=initial_vals, #initial values
                                limits=(0, 10), #limits on poly coefficients
                                coefficient_transform=None)
        
        tf_MCtempl_params = qcdeff * tf_MCtempl(Vmass_scaled, Hmass_scaled)
        
        #TODO: What am I doing?
        for iBin in range(nVmass):
            
            #TODO: Get observation from qcd model built before?
            failCh = qcdmodel["VBin%dfail%s" % (iBin, year)]
            passCh = qcdmodel["VBin%dpass%s" % (iBin, year)]
            
            failObs = failCh.getObservation()
            
            #TODO: What is this for?
            qcdparams = np.array([rl.IndependentParameter("qcdparam_VBin%d_HBin%d_%s" % (iBin, i, year), 0) for i in range(msd.nbins)])
            sigmascale = 10.0
            scaledparams = failObs * (1 + sigmascale / np.maximum(1.0, np.sqrt(failObs))) ** qcdparams
            
            #TODO: what is scaleparams[0] here???????
            #TODO: Looking like a list of two of the same thing???
            # for i in range(len(scaledparams)):
            #     print("--------------------------------------------------------------")
            #     print(scaledparams[i])
            
            #TODO: What are ParametericSample and TransferFactorSample, what are they used for?
            fail_qcd = rl.ParametericSample("VBin%dfail%s_qcd" % (iBin, year), rl.Sample.BACKGROUND, msd, scaledparams[0])
            failCh.addSample(fail_qcd)
            pass_qcd = rl.TransferFactorSample("VBin%dpass%s_qcd" % (iBin, year), rl.Sample.BACKGROUND, tf_MCtempl_params[iBin, :], fail_qcd)
            passCh.addSample(pass_qcd)

            failCh.mask = validbins[iBin]
            passCh.mask = validbins[iBin]

        #Run the fit for qcd mc pass/fail
        qcdfit_ws = ROOT.RooWorkspace("qcdfit_ws")
        
        #TODO: WHAT IS HAPPENING HERE
        simpdf, obs = qcdmodel.renderRoofit(qcdfit_ws)
        qcdfit = simpdf.fitTo(obs,
                            ROOT.RooFit.Extended(True),
                            ROOT.RooFit.SumW2Error(True),
                            ROOT.RooFit.Strategy(2),
                            ROOT.RooFit.Save(),
                            ROOT.RooFit.Minimizer("Minuit2", "migrad"),
                            ROOT.RooFit.PrintLevel(-1),)

        #TODO: SAVE THE MODEL?
        qcdfit_ws.add(qcdfit)
        qcdfit_ws.writeToFile(os.path.join(str(tmpdir), 'testModel_qcdfit_{}.root'.format(year)))
        
        # Set parameters to fitted values
        # Check what the values and if the fit fails
        allparams = dict(zip(qcdfit.nameArray(), qcdfit.valueArray()))
        pvalues = []
        for i, p in enumerate(tf_MCtempl.parameters.reshape(-1)):
            p.value = allparams[p.name]
            pvalues += [p.value]
        
        if qcdfit.status() != 0:
            print('Could not fit qcd')
            fitfailed_qcd += 1

            new_values = np.array(pvalues).reshape(tf_MCtempl.parameters.shape)
            with open("files/initial_vals.json", "w") as outfile:
                json.dump({"initial_vals":new_values.tolist()},outfile)

        else:
            print("Fitted!!!")
            break
        
        if fitfailed_qcd >=5:
            raise RuntimeError('Could not fit qcd after 5 tries')
    

    #TODO: WHAT ARE THESE PARAMETERS?
    param_names = [p.name for p in tf_MCtempl.parameters.reshape(-1)]
    decoVector = rl.DecorrelatedNuisanceVector.fromRooFitResult(tf_MCtempl.name + "_deco", qcdfit, param_names)
    tf_MCtempl.parameters = decoVector.correlated_params.reshape(tf_MCtempl.parameters.shape)
    tf_MCtempl_params_final = tf_MCtempl(Vmass_scaled, Hmass_scaled)
    
    # Start fitting data to mc transfer factor                   
    with open('files/initial_vals_data.json') as f: initial_vals_data = np.array(json.load(f)['initial_vals'])
    
    print((initial_vals_data.shape[0]-1,initial_vals_data.shape[1]-1))

    # Fitting ratio of the data and the MC prediction
    tf_dataResidual = rl.BasisPoly("tf_dataResidual_{}".format(year),
                                    (initial_vals_data.shape[0]-1,initial_vals_data.shape[1]-1), 
                                    ['Vmass', 'Hmass'],
                                    basis='Bernstein',
                                    init_params=initial_vals_data,
                                    limits=(0,20),
                                    coefficient_transform=None)

    tf_dataResidual_params = tf_dataResidual(Vmass_scaled, Hmass_scaled)
    tf_params = qcdeff * tf_MCtempl_params_final * tf_dataResidual_params
    
    # Build actual fit model which would go into the workspace.
    model = rl.Model('testModel_{}'.format(year))
    
    #Exclude QCD from MC samples
    samps = [str(x) for x in samples if str(x) not in ['QCD','data']] 
    sigs = ['ZH','WH']
    
    # Fill actual fit model with the expected fit value for every process except for QCD
    # Model need to know the signal, and background
    # Different background have different uncertainties
    # Don't treat the QCD like everything else
    # Take the QCD expectation from previous fit.
    # Take expectation from MC
    for iBin in range(nVmass):
        Vmass_bin = 'Vmass_{}'.format(iBin)
        
        for bb_region in ['pass', 'fail']: #Separate also by b scores in addition to charm scores.

            print('Vmass Bin: {}, BB region: {}'.format(iBin, bb_region))

            #Could be used to blind the Higgs mass window
            mask = validbins[iBin]
            mask_pass = ~mask #For blinding the data in the passing region, using -t -1 for now
            
            failCh.mask = mask
            passCh.mask = mask_pass
            
            ch = rl.Channel('VBin%d%s%s' % (iBin, bb_region, year))
            model.addChannel(ch)

            isPass = bb_region == 'pass'
            templates = {}
    
            for sName in samps:
                
                templates[sName] = get_template(sName=sName, bb_pass=isPass, V_bin=Vmass_bin, obs=msd, syst='nominal')
                nominal = templates[sName][0]

                if(badtemp_ma(nominal)):
                    print("Sample {} is too small, skipping".format(sName))
                    continue

                # Expectations
                templ = templates[sName]
                
                # Doesn't matter since it's defined in combine
                if sName in sigs: stype = rl.Sample.SIGNAL
                else: stype = rl.Sample.BACKGROUND
            
                sample = rl.TemplateSample(ch.name + '_' + sName, stype, templ)

                # You need one systematic
                sample.setParamEffect(sys_lumi_uncor, lumi[year]['uncorrelated'])
                sample.setParamEffect(sys_lumi_cor_161718, lumi[year]['correlated'])
                sample.setParamEffect(sys_lumi_cor_1718, lumi[year]['correlated_20172018'])

                ch.addSample(sample)

            data_obs = get_template(sName='data', bb_pass=isPass, V_bin=Vmass_bin, obs=msd, syst='nominal')
            ch.setObservation(data_obs, read_sumw2=True)
    
    #Fill in the QCD in the actual fit model. 
    for iBin in range(nVmass):

            failCh = model['VBin%dfail%s' % (iBin, year)]
            passCh = model['VBin%dpass%s' % (iBin, year)]

            qcdparams = np.array([rl.IndependentParameter("qcdparam_VBin%d_HBin%d_%s" % (iBin, i, year), 0) for i in range(msd.nbins)])
            initial_qcd = failCh.getObservation()[0].astype(float)  # Was integer, and numpy complained about subtracting float from it

            # Subtract away from data all mc processes except for QCD
            for sample in failCh: initial_qcd -= sample.getExpectation(nominal=True)

            if np.any(initial_qcd < 0.): raise ValueError('initial_qcd negative for some bins..', initial_qcd)

            sigmascale = 10  # to scale the deviation from initial                      
            scaledparams = initial_qcd * (1 + sigmascale/np.maximum(1., np.sqrt(initial_qcd)))**qcdparams
            
            fail_qcd = rl.ParametericSample("VBin%dfail%s_qcd" % (iBin, year), rl.Sample.BACKGROUND, msd, scaledparams)
            failCh.addSample(fail_qcd)
            pass_qcd = rl.TransferFactorSample("VBin%dpass%s_qcd" % (iBin, year), rl.Sample.BACKGROUND, tf_params[iBin, :], fail_qcd)
            passCh.addSample(pass_qcd)

   
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