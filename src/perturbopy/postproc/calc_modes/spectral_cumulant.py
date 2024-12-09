import numpy as np
import h5py as h5
import matplotlib.pyplot as plt
from perturbopy.postproc.calc_modes.calc_mode import CalcMode
from perturbopy.io_utils.io import open_yaml, open_hdf5, close_hdf5
import os


class SpectralCumulant(CalcMode):
    """
    A class to handle and analyze spectral functions computed using the cumulant expansion approach.

    Parameters
    ----------
    prefix : str
        Prefix for the HDF5 file containing spectral function data.

    Attributes
    ----------
    temp_array : numpy.ndarray
        Array of temperatures corresponding to the spectral data.
    freq_array : numpy.ndarray
        Array of energy values (ω) in electron volts (eV).
    freq_step : float
        Energy step size for the ω grid in eV.
    Akw : numpy.ndarray
        Spectral function data, indexed by k-point, band, temperature, and ω.
    """
    def __init__(self, spectral_file, pert_dict):
        super().__init__(pert_dict)
        if self.calc_mode != 'spectral-cum':
            raise ValueError('Calculation mode for a BandsCalcMode object should be "spectral-cum"')

        Akw = spectral_file['spectral_functions']
        w_lower = np.asarray(spectral_file['w_lower_index'])
        w_upper = np.asarray(spectral_file['w_upper_index'])
        freq_step = np.asarray(spectral_file['wfreq_step_eV'])
        self.temp_array = np.asanyarray(spectral_file['temperatures'])
        self.freq_array = np.arange(w_lower, w_upper + 1) * freq_step
        self.freq_step = freq_step
        Akw_np = []
        for key in Akw.keys():
            Akw_np.append(np.asarray(Akw[key]))
        close_hdf5(spectral_file)

        self.Akw = np.asarray(Akw_np)

    @classmethod
    def from_hdf5_yaml(cls, spectral_path, yaml_path='pert_output.yml'):
        """
        Class method to create a SpectralCumulantCalcMode object from the HDF5 file and YAML file
        generated by a Perturbo calculation

        Parameters
        ----------
        popu_path : str
           Path to the HDF5 file generated by a spectral-cum calculation
        yaml_path : str, optional
           Path to the YAML file generated by a spectral-cum calculation

        Returns
        -------

        """

        if not os.path.isfile(spectral_path):
            raise FileNotFoundError(f'File {spectral_path} not found')
        if not os.path.isfile(yaml_path):
            raise FileNotFoundError(f'File {yaml_path} not found')

        spectral_file = open_hdf5(spectral_path)
        yaml_dict = open_yaml(yaml_path)

        return cls(spectral_file, yaml_dict)

    def plot_Aw(self, plt_loc, ax, ik=0, it=0, ib=0):
        """
        Plots the spectral function A(ω) for a given k-point, temperature, and band.

        Parameters
        ----------
        plt_loc : matplotlib.pyplot
            The pyplot module for setting global plot properties.
        ax : matplotlib.axes.Axes
            Axis on which to plot the spectral function.
        ik : int, optional
            Index of the k-point in the grid. Default is 0.
        it : int, optional
            Index of the temperature in the temperature array. Default is 0.
        ib : int, optional
            Index of the band. Default is 0.

        Returns
        -------
        matplotlib.axes.Axes
            The axis object with the plotted spectral function.

        Notes
        -----
        The spectral function is normalized before plotting. The plot includes
        labels, legends, and adjusted aesthetics for better visualization.
        """
        if it > len(self.temp_array):
            raise ValueError('Temperature index is out of range')
        if ib > self.Akw[0].shape[0]:
            raise ValueError('Band index is out of range')
        if ik > len(self.Akw):
            raise ValueError('k-point index is out of range')
        A0w = self.Akw[ik][ib, it, :]
        freq_step = self.freq_step
        freq_array = self.freq_array
        # normalize
        A0w = A0w / (np.sum(A0w) * freq_step)
        # plot
        ax.plot(freq_array, A0w, lw=2, label=f'T={ int(self.temp_array[it])} K')
        ax.legend(fontsize=18)
        plt_loc.ylim([0, np.max(A0w) * 1.1])
        plt_loc.xlabel(r'$\omega-\epsilon_{nk}$ (eV)', fontsize=20)
        plt_loc.ylabel(r'A($\omega$) (eV$^{-1}$)', fontsize=20)
        plt_loc.xticks(fontsize=20)
        plt_loc.yticks(fontsize=20)
        plt_loc.tight_layout()
        return ax
