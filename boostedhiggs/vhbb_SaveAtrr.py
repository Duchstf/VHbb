from boostedhiggs.parent import *

class ParQuetProc(ParentProcessor):
    def process_shift(self, events, shift_name):
        
        #Return if there is no events
        if len(events) == 0:
            return
        
        #Some basic variables
        dataset = events.metadata['dataset']
        isRealData = not hasattr(events, "genWeight")
        
        self.pre_selection(events)
        candidatejet, secondjet, fatjets = self.jet_candidates(events)
        self.selection(events, candidatejet, secondjet)
        weights = self.weight_selection(events, candidatejet, secondjet, fatjets)
            
        #Exact B scores for Higgs candidate
        bb1 = candidatejet.particleNetMD_Xbb / (candidatejet.particleNetMD_Xbb + candidatejet.particleNetMD_QCD)
        qcd1 = candidatejet.particleNetMD_QCD

        #Exact C scores for V candidate
        cc2 = secondjet.particleNetMD_Xcc /  (secondjet.particleNetMD_Xcc + secondjet.particleNetMD_QCD)
        qcd2 = secondjet.particleNetMD_QCD
        
        
        #!LIST OF THE SELECTIONS APPLIED
        regions = { 'signal': ['trigger', 'lumimask', 'metfilter',
                               'jet1kin','jet2kin', 'jetid', 'jetacceptance',
                               'n2ddt', 'met', 'noleptons']}
        
        self.set_cuts(regions)
        
        if shift_name is None:
            systematics = [None] + list(weights.variations)
        else:
            systematics = [shift_name]
        
        for region in regions:
            if self._systematics:
                for systematic in systematics:
                    if isRealData and systematic is not None:
                        continue
                    self.save_to_parquet('bb1', bb1, weights, region, systematic)
            else:
                self.save_to_parquet('bb1', bb1, weights, region, None)
     
        return
    
    def postprocess(self, accumulator):
        return accumulator