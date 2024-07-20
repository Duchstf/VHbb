for year in 2016 2016APV 2017 2018; do
        cp templates/$year/${year}_FitSingle/plots/shapes_fit_s_wsfSingleFail.pdf plots/${year}_WtagCR_fitted_fail.pdf
        cp templates/$year/${year}_FitSingle/plots/shapes_fit_s_wsfSinglePass.pdf plots/${year}_WtagCR_fitted_pass.pdf
    done