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


logger = logging.getLogger(__name__)

class DDT(processor.ProcessorABC):
    
    def __init__(self, year='2017', jet_arbitration='T_bvc'):
        
        self._year = year
        self._jet_arbitration = jet_arbitration

        #Open the trigger files
        with open('files/muon_triggers.json') as f: self._muontriggers = json.load(f)
        with open('files/triggers.json') as f: self._triggers = json.load(f)

        # https://twiki.cern.ch/twiki/bin/view/CMS/MissingETOptionalFiltersRun2
        with open('files/metfilters.json') as f: self._met_filters = json.load(f)
        
        #Create the histogram.
        self.make_output = lambda: { 'sumw': processor.defaultdict_accumulator(float),
                                    
                                    #Might be adding a systematic
                                    'btagWeight': hist2.Hist(
                                        hist2.axis.Regular(50, 0, 3, name='val', label='BTag correction'),
                                        hist2.storage.Weight(),
                                    ),
            
                                    'h': hist.Hist(
                                        'Events',
                                        hist.Cat('dataset', 'Dataset'),
                                        hist.Cat('region', 'Region'),
                                        hist.Bin('rho', r"$\rho=ln(m^2_{reg}/p_T^2)$", 100, -7, -1.),
                                        hist.Bin('pt', r"$p_T$ (GeV)", 100, 200, 1350),
                                        hist.Bin('qcd', r"$p_T$ (GeV)", 500, 0, 1.),
                                    )}

    def process(self, events): return self.process_shift(events)

    def process_shift(self, events):
        
        dataset = events.metadata['dataset']
        #Always run ddt on QCD
        assert 'QCD' in dataset
        
        selection = PackedSelection()
        weights = Weights(len(events), storeIndividual=True)
        output = self.make_output()
        
        output['sumw'][dataset] = ak.sum(events.genWeight)
        if len(events) == 0: return output

        #Add triggers (MC only)
        selection.add('trigger', np.ones(len(events), dtype='bool'))
        selection.add('lumimask', np.ones(len(events), dtype='bool'))
        selection.add('muontrigger', np.ones(len(events), dtype='bool'))

        #Met filter
        metfilter = np.ones(len(events), dtype='bool')
        for flag in self._met_filters[self._year]['mc']: metfilter &= np.array(events.Flag[flag])
        selection.add('metfilter', metfilter)
        del metfilter

        fatjets = events.FatJet
        fatjets['msdcorr'] = corrected_msoftdrop(fatjets)
        fatjets['qcdrho'] = 2 * np.log(fatjets.msdcorr / fatjets.pt)

        candidatejets = fatjets[ (fatjets.pt > 200) & (abs(fatjets.eta) < 2.5) & fatjets.isTight] # this is loose in sampleContainer

        # Only consider first two to match generators
        leadingjets = candidatejets[:, :2]  
        
        #Pick the candidate jet based on different arbitration
        if self._jet_arbitration == 'pt': candidatejet = ak.firsts(candidatejet)
        elif self._jet_arbitration == 'mass': candidatejet = ak.firsts(candidatejet[ak.argmax(candidatejet.msdcorr, axis=1, keepdims=True)])
        elif self._jet_arbitration == 'T_bvc':
            
            pnet_bvc = leadingjets.particleNetMD_Xbb / (leadingjets.particleNetMD_Xcc + leadingjets.particleNetMD_Xbb)
            
            #Higher b score for the Higgs candidate (more b like)                                                                                                                           
            indices = ak.argsort(pnet_bvc, axis=1, ascending = False) 

            # candidate jet is more b-like (higher BvC score)                                                                                                           
            candidatejet = ak.firsts(leadingjets[indices[:, 0:1]])
            
            # second jet is more charm-like (larger BvC score)                                                                                                           
            secondjet = ak.firsts(leadingjets[indices[:, 1:2]])
            
        else:
            raise RuntimeError("Unknown candidate jet arbitration")

        
        #Exact qcd for Higgs candidate
        qcd1 = candidatejet.particleNetMD_QCD
        
        #There is a list at the end which specifies the selections being used     
        selection.add('jetacceptance', (candidatejet.msdcorr >= 40.) & (candidatejet.msdcorr < 201.) & (candidatejet.pt < 1350))
        selection.add('jetid', candidatejet.isTight)

        met = events.MET
        selection.add('met', met.pt < 140.)

        goodmuon = ((events.Muon.pt > 10) & (abs(events.Muon.eta) < 2.4) & (events.Muon.pfRelIso04_all < 0.25) & events.Muon.looseId)
        nmuons = ak.sum(goodmuon, axis=1)
        leadingmuon = ak.firsts(events.Muon[goodmuon])

        goodelectron = ( (events.Electron.pt > 10) & (abs(events.Electron.eta) < 2.5) & (events.Electron.cutBased >= events.Electron.LOOSE))
        nelectrons = ak.sum(goodelectron, axis=1)

        ntaus = ak.sum(((events.Tau.pt > 20)
                        & (abs(events.Tau.eta) < 2.3) & (events.Tau.rawIso < 5)
                        & (events.Tau.idDeepTau2017v2p1VSjet)
                        & ak.all(events.Tau.metric_table(events.Muon[goodmuon]) > 0.4, axis=2)
                        & ak.all(events.Tau.metric_table(events.Electron[goodelectron]) > 0.4, axis=2)),
                       axis=1)

        selection.add('noleptons', (nmuons == 0) & (nelectrons == 0) & (ntaus == 0))
        selection.add('onemuon', (nmuons == 1) & (nelectrons == 0) & (ntaus == 0))
        selection.add('muonkin', (leadingmuon.pt > 55.) & (abs(leadingmuon.eta) < 2.1))
        selection.add('muonDphiAK8', abs(leadingmuon.delta_phi(candidatejet)) > 2*np.pi/3)
        
        #Add weights
        weights.add('genweight', events.genWeight)

        add_pileup_weight(weights, events.Pileup.nPU, self._year)
        bosons = getBosons(events.GenPart)
        matchedBoson1 = candidatejet.nearest(bosons, axis=None, threshold=0.8)
        matchedBoson2 = secondjet.nearest(bosons, axis=None, threshold=0.8)

        genflavor1 = bosonFlavor(matchedBoson1)
        genflavor2 = bosonFlavor(matchedBoson2)

        add_VJets_kFactors(weights, events.GenPart, dataset)
        add_jetTriggerSF(weights, ak.firsts(fatjets), self._year, selection)
        add_muonSFs(weights, leadingmuon, self._year, selection)

        if self._year in ("2016APV", "2016", "2017"): weights.add("L1Prefiring", events.L1PreFiringWeight.Nom, events.L1PreFiringWeight.Up, events.L1PreFiringWeight.Dn)
        logger.debug("Weight statistics: %r" % weights.weightStatistics)

        msd1_matched = candidatejet.msdcorr * (genflavor1 > 0) + candidatejet.msdcorr * (genflavor1 == 0)
        msd2_matched = secondjet.msdcorr * (genflavor2 > 0) + secondjet.msdcorr * (genflavor2 == 0)
        
        def normalize(val, cut):
            '''not actually normalizing, just fill in the values after cuts'''
            if cut is None: return ak.to_numpy(ak.fill_none(val, np.nan))
            else: return ak.to_numpy(ak.fill_none(val[cut], np.nan))
        
        #Start timer
        import time
        tic = time.time()
        #----------------
            
        #!LIST OF THE SELECTIONS APPLIED
        regions = { 'signal': ['trigger', 'lumimask', 'metfilter', 'jetid', 'jetacceptance', 'met', 'noleptons']}

        def fill(region, systematic, wmod=None):
            
            #Get the selection from above
            selections = regions[region]
            cut = selection.all(*selections)
            
            if wmod is None:
                if systematic in weights.variations: weight = weights.weight(modifier=systematic)[cut]
                else: weight = weights.weight()[cut]
            else: weight = weights.weight()[cut] * wmod[cut]

            #! FILL THE HISTOGRAM
            output['h'].fill(dataset=dataset, region=region,
                             rho=normalize(candidatejet.qcdrho, cut),
                             pt=normalize(candidatejet.pt, cut),
                             qcd=normalize(qcd1, cut),
                             weight=weight)

        #Fill histogram
        for region in regions: fill(region, None)
                
        #End timer and report
        toc = time.time()
        output["filltime"] = toc - tic
        #-----------------------------
            
        return output

    def postprocess(self, accumulator):
        return accumulator
