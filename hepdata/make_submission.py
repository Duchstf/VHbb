from hepdata_lib import RootFileReader
from hepdata_lib import Submission, Variable, Table, Uncertainty

from array import array
import numpy as np
import pandas as pd
import json

from hepdata_lib import RootFileReader, Table, Variable, Uncertainty

def fig_1_2():
    reader = RootFileReader("data/fitDiagnosticsTest.root")
    
    table = Table("Signal strength fit")
    table.description = "Post-fit distributions for Signal and Background processes."
    table.location = "Figure 1 and 2" 
    
    # Configuration
    years = ["2016APV", "2016", "2017", "2018"]
    bins = ["VBin0fail", "VBin0pass", "VBin1fail", "VBin1pass", 
            "VBin2fail", "VBin2pass", "muonCRfail", "muonCRpass"]
            
    signals = ["WH", "ZH"]
    backgrounds = ["singlet", "ttbar", "VBFDipoleRecoilOn", "VbbVqq", 
                   "WjetsQQ", "Zjets", "Zjetsbb", "ggF", "qcd", "ttH"]
    all_procs = signals + backgrounds

    # Updated data store to include background totals
    data_store = {
        "x": [], 
        "category": [], 
        "data_obs": [], 
        "data_unc": [],
        "bkg_tot": [],     # New: Total Background Yield
        "bkg_unc": []      # New: Total Background Uncertainty
    }
    for proc in all_procs:
        data_store[proc] = []

    # Loop and Aggregate
    for bin_name in bins:
        for year in years:
            folder = f"shapes_fit_s/{bin_name}{year}"
            label = f"{bin_name}_{year}"
            
            # 1. Read Data
            try:
                data_points = reader.read_graph(f"{folder}/data")
                n_bins = len(data_points["x"])
                
                data_store["x"].extend(data_points["x"])
                data_store["category"].extend([label] * n_bins)
                data_store["data_obs"].extend(data_points["y"])
                data_store["data_unc"].extend(data_points["dy"]) 
            except:
                print(f"Skipping {folder} (Data not found)")
                continue

            # 2. Read Total Background (For Uncertainty)
            try:
                # This histogram contains the total Bkg yield + Post-fit Error
                bkg_hist = reader.read_hist_1d(f"{folder}/total_background")
                data_store["bkg_tot"].extend(bkg_hist["y"])
                data_store["bkg_unc"].extend(bkg_hist["dy"])
            except:
                # Fallback if missing (though it shouldn't be in FitDiagnostics)
                data_store["bkg_tot"].extend([0.0] * n_bins)
                data_store["bkg_unc"].extend([0.0] * n_bins)

            # 3. Read Individual MC Processes
            for proc in all_procs:
                try:
                    hist = reader.read_hist_1d(f"{folder}/{proc}")
                    data_store[proc].extend(hist["y"])
                except:
                    data_store[proc].extend([0.0] * n_bins)

    # --- Write Variables ---

    # Independent: Mass
    m_sd = Variable("$m_{SD}$", is_independent=True, is_binned=False, units="GeV")
    m_sd.values = data_store["x"]
    table.add_variable(m_sd)

    # Independent: Category
    cat = Variable("Category", is_independent=True, is_binned=False)
    cat.values = data_store["category"]
    table.add_variable(cat)

    # Dependent: Data
    data_var = Variable("Data", is_independent=False, is_binned=False, units="Events")
    data_var.values = data_store["data_obs"]
    unc_data = Uncertainty("Data Uncertainty", is_symmetric=False) 
    unc_data.values = data_store["data_unc"]
    data_var.add_uncertainty(unc_data)
    table.add_variable(data_var)

    # Dependent: Total Background (With Uncertainty)
    bkg_var = Variable("Total Background", is_independent=False, is_binned=False, units="Events")
    bkg_var.values = data_store["bkg_tot"]
    
    # TH1 errors are usually symmetric float values
    unc_bkg = Uncertainty("Background Uncertainty", is_symmetric=True)
    unc_bkg.values = data_store["bkg_unc"]
    bkg_var.add_uncertainty(unc_bkg)
    table.add_variable(bkg_var)

    # Dependent: Individual MC Processes
    for proc in all_procs:
        mc_var = Variable(proc, is_independent=False, is_binned=False, units="Events")
        mc_var.values = data_store[proc]
        table.add_variable(mc_var)

    return table

    
def table_1():

    table = Table("Table 1")
    table.description = "Fitted signal strengths"
    table.location = "Table 1"

    year = Variable("Year", is_independent=True, is_binned=False, units="")
    year.values = ["2016.0","2016.5","2017","2018","Combined"]
    table.add_variable(year)

    mu_VH = Variable("mu_VH", is_independent=False, is_binned=False, units="")
    mu_VH.values = [1.02, 1.34, 0.00, 1.04, 0.72]
    mu_VH_unc = Uncertainty("mu_VH uncertainty", is_symmetric=False)
    mu_VH_unc.set_values_from_intervals(zip([2.52,2.20,1.26,1.22,0.75],[2.23,1.87,1.18,1.10,0.71]),
                                         nominal=mu_VH.values)
    mu_VH.add_uncertainty(mu_VH_unc)
    table.add_variable(mu_VH)

    mu_VZ = Variable("mu_VZ", is_independent=False, is_binned=False, units="")
    mu_VZ.values = [-0.15, -0.83, 1.20, -0.40, 0.09]
    mu_VZ_unc = Uncertainty("mu_VZ uncertainty", is_symmetric=False)
    
    mu_VZ_unc.set_values_from_intervals(zip([1.77, 1.53, 1.28, 0.92, 0.63], 
                                            [1.77, 1.53, 1.28, 0.92, 0.63]),nominal=mu_VZ.values)
    mu_VZ.add_uncertainty(mu_VZ_unc)
    table.add_variable(mu_VZ)

    return table

def main():
    print("HEPData submission for HIG-24-017")

    submission = Submission()

    #Fig 1, Fig 2
    submission.add_table(fig_1_2())

    #Table 1
    submission.add_table(table_1())

    submission.create_files("HEPData-HIG-24-017", remove_old=True)

if __name__ == "__main__":
    main()
