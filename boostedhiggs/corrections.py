import numpy as np
import awkward as ak
import gzip
import pickle
import cloudpickle
import importlib.resources
import correctionlib
import os 

from coffea.lookup_tools.lookup_base import lookup_base
from coffea.lookup_tools.dense_lookup import dense_lookup
from coffea import lookup_tools
from coffea import util

with importlib.resources.path("boostedhiggs.data", "corrections.pkl.gz") as path:
    with gzip.open(path) as fin:
        compiled = pickle.load(fin)

def qcd_ddt_shift(pt, rho, year):
    # Define an inner function that works on individual pt and rho values

    smooth_ddtmap = np.load(f'boostedhiggs/data/ddtmap_{year}.npy')
    pt_edges = np.load("boostedhiggs/data/ddtmap_ptedges.npy")
    rho_edges = np.load("boostedhiggs/data/ddtmap_rhoedges.npy")

    def get_ddt_value_single(pt_val, rho_val):
        if not pt_val or not rho_val: return None

        # Clip pt and rho to the valid ranges of the edges
        pt_val = np.clip(pt_val, pt_edges[0], pt_edges[-1] - 1e-5)  # Clip within the pt bin edges
        rho_val = np.clip(rho_val, rho_edges[0], rho_edges[-1] - 1e-5)  # Clip within the rho bin edges

        # Find the pt bin index
        pt_bin = np.digitize([pt_val], pt_edges)[0] - 1
        rho_bin = np.digitize([rho_val], rho_edges)[0] - 1
        
        # Get the corresponding value from the smooth_ddtmap
        return smooth_ddtmap[pt_bin, rho_bin]
    
    # Apply the get_ddt_value_single function element-wise to pt and rho using ak.Array's map-like behavior
    ddt_values = ak.Array([get_ddt_value_single(p, r) for p, r in zip(pt, rho)])
    
    return ddt_values

# Msd correction for all years, 2016 used for both 2016, 2016 APV.
msdcorr = {}
for year in ["2016", "2017","2018"]:
    with importlib.resources.path("boostedhiggs.data", "msdcorr_{}.json".format(year)) as filename: msdcorr[year] = correctionlib.CorrectionSet.from_file(str(filename))

def corrected_msoftdrop(fatjets, year):
    msdraw = np.sqrt(
        np.maximum(
            0.0,
            (fatjets.subjets * (1 - fatjets.subjets.rawFactor)).sum().mass2,
        )
    )
    msoftdrop = fatjets.msoftdrop
    msdfjcorr = msdraw / (1 - fatjets.rawFactor)

    if year=='2016APV': year='2016'
    corr = msdcorr[year]["msdfjcorr"].evaluate(
        np.array(ak.flatten(msdfjcorr / fatjets.pt)),
        np.array(ak.flatten(np.log(fatjets.pt))),
        np.array(ak.flatten(fatjets.eta)),
    )

    corr = ak.unflatten(corr, ak.num(fatjets))
    corrected_mass = msdfjcorr * corr

    return corrected_mass

def powheg_to_nnlops(genpt):
    return compiled['powheg_to_nnlops'](genpt)

# All PDF weights and alpha_S weights
def add_pdf_weight(weights, pdf_weights):

    docstring = pdf_weights.__doc__

    nweights = len(weights.weight())
    nom = np.ones(nweights)

    for i in range(0,103):
        weights.add('PDF_weight_'+str(i), nom, pdf_weights[:,i])

# All 9 scale variations
def add_scalevar(weights, var_weights):

    docstring = var_weights.__doc__

    nweights = len(weights.weight())
    nom = np.ones(nweights)

    for i in range(0,9):
        weights.add('scalevar_'+str(i), nom, var_weights[:,i])

# Jennet adds PS weights
def add_ps_weight(weights,ps_weights):

    nweights = len(weights.weight())

    nom  = np.ones(nweights)

    up_isr   = np.ones(nweights)
    down_isr = np.ones(nweights)

    up_fsr   = np.ones(nweights)
    down_fsr = np.ones(nweights)

    if len(ps_weights[0]) == 4:
        up_isr = ps_weights[:,0]
        down_isr = ps_weights[:,2]

        up_fsr = ps_weights[:,1]
        down_fsr = ps_weights[:,3]
        
