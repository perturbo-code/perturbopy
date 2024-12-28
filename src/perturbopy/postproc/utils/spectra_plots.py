"""
Utils for ultrafast spectroscopy: pump pulse generation and post-processing
"""

import os
import time
import numpy as np
import matplotlib.pyplot as plt
import warnings
from scipy import special

from perturbopy.io_utils.io import open_hdf5, close_hdf5

from matplotlib.animation import FuncAnimation
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

from .memory import get_size
from .timing import TimingGroup
from .constants import energy_conversion_factor

# Plotting parameters
from .plot_tools import plotparams

plt.rcParams.update(plotparams)


def gaussian(x, mu, sig, hole_nband, elec_nband):
    """
    Gaussian function normalized to unity max occupation
    """

    return np.exp(-0.5 * ((x - mu) / sig)**2) / (hole_nband * elec_nband)


def plot_occ_ampl(e_occs, elec_kpoint_array, elec_energy_array,
                  h_occs, hole_kpoint_array, hole_energy_array, pump_energy):
    """
    Plot occupation amplitude. Currently hardcoded to the section kz = 0.

    Parameters
    ----------
    e_occ : numpy.ndarray
        Electron occupations.

    elec_kpoint_array : numpy.ndarray
        Array of electron k-points.

    elec_energy_array : numpy.ndarray
        Array of electron energies.

    h_occs : numpy.ndarray
        Hole occupations.

    hole_kpoint_array : numpy.ndarray
        Array of hole k-points.

    hole_energy_array : numpy.ndarray
        Array of hole energies.

    pump_energy: float
        Pump energy in eV.
    """

    # find where kz == 0

    fig, ax = plt.subplots(1, 1, figsize=(9, 6))

    # Plot electron occupations
    idx = np.where((elec_kpoint_array[:, 1] == 0) & (elec_kpoint_array[:, 0] == 0))
    for i in range(np.size(elec_energy_array, axis=1)):
        ax.scatter(elec_kpoint_array[idx, 2], elec_energy_array[idx, i], s=0.5, c='black', alpha=0.5)
        ax.scatter(elec_kpoint_array[idx, 2], elec_energy_array[idx, i], s=e_occs[idx, i][0] * 1000 + 1e-10, c='red', alpha=0.5)

    # Plot hole occupations
    idx = np.where((hole_kpoint_array[:, 1] == 0) & (hole_kpoint_array[:, 0] == 0))
    for i in range(np.size(hole_energy_array, axis=1)):
        ax.scatter(hole_kpoint_array[idx, 2], hole_energy_array[idx, i], s=0.5, c='black', alpha=0.5)
        ax.scatter(hole_kpoint_array[idx, 2], hole_energy_array[idx, i], s=h_occs[idx, i][0] * 1000 + 1e-10, c='red',
                   alpha=0.5)

    fsize = 16
    ax.set_title(f'Occupation amplitude for pump energy {pump_energy:.3f} eV')
    ax.set_xlabel('Electron Momentum $k_x$')
    ax.set_ylabel('Energy (eV)')

    plt.show()


def animate_pump_pulse(time_step,
                       elec_delta_occs_array, elec_kpoint_array, elec_energy_array,
                       hole_delta_occs_array, hole_kpoint_array, hole_energy_array,
                       pump_energy):
    """
    Animate the pump pulse excitation for electrons and holes.
    Defines fig and ax, initializes scatter objects for electron and hole occupations, and calls update_scatter.

    Parameters
    ----------

    time_step : float
        Time step for the simulation. Only used for the title.

    elec_delta_occs_array : numpy.ndarray
        Array of electron occupation changes.

    elec_kpoint_array : numpy.ndarray
        Array of electron k-points.

    elec_energy_array : numpy.ndarray
        Array of electron energies.

    hole_delta_occs_array : numpy.ndarray
        Array of hole occupation changes.

    hole_kpoint_array : numpy.ndarray
        Array of hole k-points.

    hole_energy_array : numpy.ndarray
        Array of hole energies.

    pump_energy: float
        Pump energy in eV, used only in title.
    """

    fig, ax = plt.subplots(1, 1, figsize=(9, 6))

    idx_elec = np.where((elec_kpoint_array[:, 1] == 0) & (elec_kpoint_array[:, 0] == 0))
    idx_hole = np.where((hole_kpoint_array[:, 1] == 0) & (hole_kpoint_array[:, 0] == 0))

    # Plot electron occupations
    elec_scat_list = []
    for i in range(np.size(elec_energy_array, axis=1)):
        ax.scatter(elec_kpoint_array[idx_elec, 2], elec_energy_array[idx_elec, i], s=0.5, c='black', alpha=0.5)
        scat_obj = ax.scatter(elec_kpoint_array[idx_elec, 2], elec_energy_array[idx_elec, i], s=0.0, c='red', alpha=0.5)
        elec_scat_list.append(scat_obj)

    # Plot hole occupations
    hole_scat_list = []
    for i in range(np.size(hole_energy_array, axis=1)):
        ax.scatter(hole_kpoint_array[idx_hole, 2], hole_energy_array[idx_hole, i], s=0.5, c='black', alpha=0.5)
        obj = ax.scatter(hole_kpoint_array[idx_hole, 2], hole_energy_array[idx_hole, i], s=0, c='red', alpha=0.5)
        hole_scat_list.append(obj)

    fsize = 16
    ax.set_title(f'Pump energy {pump_energy:.3f} eV; Time: 0.0 fs')
    ax.set_xlabel('Electron Momentum $k_x$')
    ax.set_ylabel('Energy (eV)')

    ani = FuncAnimation(fig, update_scatter, frames=elec_delta_occs_array.shape[1],
                        fargs=(ax, time_step, idx_elec, idx_hole,
                               elec_scat_list, hole_scat_list,
                               elec_delta_occs_array, hole_delta_occs_array),
                        interval=100, repeat=False)

    # Save the animation to gif
    ani.save('pump_pulse.gif', writer='imagemagick')

    plt.show()


