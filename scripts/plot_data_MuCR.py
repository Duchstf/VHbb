from imports import *

WPs = {
    
    '2016APV_bb1': 0.9883,
    '2016_bb1': 0.9883,
    '2017_bb1': 0.9870,
    '2018_bb1':  0.9880,
}

mass_range = [40., 68., 110., 201.]

samples = ['data', 'QCD', 'WH','ZH', 'VV', 'Wjets', 'Zjets', 'VBFDipoleRecoilOn', 'ggF', 'singlet', 'ttH', 'ttbar']

def plot_datamc_muoncr(h, name, xtitle, title, xlim=-1, log=True):

    fig = plt.figure()
    plt.suptitle(title)

    ax1 = fig.add_subplot(4,1,(1,3))
    plt.subplots_adjust(hspace=0)

    # https://matplotlib.org/stable/gallery/color/named_colors.html       
    labels = ['tt','single t','QCD','W+jets','Z+jets','EWKV','VV','bkg H'] 
    mc = ['ttbar','singlet','QCD','Wjets','Zjets',['EWKZ','EWKW'],'VV',['ZH','WH','ttH','ggF']]    
    colors=['purple','hotpink','white','gray','deepskyblue','sienna','darkorange','gold']

    if log:
        mc = [x for x in reversed(mc)]
        colors = [x for x in reversed(colors)]
        labels = [x for x in reversed(labels)]                                                                  

    if 'ddb1' in name:
        h = h.rebin("ddb1", hist.Bin("ddb1new", "rebinned ddb1", 25,0,1))
        
    # Plot stacked hist                                                                                                   
    hist.plot1d(h, order=mc, stack=True,fill_opts={'color':colors,'edgecolor':'black'})                              
    # Overlay data                                                                                                            
    hist.plot1d(h.integrate('process','muondata'),error_opts={'marker':'o','color':'k','markersize':5}) 
    labels = labels + ['Data']

    # if 'eta1' in name or 'dphi' in name or 'mjj' in name: 
    #     ax1.set_xlim(0,xlim)
    # if 'deta' in name:
    #     ax1.set_xlim(xlim,7)
    # ax1.get_xaxis().set_visible(False)                                                                                               
    # plt.legend(labels=labels,bbox_to_anchor=(1.05, 1), loc='upper left')                                                     

    # allweights =  hist.export1d(h.integrate('process','muondata')).numpy()[0] 
    # if log:
    #     ax1.set_yscale('log')
    #     ax1.set_ylim(0.01,5*np.amax(allweights))                                                                               

    # # ratio                                                                                                                   
    # ax2 = fig.add_subplot(4,1,(4,4))
    # hist.plotratio(num=h.integrate('process','muondata'),denom=h.integrate('process',mc),ax=ax2,unc='num',error_opts={'marker':'o','color':'k','markersize':5},guide_opts={})
    # ax2.set_ylabel('Ratio')    
    # ax2.set_xlabel(xtitle) 
    # ax2.set_xlim(ax1.get_xlim())

    # plt.savefig(f'plots/H_comp.pdf', bbox_inches='tight')
    # plt.savefig(f'plots/H_comp.png', bbox_inches='tight')

def main():
    
    year = '2017'
    
    #Define the score threshold
    bbthr = WPs[f'{year}_bb1']
    print(f'BB1 {year} Threshold: ', bbthr)
    
    pickle_path = '../output/pickle/vhbb_v7_muonCR/{}/ParticleNet_msd.pkl'.format(year)
    pickle_hist = pickle.load(open(pickle_path,'rb')).integrate('region','muoncontrol').integrate('systematic', 'nominal').integrate('pt1', int_range=slice(250., None), overflow='over').integrate('njets', int_range=slice(0,5)).sum('genflavor1', overflow='under')
    print(pickle_hist.sum('msd2', 'msd1', 'bb1').integrate('process', 'ttbar').values())
    
    """
    #Process each region
    for i in range(len(mass_range)-1):

        print('Running for {} in {} mass region'.format(year, i))
        msd2_int_range = slice(mass_range[i], mass_range[i+1])
        sig = pickle_hist.integrate('msd2', msd2_int_range)
        
        labels = {
            'QCD':'QCD',
            # 'VH': ['WH','ZH'],
            # 'VV': ['VV'],
            # 'W + jets':['Wjets'],
            # 'Z + jets':['Zjets'],
            # 'Bkg H': ['ggF', 'ttH', 'VBFDipoleRecoilOn'],
            # 'ttbar': ['ttbar'],
            # 'Single T': ['singlet'],    
        }
        
        mc = list(labels.values())
        
       
        colors=['purple']
        
        #colors = ['hotpink','white','gray','deepskyblue','sienna','darkorange','gold']

        #Split into Jet 1 score b-tag passing/failing region. 
        hpass= sig.integrate('bb1',int_range=slice(bbthr,1.))
        hfail= sig.integrate('bb1',int_range=slice(0.,bbthr))
        
        print(hpass.integrate('process', 'QCDPt').sum('msd1').values())
        
        print(hpass.axis('process').identifiers())
        
        fig = plt.figure()
        # #plt.suptitle(title)

        # ax1 = fig.add_subplot(4,1,(1,3))
        # plt.subplots_adjust(hspace=0)
        
        # Plot stacked hist                                                                                                   
        hist.plot1d(hpass, overlay='process', order=mc, stack=True, fill_opts={'color':colors,'edgecolor':'black'})
        plt.savefig(f'muon_CR/muCR_mcdata_Vmass{i}.pdf', bbox_inches='tight')
        plt.savefig(f'muon_CR/muCR_mcdata_Vmass{i}.png', bbox_inches='tight')
        """     
    
    
if __name__ == "__main__":
    main()
