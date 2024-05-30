from imports import *

def main():
    year=sys.argv[1]
    bb_WPs = { '2016APV_bb1': 0.9883, '2016_bb1': 0.9883, '2017_bb1': 0.9870, '2018_bb1':  0.9880}
    qcd_WPs = { '2016APV_qcd2': 0.0541, '2016_qcd2': 0.0882, '2017_qcd2': 0.0541, '2018_qcd2':  0.0741}

    bbthr = bb_WPs[f"{year}_bb1"]
    qcdthr = qcd_WPs[f"{year}_qcd2"]

    pickle_path = f'/uscms_data/d3/dhoang/VH_analysis/CMSSW_10_2_13/src/VHbb/output/pickle/vhbb_official/{year}/h.pkl' #Need to be defined manually
    sig_0 =  pickle.load(open(pickle_path,'rb')).integrate('region','signal').integrate('systematic', 'nominal').sum('genflavor1', 'msd1', overflow='under')
    sig = sig_0.integrate('qcd2', slice(0., qcdthr)).integrate('pt1', slice(450, None), overflow='over').integrate('msd2', slice(68,110))

    print(sig)
    
    all_H = ['WH', 'ZH', 'ggF', 'VBFDipoleRecoilOn', 'ttH']
    H_samples = [['WH', 'ZH'], 'ggF', 'VBFDipoleRecoilOn', 'ttH']
    H_labels = ['VH', 'ggF', 'VBF', 'ttH']
    label_region = ['Higgs BB Pass', 'Higgs BB Fail']
    width=0.9
    total_H = [sig.integrate('bb1', int_range=slice(bbthr,1.)).integrate('process', all_H).values()[()],
               sig.integrate('bb1', int_range=slice(0.,bbthr)).integrate('process', all_H).values()[()]]
    
    region_fraction = {}
    
    for i in range(len(H_labels)): #bb fail and bb pass
        
        sample = H_samples[i]
        fraction = []
        
        for j in range(len(label_region)):
        
            bb_int_range =slice(0.,bbthr) if label_region[j] == 'Higgs BB Fail' else slice(bbthr,1.)
            num_H = sig.integrate('bb1', int_range=bb_int_range).integrate('process', H_samples[i]).values()[()]
            
            total_H_local = sig.integrate('bb1', int_range=bb_int_range).integrate('process', all_H).values()[()]
            total_H[j] = total_H_local
            
            fraction.append(num_H/total_H_local)
        
        region_fraction[H_labels[i]] = np.asarray(fraction)
    
    fig, ax = plt.subplots()
    left = np.zeros(2)
    
    hep.cms.text("Preliminary")
    hep.cms.lumitext(f"{year} MC, {lumis[f'{year}']} $fb^{-1}$ (13 TeV)", fontsize=15)

    for samples, sample_fraction in region_fraction.items():
        p = ax.barh(label_region, sample_fraction, width, label=samples, left = left, align='center')
        left += sample_fraction
    
    y_axis_label = [f'Higgs BB Pass \n {round(float(total_H[0]),2)} Events', f'Higgs BB Fail \n {round(float(total_H[1]),2)} Events', ]
    y_pos=[0,1]
    ax.set_yticks(y_pos, labels=y_axis_label)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Higgs Process Fraction')

    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), edgecolor='black', frameon=True, borderpad=1)
    plt.savefig(f'plots/H_comp_{year}.pdf', bbox_inches='tight')
    plt.savefig(f'plots/H_comp_{year}.png', bbox_inches='tight')
        

main()