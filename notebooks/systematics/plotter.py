# Jennet's plotter for coffea histograms
# March 26, 2021

import uproot3
import numpy as np
from coffea import hist

import matplotlib
import matplotlib.pyplot as plt

import mplhep as hep
plt.style.use([hep.style.CMS])
    
def plot_syst_allbkg(h, syst, xtitle, title, name):
    
    fig, ax = plt.subplots(6,1,sharex=True)
    fig.suptitle(title)
    axes = fig.axes

    mc = ['ttbar','singlet','VV']
    names = ['W(qq\')+jets','Z(qq)+jets','Z(bb)+jets','tt','t','VV']

    hists = []
    hists += [h.integrate('process','Wjets').integrate('genflavor1',int_range=slice(1,3))]
    hists += [h.integrate('process','Zjets').integrate('genflavor1',int_range=slice(1,4))]
    hists += [h.sum('genflavor1',overflow='all').integrate('process',p) for p in mc]

    for i in range(6):
        p = names[i]
  
        nom = hists[i].integrate('systematic','nominal')
        up = hists[i].integrate('systematic',syst+'Up')
        do = hists[i].integrate('systematic',syst+'Down')

        nom_array = hist.export1d(nom).numpy()[0]
        up_array = hist.export1d(up).numpy()[0]
        do_array = hist.export1d(do).numpy()[0]
        x = hist.export1d(nom).numpy()[1]
    
        up_ratio = np.array([up_array[i]/nom_array[i] for i in range(len(nom_array))])
        do_ratio = np.array([do_array[i]/nom_array[i] for i in range(len(nom_array))])

        np.nan_to_num(up_ratio,copy=False,nan=1,posinf=1)
        np.nan_to_num(do_ratio,copy=False,nan=1,posinf=1)

        axes[i].set_xlim(x[0],x[-1])
        axes[i].hist(x[:-1],weights=np.ones(len(up_ratio)),bins=x,histtype='step',color='gray',linestyle='--')
        axes[i].hist(x=x[:-1],weights=up_ratio,bins=x,histtype='step',color='blue',linewidth=2)
        axes[i].hist(x=x[:-1],weights=do_ratio,bins=x,histtype='step',color='red',linewidth=2)
    
        allweights_ratio = np.concatenate([up_ratio,do_ratio])
        ratmin = 0
        ratmax = 1
        if np.amin(allweights_ratio) > 0:
            ratmin = 0.95*np.amin(allweights_ratio)
        if np.amax(allweights_ratio) > 1:
            ratmax = 1.05*np.amax(allweights_ratio)
        axes[i].set_ylim(ratmin,ratmax)
        axes[i].set_ylabel(names[i],rotation=45)

    axes[5].set_xlabel(xtitle)     

    png_name = name+'.png'
    plt.savefig(png_name,bbox_inches='tight')

    pdf_name = name+'.pdf'
    plt.savefig(pdf_name,bbox_inches='tight')
    
def plot_syst_allsig(h, syst, xtitle, title, name):
    
    fig, ax = plt.subplots(5,1,sharex=True)
    fig.suptitle(title)
    axes = fig.axes

    mc = ['ggF','VBFDipoleRecoilOn','WH','ZH','ttH']
    names = ['ggF','VBFDipoleRecoilOn','WH','ZH','ttH']

    hists = [h.sum('genflavor1',overflow='all').integrate('process',p) for p in mc]

    for i in range(5):
        p = names[i]
  
        nom = hists[i].integrate('systematic','nominal')
        up = hists[i].integrate('systematic',syst+'Up')
        do = hists[i].integrate('systematic',syst+'Down')

        nom_array = hist.export1d(nom).numpy()[0]
        up_array = hist.export1d(up).numpy()[0]
        do_array = hist.export1d(do).numpy()[0]
        x = hist.export1d(nom).numpy()[1]
    
        up_ratio = np.array([up_array[i]/nom_array[i] for i in range(len(nom_array))])
        do_ratio = np.array([do_array[i]/nom_array[i] for i in range(len(nom_array))])

        np.nan_to_num(up_ratio,copy=False,nan=1,posinf=1)
        np.nan_to_num(do_ratio,copy=False,nan=1,posinf=1)

        axes[i].set_xlim(x[0],x[-1])
        axes[i].hist(x[:-1],weights=np.ones(len(up_ratio)),bins=x,histtype='step',color='gray',linestyle='--')
        axes[i].hist(x=x[:-1],weights=up_ratio,bins=x,histtype='step',color='blue',linewidth=2)
        axes[i].hist(x=x[:-1],weights=do_ratio,bins=x,histtype='step',color='red',linewidth=2)
    
        allweights_ratio = np.concatenate([up_ratio,do_ratio])
        ratmin = 0
        ratmax = 1
        if np.amin(allweights_ratio) > 0:
            ratmin = 0.95*np.amin(allweights_ratio)
        if np.amax(allweights_ratio) > 1:
            ratmax = 1.05*np.amax(allweights_ratio)
        axes[i].set_ylim(ratmin,ratmax)
        axes[i].set_ylabel(names[i],rotation=45)

    axes[4].set_xlabel(xtitle)     

    png_name = name+'.png'
    plt.savefig(png_name,bbox_inches='tight')

    pdf_name = name+'.pdf'
    plt.savefig(pdf_name,bbox_inches='tight')
    