#        up = np.maximum.reduce([up_isr, up_fsr, down_isr, down_fsr])
#        down = np.minimum.reduce([up_isr, up_fsr, down_isr, down_fsr])

    elif len(ps_weights[0]) > 1:
        print("PS weight vector has length ", len(ps_weights[0]))

    weights.add('UEPS_ISR', nom, up_isr, down_isr)
    weights.add('UEPS_FSR', nom, up_fsr, down_fsr)


def add_pileup_weight(weights, nPU, year='2017'):
        weights.add(
            'pileup_weight',
            compiled[f'{year}_pileupweight'](nPU),
            compiled[f'{year}_pileupweight_puUp'](nPU),
            compiled[f'{year}_pileupweight_puDown'](nPU),
        )

with importlib.resources.path("boostedhiggs.data", "EWHiggsCorrections.json") as filename:
    hew_kfactors = correctionlib.CorrectionSet.from_file(str(filename))

def add_HiggsEW_kFactors(weights, genpart, dataset):
    """EW Higgs corrections"""
    def get_hpt():
        boson = ak.firsts(genpart[
            (genpart.pdgId == 25)
            & genpart.hasFlags(["fromHardProcess", "isLastCopy"])
        ])
        return np.array(ak.fill_none(boson.pt, 0.))

    if "VBF" in dataset:
        hpt = get_hpt()
        ewkcorr = hew_kfactors["VBF_EW"]
        ewknom = ewkcorr.evaluate(hpt)
        weights.add("VBF_EW", ewknom)

    if "WplusH" in dataset or "WminusH" in dataset or "ZH" in dataset:
        hpt = get_hpt()
        ewkcorr = hew_kfactors["VH_EW"]
        ewknom = ewkcorr.evaluate(hpt)
        weights.add("VH_EW", ewknom)

    if "ttH" in dataset:
        hpt = get_hpt()
        ewkcorr = hew_kfactors["ttH_EW"]
        ewknom = ewkcorr.evaluate(hpt)
        weights.add("ttH_EW", ewknom)

with importlib.resources.path("boostedhiggs.data", "ULvjets_corrections.json") as filename:
    vjets_kfactors = correctionlib.CorrectionSet.from_file(str(filename))

def add_VJets_kFactors(weights, genpart, dataset):
    """Revised version of add_VJets_NLOkFactor, for both NLO EW and ~NNLO QCD"""
    def get_vpt(check_offshell=False):
        """Only the leptonic samples have no resonance in the decay tree, and only
        when M is beyond the configured Breit-Wigner cutoff (usually 15*width)
        """
        boson = ak.firsts(genpart[
            ((genpart.pdgId == 23)|(abs(genpart.pdgId) == 24))
            & genpart.hasFlags(["fromHardProcess", "isLastCopy"])
        ])
        if check_offshell:
            offshell = genpart[
                genpart.hasFlags(["fromHardProcess", "isLastCopy"])
                & ak.is_none(boson)
                & (abs(genpart.pdgId) >= 11) & (abs(genpart.pdgId) <= 16)
            ].sum()
            return ak.where(ak.is_none(boson.pt), offshell.pt, boson.pt)
        return np.array(ak.fill_none(boson.pt, 0.))

    common_systs = [
        "d1K_NLO",
        "d2K_NLO",
        "d3K_NLO",
        "d1kappa_EW",
    ]
    zsysts = common_systs + [
        "Z_d2kappa_EW",
        "Z_d3kappa_EW",
    ]
    wsysts = common_systs + [
        "W_d2kappa_EW",
        "W_d3kappa_EW",
    ]

    def add_systs(systlist, qcdcorr, ewkcorr, vpt):
        ewknom = ewkcorr.evaluate("nominal", vpt)
        weights.add("vjets_nominal", qcdcorr * ewknom if qcdcorr is not None else ewknom)
        ones = np.ones_like(vpt)
        for syst in systlist:
            weights.add(syst, ones, ewkcorr.evaluate(syst + "_up", vpt) / ewknom, ewkcorr.evaluate(syst + "_down", vpt) / ewknom)

    if "ZJetsToQQ_HT" in dataset or "DYJetsToLL_M-50" in dataset:
        vpt = get_vpt()
        qcdcorr = vjets_kfactors["ULZ_MLMtoFXFX"].evaluate(vpt)
        ewkcorr = vjets_kfactors["Z_FixedOrderComponent"]
        add_systs(zsysts, qcdcorr, ewkcorr, vpt)
    elif "WJetsToQQ_HT" in dataset or "WJetsToLNu" in dataset:
        vpt = get_vpt()
        qcdcorr = vjets_kfactors["ULW_MLMtoFXFX"].evaluate(vpt)
        ewkcorr = vjets_kfactors["W_FixedOrderComponent"]
        add_systs(wsysts, qcdcorr, ewkcorr, vpt)


