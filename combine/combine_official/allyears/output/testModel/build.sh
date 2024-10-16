combineCards.py \
muonCRfail2016APV=muonCRfail2016APV.txt muonCRpass2016APV=muonCRpass2016APV.txt VBin0fail2016APV=VBin0fail2016APV.txt VBin0pass2016APV=VBin0pass2016APV.txt VBin1fail2016APV=VBin1fail2016APV.txt VBin1pass2016APV=VBin1pass2016APV.txt VBin2fail2016APV=VBin2fail2016APV.txt VBin2pass2016APV=VBin2pass2016APV.txt \
muonCRfail2016=muonCRfail2016.txt muonCRpass2016=muonCRpass2016.txt VBin0fail2016=VBin0fail2016.txt VBin0pass2016=VBin0pass2016.txt VBin1fail2016=VBin1fail2016.txt VBin1pass2016=VBin1pass2016.txt VBin2fail2016=VBin2fail2016.txt VBin2pass2016=VBin2pass2016.txt \
muonCRfail2017=muonCRfail2017.txt muonCRpass2017=muonCRpass2017.txt VBin0fail2017=VBin0fail2017.txt VBin0pass2017=VBin0pass2017.txt VBin1fail2017=VBin1fail2017.txt VBin1pass2017=VBin1pass2017.txt VBin2fail2017=VBin2fail2017.txt VBin2pass2017=VBin2pass2017.txt \
muonCRfail2018=muonCRfail2018.txt muonCRpass2018=muonCRpass2018.txt VBin0fail2018=VBin0fail2018.txt VBin0pass2018=VBin0pass2018.txt VBin1fail2018=VBin1fail2018.txt VBin1pass2018=VBin1pass2018.txt VBin2fail2018=VBin2fail2018.txt VBin2pass2018=VBin2pass2018.txt > model_combined.txt

text2workspace.py model_combined.txt -P HiggsAnalysis.CombinedLimit.PhysicsModel:multiSignalModel --PO verbose  --PO 'map=.*(ZH|WH).*:rVH[1,-5,5]'  --PO 'map=.*(VqqVqq|VbbVqq).*:rVV[1,-5,5]'
