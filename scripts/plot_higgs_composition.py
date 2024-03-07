from imports import *

def main():
    
    pickle_path = '/uscms_data/d3/dhoang/VH_analysis/CMSSW_10_2_13/src/VHbb/output/pickle/vhbb_official_v4/2017/ParticleNet_msd.pkl' #Need to be defined manually
    sig_0 =  pickle.load(open(pickle_path,'rb')).integrate('region','signal').integrate('systematic', 'nominal').sum('genflavor1', 'msd1', overflow='all')
    sig = sig_0.integrate('pt1', int_range=slice(450., None), overflow='over').integrate('msd2',int_range=slice(68.,103.))
    
    bbthr = 0.9870
    
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
    
    print(H_samples)
    print(label_region)
    print(total_H)
    print(region_fraction)
    
    fig, ax = plt.subplots()
    left = np.zeros(2)
    
    hep.cms.text("Preliminary")
    hep.cms.lumitext(f"2017 MC, {lumis['2017']} $fb^{-1}$ (13 TeV)", fontsize=15)

    for samples, sample_fraction in region_fraction.items():
        p = ax.barh(label_region, sample_fraction, width, label=samples, left = left, align='center')
        left += sample_fraction
    
    y_axis_label = [f'Higgs BB Pass \n {round(float(total_H[0]),2)} Events', f'Higgs BB Fail \n {round(float(total_H[1]),2)} Events', ]
    y_pos=[0,1]
    ax.set_yticks(y_pos, labels=y_axis_label)
    ax.invert_yaxis()  # labels read top-to-bottom
    ax.set_xlabel('Signal Fraction')

    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), edgecolor='black', frameon=True, borderpad=1)
    plt.savefig(f'plots/H_comp.pdf', bbox_inches='tight')
    plt.savefig(f'plots/H_comp.png', bbox_inches='tight')
        

main()