with importlib.resources.path("boostedhiggs.data", "fatjet_triggerSF.json") as filename:
    jet_triggerSF = correctionlib.CorrectionSet.from_file(str(filename))


def add_jetTriggerSF(weights, leadingjet, year, selection):
    def mask(w):
        return np.where(selection.all('noleptons'), w, 1.)

    # Same for 2016 and 2016APV
    if '2016' in year:
        year = '2016'

    jet_pt = np.array(ak.fill_none(leadingjet.pt, 0.))
    jet_msd = np.array(ak.fill_none(leadingjet.msoftdrop, 0.))  # note: uncorrected
    nom = mask(jet_triggerSF[f'fatjet_triggerSF{year}'].evaluate("nominal", jet_pt, jet_msd))
    up = mask(jet_triggerSF[f'fatjet_triggerSF{year}'].evaluate("stat_up", jet_pt, jet_msd))
    down = mask(jet_triggerSF[f'fatjet_triggerSF{year}'].evaluate("stat_dn", jet_pt, jet_msd))
    weights.add('jet_trigger', nom, up, down)

with importlib.resources.path("boostedhiggs.data", "jec_compiled.pkl.gz") as path:
    with gzip.open(path) as fin:
        jmestuff = cloudpickle.load(fin)

jet_factory = jmestuff["jet_factory"]
fatjet_factory = jmestuff["fatjet_factory"]
met_factory = jmestuff["met_factory"]

def add_jec_variables(jets, event_rho):
    jets["pt_raw"] = (1 - jets.rawFactor)*jets.pt
    jets["mass_raw"] = (1 - jets.rawFactor)*jets.mass
    jets["pt_gen"] = ak.values_astype(ak.fill_none(jets.matched_gen.pt, 0), np.float32)
    jets["event_rho"] = ak.broadcast_arrays(event_rho, jets.pt)[0]
    return jets


def build_lumimask(filename):
    from coffea.lumi_tools import LumiMask
    with importlib.resources.path("boostedhiggs.data", filename) as path:
        return LumiMask(path)


lumiMasks = {
    "2016": build_lumimask("Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt"),
    "2017": build_lumimask("Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt"),
    "2018": build_lumimask("Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt"),
}

basedir = 'boostedhiggs/data/'
mutriglist = {
    '2016preVFP':{
        'TRIGNOISO':'NUM_Mu50_or_TkMu50_DEN_CutBasedIdGlobalHighPt_and_TkIsoLoose_abseta_pt',
    },
    '2016postVFP':{
        'TRIGNOISO':'NUM_Mu50_or_TkMu50_DEN_CutBasedIdGlobalHighPt_and_TkIsoLoose_abseta_pt',
    },
    '2017':{
        'TRIGNOISO':'NUM_Mu50_or_OldMu100_or_TkMu100_DEN_CutBasedIdGlobalHighPt_and_TkIsoLoose_abseta_pt',
    },
    '2018':{
        'TRIGNOISO':'NUM_Mu50_or_OldMu100_or_TkMu100_DEN_CutBasedIdGlobalHighPt_and_TkIsoLoose_abseta_pt',
    },
}

