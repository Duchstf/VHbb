from imports import *
import copy
import sys

WPs = {
    
    '2016APV_bb1': 0.9883,
    '2016_bb1': 0.9883,
    '2017_bb1': 0.9870,
    '2018_bb1':  0.9880,
}

#Dataset parameters
lumis = {
    "2016APV": 19.52,
    "2016": 16.81,
    "2017": 41.48,
    "2018": 59.83
}

samples = ['data', 'QCD', 'WH','ZH', 'VV', 'Wjets', 'Zjets', 'VBFDipoleRecoilOn', 'ggF', 'singlet', 'ttH', 'ttbar']

def plot_h(h, labels, name, year):

    labels = copy.copy(labels)
    figtext = f'BB PASS' if name == 'bb_pass' else f'BB FAIL'
    # if name == 'bb_pass': del labels['QCD'] #Delete QCD in the bb passing region
    mc = list(labels.values())
    
    #Plot now
    fig = plt.figure()

    ax1 = fig.add_subplot(4,1,(1,3))
    plt.subplots_adjust(hspace=0)
    
    # Plot stacked hist
    colors = ['#94a4a2','#832db6','#bd1f01','sandybrown']
    colors = colors[:-1] if name == 'bb_pass' else colors

    hist.plot1d(h, overlay='process', order=mc, stack=True, fill_opts={'edgecolor':'black', 'color':colors})
    
    # Overlay data
    # Overall - both left and right annotation
    hep.cms.label('Preliminary', lumi=lumis[year], data=True, year=year)                                                                                                      
    hist.plot1d(h.integrate('process','muondata'),error_opts={'marker':'o','color':'k','markersize':5}) 
    ax1.get_xaxis().set_visible(False)    

    labels['Data'] = 'muondata'

    ##I'll do anything for legends lol>>>>>>>>>>                                                                                           
    legend = ax1.legend(labels=labels, bbox_to_anchor=(1.05, 1), loc='upper left')

    # Get the bounding box of the legend in the figure coordinates
    legend_box = legend.get_window_extent()

    # Convert the bounding box coordinates from figure to data coordinates
    inv = ax1.transAxes.inverted()
    data_bbox = inv.transform(legend_box)

    # Calculate the coordinates to place the text "BB FAIL" above the legend
    x_text = data_bbox[0][0]
    y_text = data_bbox[1][1] + 0.02  # Adjust the 0.02 to place the text slightly above the legend
  
    plt.text(x_text+0.25, y_text + 0.03, figtext, horizontalalignment='right', verticalalignment='top', transform=plt.gca().transAxes)                                          

     ##<<<<<<<<<<<<<<<<<<<I'll do anything for legends lol                                                      

    # ratio                                                                                                                   
    ax2 = fig.add_subplot(4,1,(4,4))
    hist.plotratio(num=h.integrate('process','muondata'),denom=h.integrate('process',mc),ax=ax2,unc='num',error_opts={'marker':'o','color':'k','markersize':5},guide_opts={})
    ax2.set_ylabel(r'$\frac{Data - Bkg}{\sigma_{data}}$')    
    ax2.set_xlabel('Jet Mass [GeV]') 
    ax2.set_xlim(ax1.get_xlim())
    
    plt.savefig(f'plots/{year}_muCR_{name}.pdf', bbox_inches='tight')
    plt.savefig(f'plots/{year}_muCR_{name}.png', bbox_inches='tight')
    

def main():
    
    year = sys.argv[1]
    
    #Define the score threshold
    bbthr = WPs[f'{year}_bb1']
    print(f'BB1 {year} Threshold: ', bbthr)
    
    pickle_path = f'../../output/pickle/muonCR/{year}/h.pkl'
    pickle_hist = pickle.load(open(pickle_path,'rb')).integrate('region','muoncontrol').integrate('systematic', 'nominal').integrate('genflavor1', slice(None,4), overflow='under')
    
    #Process each region    
    sig = pickle_hist
        
    labels = {
        'TTbar': 'ttbar',
        'Single T': 'singlet',
        'W(Lep.)':'Wjets',
        # 'Z + jets':'Zjets', #'#2ca02c'
        'QCD':'QCD',  
    }

    #Split into Jet 1 score b-tag passing/failing region. 
    hpass= sig.integrate('bb1',int_range=slice(bbthr,1.))
    hfail= sig.integrate('bb1',int_range=slice(0.,bbthr))
    
    #print(hpass.axis('process').identifiers())
    plot_h(hpass, labels, 'bb_pass', year)
    plot_h(hfail, labels, 'bb_fail', year)

if __name__ == "__main__":
    main()
