import logging
import numpy as np
import awkward as ak
import json
import copy
from collections import defaultdict
from coffea import processor, hist
import hist as hist2
from coffea.analysis_tools import Weights, PackedSelection
from coffea.lumi_tools import LumiMask
from boostedhiggs.btag import BTagCorrector
from boostedhiggs.common import (
    getBosons,
    bosonFlavor,
)
from boostedhiggs.corrections import (
    corrected_msoftdrop,
    add_pileup_weight,
    add_HiggsEW_kFactors,
    add_VJets_kFactors,
    add_jetTriggerSF,
    add_muonSFs,
    jet_factory,
    fatjet_factory,
    add_jec_variables,
    met_factory,
    lumiMasks,
    get_VetoMap,
)

#Import the working points
from boostedhiggs.WPs import *

logger = logging.getLogger(__name__)

def update(events, collections):
    """Return a shallow copy of events array with some collections swapped out"""
    out = events
    for name, value in collections.items(): out = ak.with_field(out, value, name)
    return out

def ak4_jets(events, year):

    """
    Related dicussion on how to apply jet veto maps from here

    https://cms-talk.web.cern.ch/t/questions-about-jet-veto-maps-and-2018-hem/43448
    """

    jets = events.Jet

    #Loose jet selection as recommended here
    # https://cms-jerc.web.cern.ch/Recommendations/#jet-veto-maps

    jets_selection = ((jets.pt > 30.) & 
                      (abs(jets.eta) < 2.5) & 
                      (jets.isTight) & 
                      (jets.chEmEF + jets.neEmEF < 0.9) & 
                      ((jets.pt >= 50) | ((jets.pt < 50) & (jets.puId & 2) == 2)))
    
    jets = jets[jets_selection]

    #Apply jet veto maps
    jet_veto_map, _ = get_VetoMap(jets, year)
    jets = jets[jet_veto_map]

    return jets


