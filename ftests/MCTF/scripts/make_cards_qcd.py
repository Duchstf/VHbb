from __future__ import print_function, division
import sys, os
import json
import numpy as np
import pickle
import ROOT

import rhalphalib as rl
from rhalphalib import AffineMorphTemplate, MorphHistW2

rl.util.install_roofit_helpers()

# Read the histogram
def get_template(sName, bb_pass, V_bin, obs, syst, muon=False):
    """
    Read msd template from root file
    """
    f = ROOT.TFile.Open('../signalregion.root')
    if muon: f = ROOT.TFile.Open('../muonCRregion.root')

    #Jet 1 ParticleNet bb pass/failing region
    name_bb = 'pass' if bb_pass else 'fail'
    name='{}_{}_{}_{}'.format(V_bin, name_bb, sName, syst)
    print("Extracting ... ", name)
    h = f.Get(name)

    sumw = []
    sumw2 = []
    
    for i in range(1, h.GetNbinsX()+1):
        sumw += [h.GetBinContent(i)]
        sumw2 += [h.GetBinError(i)*h.GetBinError(i)]

    return (np.array(sumw), obs.binning, obs.name, np.array(sumw2))

def vh_rhalphabet(tmpdir, year):
    """ 
    Create the data cards!

    - Set up the systematics variable.
    - Start setting up the fit.
    
    Then,
    1. Fit QCD TF in fail -> pass
    2. Fit Data/MC TF. 
    """

    VmassBins = [40.0, 68.0, 110.0, 201.0]
    print("Current mass bins: ", VmassBins)
    nVmass = len(VmassBins) - 1
    msdbins = np.linspace(40, 201, 24)
    msd = rl.Observable("msd", msdbins)

    # Run qcd fit for 5 times
    fitfailed_qcd = 0
    fitfailed_limit = 5 
    
    # QCD Transfer Factors are dependent on pt and rho
    ptbins = np.array([450, 1200])
    n_ptbins = ptbins.shape[0] - 1

    ptpts, msdpts = np.meshgrid(ptbins[:-1] + 0.3 * np.diff(ptbins), msdbins[:-1] + 0.5 * np.diff(msdbins), indexing="ij")
    rhopts = 2 * np.log(msdpts / ptpts)

    ptscaled = (ptpts - 450.0) / (1200.0 - 450.0)
    rhoscaled = (rhopts - (-6)) / ((-2.1) - (-6))

    validbins = (rhoscaled >= 0) & (rhoscaled <= 1)
    rhoscaled[~validbins] = 1
    validbins = validbins[0] #validbin is a 1D array of 23 bins

    while fitfailed_qcd < fitfailed_limit: #Fail if choose bad initial values, start from where the fits fail. 
   
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
        # {"initial_vals":[[1,1]]} in json file (1st pt and 1st in rho)                                                               
        print('Initial fit values read from file initial_vals*')
        with open('initial_vals.json') as f: initial_vals = np.array(json.load(f)['initial_vals'])
        print("Initial fit values: ", initial_vals)
        print("Poly Shape: ", (initial_vals.shape[0]-1,initial_vals.shape[1]-1))
        
        tf_MCtempl = rl.BasisPoly("tf_MCtempl_{}".format(year),
                                (initial_vals.shape[0]-1,initial_vals.shape[1]-1), #shape
                                ["pt", "rho"], #variable names
                                basis='Bernstein', #type of polys
                                init_params=initial_vals, #initial values
                                limits=(0, 10), #limits on poly coefficients
                                coefficient_transform=None)
        
        tf_MCtempl_params = qcdeff * tf_MCtempl(ptscaled, rhoscaled)
        
        for iBin in range(nVmass):
            failCh = qcdmodel["VBin%dfail%s" % (iBin, year)]
            passCh = qcdmodel["VBin%dpass%s" % (iBin, year)]
            
            failObs = failCh.getObservation()
            qcdparams = np.array([rl.IndependentParameter("qcdparam_VBin%d_HBin%d_%s" % (iBin, i, year), 0) for i in range(msd.nbins)])
            sigmascale = 10.0
            scaledparams = failObs * (1 + sigmascale / np.maximum(1.0, np.sqrt(failObs))) ** qcdparams
            
            fail_qcd = rl.ParametericSample("VBin%dfail%s_qcd" % (iBin, year), rl.Sample.BACKGROUND, msd, scaledparams[0])
            failCh.addSample(fail_qcd)
            pass_qcd = rl.TransferFactorSample("VBin%dpass%s_qcd" % (iBin, year), rl.Sample.BACKGROUND, tf_MCtempl_params[n_ptbins-1, :], fail_qcd)
            passCh.addSample(pass_qcd)

            failCh.mask = validbins
            passCh.mask = validbins

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
    tf_MCtempl_params_final = tf_MCtempl(ptscaled, rhoscaled)

    # Fitting ratio of the data and the MC prediction
    tf_dataResidual = rl.BasisPoly("tf_dataResidual_{}".format(year),
                                    (0,0), 
                                    ['pt', 'rho'],
                                    basis='Bernstein',
                                    init_params=np.array([[1]]),
                                    limits=(0,20),
                                    coefficient_transform=None)

    tf_dataResidual_params = tf_dataResidual(ptscaled, rhoscaled)
    tf_params = qcdeff * tf_MCtempl_params_final * tf_dataResidual_params
    
    # Build actual fit model which would go into the workspace.
    model = rl.Model('testModel_{}'.format(year))
    
    #COMBINE INSISTS THAT YOU HAVE A SIGNAL PROCESS, BUT IT WILL FIT TO 0
    #DUMMY FOR NOW
    samps = ['WH'] 
    sigs = ['WH']
    
    for iBin in range(nVmass):
        Vmass_bin = 'Vmass_{}'.format(iBin)
        
        for bb_region in ['pass', 'fail']: #Separate also by b scores in addition to charm scores.

            print('Vmass Bin: {}, BB region: {}'.format(iBin, bb_region))            
            ch = rl.Channel('VBin%d%s%s' % (iBin, bb_region, year))
            model.addChannel(ch)

            isPass = bb_region == 'pass'
            templates = {}
    
            for sName in samps:
                
                templates[sName] = get_template(sName=sName, bb_pass=isPass, V_bin=Vmass_bin, obs=msd, syst='nominal')
                templ = templates[sName] 
                
                # Doesn't matter since it's defined in combine
                if sName in sigs: stype = rl.Sample.SIGNAL
                else: stype = rl.Sample.BACKGROUND
            
                sample = rl.TemplateSample(ch.name + '_' + sName, stype, templ)
                ch.addSample(sample)

            #Observed data = QCD MC
            data_obs = get_template(sName='QCD', bb_pass=isPass, V_bin=Vmass_bin, obs=msd, syst='nominal')
            ch.setObservation(data_obs, read_sumw2=True)
    
    #Fill in the QCD in the actual fit model. 
    for iBin in range(nVmass):

            failCh = model['VBin%dfail%s' % (iBin, year)]
            passCh = model['VBin%dpass%s' % (iBin, year)]

            qcdparams = np.array([rl.IndependentParameter("qcdparam_VBin%d_HBin%d_%s" % (iBin, i, year), 0) for i in range(msd.nbins)])
            initial_qcd = failCh.getObservation()[0].astype(float)  # Was integer, and numpy complained about subtracting float from it

            if np.any(initial_qcd < 0.): raise ValueError('initial_qcd negative for some bins..', initial_qcd)

            sigmascale = 10  # to scale the deviation from initial                      
            scaledparams = initial_qcd * (1 + sigmascale/np.maximum(1., np.sqrt(initial_qcd)))**qcdparams
            
            fail_qcd = rl.ParametericSample("VBin%dfail%s_qcd" % (iBin, year), rl.Sample.BACKGROUND, msd, scaledparams)
            failCh.addSample(fail_qcd)
            pass_qcd = rl.TransferFactorSample("VBin%dpass%s_qcd" % (iBin, year), rl.Sample.BACKGROUND, tf_params[n_ptbins-1, :], fail_qcd)
            passCh.addSample(pass_qcd)
    
    with open(os.path.join(str(tmpdir), 'testModel_{}.pkl'.format(year)), 'wb') as fout: pickle.dump(model, fout)
    model.renderCombine(os.path.join(str(tmpdir), 'testModel_{}'.format(year)))

if __name__ == '__main__':

    year = "2016"
    thisdir = os.getcwd()
    if "2016APV" in thisdir: year = "2016APV"
    elif "2017" in thisdir: year = "2017"
    elif "2018" in thisdir: year = "2018" 
    print("Running for ", year)

    if not os.path.exists('output'): os.mkdir('output')
    vh_rhalphabet('output', year)