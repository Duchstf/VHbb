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

    #Variables to divide the phase space
    VmassBins = [40.0, 68.0, 110.0, 201.0]
    nVmass = len(VmassBins) - 1

    msdbins = np.linspace(40, 201, 24)
    msd = rl.Observable("msd", msdbins)

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

    #Dummy parameter for signal
    #Just a quick hack so that combine produces prefit
    dumb = rl.NuisanceParameter('LOL', 'lnN')

    qcdpass, qcdfail = 0.0, 0.0
    for iBin in range(nVmass):
        Vmass_bin = 'Vmass_{}'.format(iBin)
        
        failCh = rl.Channel("VBin%d%s%s" % (iBin, "fail", year)) #Naming convention prevents using "_"
        passCh = rl.Channel("VBin%d%s%s" % (iBin, "pass", year))
        
        failTempl = get_template(sName='QCD', bb_pass=0, V_bin=Vmass_bin, obs=msd, syst='nominal')
        passTempl = get_template(sName='QCD', bb_pass=1, V_bin=Vmass_bin, obs=msd, syst='nominal')
        
        failCh.setObservation(failTempl, read_sumw2=True)
        passCh.setObservation(passTempl, read_sumw2=True)
        
        qcdfail += sum([val for val in failCh.getObservation()[0]])
        qcdpass += sum([val for val in passCh.getObservation()[0]])
            
        
    qcdeff = qcdpass / qcdfail
    print('Inclusive P/F from Monte Carlo: ', str(qcdeff))

    #Define the TF Data (the data is true passing QCD in this case)                                                         
    with open('initial_vals.json') as f: initial_vals = np.asarray(json.load(f)['initial_vals'])
    print("Poly Shape: ", (initial_vals.shape[0]-1, initial_vals.shape[1]-1))
    tf_dataResidual = rl.BasisPoly("tf_dataResidual_{}".format(year),
                                    (initial_vals.shape[0]-1, initial_vals.shape[1]-1), #shape 
                                    ['pt', 'rho'],
                                    basis='Bernstein',
                                    init_params=initial_vals,
                                    limits=(0,20),
                                    coefficient_transform=None)
    tf_dataResidual_params = tf_dataResidual(ptscaled, rhoscaled)

    tf_params = qcdeff * tf_dataResidual_params

    # Build actual fit model which would go into the workspace.
    model = rl.Model('testModel_{}'.format(year))
    
    #COMBINE INSISTS THAT YOU HAVE A SIGNAL PROCESS, BUT IT WILL FIT TO 0, INJECT SIGNAL SUMMY
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
                sample.autoMCStats(lnN=True) 
                sample.setParamEffect(dumb, 1.001)
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