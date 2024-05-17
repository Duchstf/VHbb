import os
import numpy as np
import ROOT
import argparse

def gen_toys(infile, ntoys, seed=123456):
    combine_cmd = "combine -M GenerateOnly -m 125 -d " + infile + "\
    --snapshotName MultiDimFit --bypassFrequentistFit \
    -n \"Toys\" -t "+str(ntoys)+" --saveToys \
    --seed "+str(seed)
    os.system(combine_cmd)

def GoF(infile, ntoys, seed=123456):

    combine_cmd = "combine -M GoodnessOfFit -m 125 -d " + infile + "\
    --snapshotName MultiDimFit --bypassFrequentistFit \
    -n \"Toys\" -t " + str(ntoys) + " --algo \"saturated\" --toysFile higgsCombineToys.GenerateOnly.mH125."+str(seed)+".root \
    --seed "+str(seed)
    os.system(combine_cmd)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='F-test')
    parser.add_argument('-p','--pt',  type=int, help='pt of vh baseline')
    parser.add_argument('-r','--rho',  type=int, help='rho of vh baseline')
    parser.add_argument('-n','--ntoys', type=int, help='number of toys')
    parser.add_argument('-i','--index', type=int, help='index for random seed')
    args = parser.parse_args()

    pt = args.pt
    rho = args.rho
    ntoys = args.ntoys
    seed = 123456+args.index*100+31
    
    baseline = "pt{}rho{}".format(pt, rho)
    alternatives = []
    pvalues = []

#    alternatives += ["pt"+str(pt+1)+"rho"+str(rho)]
    alternatives += ["pt{}rho{}".format(pt, rho+1)]
    alternatives = list(set(alternatives))

    for i,alt in enumerate(alternatives):

        pt_alt = int(alt.split("rho")[0].split("pt")[1])
        rho_alt = int(alt.split("rho")[1])
        print("(pt, rho) alternative: {},{}".format(pt_alt, rho_alt))

        thedir = "{}_vs_{}".format(baseline, alt)
        os.mkdir(thedir)
        os.chdir(thedir)

        # Copy what we need
        os.system("cp ../{}/higgsCombineSnapshot.MultiDimFit.mH125.root baseline.root".format(baseline))
        os.system("cp ../{}/higgsCombineSnapshot.MultiDimFit.mH125.root alternative.root".format(alt))

        gen_toys("baseline.root", ntoys,seed=seed)

        # run baseline gof                                                                                                                              
        GoF("baseline.root", ntoys,seed=seed)
        os.system('mv higgsCombineToys.GoodnessOfFit.mH125.{}.root higgsCombineToys.baseline.GoodnessOfFit.mH125.{}.root'.format(seed, seed))

        # run alternative gof                                                                                                                           
        GoF("alternative.root", ntoys,seed=seed)
        os.system('mv higgsCombineToys.GoodnessOfFit.mH125.{}.root higgsCombineToys.alternative.GoodnessOfFit.mH125.{}.root'.format(seed, seed))

        os.chdir('../')