class VHBB_MuonCR_Processor(processor.ProcessorABC):
    
    def __init__(self, year='2017', jet_arbitration='T_bvq', systematics=True):
        
        self._year = year
        self._jet_arbitration = jet_arbitration
        self._systematics = systematics
        self._btagSF = BTagCorrector('M', 'deepJet', year)

        #Open the trigger files
        with open('files/muon_triggers.json') as f: self._muontriggers = json.load(f)
        with open('files/triggers.json') as f: self._triggers = json.load(f)
        with open('files/metfilters.json') as f: self._met_filters = json.load(f) # https://twiki.cern.ch/twiki/bin/view/CMS/MissingETOptionalFiltersRun2
            
        #Scan thresholds for bb
        bb_bins = bb_WPs['{}_bb'.format(self._year)]
        
        #Create the histogram.
        self.make_output = lambda: {
            
            'sumw': processor.defaultdict_accumulator(float),
            'btagWeight': hist2.Hist(
                hist2.axis.Regular(50, 0, 3, name='val', label='BTag correction'),
                hist2.storage.Weight(),
            ),
            'h': hist.Hist(
                'Events',
                hist.Cat('dataset', 'Dataset'),
                hist.Cat('region', 'Region'),
                hist.Cat('systematic', 'Systematic'),
                hist.Bin('msd1', r'Jet 1 $m_{sd}$', 23, 40, 201),
                hist.Bin('bb1', r'Jet 1 Paticle Net B Score', bb_bins),
                hist.Bin('genflavor1', 'Gen. jet 1 flavor', [1, 2, 3, 4]), #1 light, 2 charm, 3 b, 4 upper edge. B falls into 3-4.
            )
        }

    def process(self, events):
        isRealData = not hasattr(events, "genWeight")
        isQCDMC = 'QCD' in events.metadata['dataset']

        if isRealData or isQCDMC: return self.process_shift(events, None) # Nominal JEC are already applied in data
        if np.sum(ak.num(events.FatJet, axis=1)) < 1: return self.process_shift(events, None)

        jec_cache = {}

        thekey = f"{self._year}mc"
        if self._year == "2016": thekey = "2016postVFPmc"
        elif self._year == "2016APV": thekey = "2016preVFPmc"

        fatjets = fatjet_factory[thekey].build(add_jec_variables(events.FatJet, events.fixedGridRhoFastjetAll), jec_cache)
        jets = jet_factory[thekey].build(add_jec_variables(events.Jet, events.fixedGridRhoFastjetAll), jec_cache)
        met = met_factory.build(events.MET, jets, {})

        shifts = [({"Jet": jets, "FatJet": fatjets, "MET": met}, None)]
        if self._systematics:
            shifts = [
                ({"Jet": jets, "FatJet": fatjets, "MET": met}, None),
                ({"Jet": jets.JES_jes.up, "FatJet": fatjets.JES_jes.up, "MET": met.JES_jes.up}, "JESUp"),
                ({"Jet": jets.JES_jes.down, "FatJet": fatjets.JES_jes.down, "MET": met.JES_jes.down}, "JESDown"),
                ({"Jet": jets, "FatJet": fatjets, "MET": met.MET_UnclusteredEnergy.up}, "UESUp"),
                ({"Jet": jets, "FatJet": fatjets, "MET": met.MET_UnclusteredEnergy.down}, "UESDown"),
                ({"Jet": jets.JER.up, "FatJet": fatjets.JER.up, "MET": met.JER.up}, "JERUp"),
                ({"Jet": jets.JER.down, "FatJet": fatjets.JER.down, "MET": met.JER.down}, "JERDown"),
            ]

        return processor.accumulate(self.process_shift(update(events, collections), name) for collections, name in shifts)

    def process_shift(self, events, shift_name):

        dataset = events.metadata['dataset']
        isRealData = not hasattr(events, "genWeight")
        isQCDMC = 'QCD' in dataset
        selection = PackedSelection()
        weights = Weights(len(events), storeIndividual=True)
        output = self.make_output()
        
        if shift_name is None and not isRealData: output['sumw'][dataset] = ak.sum(events.genWeight)
        if len(events) == 0: return output

        #Add muon triggers
        if isRealData: selection.add('lumimask', lumiMasks[self._year[:4]](events.run, events.luminosityBlock))
        else: selection.add('lumimask', np.ones(len(events), dtype='bool'))

        trigger = np.zeros(len(events), dtype='bool')
        for t in self._muontriggers[self._year]:
            if t in events.HLT.fields:
                trigger = trigger | events.HLT[t]
        selection.add('muontrigger', trigger)
        del trigger

        metfilter = np.ones(len(events), dtype='bool')
        for flag in self._met_filters[self._year]['data' if isRealData else 'mc']:
            metfilter &= np.array(events.Flag[flag])
        selection.add('metfilter', metfilter)
        del metfilter

        fatjets = events.FatJet
        fatjets['msdcorr'] = corrected_msoftdrop(fatjets, self._year)
        fatjets['qcdrho'] = 2 * np.log(fatjets.msdcorr / fatjets.pt)
        fatjets['msdcorr_full'] = fatjets['msdcorr']

        candidatejets = fatjets[ (fatjets.pt > 200) & (abs(fatjets.eta) < 2.5)  & fatjets.isTight]  # this is loose in sampleContainer
        candidatejets = candidatejets[:, :2]  # Only consider first two to match generators
        
        #Pick the candidate jet based on different arbitration
        if self._jet_arbitration == 'T_bvq':
            #Order the jets based on particle net scores
            leadingjets = candidatejets[:, 0:2]
            
            pnet_bvq = leadingjets.particleNetMD_Xbb / (leadingjets.particleNetMD_Xcc + leadingjets.particleNetMD_Xbb + leadingjets.particleNetMD_Xqq)                                                                                       
            indices = ak.argsort(pnet_bvq, axis=1, ascending = False) #Higher b score for the Higgs candidate (more b like)                                                            
            candidatejet = ak.firsts(leadingjets[indices[:, 0:1]]) # candidate jet is more b-like (higher BvC score)
            secondjet = ak.firsts(leadingjets[indices[:, 1:2]]) # second jet is more charm-like (larger BvC score) 
            
        else: raise RuntimeError("Unknown candidate jet arbitration")

        bb1 = candidatejet.particleNetMD_Xbb / (candidatejet.particleNetMD_Xbb + candidatejet.particleNetMD_QCD) #Exact B scores for Higgs candidate
        selection.add('bbpass', (bb1 >= bb_WPs['{}_bb'.format(self._year)][-2]))

        #!Add selections------------------>
        #There is a list at the end which specifies the selections being used  
        selection.add('jetid', candidatejet.isTight)

        # Selections for muon control region
        selection.add('minjetkinmu',
            (candidatejet.pt >= 450)
            & (candidatejet.pt < 1200)
            & (candidatejet.msdcorr >= 40.)
            & (candidatejet.msdcorr < 201.)
            & (abs(candidatejet.eta) < 2.5))

        #Count the number of ak4 jets that are away
        ak4_jets_events = ak4_jets(events, self._year)
                
        jets = ak4_jets_events[:, :4]
        dphi = abs(jets.delta_phi(candidatejet))
        ak4_away = jets[dphi > 0.8] 
        selection.add('ak4btagMedium08', ak.max(ak4_away.btagDeepFlavB, axis=1, mask_identity=False) > self._btagSF._btagwp)

        met = events.MET 
        selection.add('met', met.pt < 140.)

        #Lepton vetos
        goodmuon = ((events.Muon.pt > 10) & (abs(events.Muon.eta) < 2.4) & (events.Muon.pfRelIso04_all < 0.15) & events.Muon.looseId)
        nmuons = ak.sum(goodmuon, axis=1)
        leadingmuon = ak.firsts(events.Muon[goodmuon])

        goodelectron = ((events.Electron.pt > 10) & (abs(events.Electron.eta) < 2.5) & (events.Electron.cutBased >= events.Electron.LOOSE))
        nelectrons = ak.sum(goodelectron, axis=1)

        ntaus = ak.sum(
            (
                (events.Tau.pt > 20)
                & (abs(events.Tau.dz) < 0.2)
                & (abs(events.Tau.eta) < 2.3)
                & (events.Tau.decayMode >= 0)
                & (events.Tau.decayMode != 5)
                & (events.Tau.decayMode != 6)
                & (events.Tau.decayMode != 7)
                & (events.Tau.idDeepTau2017v2p1VSe >= 2)
                & (events.Tau.idDeepTau2017v2p1VSjet >= 16)
                & (events.Tau.idDeepTau2017v2p1VSmu >= 8)
            ),
            axis=1,
        )

        selection.add('noleptons', (nmuons == 0) & (nelectrons == 0) & (ntaus == 0))
        selection.add('onemuon', (nmuons == 1) & (nelectrons == 0) & (ntaus == 0))
        selection.add('muonkin', (leadingmuon.pt > 55.) & (abs(leadingmuon.eta) < 2.1))
        selection.add('muonDphiAK8', abs(leadingmuon.delta_phi(candidatejet)) > 2*np.pi/3)

        if isRealData: genflavor1 = ak.zeros_like(candidatejet.pt)
        else:
            weights.add('genweight', events.genWeight)

            add_pileup_weight(weights, events.Pileup.nPU, self._year)
            bosons = getBosons(events.GenPart)
            matchedBoson1 = candidatejet.nearest(bosons, axis=None, threshold=0.8)

            #Tight matching
            match_mask1 = (abs(candidatejet.pt - matchedBoson1.pt)/matchedBoson1.pt < 0.5) & (abs(candidatejet.msdcorr - matchedBoson1.mass)/matchedBoson1.mass < 0.3)
            selmatchedBoson1 = ak.mask(matchedBoson1, match_mask1)
            genflavor1 = bosonFlavor(selmatchedBoson1)

            genBosonPt = ak.fill_none(ak.firsts(bosons.pt), 0)

            add_VJets_kFactors(weights, events.GenPart, dataset)
            add_muonSFs(weights, leadingmuon, self._year, selection)

            if self._year in ("2016APV", "2016", "2017"): weights.add("L1Prefiring", events.L1PreFiringWeight.Nom, events.L1PreFiringWeight.Up, events.L1PreFiringWeight.Dn)
            logger.debug("Weight statistics: %r" % weights.weightStatistics)
        
        if shift_name is None:
            output['btagWeight'].fill(val=self._btagSF.addBtagWeight(ak4_away, weights))


        msd1_matched = candidatejet.msdcorr * (genflavor1 > 0) + candidatejet.msdcorr * (genflavor1 == 0)
        
        def normalize(val, cut):
            '''not actually normalizing, just fill in the values after cuts'''
            if cut is None: return ak.to_numpy(ak.fill_none(val, np.nan))
            else: return ak.to_numpy(ak.fill_none(val[cut], np.nan))
        
        #Start timer
        import time
        tic = time.time()
        #----------------

        if shift_name is None: systematics = [None] + list(weights.variations)
        else: systematics = [shift_name]

        #!LIST OF THE SELECTIONS APPLIED
        regions = { 'muoncontrol': ['muontrigger','lumimask','metfilter','minjetkinmu', 'jetid', 'onemuon', 'muonkin', 'ak4btagMedium08','muonDphiAK8']}
            
        def fill(region, systematic, wmod=None):
            
            #Get the selection from above
            selections = regions[region]
            cut = selection.all(*selections)
            
            #Using nomial systematic if none is defined
            sname = 'nominal' if systematic is None else systematic
            
            if wmod is None:
                if systematic in weights.variations:
                    weight = weights.weight(modifier=systematic)[cut]
                else:
                    weight = weights.weight()[cut]
            else:
                weight = weights.weight()[cut] * wmod[cut]

            #! FILL THE HISTOGRAM
            output['h'].fill(
                dataset=dataset,
                region=region,
                systematic=sname,
                msd1=normalize(msd1_matched, cut),
                bb1=normalize(bb1, cut),
                genflavor1=normalize(genflavor1, cut),
                weight=weight,
            )

        for region in regions:
            if self._systematics:
                for systematic in systematics:
                    if isRealData and systematic is not None:
                        continue
                    fill(region, systematic)
            else:
                fill(region, None)
                
        #End timer and report
        toc = time.time()
        output["filltime"] = toc - tic
        #-----------------------------
            
        return output

    def postprocess(self, accumulator): return accumulator
