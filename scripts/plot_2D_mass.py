
# Main method
from imports import *

def main():
    
    pickle_path = '../output/pickle/vhbb_v3_msd2/2017/ParticleNet_msd.pkl' #Need to be defined manually
    
    #TODO: Full sample is ['QCD', 'VBFDipoleRecoilOff', 'WH', 'WW', 'WZ', 'Wjets', 'ZH', 'ZZ', 'Zjets', 'ZjetsHT', 'data', 'ggF', 'singlet', 'ttH', 'ttbar', 'ttbarBoosted']
    
    #TODO: Current VBF sample is with DipoleRecoil Off, Jennet is generating a new sample with Dipole Recoil On. 
    #TODO: Doesn't matter if using Zjets or ZjetsHT (only the DY samples are different). 
    #TODO: ttbarboosted for higher statistics.
    #TODO: Don't need EWK V

    #! USE THE EXACT SAME SAMPLE IN make_cards.py
    samples = ['data',
            'QCD',
            'WH','ZH',
            'VV',
            'Wjets', 'Zjets',
            'VBFDipoleRecoilOff', #Double checking this.
            'ggF', 
            'singlet',
            'ttH',
            'ttbarBoosted']
    
    p = ['Wjets']
    h = pickle.load(open(pickle_path,'rb')).integrate('region','signal').integrate('systematic', 'nominal').sum( 'bb1', 'cc2', 'dr')
    hp = h.integrate('process',p)

    hist.plot2d(hp, xaxis="msd1", patch_opts={'norm': plt.Normalize(vmin=0, vmax=80)})
    plt.xlabel(r'Jet 1 $m_{sd}$ [GeV] ')
    plt.ylabel(r'Jet 2 $m_{sd}$ [GeV] ')
    plt.savefig(f'plots/mass2D_{p[0]}.pdf', bbox_inches='tight')
    plt.savefig(f'plots/mass2D_{p[0]}.png', bbox_inches='tight')
    

if __name__ == "__main__":
    main()
