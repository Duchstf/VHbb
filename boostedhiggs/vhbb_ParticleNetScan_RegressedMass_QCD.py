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


logger = logging.getLogger(__name__)


def update(events, collections):
    """Return a shallow copy of events array with some collections swapped out"""
    out = events
    for name, value in collections.items():
        out = ak.with_field(out, value, name)
    return out


class ParticleNetMsdProcessor(processor.ProcessorABC):
    
    def __init__(self,
                 year='2017',
                 jet_arbitration='T_bvc',
                 skipJER=False,
                 tightMatch=False,
                 ak4tagger='deepJet', #TODO: NEED TO CHECK WITH JENNET IF I NEED TO CHANGE THIS FOR PARTICLE NET
                 ewkHcorr=True,
                 systematics=True
                 ):
        
        self._year = year
        self._ak4tagger = ak4tagger
        self._ewkHcorr = ewkHcorr
        self._jet_arbitration = jet_arbitration
        self._skipJER = skipJER
        self._tightMatch = tightMatch
        self._systematics = systematics

        #Raise errors for some taggers
        if self._ak4tagger == 'deepcsv':
            raise NotImplementedError()
#            self._ak4tagBranch = 'btagDeepB'
        elif self._ak4tagger == 'deepJet':
            self._ak4tagBranch = 'btagDeepFlavB'
        else:
            raise NotImplementedError()

        self._btagSF = BTagCorrector('M', self._ak4tagger, year)

        #Open the trigger files
        with open('files/muon_triggers.json') as f:
            self._muontriggers = json.load(f)

        with open('files/triggers.json') as f:
            self._triggers = json.load(f)

        # https://twiki.cern.ch/twiki/bin/view/CMS/MissingETOptionalFiltersRun2
        with open('files/metfilters.json') as f:
            self._met_filters = json.load(f)
        
        ParticleNet_WorkingPoints = {
                '2017_bb': [0.0, 0.9105, 0.9714, 0.9870],
                '2017_cc':[0.0, 0.9347, 0.9765, 0.9909]
        }
        
        #Create the histogram.
        self.make_output = lambda: {
            
            'sumw': processor.defaultdict_accumulator(float),
            
            #TODO: WHAT IS THIS USED FOR?
            'btagWeight': hist2.Hist(
                hist2.axis.Regular(50, 0, 3, name='val', label='BTag correction'),
                hist2.storage.Weight(),
            ),
            
            'ParticleNet_msd': hist.Hist(
                'Events',
                hist.Cat('dataset', 'Dataset'),
                hist.Cat('region', 'Region'),
                hist.Bin('msd1', r'Jet 1 $m_{sd}$', 23, 40, 201),
                hist.Bin('genflavor2', 'Gen. jet 2 flavor', [1, 2, 3, 4]), #1 light, 2 charm, 3 b, 4 upper edge. B falls into 3-4.
                hist.Bin('bb1', r'Jet 1 Paticle Net BB Score', ParticleNet_WorkingPoints['{}_bb'.format(self._year)]), # b working points
                hist.Bin('cc2', r'Jet 2 Particle Net CC Score', ParticleNet_WorkingPoints['{}_cc'.format(self._year)]), # c working points
                hist.Bin('bb2', r'Jet 2 BB Score', ParticleNet_WorkingPoints['{}_bb'.format(self._year)]), # b working points
                hist.Bin('qcd2', r'Jet 2 QCD Score', [round(x,2) for x in list(np.linspace(0,1,21))]), #20 bins
                hist.Bin('qq2', r'Jet 2 QQ Score', [round(x,2) for x in list(np.linspace(0,1,21))]), #20 bins
            )
        }

    def process(self, events):
        isRealData = not hasattr(events, "genWeight")
        isQCDMC = 'QCD' in events.metadata['dataset']

        if isRealData or isQCDMC:
            # Nominal JEC are already applied in data
            return self.process_shift(events, None)

        if np.sum(ak.num(events.FatJet, axis=1)) < 1:
            return self.process_shift(events, None)

        jec_cache = {}

        thekey = f"{self._year}mc"
        if self._year == "2016":
            thekey = "2016postVFPmc"
        elif self._year == "2016APV":
            thekey = "2016preVFPmc"

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
        
        if shift_name is None and not isRealData:
            output['sumw'][dataset] = ak.sum(events.genWeight)

        if len(events) == 0:
            return output

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

        if isRealData:
            selection.add('lumimask', lumiMasks[self._year[:4]](events.run, events.luminosityBlock))
        else:
            selection.add('lumimask', np.ones(len(events), dtype='bool'))

        if isRealData:
            trigger = np.zeros(len(events), dtype='bool')
            for t in self._muontriggers[self._year]:
                if t in events.HLT.fields:
                    trigger = trigger | events.HLT[t]
            selection.add('muontrigger', trigger)
            del trigger
        else:
            selection.add('muontrigger', np.ones(len(events), dtype='bool'))

        metfilter = np.ones(len(events), dtype='bool')
        for flag in self._met_filters[self._year]['data' if isRealData else 'mc']:
            metfilter &= np.array(events.Flag[flag])
        selection.add('metfilter', metfilter)
        del metfilter

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
        
        #Pick the candidate jet based on different arbitration
        if self._jet_arbitration == 'pt':
            candidatejet = ak.firsts(candidatejet)
        elif self._jet_arbitration == 'mass':
            candidatejet = ak.firsts(candidatejet[ak.argmax(candidatejet.msdcorr, axis=1, keepdims=True)])
        elif self._jet_arbitration == 'n2':
            candidatejet = ak.firsts(candidatejet[ak.argmin(candidatejet.n2ddt, axis=1, keepdims=True)])
        elif self._jet_arbitration == 'ddb':
            candidatejet = ak.firsts(candidatejet[ak.argmax(candidatejet.btagDDBvLV2, axis=1, keepdims=True)])
        elif self._jet_arbitration == 'ddc':
            candidatejet = ak.firsts(candidatejet[ak.argmax(candidatejet.btagDDCvLV2, axis=1, keepdims=True)])
        elif self._jet_arbitration == 'ddcvb':
            leadingjets = candidatejet[:, 0:2]
            # ascending = true                                                                                                                                
            indices = ak.argsort(leadingjets.btagDDCvBV2,axis=1)

            # candidate jet is more b-like                                                                                                               
            candidatejet = ak.firsts(leadingjets[indices[:, 0:1]])
            # second jet is more charm-like                                                                                                              
            secondjet = ak.firsts(leadingjets[indices[:, 1:2]])
            
        elif self._jet_arbitration == 'T_bvc':
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

        #Exact C scores for V candidate
        cc2 = secondjet.particleNetMD_Xcc /  (secondjet.particleNetMD_Xcc + secondjet.particleNetMD_QCD)
        bb2 = secondjet.particleNetMD_Xbb / (secondjet.particleNetMD_Xbb + secondjet.particleNetMD_QCD)
        qcd2 = secondjet.particleNetMD_QCD
        qq2 = secondjet.particleNetMD_Xqq
        

        #!Add selections------------------>
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

        # Only consider first 4 jets to be consistent with old framework  
        jets = jets[:, :4]
        dR = abs(jets.delta_r(candidatejet))
        ak4_away = jets[dR > 0.8]