def plot_syst_mucr(h, syst, xtitle, title, name):
    fig, ax = plt.subplots(6,1,sharex=True)
    fig.suptitle(title)
    axes = fig.axes

    mc = ['ttbar','singlet','VV']
    names = ['W(qq\')+jets','Z(qq)+jets','Z(bb)+jets','tt','t','VV']
    
    hists = []
    hists += [h.integrate('process','Wjets').integrate('genflavor',int_range=slice(1,3))]
    hists += [h.integrate('process','Zjets').integrate('genflavor',int_range=slice(1,4))]
    hists += [h.sum('genflavor',overflow='all').integrate('process',p) for p in mc]

    for i in range(6):
        p = names[i]

        nom = hists[i].integrate('systematic','nominal')
        up = hists[i].integrate('systematic',syst+'Up')
        do = hists[i].integrate('systematic',syst+'Down')

        nom_array = hist.export1d(nom).numpy()[0]
        up_array = hist.export1d(up).numpy()[0]
        do_array = hist.export1d(do).numpy()[0]
        x = hist.export1d(nom).numpy()[1]
    
        up_ratio = np.array([up_array[i]/nom_array[i] for i in range(len(nom_array))])
        do_ratio = np.array([do_array[i]/nom_array[i] for i in range(len(nom_array))])

        np.nan_to_num(up_ratio,copy=False,nan=1,posinf=1)
        np.nan_to_num(do_ratio,copy=False,nan=1,posinf=1)

        axes[i].set_xlim(x[0],x[-1])
        axes[i].hist(x[:-1],weights=np.ones(len(up_ratio)),bins=x,histtype='step',color='gray',linestyle='--')
        axes[i].hist(x=x[:-1],weights=up_ratio,bins=x,histtype='step',color='blue',linewidth=2)
        axes[i].hist(x=x[:-1],weights=do_ratio,bins=x,histtype='step',color='red',linewidth=2)
    
        allweights_ratio = np.concatenate([up_ratio,do_ratio])
        ratmin = 0
        ratmax = 1
        if np.amin(allweights_ratio) > 0:
            ratmin = 0.995*np.amin(allweights_ratio)
        if np.amax(allweights_ratio) > 1:
            ratmax = 1.005*np.amax(allweights_ratio)
        axes[i].set_ylim(ratmin,ratmax)
        axes[i].set_ylabel(names[i],rotation=45)
    
    axes[0].set_title(syst)
    axes[5].set_xlabel(xtitle)     

    png_name = name+'.png'
    plt.savefig(png_name,bbox_inches='tight')

    pdf_name = name+'.pdf'
    plt.savefig(pdf_name,bbox_inches='tight')
    