def update_scatter(anim_time, ax, time_step, idx_elec, idx_hole,
                   elec_scat_list, hole_scat_list,
                   elec_delta_occs_array, hole_delta_occs_array):
    """
    Animate the pump pulse excitation for electrons and holes.

    Parameters
    ----------

    anim_time : float
        Animation time.

    ax : matplotlib.axes.Axes
        Axis for plotting the pump pulse excitation.

    time_step: float
        Time step for the simulation. Only used for the title.

    idx_elec : numpy.ndarray
        Index for the electron k-points to plot.

    idx_hole : numpy.ndarray
        Index for the hole k-points to plot.

    elec_scat_list : list
        List of scatter objects for the electron occupations.

    hole_scat_list : list
        List of scatter objects for the hole occupations.

    elec_delta_occs_array : numpy.ndarray
        Array of electron occupation changes. Sizes of the scatter objects are set based on this array.

    hole_delta_occs_array : numpy.ndarray
        Array of hole occupation changes, similar to elec_delta_occs_array.
    """

    elec_num_bands = elec_delta_occs_array.shape[0]
    hole_num_bands = hole_delta_occs_array.shape[0]

    for i in range(elec_num_bands):
        elec_scat_list[i].set_sizes(elec_delta_occs_array[i, anim_time, idx_elec].flatten() * 2e4 + 1e-10)

    for i in range(hole_num_bands):
        hole_scat_list[i].set_sizes(hole_delta_occs_array[i, anim_time, idx_hole].flatten() * 2e4 + 1e-10)

    suffix = ax.get_title().split(';')[0]
    ax.set_title(f'{suffix}; Time: {anim_time * time_step:.2f} fs')


def plot_trans_abs_map(ax, time_grid, energy_grid, trans_abs,
                       num_contours=500, cmap=plt.cm.RdGy,
                       vmin=None, vmax=None):
    """
    Plot the transient absorption map as a function of time (x-axis) and energy (y-axis).
    Color represents the absorption intensity.

    Parameters
    ----------

    ax : matplotlib.axes.Axes
        Axis for plotting the transient absorption map.

    time_grid : numpy.ndarray
        Time grid for the transient absorption in fs.

    energy_grid : numpy.ndarray
        Energy grid for the transient absorption in eV.

    trans_abs : numpy.ndarray
        Transient absorption 2D array. Shape: (len(enery_grid), len(time_grid)).
        Can be full, electron, or hole contributions.

    num_contours : int
        Number of contours to plot.

    cmap : matplotlib.colors.Colormap
        Colormap for the plot.

    vmin : float
        Minimum value for the transient absorption.

    vmax : float
        Maximum value for the transient absorption.

    Returns
    -------
    ax : matplotlib.axes.Axes
        Axis for plotting the transient absorption map.
    """

    time_mesh, energy_mesh = np.meshgrid(time_grid, energy_grid)

    # Min and max values for plot
    if vmin is None:
        vmin = np.min(trans_abs)
    if vmax is None:
        vmax = np.max(trans_abs)

    ax.contourf(time_mesh, energy_mesh, trans_abs, num_contours, cmap=cmap, vmin=vmin, vmax=vmax)

    fsize = 24
    ax.set_xlabel('Time delay (fs)', fontsize=fsize)
    ax.set_ylabel('Energy (eV)', fontsize=fsize)

    # Add colorbar as a separate axis
    norm = Normalize(vmin=vmin, vmax=vmax)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='5%', pad=0.08)
    cbar = plt.colorbar(ScalarMappable(cmap=cmap, norm=norm), cax=cax, orientation='vertical', format='%.1f')
    cbar.set_label(r'$\Delta A$ (arb. units)', fontsize=fsize)

    return ax


def plot_occs_on_bands(ax, kpath, bands, first_el_band_idx,
                       pump_energy, pump_energy_broadening,
                       scale=0.2):
    """
    Plot the occupations created by a pump pulse on the bands.
    """


    # Total number of bands
    nband = len(bands)

    # Total number of k-points
    npoint = len(bands[1])

    # Occupation amplitude for each bands
    occs_amplitude_bands = np.zeros((nband, npoint))

    elec_band_list = list(range(first_el_band_idx, nband))
    hole_band_list = list(range(1, first_el_band_idx))

    elec_nband = len(elec_band_list)
    hole_nband = len(hole_band_list)

    # First, compute the occupations for every valence-conduction pair
    for i_elec_band in elec_band_list:
        for i_hole_band in hole_band_list:
            elec_band = bands[i_elec_band]
            hole_band = bands[i_hole_band]

            occ = gaussian(elec_band - hole_band,
                           pump_energy, pump_energy_broadening, hole_nband, elec_nband)

            occs_amplitude_bands[i_elec_band - 1, :] += occ
            occs_amplitude_bands[i_hole_band - 1, :] += occ

    max_occ = np.max(occs_amplitude_bands.ravel())
    factor = scale / max_occ
    occs_amplitude_bands *= factor

    # Plot the occupations on bands with fill_between
    # use kpath
    for iband in range(1, nband):

        band = bands[iband]

        occ_top = band + occs_amplitude_bands[iband - 1, :]
        occ_bottom = band - occs_amplitude_bands[iband - 1, :]

        if iband >= first_el_band_idx:
            color = 'red'
        else:
            color = 'blue'

        ax.fill_between(kpath, occ_top, occ_bottom, color=color)

    return ax
