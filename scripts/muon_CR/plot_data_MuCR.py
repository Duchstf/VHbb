from imports import *
from hist import Hist
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

def plot_h(h, labels, name, year):

    labels = copy.copy(labels)
    figtext = f'BB PASS' if name == 'bb_pass' else f'BB FAIL'
    if name == 'bb_pass': del labels['QCD'] #Delete QCD in the bb passing region
    mc = list(labels.values())
    
    # Create figure and axis
    fig = plt.figure()
    ax1 = fig.add_subplot(4, 1, (1, 3))
    plt.subplots_adjust(hspace=0)

    # Prepare MC histograms
    mc_hists = [h[{'process': process}] for process in mc]
    data_hist = h[{'process': 'muondata'}]

    # Integrate all MC histograms into one
    total_mc_hist = sum(mc_hists)
    total_mc_values = total_mc_hist.view().value
    total_mc_errors = np.sqrt(total_mc_hist.view().variance)  # Calculate standard deviation from variance

    # Plot stacked MC histograms
    colors = ['#94a4a2', '#832db6', '#bd1f01', 'sandybrown', 'steelblue']
    cumulative_hist = np.zeros_like(mc_hists[0].view().value)
    previous_cumulative_hist = np.zeros_like(mc_hists[0].view().value)
    for hist_data, color, label in zip(mc_hists, colors, mc):
        cumulative_hist += hist_data.view().value
        ax1.fill_between(hist_data.axes[0].centers, previous_cumulative_hist, cumulative_hist, step='mid', alpha=0.5, color=color, label=label)
        previous_cumulative_hist += hist_data.view().value

    # Plot MC statistical uncertainties as hatches
    mc_centers = total_mc_hist.axes[0].centers
    ax1.fill_between(mc_centers, total_mc_values - total_mc_errors, total_mc_values + total_mc_errors,
                     step='mid', alpha=0.2, color='none', edgecolor='gray', hatch='//', linewidth=0)
    # Overlay data
    hep.cms.label('Preliminary', lumi=lumis[year], data=True, year=year)
    data_hist.plot(ax=ax1, histtype='errorbar', color='k', marker='o', label='Data')
    ax1.get_xaxis().set_visible(False)
    
    ##I'll do anything for legends lol>>>>>>>>>> 
    legend = ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
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

    # Ratio plot
    ax2 = fig.add_subplot(4, 1, (4, 4))
    data_values = data_hist.view().value
    data_errors = np.sqrt(data_hist.view().variance)
    
    # Calculate the ratio and its errors
    ratio = data_values / total_mc_values
    ratio_errors =ratio * np.sqrt((data_errors / data_values)**2 + (total_mc_errors / total_mc_values)**2)
    
    ax2.errorbar(mc_centers, ratio, yerr=ratio_errors, fmt='o', color='k', markersize=5)
    ax2.set_ylabel(r'$Data/MC$')
    ax2.set_xlabel(r'Jet $m_{SD}$ [GeV]')
    ax2.set_xlim(ax1.get_xlim())
    ax2.set_ylim(0, 2)
    
    # Add horizontal line at 1
    ax2.axhline(1, color='black', linestyle='--', linewidth=1)
    
    plt.savefig(f'plots/{year}_muCR_{name}.pdf', bbox_inches='tight')
    # plt.savefig(f'plots/{year}_muCR_{name}.png', bbox_inches='tight')
    

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
        'W(Lep.)':'WLNu',
        #'Z + jets':'Zjets', #'#2ca02c'
        'QCD':'QCD',  
    }

    #Split into Jet 1 score b-tag passing/failing region. 
    hpass= sig.integrate('bb1',int_range=slice(bbthr,1.))
    hfail= sig.integrate('bb1',int_range=slice(0.,bbthr))

    #Convert to hist objects
    hfail=hfail.to_hist()
    hpass=hpass.to_hist()
    
    #print(hpass.axis('process').identifiers())
    plot_h(hpass, labels, 'bb_pass', year)
    plot_h(hfail, labels, 'bb_fail', year)

if __name__ == "__main__":
    main()
