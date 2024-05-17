import logging
import numpy as np
import awkward as ak
import json

from coffea import processor, hist
from coffea.analysis_tools import Weights, PackedSelection
from boostedhiggs.common import (
    getBosons,
    bosonFlavor,
)
from boostedhiggs.corrections import (
    corrected_msoftdrop,
    n2ddt_shift,
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
)

#Import the working points
from boostedhiggs.WPs import *

logger = logging.getLogger(__name__)
def update(events, collections):
    """Return a shallow copy of events array with some collections swapped out"""
    out = events
    for name, value in collections.items():
        out = ak.with_field(out, value, name)
    return out

def ak4_jets(events, year):

    jets = events.Jet
    jets = jets[(jets.pt > 30.) & (abs(jets.eta) < 5.0) & jets.isTight & (jets.puId > 0)]
        
    # EE noise for 2017                                             
    if year == '2017':
        jets = jets[
            (jets.pt > 50)
            | (abs(jets.eta) < 2.65)
            | (abs(jets.eta) > 3.139)]
        
    return jets


class VhbbPNQCDScan(processor.ProcessorABC):
    
    def __init__(self, year='2017', jet_arbitration='T_bvq',
                 tightMatch=True, ewkHcorr=True, systematics=True):
        
        self._year = year
        self._ewkHcorr = ewkHcorr
        self._jet_arbitration = jet_arbitration
        self._tightMatch = tightMatch
        self._systematics = systematics

        #Open the trigger files
        with open('files/muon_triggers.json') as f: self._muontriggers = json.load(f)
        with open('files/triggers.json') as f: self._triggers = json.load(f)

        # https://twiki.cern.ch/twiki/bin/view/CMS/MissingETOptionalFiltersRun2
        with open('files/metfilters.json') as f: self._met_filters = json.load(f)
        
        #Scan thresholds for bb
        bb_bins = bb_WPs['{}_bb'.format(self._year)]
        qcd_bins = [round(x,4) for x in list(np.linspace(0.,1.,500))]
        
        #Create the histogram.
        self.make_output = lambda: {
            
            'sumw': processor.defaultdict_accumulator(float),
            
            'h': hist.Hist(
                'Events',
                hist.Cat('dataset', 'Dataset'),
                hist.Cat('region', 'Region'),
                hist.Cat('systematic', 'Systematic'),
                hist.Bin('msd1', r'Jet 1 $m_{sd}$', 23, 40, 201),
                hist.Bin('msd2', r'Jet 2 $m_{sd}$', [40., 68.,  75.,  82.,  89.,  96., 103., 110., 201.]),

                hist.Bin('bb1', r'Jet 1 Paticle Net B Score', bb_bins),
                hist.Bin('qcd2', r'Jet 2 Paticle Net QCD Score', qcd_bins),

                hist.Bin('genflavor1', 'Gen. jet 1 flavor', [1, 2, 3, 4]) #1 light, 2 charm, 3 b, 4 upper edge. B falls into 3-4.
            )
        }

    def process(self, events):
        isRealData = not hasattr(events, "genWeight")
        isQCDMC = 'QCD' in events.metadata['dataset']

        if isRealData or isQCDMC: return self.process_shift(events, None)  # Nominal JEC are already applied in data
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
        selection = PackedSelection()
        weights = Weights(len(events), storeIndividual=True)
        output = self.make_output()
        
        if shift_name is None and not isRealData: output['sumw'][dataset] = ak.sum(events.genWeight)
        if len(events) == 0: return output

        #Add triggers
        if isRealData:
            trigger = np.zeros(len(events), dtype='bool')
            for t in self._triggers[self._year]:
                if t in events.HLT.fields:
                    trigger |= np.array(events.HLT[t])
            selection.add('trigger', trigger)
            del trigger
        else:
            selection.add('trigger', np.ones(len(events), dtype='bool'))
        
        #Add lumimask
        if isRealData: selection.add('lumimask', lumiMasks[self._year[:4]](events.run, events.luminosityBlock))
        else: selection.add('lumimask', np.ones(len(events), dtype='bool'))

        #Add muon trigger
        if isRealData:
            trigger = np.zeros(len(events), dtype='bool')
            for t in self._muontriggers[self._year]:
                if t in events.HLT.fields:
                    trigger = trigger | events.HLT[t]
            selection.add('muontrigger', trigger)
            del trigger
        else:
            selection.add('muontrigger', np.ones(len(events), dtype='bool'))

        #Met filter
        metfilter = np.ones(len(events), dtype='bool')
        for flag in self._met_filters[self._year]['data' if isRealData else 'mc']:
            metfilter &= np.array(events.Flag[flag])
        selection.add('metfilter', metfilter)
        del metfilter

        #Fat jets processing
        fatjets = events.FatJet
        fatjets['msdcorr'] = corrected_msoftdrop(fatjets, self._year)
        fatjets['qcdrho'] = 2 * np.log(fatjets.msdcorr / fatjets.pt)
        fatjets['n2ddt'] = fatjets.n2b1 - n2ddt_shift(fatjets, year=self._year)
        fatjets['msdcorr_full'] = fatjets['msdcorr']

        candidatejets = fatjets[(fatjets.pt > 200) & (abs(fatjets.eta) < 2.5) & fatjets.isTight] # this is loose in sampleContainer
        
        #Pick the candidate jet based on different arbitration
        if self._jet_arbitration == 'T_bvq':
            #Order the jets based on particle net scores
            leadingjets = candidatejets[:, 0:2]
    
            pnet_bvq = leadingjets.particleNetMD_Xbb / (leadingjets.particleNetMD_Xcc + leadingjets.particleNetMD_Xbb + leadingjets.particleNetMD_Xqq)                                                                                 
            indices = ak.argsort(pnet_bvq, axis=1, ascending = False) #Higher b score for the Higgs candidate (more b like)               
            candidatejet = ak.firsts(leadingjets[indices[:, 0:1]])  # candidate jet is more b-like (higher BvC score)                                                              
            secondjet = ak.firsts(leadingjets[indices[:, 1:2]]) # second jet is more charm-like (larger BvC score) 
            
        else: raise RuntimeError("Unknown candidate jet arbitration")
        
        bb1 = candidatejet.particleNetMD_Xbb / (candidatejet.particleNetMD_Xbb + candidatejet.particleNetMD_QCD) #Exact B scores for Higgs candidate
        qcd2 = secondjet.particleNetMD_QCD #Exact C scores for V candidate
        
        #!Add selections------------------>
        #There is a list at the end which specifies the selections being used 
        selection.add('jet1kin', (abs(candidatejet.eta) < 2.5) & (candidatejet.pt >= 450))
        selection.add('jet2kin', (secondjet.pt >= 200) & (abs(secondjet.eta) < 2.5))

        selection.add('jetacceptance',
            (candidatejet.msdcorr >= 40.)
            & (candidatejet.pt < 1200)
            & (candidatejet.msdcorr < 201.)
            & (secondjet.msdcorr >= 40.)
            & (secondjet.pt < 1200)
            & (secondjet.msdcorr < 201.)
        )

        selection.add('jetid', candidatejet.isTight & secondjet.isTight)
        
        #Count the number of ak4 jets that are away
        ak4_jets_events = ak4_jets(events, self._year)
        n_ak4_jets = ak.count(ak4_jets_events.pt, axis=1)
        selection.add('njets', n_ak4_jets < 5.)

        met = events.MET
        selection.add('met', met.pt < 140.)

        goodmuon = (
            (events.Muon.pt > 10)
            & (abs(events.Muon.eta) < 2.4)
            & (events.Muon.pfRelIso04_all < 0.25)
            & events.Muon.looseId
        )
        nmuons = ak.sum(goodmuon, axis=1)
        leadingmuon = ak.firsts(events.Muon[goodmuon])

        goodelectron = (
            (events.Electron.pt > 10)
            & (abs(events.Electron.eta) < 2.5)
            & (events.Electron.cutBased >= events.Electron.LOOSE)
        )
        nelectrons = ak.sum(goodelectron, axis=1)

        ntaus = ak.sum(
            (
                (events.Tau.pt > 20)
                & (abs(events.Tau.eta) < 2.3)
                & (events.Tau.rawIso < 5)
                & (events.Tau.idDeepTau2017v2p1VSjet)
                & ak.all(events.Tau.metric_table(events.Muon[goodmuon]) > 0.4, axis=2)
                & ak.all(events.Tau.metric_table(events.Electron[goodelectron]) > 0.4, axis=2)
            ),
            axis=1,
        )

        selection.add('noleptons', (nmuons == 0) & (nelectrons == 0) & (ntaus == 0))
        selection.add('onemuon', (nmuons == 1) & (nelectrons == 0) & (ntaus == 0))
        selection.add('muonkin', (leadingmuon.pt > 55.) & (abs(leadingmuon.eta) < 2.1))
        selection.add('muonDphiAK8', abs(leadingmuon.delta_phi(candidatejet)) > 2*np.pi/3)

        if isRealData :
            genflavor1 = ak.zeros_like(candidatejet.pt)
            genflavor2 = ak.zeros_like(secondjet.pt)
        else:
            weights.add('genweight', events.genWeight)
            if 'HToBB' in dataset:
                if self._ewkHcorr: add_HiggsEW_kFactors(weights, events.GenPart, dataset)

                # if self._systematics:
                #     # Jennet adds theory variations                                                                               
                #     add_ps_weight(weights, events.PSWeight)
                #     if "LHEPdfWeight" in events.fields:
                #         add_pdf_weight(weights,events.LHEPdfWeight)
                #     else:
                #         add_pdf_weight(weights,[])
                #     if "LHEScaleWeight" in events.fields:
                #         add_scalevar_7pt(weights, events.LHEScaleWeight)
                #         add_scalevar_3pt(weights, events.LHEScaleWeight)
                #     else:
                #         add_scalevar_7pt(weights,[])
                #         add_scalevar_3pt(weights,[])

            add_pileup_weight(weights, events.Pileup.nPU, self._year)
            bosons = getBosons(events.GenPart)
            matchedBoson1 = candidatejet.nearest(bosons, axis=None, threshold=0.8)
            matchedBoson2 = secondjet.nearest(bosons, axis=None, threshold=0.8)
            
            if self._tightMatch:
                #First boson
                match_mask1 = (abs(candidatejet.pt - matchedBoson1.pt)/matchedBoson1.pt < 0.5) & (abs(candidatejet.msdcorr - matchedBoson1.mass)/matchedBoson1.mass < 0.3)
                selmatchedBoson1 = ak.mask(matchedBoson1, match_mask1)
                
                #Second boson
                match_mask2 = (abs(secondjet.pt - matchedBoson2.pt)/matchedBoson2.pt < 0.5) & (abs(secondjet.msdcorr - matchedBoson2.mass)/matchedBoson2.mass < 0.3)
                selmatchedBoson2 = ak.mask(matchedBoson2, match_mask2)
                
                genflavor1 = bosonFlavor(selmatchedBoson1)
                genflavor2 = bosonFlavor(selmatchedBoson2)

            else:
                genflavor1 = bosonFlavor(matchedBoson1)
                genflavor2 = bosonFlavor(matchedBoson2)

            genBosonPt = ak.fill_none(ak.firsts(bosons.pt), 0)
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
        
        if shift_name is None: systematics = [None] + list(weights.variations)
        else: systematics = [shift_name]
            
        #!LIST OF THE SELECTIONS APPLIED
        regions = {'signal': ['trigger', 'lumimask', 'metfilter', 'jet1kin', 'jet2kin', 'jetid', 'jetacceptance', 'met', 'noleptons','njets'],}

        def fill(region, systematic, wmod=None):
            
            #Get the selection from above
            selections = regions[region]
            cut = selection.all(*selections)
            
            #Using nomial systematic if none is defined
            sname = 'nominal' if systematic is None else systematic
            
            if wmod is None:
                if systematic in weights.variations: weight = weights.weight(modifier=systematic)[cut]
                else: weight = weights.weight()[cut]
            else: weight = weights.weight()[cut] * wmod[cut]

            #! FILL THE HISTOGRAM
            output['h'].fill(
                dataset=dataset,
                region=region,
                systematic=sname,
                msd1=normalize(msd1_matched, cut),
                msd2=normalize(msd2_matched, cut),

                bb1=normalize(bb1, cut),
                qcd2=normalize(qcd2, cut),

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