def plot_syst_scalevar(h, title, name):
    
    fig, ax = plt.subplots(5,1,sharex=True)
    fig.suptitle(title)
    axes = fig.axes

    mc = ['ggF','VBFDipoleRecoilOn','WH','ZH','ttH']
    names = ['ggF','VBFDipoleRecoilOn','WH','ZH','ttH']
    syst = ['scalevar_7pt','scalevar_3pt','scalevar_3pt','scalevar_3pt','scalevar_7pt']

    hists = [h.sum('genflavor1',overflow='all').integrate('process',p) for p in mc]

    for i in range(5):
        p = names[i]
  
        nom = hists[i].integrate('systematic','nominal')
        up = hists[i].integrate('systematic',syst[i]+'Up')
        do = hists[i].integrate('systematic',syst[i]+'Down')

        nom_array = hist.export1d(nom).numpy()[0]
        up_array = hist.export1d(up).numpy()[0]
        do_array = hist.export1d(do).numpy()[0]
        x = hist.export1d(nom).numpy()[1]
    
        up_ratio = np.array([up_array[i]/nom_array[i] for i in range(len(nom_array))])
        do_ratio = np.array([do_array[i]/nom_array[i] for i in range(len(nom_array))])

        np.nan_to_num(up_ratio,copy=False,nan=1,posinf=1)
        np.nan_to_num(do_ratio,copy=False,nan=1,posinf=1)

        axes[i].set_xlim(x[0],x[-1])
        axes[i].hist(x[:-1],weights=np.ones(len(up_ratio)),bins=x,histtype='step',color='gray',linestyle='--')
        axes[i].hist(x=x[:-1],weights=up_ratio,bins=x,histtype='step',color='blue',linewidth=2)
        axes[i].hist(x=x[:-1],weights=do_ratio,bins=x,histtype='step',color='red',linewidth=2)
    
        allweights_ratio = np.concatenate([up_ratio,do_ratio])
        ratmin = 0
        ratmax = 1
        if np.amin(allweights_ratio) > 0:
            ratmin = 0.95*np.amin(allweights_ratio)
        if np.amax(allweights_ratio) > 1:
            ratmax = 1.05*np.amax(allweights_ratio)
        axes[i].set_ylim(ratmin,ratmax)
        axes[i].set_ylabel(names[i],rotation=45)

    png_name = name+'.png'
    plt.savefig(png_name,bbox_inches='tight')

    pdf_name = name+'.pdf'
    plt.savefig(pdf_name,bbox_inches='tight')
    
def plot_syst_Vjets(h, p, xtitle, title, name):
    
    fig, ax = plt.subplots(6,1,sharex=True)
    fig.suptitle(title)
    axes = fig.axes

    names = ['d1K_NLO','d2K_NLO','d3K_NLO','d1kappa_EW']

    if p == 'Wjets':
        hists = h.integrate('genflavor1',int_range=slice(1,3)).integrate('process',p)
        names += ['W_d2kappa_EW','W_d3kappa_EW']
    if p == 'Zjets':
        hists = h.integrate('genflavor1',int_range=slice(1,4)).integrate('process',p)
        names += ['Z_d2kappa_EW','Z_d3kappa_EW']
                                           
    syst = names
        
    for i in range(6):
        p = names[i]
  
        nom = hists.integrate('systematic','nominal')
        up = hists.integrate('systematic',syst[i]+'Up')
        do = hists.integrate('systematic',syst[i]+'Down')

        nom_array = hist.export1d(nom).numpy()[0]
        up_array = hist.export1d(up).numpy()[0]
        do_array = hist.export1d(do).numpy()[0]
        x = hist.export1d(nom).numpy()[1]
    
        up_ratio = np.array([up_array[i]/nom_array[i] for i in range(len(nom_array))])
        do_ratio = np.array([do_array[i]/nom_array[i] for i in range(len(nom_array))])

        np.nan_to_num(up_ratio,copy=False,nan=1,posinf=1)
        np.nan_to_num(do_ratio,copy=False,nan=1,posinf=1)

        axes[i].set_xlim(x[0],x[-1])
        axes[i].hist(x[:-1],weights=np.ones(len(up_ratio)),bins=x,histtype='step',color='gray',linestyle='--')
        axes[i].hist(x=x[:-1],weights=up_ratio,bins=x,histtype='step',color='blue',linewidth=2)
        axes[i].hist(x=x[:-1],weights=do_ratio,bins=x,histtype='step',color='red',linewidth=2)
    
        allweights_ratio = np.concatenate([up_ratio,do_ratio])
        ratmin = 0
        ratmax = 1
        if np.amin(allweights_ratio) > 0:
            ratmin = 0.95*np.amin(allweights_ratio)
        if np.amax(allweights_ratio) > 1:
            ratmax = 1.05*np.amax(allweights_ratio)
        axes[i].set_ylim(ratmin,ratmax)
        axes[i].set_ylabel(names[i],rotation=45)

    png_name = name+'.png'
    plt.savefig(png_name,bbox_inches='tight')

    pdf_name = name+'.pdf'
    plt.savefig(pdf_name,bbox_inches='tight')
    

