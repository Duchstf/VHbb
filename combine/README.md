# Combine steps for VHbb

1. Make the pickles
2. Run the `make-hists` scripts → there are usually different make hists according to different regions. 
3. Then run `make-cards` on the root file (remember to enable the CMSSW environment).
4. Run `make_workspace` (again, remember to enable cmssw environment)
5. To check significance: run `exp_significance`