#       selection.add('noExtraBJets', ak.max(ak4_away.btagDeepB, axis=1, mask_identity=False) < self._btagSF._btagwp)

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

            if shift_name is None:
                output['btagWeight'].fill(val=self._btagSF.addBtagWeight(ak4_away, weights))

            add_jetTriggerSF(weights, ak.firsts(fatjets), self._year, selection)

            add_muonSFs(weights, leadingmuon, self._year, selection)

            if self._year in ("2016APV", "2016", "2017"):
                weights.add("L1Prefiring", events.L1PreFiringWeight.Nom, events.L1PreFiringWeight.Up, events.L1PreFiringWeight.Dn)


            logger.debug("Weight statistics: %r" % weights.weightStatistics)

        msd1_matched = candidatejet.msdcorr * (genflavor1 > 0) + candidatejet.msdcorr * (genflavor1 == 0)
        ParticleNetM_matched = candidatejet.particleNet_mass * (genflavor1 > 0) + candidatejet.particleNet_mass * (genflavor1 == 0)
        msd2_matched = secondjet.msdcorr * (genflavor2 > 0) + secondjet.msdcorr * (genflavor2 == 0)
        
        def normalize(val, cut):
            '''not actually normalizing, just fill in the values after cuts'''
            if cut is None:
                ar = ak.to_numpy(ak.fill_none(val, np.nan))
                return ar
            else:
                ar = ak.to_numpy(ak.fill_none(val[cut], np.nan))
                return ar
        
        #Start timer
        import time
        tic = time.time()
        #----------------
        
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
            output['ParticleNet_msd'].fill(
                dataset=dataset,
                region=region,
                msd1=normalize(ParticleNetM_matched, cut),
                genflavor2=normalize(genflavor2,cut),
                bb1=normalize(bb1, cut),
                cc2=normalize(cc2, cut),
                bb2= normalize(bb2, cut),
                qcd2=normalize(qcd2, cut),
                qq2=normalize(qq2,cut),
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
        
        #TODO: IS THIS NEEDED ANYMORE?
        if shift_name is None:
            output["weightStats"] = weights.weightStatistics
            
        return output

    def postprocess(self, accumulator):
        return accumulator
