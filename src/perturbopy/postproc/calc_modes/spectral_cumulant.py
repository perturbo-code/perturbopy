import numpy as np
import h5py as h5 
import matplotlib.pyplot as plt
from perturbopy.postproc.calc_modes.calc_mode import CalcMode

class SpectralCumulant(CalcMode):
    """
    A class to handle and analyze spectral functions computed using the cumulant expansion approach.

    Attributes:
    - T (numpy.ndarray): Array of temperatures corresponding to the spectral data.
    - w (numpy.ndarray): Array of energy values (ω) in electron volts (eV).
    - dw (float): Energy step size for the ω grid in eV.
    - Akw (numpy.ndarray): Spectral function data, indexed by k-point, band, temperature, and ω.
    """    
    def __init__(self, prefix):
        f = h5.File(f"{prefix}_spectral_cumulant.h5", "r") 
        print( [key for key in f.keys()],'\n' )
        Akw = f['spectral_functions']
        print( [key for key in Akw.keys()],'\n' )
        w_lower = np.asarray(f['w_lower_index'])
        w_upper = np.asarray(f['w_upper_index'])
        dw = np.asarray(f['wfreq_step_eV'])
        self.T = np.asanyarray(f['temperatures'])
        self.w = np.arange(w_lower,w_upper+1)*dw
        self.dw = dw
        Akw_np = []
        for key in Akw.keys():
            Akw_np.append(np.asarray(Akw[key]))
        f.close()
        self.Akw = np.asarray(Akw_np) 

    def plot_Aw(self, ik=0, it=0, ib=0):
        if (it>len(self.T)):
            print('Temperature index is out of range')
            return
        if ib>self.Akw[0].shape[0]:
            print('Band index is out of range')
            return
        if ik>len(self.Akw):
            print('k-point index is out of range')
            return 
        fig, ax = plt.subplots()
        self.plot_Aw_(plt, ax, ik, it, ib)
        return 
    
    def plot_Aw_(self, plt_loc, ax,ik=0, it=0, ib=0):
        """
        Plots the spectral function A(ω) for a given k-point index (ik), 
        temperature index (it), and band index (ib).

        Parameters:
        - ax : Axis on which to plot the bands.
        - ik (int): Index of the k-point in the grid.
        - it (int): Index of the temperature in the temperature array.
        - ib (int): Index of the band.

        Functionality:
        - Plots the normalized spectral function A(ω) as a function of energy (ω).
        - Adds labels, legends, and adjusts plot aesthetics for better visualization.

        Returns:
        None
        """
        if (it>len(self.T)):
            print('Temperature index is out of range')
            return
        if ib>self.Akw[0].shape[0]:
            print('Band index is out of range')
            return
        if ik>len(self.Akw):
            print('k-point index is out of range')
            return 

        A0w  = self.Akw[ik][ib,it,:]
        dw = self.dw 
        w = self.w 
        #normalize
        A0w = A0w /(np.sum(A0w)*dw)   
        #plot
        ax.plot(w,A0w,lw=2,label=f'T={ int(self.T[it])} K')
        ax.legend(fontsize=18)
        plt_loc.ylim([0,np.max(A0w)*1.1])    
        plt_loc.xlabel(r'$\omega-\epsilon_{nk}$ (eV)',fontsize=20)
        plt_loc.ylabel(r'A($\omega$) (eV$^{-1}$)',fontsize=20)
        plt_loc.xticks(fontsize=20)
        plt_loc.yticks(fontsize=20)
        plt_loc.tight_layout()
        return ax
    
    