import logging
import numpy as np
import awkward as ak
import json
from coffea import processor, hist
import hist as hist2
from coffea.analysis_tools import Weights, PackedSelection
from boostedhiggs.btag import BTagCorrector
from boostedhiggs.common import (
    getBosons,
    bosonFlavor,
)
from boostedhiggs.corrections import (
    corrected_msoftdrop,
    add_pileup_weight,
    add_VJets_kFactors,
    add_jetTriggerSF,
    add_muonSFs,
)

#Import the working points
from boostedhiggs.WPs import *


logger = logging.getLogger(__name__)

def normalize(val, cut):
    '''not actually normalizing, just fill in the values after cuts'''
    if cut is None: return ak.to_numpy(ak.fill_none(val, np.nan))
    else: return ak.to_numpy(ak.fill_none(val[cut], np.nan))

class DDT(processor.ProcessorABC):
    
    def __init__(self, year='2017', jet_arbitration='T_bvq'):
        
        self._year = year
        self._jet_arbitration = jet_arbitration
        qcd_bins = [round(x,4) for x in list(np.linspace(0.,1.,500))]


        #Open the trigger files
        with open('files/muon_triggers.json') as f: self._muontriggers = json.load(f)
        with open('files/triggers.json') as f: self._triggers = json.load(f)

        # https://twiki.cern.ch/twiki/bin/view/CMS/MissingETOptionalFiltersRun2
        with open('files/metfilters.json') as f: self._met_filters = json.load(f)
        
        #Create the histogram.
        self.make_output = lambda: { 'sumw': processor.defaultdict_accumulator(float),
                                    
                                    'h': hist.Hist( 'Events',
                                        hist.Cat('dataset', 'Dataset'), hist.Cat('region', 'Region'),
                                        hist.Bin('rho', r"$\rho=ln(m^2_{reg}/p_T^2)$", 100, -7, -1.),
                                        hist.Bin('pt', r"$p_T$ (GeV)", 100, 200, 1350),
                                        hist.Bin('qcd', r"ParticleNet QCD score", qcd_bins),)}

    def process(self, events): return self.process_shift(events)

    def process_shift(self, events):
        
        dataset = events.metadata['dataset']
        assert 'QCD' in dataset #Always run ddt on QCD
        
        selection = PackedSelection()
        weights = Weights(len(events), storeIndividual=True)
        output = self.make_output()
        
        output['sumw'][dataset] = ak.sum(events.genWeight)
        if len(events) == 0: return output

        #Add triggers
        trigger = np.zeros(len(events), dtype='bool')
        for t in self._triggers[self._year]:
            if t in events.HLT.fields:
                trigger |= np.array(events.HLT[t])
        selection.add('trigger', trigger)
        del trigger

        #Add muon trigger
        trigger = np.zeros(len(events), dtype='bool')
        for t in self._muontriggers[self._year]:
            if t in events.HLT.fields:
                trigger = trigger | events.HLT[t]
        selection.add('muontrigger', trigger)
        del trigger

        # MET Filter
        metfilter = np.ones(len(events), dtype='bool')
        for flag in self._met_filters[self._year]['mc']: metfilter &= np.array(events.Flag[flag])
        selection.add('metfilter', metfilter)
        del metfilter

        #Fat Jet Processing
        fatjets = events.FatJet
        fatjets['msdcorr'] = corrected_msoftdrop(fatjets, self._year)
        fatjets['qcdrho'] = 2 * np.log(fatjets.msdcorr / fatjets.pt)

        candidatejets = fatjets[(fatjets.pt > 200) & (abs(fatjets.eta) < 2.5) & fatjets.isTight] # this is loose in sampleContainer

        # Only consider first two to match generators
        leadingjets = candidatejets[:, :2]  
        
        #Pick the candidate jet based on different arbitration
        if self._jet_arbitration == 'T_bvq':
            pnet_bvq = leadingjets.particleNetMD_Xbb / (leadingjets.particleNetMD_Xcc + leadingjets.particleNetMD_Xbb + leadingjets.particleNetMD_Xqq)                                                                                                    
            indices = ak.argsort(pnet_bvq, axis=1, ascending = False)  #Higher b score for the Higgs candidate (more b like)                                                                      
            candidatejet = ak.firsts(leadingjets[indices[:, 0:1]])  # candidate jet is more b-like (higher BvQ score)       
            secondjet = ak.firsts(leadingjets[indices[:, 1:2]])
                                                                 
        else: raise RuntimeError("Unknown candidate jet arbitration")

        #Exact qcd for V candidate
        qcd = secondjet.particleNetMD_QCD
        
        #There is a list at the end which specifies the selections being used     
        selection.add('met', events.MET.pt < 140.)

        #Lepton veto
        goodmuon = ((events.Muon.pt > 10) & (abs(events.Muon.eta) < 2.4) & (events.Muon.pfRelIso04_all < 0.25) & events.Muon.looseId)
        nmuons = ak.sum(goodmuon, axis=1)
        leadingmuon = ak.firsts(events.Muon[goodmuon])

        electrons_selection = ((events.Electron.pt > 10) & (abs(events.Electron.eta) < 2.5) & (events.Electron.cutBased >= events.Electron.LOOSE))
        goodelectrons = events.Electron[electrons_selection]
        nelectrons = ak.sum(electrons_selection, axis=1)

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
                
        #Add weights
        weights.add('genweight', events.genWeight)

        #Add different weights
        add_pileup_weight(weights, events.Pileup.nPU, self._year)
        add_VJets_kFactors(weights, events.GenPart, dataset)

        if self._year in ("2016APV", "2016", "2017"): weights.add("L1Prefiring", events.L1PreFiringWeight.Nom, events.L1PreFiringWeight.Up, events.L1PreFiringWeight.Dn)
        logger.debug("Weight statistics: %r" % weights.weightStatistics)
            
        #!LIST OF THE SELECTIONS APPLIED
        regions = { 'signal': ['metfilter', 'met', 'noleptons']}

        def fill(region, systematic, wmod=None):
            
            selections = regions[region]; cut = selection.all(*selections) #Get the selection from above
            
            if wmod is None:
                if systematic in weights.variations: weight = weights.weight(modifier=systematic)[cut]
                else: weight = weights.weight()[cut]
            else: weight = weights.weight()[cut] * wmod[cut]

            #! FILL THE HISTOGRAM
            output['h'].fill(dataset=dataset, region=region,
                             rho=normalize(secondjet.qcdrho, cut),
                             pt=normalize(secondjet.pt, cut),
                             qcd=normalize(secondjet.particleNetMD_QCD, cut),
                             weight=weight)

        #Fill histogram
        for region in regions: fill(region, None)
            
        return output

    def postprocess(self, accumulator): return accumulator
