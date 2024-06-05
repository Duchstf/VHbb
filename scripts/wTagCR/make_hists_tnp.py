#!/usr/bin/python  

import os, sys
import subprocess
import json
import uproot3
import awkward as ak
import numpy as np
from coffea import processor, util, hist
import pickle

qcd_WPs = { '2016APV_qcd2': 0.0541, '2016_qcd2': 0.0882, '2017_qcd2': 0.0541, '2018_qcd2':  0.0741}


# Main method
def main():

    if len(sys.argv) < 2:
        print("Enter year")
        return

    elif len(sys.argv) > 3:
        print("Incorrect number of arguments")
        return

    year = sys.argv[1]

    qcdthr = qcd_WPs[f'{year}_qcd2']

    template_out = f'templates/{year}/TnP.root'
    if os.path.isfile(template_out): os.remove(template_out)
    fout = uproot3.create(template_out)

    # Check if pickle exists     
    picklename = f'templates/{year}/h.pkl'
    if not os.path.isfile(picklename): raise FileNotFoundError("You need to link the pickle file (using absolute paths)")

    # Read the histogram from the pickle file
    tnp = pickle.load(open(picklename,'rb')).integrate('region','tnp')

    # data first
    p = "muondata"
    hpass_data = tnp.integrate('qcd1', int_range=slice(0.,qcdthr)).integrate('process',p).sum('genflavor1')
    hfail_data = tnp.integrate('qcd1', int_range=slice(qcdthr,1.)).integrate('process',p).sum('genflavor1')

    fout[f"data_obs_pass_nominal"] = hist.export1d(hpass_data)
    fout[f"data_obs_fail_nominal"] = hist.export1d(hfail_data)

    # samples included
    p = ["ttbar","singlet","QCD","Wjets","Zjets"]

    # matched
    hpass_matched = tnp.integrate('qcd1',int_range=slice(0.,qcdthr)).integrate('process',p).integrate('genflavor1',int_range=slice(1,4))
    hfail_matched = tnp.integrate('qcd1',int_range=slice(qcdthr,1.)).integrate('process',p).integrate('genflavor1',int_range=slice(1,4))
    fout["matched_pass_nominal"] = hist.export1d(hpass_matched)
    fout["matched_fail_nominal"] = hist.export1d(hfail_matched)

    # unmatched
    hpass_unmatched = tnp.integrate('qcd1',int_range=slice(0.,qcdthr)).integrate('process',p).integrate('genflavor1',int_range=slice(0,1))
    hfail_unmatched = tnp.integrate('qcd1',int_range=slice(qcdthr,1.)).integrate('process',p).integrate('genflavor1',int_range=slice(0,1))
    fout["unmatched_pass_nominal"] = hist.export1d(hpass_unmatched)
    fout["unmatched_fail_nominal"] = hist.export1d(hfail_unmatched)

    return

if __name__ == "__main__":
    main()