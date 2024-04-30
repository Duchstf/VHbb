from imports import *

WPs = {
    
    '2016APV_bb1': 0.9883,
    '2016_bb1': 0.9883,
    '2017_bb1': 0.9870,
    '2018_bb1':  0.9880,
}

mass_range = [40., 68., 110., 201.]

samples = ['data', 'QCD', 'WH','ZH', 'VV', 'Wjets', 'Zjets', 'VBFDipoleRecoilOn', 'ggF', 'singlet', 'ttH', 'ttbar']

def plot_h(h, labels, name=''):
    
    mc = list(labels.values())
    
    fig = plt.figure()

    ax1 = fig.add_subplot(4,1,(1,3))
    plt.subplots_adjust(hspace=0)
    
    # Plot stacked hist                                                                                                   
    hist.plot1d(h, overlay='process', order=mc, stack=True, fill_opts={'edgecolor':'black'})
    
        # Overlay data                                                                                                            
    hist.plot1d(h.integrate('process','muondata'),error_opts={'marker':'o','color':'k','markersize':5}) 
    # labels = labels + ['Data']
    
    ax1.get_xaxis().set_visible(False)                                                                                               
    plt.legend(labels=labels,bbox_to_anchor=(1.05, 1), loc='upper left')                                                     

    allweights =  hist.export1d(h.integrate('process','muondata')).numpy()[0]                                                                              

    # ratio                                                                                                                   
    ax2 = fig.add_subplot(4,1,(4,4))
    hist.plotratio(num=h.integrate('process','muondata'),denom=h.integrate('process',mc),ax=ax2,unc='num',error_opts={'marker':'o','color':'k','markersize':5},guide_opts={})
    ax2.set_ylabel('Ratio')    
    ax2.set_xlabel('') 
    ax2.set_xlim(ax1.get_xlim())
    
    plt.savefig(f'plots/muCR_{name}.pdf', bbox_inches='tight')
    plt.savefig(f'plots/muCR_{name}.png', bbox_inches='tight')
    

def main():
    
    year = '2017'
    
    #Define the score threshold
    bbthr = WPs[f'{year}_bb1']
    print(f'BB1 {year} Threshold: ', bbthr)
    
    pickle_path = '../output/pickle/vhbb_v7_muonCR/{}/ParticleNet_msd.pkl'.format(year)
    pickle_hist = pickle.load(open(pickle_path,'rb')).integrate('region','muoncontrol').integrate('systematic', 'nominal').integrate('pt1', int_range=slice(400., None), overflow='over').integrate('njets', int_range=slice(0,None)).sum('genflavor1', overflow='all')
    #print(pickle_hist.sum('msd1', 'bb1').integrate('process', 'ttbar').values())
    
    #Process each region    
    sig = pickle_hist
        
    labels = {
        'QCD':'QCD',
        # 'VH': ['WH','ZH'],
        'VV': 'VV',
        'W + jets':'Wjets',
        'Z + jets':'Zjets',
        # 'Bkg H': ['ggF', 'ttH', 'VBFDipoleRecoilOn'],
        'ttbar': 'ttbar',
        'Single T': 'singlet',    
    }
        
   
    
    # colors=['purple']
    
    colors = ['hotpink','gray','deepskyblue','sienna','darkorange','gold']

    #Split into Jet 1 score b-tag passing/failing region. 
    hpass= sig.integrate('bb1',int_range=slice(0.,1.))
    hfail= sig.integrate('bb1',int_range=slice(0.,bbthr))
    
    print(hpass.integrate('process', 'QCD').sum('msd1').values())
    
    print("Compare ttbar")
    print(hpass.integrate('process', 'ttbar').sum('msd1').values())
    print(hpass.integrate('process', 'muondata').sum('msd1').values())
    
    print("Compare singletop")
    print(hpass.integrate('process', 'singlet').sum('msd1').values())
    print(hpass.integrate('process', 'muondata').sum('msd1').values())
    
    #print(hpass.axis('process').identifiers())
    
    plot_h(hpass, labels, name='bb_pass')

if __name__ == "__main__":
    main()
