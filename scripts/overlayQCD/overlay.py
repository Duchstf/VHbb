import uproot
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep

# Set the style
hep.style.use("CMS")

def extract_and_overlay(branch):
    
    withcut=None
    nocut=None

    # Open the ROOT file
    with uproot.open("WithCut.root") as file: withcut = file[f"shapes_prefit/{branch}/qcd"]
    with uproot.open("NoCut.root") as file: nocut = file[f"shapes_prefit/{branch}/qcd"]
    
    _, hist_egdes= withcut.to_numpy()
    
    #Normalize the values
    withcut_values = withcut.values()/(sum(withcut.values()))
    nocut_values = nocut.values()/(sum(nocut.values()))
    
    # Plotting the histogram using matplotlib
    plt.figure()
    plt.step(hist_egdes[:-1], withcut_values, where='post', label="QCD With Cut")
    plt.step(hist_egdes[:-1], nocut_values, where='post', label="QCD No Cut")

    # Adding labels and titles
    plt.xlabel(r"Jet 1 $m_{SD}$ [GeV]")
    plt.ylabel("A.U")
    hep.cms.text(f"{branch}")
    plt.legend()

    # Save or show the plot
    plt.savefig(f"overlay_{branch}.png")  # Save the plot

def main():
    
    branches = ['VBin0fail2017', 'VBin1fail2017', 'VBin2fail2017', 'VBin0pass2017', 'VBin1pass2017', 'VBin2pass2017']
    
    for branch in branches:
        extract_and_overlay(branch)
        
main()