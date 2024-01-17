import logging
import json
import os

import awkward as ak
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from coffea import processor, hist
import hist as hist2
from coffea.analysis_tools import Weights, PackedSelection
from coffea.lumi_tools import LumiMask
from boostedhiggs.btag import BTagCorrector
from boostedhiggs.common import (
    getBosons,
    bosonFlavor,
)

logger = logging.getLogger(__name__)

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

    # Jennet adds theory variations                                                                                                
    add_ps_weight,
    add_scalevar_7pt,
    add_scalevar_3pt,
    add_pdf_weight,
)

class ParQuetProc(processor.ProcessorABC):
    
    def __init__(self,
                 year='2017',
                 jet_arbitration='T_bvc',
                 ewkHcorr=True,
                 systematics=True,
                 output_location="./output/parquet/"
                 ):
        
        self._year = year
        self._ewkHcorr = ewkHcorr
        self._jet_arbitration = jet_arbitration
        self._systematics = systematics
        self._output_location = output_location
        self._chunk_counter = 0

        #Open the trigger files
        with open('files/muon_triggers.json') as f:
            self._muontriggers = json.load(f)

        with open('files/triggers.json') as f:
            self._triggers = json.load(f)

        # https://twiki.cern.ch/twiki/bin/view/CMS/MissingETOptionalFiltersRun2
        with open('files/metfilters.json') as f:
            self._met_filters = json.load(f)
            
        self._histograms = hist.Hist(
            "Events",
            hist.Cat("sample", "Sample"),
            )
        
    def update(self, events, collections):
        """Return a shallow copy of events array with some collections swapped out"""
        out = events
        for name, value in collections.items():
            out = ak.with_field(out, value, name)
        return out
    
    def ak_to_parquet(self, val: ak.Array, cut, ArrayName, dataset):
        '''Export the arrays to Paquet DataFrame (taking into account the cuts)'''
        output_path = '{}/{}/'.format(self._output_location, dataset)
        os.system('mkdir -p {}'.format(output_path))
        
        if cut is None:
            ar = ak.to_parquet(ak.fill_none(val, np.nan), output_path + ArrayName)
            return ar
        else:
            ar = ak.to_parquet(ak.fill_none(val[cut], np.nan), output_path + ArrayName)
            return ar
        
    
    @property
    def accumulator(self):
        return self._histograms
    
    def process(self, events):
        """"Return skimmed events which pass preselection cuts"""
        
        #Dummy outputs, just return the name of the data set
        output = self.accumulator.identity()
        dataset = events.metadata['dataset']
        output.fill(sample=dataset)
        
        isRealData = not hasattr(events, "genWeight") # Data doesn't have genweight in it
        isQCDMC = 'QCD' in events.metadata['dataset']

        if isRealData or isQCDMC:
            # Nominal JEC are already applied in data
            self.process_shift(events, None)

        if np.sum(ak.num(events.FatJet, axis=1)) < 1:
            self.process_shift(events, None)

        jec_cache = {}

        thekey = f"{self._year}mc"
        if self._year == "2016":
            thekey = "2016postVFPmc"
            
        elif self._year == "2016APV":
            thekey = "2016preVFPmc"

        fatjets = fatjet_factory[thekey].build(add_jec_variables(events.FatJet, events.fixedGridRhoFastjetAll), jec_cache)
        jets = jet_factory[thekey].build(add_jec_variables(events.Jet, events.fixedGridRhoFastjetAll), jec_cache)
        met = met_factory.build(events.MET, jets, {})
        
        # Need to add more shifts if accounting for the full systematics
        shifts = [({"Jet": jets, "FatJet": fatjets, "MET": met}, None)]
        
        for collections, name in shifts:
            self.process_shift(self.update(events, collections), name)
        
        #Return dummy outputs
        self._chunk_counter += 1
        return output
    
    def process_shift(self, events, shift_name):
        dataset = events.metadata['dataset']
        isRealData = not hasattr(events, "genWeight")
        
        selection = PackedSelection()
        weights = Weights(len(events), storeIndividual=True)
        
        if len(events) == 0:
            return
        
        ################################################! TRIGGER AND FILTERS
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
            
        #Lumi mask
        if isRealData:
            selection.add('lumimask', lumiMasks[self._year[:4]](events.run, events.luminosityBlock))
        else:
            selection.add('lumimask', np.ones(len(events), dtype='bool'))
            
        #Muon trigger
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
        ################################################################################################
        
        
        ############################! JET MATCHING
        #Process collection of jets
        fatjets = events.FatJet
        fatjets['msdcorr'] = corrected_msoftdrop(fatjets)
        fatjets['qcdrho'] = 2 * np.log(fatjets.msdcorr / fatjets.pt)
        fatjets['n2ddt'] = fatjets.n2b1 - n2ddt_shift(fatjets, year=self._year)
        fatjets['msdcorr_full'] = fatjets['msdcorr']

        candidatejet = fatjets[
            (fatjets.pt > 200)
            & (abs(fatjets.eta) < 2.5)
            & fatjets.isTight  # this is loose in sampleContainer
        ]
        
        # Only consider first two to match generators
        candidatejet = candidatejet[:, :2]  
        
        #Process them with different jet arbitration
        if self._jet_arbitration == 'T_bvc':
            #Order the jets based on particle net scores
            leadingjets = candidatejet[:, 0:2]
            
            pnet_bvc = leadingjets.particleNetMD_Xbb / (leadingjets.particleNetMD_Xcc + leadingjets.particleNetMD_Xbb)
            
            #Higher b score for the Higgs candidate (more b like)                                                                                                                           
            indices = ak.argsort(pnet_bvc, axis=1, ascending = False) 

            # candidate jet is more b-like (higher BvC score)                                                                                                           
            candidatejet = ak.firsts(leadingjets[indices[:, 0:1]])
            
            # second jet is more charm-like (larger BvC score)                                                                                                           
            secondjet = ak.firsts(leadingjets[indices[:, 1:2]])
            
        else:
            raise RuntimeError("Unknown candidate jet arbitration")
        
        #Exact B scores for Higgs candidate
        bb1 = candidatejet.particleNetMD_Xbb / (candidatejet.particleNetMD_Xbb + candidatejet.particleNetMD_QCD)
        qcd1 = candidatejet.particleNetMD_QCD

        #Exact C scores for V candidate
        cc2 = secondjet.particleNetMD_Xcc /  (secondjet.particleNetMD_Xcc + secondjet.particleNetMD_QCD)
        qcd2 = secondjet.particleNetMD_QCD
        ################################################################################################
        
        
        #################################################! TRIGGER AND FILTERS
        #There is a list at the end which specifies the selections being used 
        selection.add('jet1kin',
            (candidatejet.pt >= 450)
            & (abs(candidatejet.eta) < 2.5)
        )
        selection.add('jet2kin',
            (secondjet.pt >= 200)
            & (abs(secondjet.eta) < 2.5)
            & (secondjet.msdcorr < 150) 
        )

        selection.add('jetacceptance',
            (candidatejet.msdcorr >= 40.)
            & (candidatejet.pt < 1200)
            & (candidatejet.msdcorr < 201.)
            & (secondjet.msdcorr >= 40.)
            & (secondjet.pt < 1200)
            & (secondjet.msdcorr < 201.)
        )

        selection.add('jetid',
                      candidatejet.isTight
                      & secondjet.isTight
        )

        selection.add('n2ddt',
                      (candidatejet.n2ddt < 0.)
                      & (secondjet.n2ddt < 0.)
        )

        jets = events.Jet
        jets = jets[
            (jets.pt > 30.)
            & (abs(jets.eta) < 5.0)
            & jets.isTight
            & (jets.puId > 0)
        ]
        
        # EE noise for 2017                                             
        if self._year == '2017':
            jets = jets[
                (jets.pt > 50)
                | (abs(jets.eta) < 2.65)
                | (abs(jets.eta) > 3.139)
            ]

        #NO MET ALLOWED IN THIS ANALYSIS
        met = events.MET
        selection.add('met', met.pt < 140.)
        
        #LEPTON CUTS
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
        ##############################################################################################
        

        #################################################! WEIGHT CORRECTIONS
        if isRealData :
            genflavor1 = ak.zeros_like(candidatejet.pt)
            genflavor2 = ak.zeros_like(secondjet.pt)
        else:
            weights.add('genweight', events.genWeight)

            if 'HToBB' in dataset:

                if self._ewkHcorr:
                    add_HiggsEW_kFactors(weights, events.GenPart, dataset)

                if self._systematics:
                    # Jennet adds theory variations                                                                               
                    add_ps_weight(weights, events.PSWeight)
                    if "LHEPdfWeight" in events.fields:
                        add_pdf_weight(weights,events.LHEPdfWeight)
                    else:
                        add_pdf_weight(weights,[])
                    if "LHEScaleWeight" in events.fields:
                        add_scalevar_7pt(weights, events.LHEScaleWeight)
                        add_scalevar_3pt(weights, events.LHEScaleWeight)
                    else:
                        add_scalevar_7pt(weights,[])
                        add_scalevar_3pt(weights,[])

            add_pileup_weight(weights, events.Pileup.nPU, self._year)
            bosons = getBosons(events.GenPart)
            matchedBoson1 = candidatejet.nearest(bosons, axis=None, threshold=0.8)
            matchedBoson2 = secondjet.nearest(bosons, axis=None, threshold=0.8)

            genflavor1 = bosonFlavor(matchedBoson1)
            genflavor2 = bosonFlavor(matchedBoson2)

            genBosonPt = ak.fill_none(ak.firsts(bosons.pt), 0)
            add_VJets_kFactors(weights, events.GenPart, dataset)

            add_jetTriggerSF(weights, ak.firsts(fatjets), self._year, selection)

            add_muonSFs(weights, leadingmuon, self._year, selection)

            if self._year in ("2016APV", "2016", "2017"):
                weights.add("L1Prefiring", events.L1PreFiringWeight.Nom, events.L1PreFiringWeight.Up, events.L1PreFiringWeight.Dn)


            logger.debug("Weight statistics: %r" % weights.weightStatistics)
        ##############################################################################################
        
        if shift_name is None:
            systematics = [None] + list(weights.variations)
        else:
            systematics = [shift_name]
            
        #!LIST OF THE SELECTIONS APPLIED
        regions = {
            'signal': ['trigger',
                       'lumimask',
                       'metfilter',
                       'jet1kin',
                       'jet2kin',
                       'jetid',
                       'jetacceptance',
                       'n2ddt',
                       'met',
                       'noleptons'],
        }
        
        
        def save_to_parquet(region, systematic, wmod=None):
            
            #Get the selection from above
            selections = regions[region]
            cut = selection.all(*selections)
            
            if wmod is None:
                if systematic in weights.variations:
                    weight = weights.weight(modifier=systematic)[cut]
                else:
                    weight = weights.weight()[cut]
            else:
                weight = weights.weight()[cut] * wmod[cut]
            
            #Save the  needed array
            fname_placeholder = "{}_VARNAME_{}.parquet".format(dataset, self._chunk_counter)
        
            #Save the data to parquet
            self.ak_to_parquet(candidatejet.msdcorr, cut, fname_placeholder.replace('VARNAME', 'jet1_msd'), dataset)
        
        for region in regions:
            if self._systematics:
                for systematic in systematics:
                    if isRealData and systematic is not None:
                        continue
                    save_to_parquet(region, systematic)
            else:
                save_to_parquet(region, None)
     
        return

        
    
    def postprocess(self, accumulator):
        return accumulator