from coffea import processor
import numpy as np
import awkward as ak
import coffea.hist
from coffea.analysis_tools import PackedSelection


def PackedSelection_any(self, *names):
    consider = 0
    for name in names:
        idx = self._names.index(name)
        consider |= 1 << idx
    return (self._data & consider) != 0


class TriggerProcessor(processor.ProcessorABC):
    def __init__(self, year="2017"):
        self._year = year
        self._triggers = {
            '2016': [
                'PFHT800',
                'PFHT900',
                'AK8PFJet360_TrimMass30',
                'AK8PFHT700_TrimR0p1PT0p03Mass50',
                'PFHT650_WideJetMJJ950DEtaJJ1p5',
                'PFHT650_WideJetMJJ900DEtaJJ1p5',
                'AK8DiPFJet280_200_TrimMass30_BTagCSV_p20',
                'PFJet450',
            ],
            '2017': [
                'AK8PFJet330_PFAK8BTagCSV_p17',
                'PFHT1050',
                'AK8PFJet400_TrimMass30',
                'AK8PFJet420_TrimMass30', # redundant
                'AK8PFHT800_TrimMass50',
                'PFJet500',
                'AK8PFJet500',

            ],
            '2018': [
                'AK8PFJet400_TrimMass30',
                'AK8PFJet420_TrimMass30',
                'AK8PFHT800_TrimMass50',
                'PFHT1050',
                'PFJet500',
                'AK8PFJet500',
                'AK8PFJet330_TrimMass30_PFAK8BoostedDoubleB_np4',
            ],
        }
        # https://twiki.cern.ch/twiki/bin/viewauth/CMS/MuonHLT
        self._mutriggers = {
            '2016': [
                "IsoMu24",
                "IsoTkMu24",
                "Mu50",
                "TkMu50",
            ],
            '2017': [
                "IsoMu27",
                "Mu50",
                "OldMu100",  # not in all eras
                "TkMu100",
            ],
            '2018': [
                "IsoMu24",
                "Mu50",
                "OldMu100",
                "TkMu100",
            ]
        }
        self._era_runranges = {
            "Run2016B": (272007, 275376),
            "Run2016C": (275657, 276283),
            "Run2016D": (276315, 276811),
            "Run2016E": (276831, 277420),
            "Run2016F": (277772, 278808),
            "Run2016G": (278820, 280385),
            "Run2016H": (280919, 284044),
            "2017A": (294645, 297019),
            "2017B": (297020, 299329),
            "2017C": (299337, 302029),
            "2017D": (302030, 303434),
            "2017E": (303435, 304826),
            "2017F": (304911, 306462),
            "Run2018A": (315252, 316995),
            "Run2018B": (316998, 319312),
            "Run2018C": (319313, 320393),
            "Run2018D": (320394, 325273),
            "Run2018E": (325274, 325765),
        }
        
        commonaxes = (
            coffea.hist.Cat("dataset", "Dataset name"),
            coffea.hist.Cat("era", "Run era"),
            coffea.hist.Bin("pt", "Leading jet $p_T$", 100, 0, 1000),
            coffea.hist.Bin("msd", "Leading jet $m_{SD}$", 30, 0, 300),
            coffea.hist.Bin("ddb", "Leading jet DDBvL score", 20, 0, 1),
        )
        self._accumulator = processor.dict_accumulator({
            "nevents": processor.defaultdict_accumulator(float),
            "trigger_exclusive": coffea.hist.Hist(
                "Events",
                coffea.hist.Cat("trigger", "Trigger name"),
                *commonaxes
            ),
            "trigger_inclusive": coffea.hist.Hist(
                "Events",
                coffea.hist.Cat("trigger", "Trigger name"),
                *commonaxes
            ),
        })

    @property
    def accumulator(self):
        return self._accumulator

    def process(self, events):
        output = self.accumulator.identity()
        dataset = events.metadata["dataset"]
        isRealData = not "genWeight" in events.fields
        if isRealData:
            for name, (runlo, runhi) in self._era_runranges.items():
                # assumes no era will be split across input files
                if events.run[0] >= runlo and events.run[0] <= runhi:
                    era = name
                    break
        else:
            era = "MC"
        output["nevents"][dataset] += len(events)
        
        triggers = PackedSelection()
        trigger_names = self._triggers[self._year]
        for tname in trigger_names:
            if tname in events.HLT.fields:
                triggers.add(tname, events.HLT[tname])
            else:
                triggers.add(tname, np.zeros(len(events), dtype=bool))

        # All with respect to independent muon reference trigger
        muontrigger = np.zeros(len(events), dtype=bool)
        for tname in self._mutriggers[self._year]:
            if tname in events.HLT.fields:
                muontrigger |= ak.to_numpy(events.HLT[tname])
        muons = events.Muon[
            (events.Muon.pt > 25)
            & (abs(events.Muon.eta) < 2.4)
            & (events.Muon.pfRelIso04_all < 0.25)
            & events.Muon.looseId
        ]
        # take highest pT
        jet = ak.firsts(events.FatJet[
            (events.FatJet.pt > 200)
            & (abs(events.FatJet.eta) < 2.5)
            & events.FatJet.isTight
            & ak.all(events.FatJet.metric_table(muons) > 0.8, axis=-1)  # default metric: delta_r
        ])
        jet_exists = ~ak.is_none(jet) & muontrigger

        output["trigger_exclusive"].fill(
            dataset=dataset,
            era=era,
            pt=jet[jet_exists].pt,
            msd=jet[jet_exists].msoftdrop,
            ddb=jet[jet_exists].btagDDBvLV2,
            trigger="none",
        )
        cut = jet_exists & PackedSelection_any(triggers, *set(trigger_names))
        output["trigger_inclusive"].fill(
            dataset=dataset,
            era=era,
            pt=jet[cut].pt,
            msd=jet[cut].msoftdrop,
            ddb=jet[cut].btagDDBvLV2,
            trigger="all",
        )

        for tname in trigger_names:
            cut = jet_exists & triggers.all(tname)
            output["trigger_exclusive"].fill(
                dataset=dataset,
                era=era,
                pt=jet[cut].pt,
                msd=jet[cut].msoftdrop,
                ddb=jet[cut].btagDDBvLV2,
                trigger=tname,
            )
            cut = jet_exists & PackedSelection_any(triggers, *(set(trigger_names) - {tname}))
            output["trigger_inclusive"].fill(
                dataset=dataset,
                era=era,
                pt=jet[cut].pt,
                msd=jet[cut].msoftdrop,
                ddb=jet[cut].btagDDBvLV2,
                trigger=tname,
            )
            
        return output

    def postprocess(self, accumulator):
        return accumulator