# June 24, 2024: VHbb Conveners Feedbacks on AN V1.

> Dear Duc, analysis team, 

> Thanks a lot! We’d like to congratulate you for the excellent quality of the AN, which is quite complete and allows us to focus on physics. Please find a list of comments below. As usual, please open a Twiki page with the answers to the comments for the review process. 

> We look forward to the update in the Hbb meeting. 

> Cheers,

> Chayanit and Marko

> General comments
> - Add changelog in the next iterations
* Yes! 
> - When will the red texts be completed (apart from the ones after unblinding)?
* Jul 1, 2024 response: theory systematics included, signal injection bias test to be completed within the week.

> Introduction:
> As a suggestion, it might be nice to add specific models predicting enhanced couplings in VH or Hbb at high pT. One comment that might happen down the line is ‘VHbb is already measured at > 5 sigma, what is the added value of this measurement?’ If you have specific models it might help the discussion here.

> Section 2
> - Which PD? Add to AN.
> - Add Data/MC comparison before/after V+jet corrections (Figure 13,14 not just ratio?)
> - HH samples contribution? Possible to briefly quantify the contribution by running on HH4b sample?
> - Figure 16 What does theory prediction come from? What is EW correction? Why is ggZH with Powheg LO not NLO? 
> - 2.2 Trigger, line 76: explicitly mention the pT thresholds for 17 and 18 and the difference for 16. Given the comparisons you perform, it will help understand differences in the final results

> Section 3
> - Table 11 : PNet p(QCD) optimized WPs and corresponding SFs? Changes in selection require dedicated calibrations of PNet, how much does the p(QCD) working point add to the analysis?
> - Line 306-307 jet veto maps used for this? Not present in 2018? HEM applied? 

> Section 4
> - Figure 18: maybe I missed it but how are jet1 and jet2 defined? Ordered by PNet Xbb score? Mass?  
> - Overlapping with HH boosted region?
> - Table 12-15 MC with all corrections applied?
> - Table 12-15 MC: yields are not scaling with lumi across the years for QCD and other backgrounds?  In general 2016 seems to be an outlier, do you understand these? Event selection different? Performance of taggers?
> - Why AK4Jet < 5 and not tighter given boosted products on both V and H? Do you apply an overlap removal with the AK8 jets when defining the AK4 for the veto?
> - Figure 20-28: can you clarify how you obtain the flavour of the jets? Do you count the number of b-quarks, c-quarks and light quarks in the jets? Requirement on having 2 quarks? Selection on the momentum of the hadrons? 
> - Fig 20-28: These plots are very interesting, one general comment, there seems to be a non-negligible level of mass sculpting from the ttbar contribution, that happens for c-like category. Events selected are shaped into a peak at 100-150 GeV. Based on your yields, this is also more statistically populated than your signal. The risk here is that any fluctuation in the ttbar would create a bias that will be absorbed by the signal strength of the VH process once floated. It also raises the question if something similar happens with QCD? Can you produce the plot for the QCD template too? Using the same definition of the flavour you use here. 
> - Fig20-28: this shaping is absent from the other processes, at the exception of ttH maybe, which has a larger c-like contribution in this region. Can you clarify if this is bW(->cb) jets or bW(->cs)? 
> - Fig 20-28: can you discuss how these affect the background estimate? Given that the peak is not observed in the fail region, any sculpting in a subset of events with c-like components would be neglected by the transfer factor right? 
> - In general, the strategy with the PNet calibrations is different from what one would ideally have. Now the question is if the approximation is sufficient for the analysis. In an ideal scenario, each process would need to be calibrated based on the final state in the jets. Currently, X->bb signatures are to some extent covered, but calibrations are missing for any mixture: X->bc, X->cs, the ttbar is a special case on itself with t->bcb, t->bcs and any component where one quark is outside the AK8. 
> - Figure 26: large deficit around the Higgs mass, can you add the MC stat in the plot to understand if this is significant? Similar comment for Figure 28

> Section 5

> 5.1 
> - Why DeepCSVv2 not DeepJet? DeepJet is the official tagger recommended by BTV in UL, to simplify the object review, would it be possible to update the tagger? Can you also comment if you apply the calibration on the tagged b-jets before extracting the ttbar scale factors?
> - Can you clarify why there are 2 scale factors derived for ttbar? In principle, the effect of PNet is first order a normalisation effect and then an additional shape effect. 
> - Table 16 : are these taken as rate parameters in the final fit? Please provide results from Asimov to confirm these SFs are close to 1. 
> - Figure 29-32: large excess at low mass in 16APV, 17, 18, not taken into account by the fit? Would it be possible to run postfit b-only? Is this due to the QCD fakes?
> - Fig.37-40 not sure I understood these plots? Why good agreement in 2018 between pre- and post-fit?
> - Fig 40: can you comment about the large deviation in the bin at 90 GeV, mostly visible in the bin0? This looks like a z-peak, can you clarify if this is the QCD template only? Or a mixture of different MCs?
> - Fig 37-40: can you also comment on the fluctuations seen in the template? It seems that the bins are not fluctuating statistically?

> Fit model
> - Table 24: 2016 combined would be more sensitive than 2017, can you comment on this? Is it due to the trigger? Based on a simple combination, 2016 is 13% better than 2017 for 5 fb-1 less, in case there’s a reason it would be nice to add it in the AN.
> - Would it be possible to unblind the sidebands for all the plots:
>  - bin0: unblind 40-60 and then > 120 GeV
>   - bin1: unblind 40-60 and then > 150 GeV
>   - bin2: unblind 40-60 and then > 120 GeV 
>   - Fail regions: completely unblind the entire distribution
> - Impact: tf_MCtempl is a shape uncertainty? Can you plot the +1-1 sigma?
> - JES and JER, not clear how this is applied? It seems the JES and JER are applied as a normalisation effect but in principle this is a shape effect. Do I understand correctly the JMS and JMR are covering for this and the role of the JES and JER is to account for differences in the normalisation of events failing the selection within the uncertainties? 