ext = lookup_tools.extractor()
for year in ['2016preVFP','2016postVFP','2017','2018']:
    ext.add_weight_sets([f'muon_ID_{year}_value NUM_MediumPromptID_DEN_TrackerMuons_abseta_pt {basedir}Efficiencies_muon_generalTracks_Z_Run{year}_UL_ID.root'])
    ext.add_weight_sets([f'muon_ID_{year}_error NUM_MediumPromptID_DEN_TrackerMuons_abseta_pt_error {basedir}Efficiencies_muon_generalTracks_Z_Run{year}_UL_ID.root'])

    ext.add_weight_sets([f'muon_ISO_{year}_value NUM_LooseRelIso_DEN_MediumPromptID_abseta_pt {basedir}Efficiencies_muon_generalTracks_Z_Run{year}_UL_ISO.root'])
    ext.add_weight_sets([f'muon_ISO_{year}_error NUM_LooseRelIso_DEN_MediumPromptID_abseta_pt_error {basedir}Efficiencies_muon_generalTracks_Z_Run{year}_UL_ISO.root'])

    for trigopt in mutriglist[year]:
        trigname = mutriglist[year][trigopt]
        ext.add_weight_sets([f'muon_{trigopt}_{year}_value {trigname} {basedir}Efficiencies_muon_generalTracks_Z_Run{year}_UL_SingleMuonTriggers.root'])
        ext.add_weight_sets([f'muon_{trigopt}_{year}_error {trigname}_error {basedir}Efficiencies_muon_generalTracks_Z_Run{year}_UL_SingleMuonTriggers.root'])
ext.finalize()
lepsf_evaluator = ext.make_evaluator()
lepsf_keys = lepsf_evaluator.keys()

def add_muonSFs(weights, leadingmuon, year, selection):
    def mask(w):
        return np.where(selection.all('onemuon'), w, 1.)

    yeartag = year
    if year == '2016':
        yeartag = '2016postVFP'
    elif year == '2016APV':
        yeartag = '2016preVFP'

    for sf in lepsf_keys:

        if yeartag not in sf:
            continue
        if 'muon' not in sf:
            continue

        lep_pt = np.array(ak.fill_none(leadingmuon.pt, 0.))
        lep_eta = np.array(ak.fill_none(leadingmuon.eta, 0.))

        if 'value' in sf:
            nom = mask(lepsf_evaluator[sf](np.abs(lep_eta),lep_pt))
            shift = mask(lepsf_evaluator[sf.replace('_value','_error')](np.abs(lep_eta),lep_pt))

            weights.add(sf, nom, shift, shift=True)


def get_VetoMap(jets, year: str):
    """
    Jet Veto Maps recommendation from JERC.

    All JERC analysers and anybody doing precision measurements with jets should use the strictest veto maps.
    Recommended for analyses strongly relying on events with large MET.

    Recommendation link: https://cms-jerc.web.cern.ch/Recommendations/#run-3_2

    Get event selection that rejects events with jets in the veto map. 
    """

    #Jet veto maps are synced daily here
    era_tags = {
        "2016APV": "2016preVFP_UL",
        "2016"   : "2016postVFP_UL",
        "2017"   : "2017_UL",
        "2018"   : "2018_UL"
    }
    era_tag = era_tags[year]

    fname = f'/cvmfs/cms.cern.ch/rsync/cms-nanoAOD/jsonpog-integration/POG/JME/{era_tag}/jetvetomaps.json.gz'

    # correctionlib doesn't support awkward arrays, so we have to flatten them out
    j, nj = ak.flatten(jets), ak.num(jets)
    j_phi = np.clip(np.array(j.phi), -3.1415, 3.1415)
    j_eta = np.clip(np.array(j.eta), -4.7, 4.7)

    # load the correction set
    evaluator = correctionlib.CorrectionSet.from_file(fname)

    # apply the correction and recreate the awkward array shape
    hname = {
        "2016APV": "Summer19UL16_V1",
        "2016"   : "Summer19UL16_V1",
        "2017"   : "Summer19UL17_V1",
        "2018"   : "Summer19UL18_V1"
    }

    weight = evaluator[hname[year]].evaluate('jetvetomap', j_eta, j_phi)
    weight_ak = ak.unflatten(
        np.array(weight),
        counts=nj
    )

    # any non-zero weight means the jet is vetoed
    jetmask = (weight_ak == 0)

    # events are selected only if they have no jets in the vetoed region
    eventmask = ak.sum(weight_ak, axis=-1) == 0

    return jetmask, eventmask
