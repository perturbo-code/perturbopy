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

from .memory import get_size
from .timing import TimingGroup
from .constants import energy_conversion_factor

# Plotting parameters
from .plot_tools import plotparams
plt.rcParams.update(plotparams)


def plot_occ_ampl(e_occs, elec_kpoint_array, elec_energy_array,
                  h_occs, hole_kpoint_array, hole_energy_array, pump_energy):
    """
    Plot occupation amplitude. Currently hardcoded to the section kz = 0.
    """

    # find where kz == 0

    fig, ax = plt.subplots(1, 1, figsize=(9, 6))

    # Plot electron occupations
    idx = np.where((elec_kpoint_array[:, 1] == 0) & (elec_kpoint_array[:, 0] == 0))
    for i in range(np.size(elec_energy_array, axis=1)):
        ax.scatter(elec_kpoint_array[idx, 2], elec_energy_array[idx], s=0.5, c='black', alpha=0.5)
        ax.scatter(elec_kpoint_array[idx, 2], elec_energy_array[idx], s=e_occs[idx]
                    * 1000 + 1e-10, c='red', alpha=0.5)

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
    """

    fig, ax = plt.subplots(1, 1, figsize=(9, 6))

    idx_elec = np.where((elec_kpoint_array[:, 1] == 0) & (elec_kpoint_array[:, 0] == 0))
    idx_hole = np.where((hole_kpoint_array[:, 1] == 0) & (hole_kpoint_array[:, 0] == 0))

    # Plot electron occupations
    elec_scat_list = []
    for i in range(np.size(elec_energy_array, axis=1)):
        ax.scatter(elec_kpoint_array[idx_elec, 2], elec_energy_array[idx_elec], s=0.5, c='black', alpha=0.5)
        scat_obj = ax.scatter(elec_kpoint_array[idx_elec, 2], elec_energy_array[idx_elec], s=0.0, c='red', alpha=0.5)
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
                               elec_delta_occs_array, elec_kpoint_array, elec_energy_array,
                               hole_delta_occs_array, hole_kpoint_array, hole_energy_array),
                        interval=100, repeat=False)

    # Save the animation to gif
    ani.save('pump_pulse.gif', writer='imagemagick')

    plt.show()


def update_scatter(anim_time, ax, time_step, idx_elec, idx_hole,
                   elec_scat_list, hole_scat_list,
                   elec_delta_occs_array, elec_kpoint_array, elec_energy_array,
                   hole_delta_occs_array, hole_kpoint_array, hole_energy_array):
    """
    Animate the pump pulse excitation for electrons and holes.

    Parameters
    ----------

    anim_time : float
        Animation time.

    ax : matplotlib.axes.Axes
        Axis for plotting the pump pulse excitation.
    """

    elec_num_bands = elec_delta_occs_array.shape[0]
    hole_num_bands = hole_delta_occs_array.shape[0]

    for i in range(elec_num_bands):
        elec_scat_list[i].set_sizes(elec_delta_occs_array[i, anim_time, idx_elec].flatten() * 2e4 + 1e-10)

    for i in range(hole_num_bands):
        hole_scat_list[i].set_sizes(hole_delta_occs_array[i, anim_time, idx_hole].flatten() * 2e4 + 1e-10)

    suffix = ax.get_title().split(';')[0]
    ax.set_title(f'{suffix}; Time: {anim_time * time_step:.2f} fs')
