from imports import *
import copy

def main():
    
    year = '2017'
    cuts = ['muontrigger','lumimask','metfilter','minjetkinmu', 'jetid', 'onemuon', 'muonkin', 'ak4btagMedium08','muonDphiAK8', 'bbpass']

    pickle_path = f'../../output/pickle/muonCR/{year}/cutflow.pkl'
    pickle_hist = pickle.load(open(pickle_path,'rb')).sum('msd1').integrate('genflavor', slice(None,1) ,overflow='under').integrate('region', 'muoncontrol')
    
    #Process each region    
    sig = pickle_hist
    print(sig.identifiers('cut'))
    for i in range(0,10):
        print(f"---------i={i}-------CUT: {cuts[i]}----------")
        print(sig.integrate('cut', slice(i, i+1)).values())
        

if __name__ == "__main__":
    main()
