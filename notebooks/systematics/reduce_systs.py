import numpy as np
from coffea import hist

# run this per msd2 bin
def reduce_scalevar(h, p, point=7):

    # Recommendation from LHC H WG is 3 point for VH, VBF and 7 point for ggF, ttH

    # Read in all the up histograms, conver to numpy arrays
    hists = np.array([h.integrate('systematic','scalevar_'+str(i)+'Up').values()[()] for i in range(0,9)])

    if point == 7:
        up = np.maximum(hists[0], hists[8])
        down = np.minimum(hists[0], hists[8])
        for i in range(1,8):
            up = np.maximum(up, hists[i])
            down = np.minimum(down, hists[i])

    elif point == 3:
        up = np.maximum(hists[0], hists[8])
        down = np.minimum(hists[0], hists[8])
        
    else:
        print("unknown point value")
    
    return up, down

# run this per msd2 bin
def reduce_pdfvar(h, p):

    # NNPDF31_nnlo_hessian_pdfas
    # https://lhapdfsets.web.cern.ch/current/NNPDF31_nnlo_hessian_pdfas/NNPDF31_nnlo_hessian_pdfas.info

    # Nominal (sigma^0)
    sigma0 = np.array(h.integrate('systematic','PDF_weight_0Up').values()[()])
    
    # Hessian PDF weights
    # Eq. 21 of https://arxiv.org/pdf/1510.03865v1.pdf  
    hists_pdf = np.array([h.integrate('systematic','PDF_weight_'+str(i)+'Up').values()[()] - sigma0 for i in range(1,101)])
    summed = np.sum(np.square(hists_pdf),axis=0)
    pdf_unc = np.sqrt( (1./99.) * summed ) 

    # alpha_S weights
    # Eq. 27 of same ref
    hists_aS = np.array([h.integrate('systematic','PDF_weight_'+str(i)+'Up').values()[()] for i in range(101,103)])
    as_unc = 0.5*(hists_aS[1] - hists_aS[0]) 

    # PDF + alpha_S weights
    # Eq. 28 of same ref
    pdfas_unc = np.sqrt( np.square(pdf_unc) + np.square(as_unc) ) 
    
    return sigma0 + pdfas_unc, sigma0 - pdfas_unc