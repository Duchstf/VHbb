from hepdata_lib import RootFileReader
from hepdata_lib import Submission, Variable, Table, Uncertainty

from array import array
import numpy as np
import pandas as pd
import json

#Figures and tables numbers correspond to HIG-24-017 paper
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

    #

    #Table 1
    submission.add_table(table_1())

    submission.create_files("HEPData-HIG-24-017", remove_old=True)

if __name__ == "__main__":
    main()
