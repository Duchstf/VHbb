from imports import *
import copy

WPs = {
    
    '2016APV_bb1': 0.9883,
    '2016_bb1': 0.9883,
    '2017_bb1': 0.9870,
    '2018_bb1':  0.9880,
}

samples = ['data', 'QCD', 'WH','ZH', 'VV', 'Wjets', 'Zjets', 'VBFDipoleRecoilOn', 'ggF', 'singlet', 'ttH', 'ttbar']

def plot_h(h, labels, name, year):

    labels = copy.copy(labels)
    mc = list(labels.values())
    figtext = f'BB PASS, {year}' if name == 'bb_pass' else f'BB FAIL, {year}'
    
    fig = plt.figure()

    ax1 = fig.add_subplot(4,1,(1,3))
    plt.subplots_adjust(hspace=0)
    
    # Plot stacked hist                                                                                                   
    hist.plot1d(h, overlay='process', order=mc, stack=True, fill_opts={'edgecolor':'black'})
    
    # Overlay data                                                                                                            
    hist.plot1d(h.integrate('process','muondata'),error_opts={'marker':'o','color':'k','markersize':5}) 
    ax1.get_xaxis().set_visible(False)    

    labels['Data'] = 'muondata'                                                                                           
    plt.legend(labels=labels, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.text(0.95, 0.95, figtext, horizontalalignment='right', verticalalignment='top', transform=plt.gca().transAxes)                                          

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
    
    pickle_path = f'../../output/pickle/muonCR/{year}/h.pkl'
    pickle_hist = pickle.load(open(pickle_path,'rb')).integrate('region','muoncontrol').integrate('systematic', 'nominal').sum('genflavor1', overflow='all')
    
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
        # 'Boosted ttbar': 'ttbarBoosted',
        'Single T': 'singlet',  
    }
    
    # colors=['purple']
    
    colors = ['hotpink','gray','deepskyblue','sienna','darkorange','gold']

    #Split into Jet 1 score b-tag passing/failing region. 
    hpass= sig.integrate('bb1',int_range=slice(bbthr,1.))
    hfail= sig.integrate('bb1',int_range=slice(0.,bbthr))
    
    #print(hpass.axis('process').identifiers())
    plot_h(hpass, labels, 'bb_pass', year)
    plot_h(hfail, labels, 'bb_fail', year)

if __name__ == "__main__":
    main()
