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


def sigma_from_fwhm(fwhm):
    """
    Gaussian sigma: f(t) = A / ( sigma * sqrt(2pi)) exp(-(t-t0)^2 / (2sigma^2))
    """

    sigma = 1.0 / (2.0 * np.sqrt(2.0 * np.log(2.0))) * fwhm

    return sigma


def delta_occs_pulse_coef(t, dt, tw, sigma):
    """
    Additional occupation due to the pulse excitation.
    Assuming the Gaussian pulse shape, the occupation is increasing in
    time according to the error function.
    """

    numer = special.erf((t - tw / 2) / (np.sqrt(2) * sigma)) - \
        special.erf((t - dt - tw / 2) / (np.sqrt(2) * sigma))

    denom = special.erf(tw / 2 / (np.sqrt(2) * sigma))

    return 0.5 * numer / denom


def gaussian_excitation(pump_file, occs_amplitude, time_grid, time_window, pulse_fwhm, time_step, hole=False, finite_width=True):
    """
    The Gaussian pulse excitation for the Perturbo dynamics.
    Pump pulses for electrons and holes must be dumped into separate HDF5 files.
    In Perturbo, set `pump_pulse = .true.` and `pump_pulse_fname = ...` in pert.in.

    In Perturbo, step_0 will be initialized with `init_boltz_dist` parameter,
    the pump pulse will be applied starting from step_1.

    Parameters
    ----------

    pump_pulse_file : h5py.File
        The HDF5 file for the pump pulse excitation. Typically, `pump_pulse_Epump_...h5`.

    occs_amplitude : np.ndarray
        Electron or hole occupation amplitude: for each k-point, its _additional_ occupation in time
        is modeled as Gaussian with the given FWHM and amplitude.

    time_window : float
        The time window for the pump pulse (fs). During this time window, the pump pulse will be active.

    pulse_fwhm : float
        The full width at half maximum of the pump pulse (fs).

    time_step : float
        Time step in fs for the pump pulse generation.
        Note: the pump_time_step MUST match the one used in the dynamics run in Perturbo!

    hole : bool, optional
        If True, the pump pulse is for holes. Default is False (electrons).

    finite_width : bool, optional
        If True, the pulse is finite in time. If False, the pulse is a step function
        and occs_amplitude will be set as initial occupation.
    """

    print('\nCreating the pulse dataset...')
    t_dataset = TimingGroup('dataset')
    t_dataset.add('total', level=3).start()

    # Number of time steps
    num_steps = time_grid.shape[0]

    # Compute the Gaussian sigma from the full width at half maximum (FWHM)
    sigma = sigma_from_fwhm(pulse_fwhm)

    # Number of k-points and bands
    num_k, num_bands = occs_amplitude.shape

    # Additional occupatons for each step due to the pulse
    delta_occs_array = np.zeros((num_bands, num_steps, num_k))

    # A pre-factor for the pump pulse, num_steps steps
    pulse_coef = delta_occs_pulse_coef(time_grid[:], time_step, time_window, sigma)

    # t - time, j - band, k - k-point
    delta_occs_array[:, :, :] = np.einsum('t,jk->ktj', pulse_coef[:], occs_amplitude[:, :])

    # Print the size of the array since it can be large: num_bands * num_steps * num_k
    carrier = 'holes' if hole else 'electrons'
    get_size(delta_occs_array, f'delta(fnk(t)) {carrier}', dump=True)

    # Get the pump_pulse group
    pump_group = pump_file['pump_pulse_snaps']

    # 1 for electrons, -1 for holes
    sign = 1 if not hole else -1

    if finite_width:
        # Apply pump pulse starting from pulse_snap_t_1
        for itime in range(num_steps):
            pump_group.create_dataset(f'pulse_snap_t_{itime + 1}',
                                      data=sign * delta_occs_array[:, itime, :].T)

    else:
        pump_group.create_dataset('pulse_snap_t_1', data=sign * occs_amplitude)

    t_dataset.timings['total'].stop()

    print(f'---Pump pulse HDF5 writings time {carrier}: {t_dataset.timings["total"].t_delta:.4f} s---\n')


def plot_occ_ampl(e_occs, elec_kpoint_array, elec_energy_array,
                  h_occs, hole_kpoint_array, hole_energy_array, pump_energy):
    """
    Plot occupation amplitude. Currently hardcoded to the section kz = 0.
    """

    # find where kz == 0
    idx = np.where((elec_kpoint_array[:, 1] == 0) & (elec_kpoint_array[:, 0] == 0))

    fig, ax = plt.subplots(1, 1, figsize=(9, 6))
    plt.scatter(elec_kpoint_array[idx, 2], elec_energy_array[idx], s=0.5, c='black', alpha=0.5)
    plt.scatter(elec_kpoint_array[idx, 2], elec_energy_array[idx], s=e_occs[idx]
                * 1000 + 1e-10, c='red', alpha=0.5)

    idx = np.where((hole_kpoint_array[:, 1] == 0) & (hole_kpoint_array[:, 0] == 0))
    for i in range(np.size(hole_energy_array, axis=1)):
        plt.scatter(hole_kpoint_array[idx, 2], hole_energy_array[idx, i], s=0.5, c='black', alpha=0.5)
        plt.scatter(hole_kpoint_array[idx, 2], hole_energy_array[idx, i], s=h_occs[idx, i][0] * 1000 + 1e-10, c='red',
                    alpha=0.5)

    fsize = 16
    ax.set_title(f'Occupation amplitude for pump energy {pump_energy:.3f} eV')
    ax.set_xlabel('Electron Momentum $k_x$')
    ax.set_ylabel('Energy (eV)')

    plt.show()


def setup_pump_pulse(elec_pump_pulse_path, hole_pump_pulse_path,
                     elec_dyna_run, hole_dyna_run,
                     pump_energy,
                     pump_time_step=1.0,
                     pump_fwhm=20.0,
                     pump_energy_broadening=0.040,
                     pump_time_window=50.0,
                     finite_width=True,
                     ):
    """
    Setup the Gaussian pump pulse excitation for electrons and holes.
    Write into the pump_pulse.h5 HDF5 file.
    We use raw k-point and energy arrays as read from the HDF5 files for efficiency.
    All energies in eV, k points in crystal coordinates.

    Parameters
    ----------

    elec_pump_pulse_path : str
        Path to the HDF5 file for the pump pulse excitation for electrons.

    hole_pump_pulse_path : str
        Path to the HDF5 file for the pump pulse excitation for holes.

    elec_dyna_run : DynamicsRunCalcMode
        The DynaRun object for electrons from the HDF5 and YAML files.
        It is expected that the dyanmics was run only for one step, and only dynamics_run_1 group
        exists in prefix_cdyna.h5 and ZERO electron occupation is setup.

    hole_dyna_run : DynamicsRunCalcMode
        The DynaRun object for holes from the HDF5 and YAML files. See elec_dyna_run.

    pump_energy : float
        The energy of the pump pulse (eV)

    pump_time_step : float, optional
        Time step in fs for the pump pulse generation.
        Note: the pump_time_step MUST match the one used in the dynamics run in Perturbo!

    pump_fwhm : float, optional
        The full width at half maximum of the pump pulse (fs).

    pump_energy_broadening : float, optional
        Energy broadening of the pump pulse (eV).

    pump_time_window : float, optional
        The time window for the pump pulse (fs).
        During this time window, the pump pulse will be active.
        The number of the snapshots in the pump_pulse.h5 file will be
        equal to pump_time_window / pump_time_step.

    finite_width : bool, optional
        If True, the pulse is finite in time. If False, the pulse is a step function
        and occs_amplitude will be set as initial occupation.
    """

    print(f"{'PUMP PULSE PARAMETERS':*^70}")
    print(f"{'Pump pulse energy (eV):':>40} {pump_energy:.3f}")
    print(f"{'Pump pulse energy broadening (eV):':>40} {pump_energy_broadening:.4f}")
    print(f"{'Finite width:':>40} {finite_width}")
    if finite_width:
        print(f"{'Pump pulse time step (fs):':>40} {pump_time_step:.3f}")
        print(f"{'Pump pulse FWHM (fs):':>40} {pump_fwhm:.3f}")
        print(f"{'Pump pulse time window (fs):':>40} {pump_time_window:.3f}")
    print("")

    # Check electron and hole time steps
    elec_dyna_time_step = elec_dyna_run[1].time_step
    hole_dyna_time_step = hole_dyna_run[1].time_step

    if np.abs(elec_dyna_time_step - pump_time_step) > 1e-6 and finite_width:
        warnings.warn(f'Electron dynamics time step ({elec_dyna_time_step:.3f} fs) '
                      f'is different from the pump pulse time step ({pump_time_step:.3f} fs).',
                      RuntimeWarning)

    if np.abs(hole_dyna_time_step - pump_time_step) > 1e-6 and finite_width:
        warnings.warn(f'Hole dynamics time step ({hole_dyna_time_step:.3f} fs) '
                      f'is different from the pump pulse time step ({pump_time_step:.3f} fs).',
                      RuntimeWarning)

    # Raw energy and kpoint arrays for electrons and holes
    elec_energy_array = elec_dyna_run._energies
    elec_kpoint_array = elec_dyna_run._kpoints

    hole_energy_array = hole_dyna_run._energies
    hole_kpoint_array = hole_dyna_run._kpoints

    # Convert from Ry to eV
    elec_energy_array *= energy_conversion_factor('Ry', 'eV')
    hole_energy_array *= energy_conversion_factor('Ry', 'eV')

    VBM = max(hole_energy_array[:, -1])
    CBM = min(elec_energy_array[:, -1])
    bandgap = CBM - VBM

    elec_nband = len(elec_dyna_run.bands)
    hole_nband = len(hole_dyna_run.bands)

    print(f"{'BAND STRUCTURE PARAMETERS':*^70}")
    print(f"{'Num. of electron bands:':>40} {elec_nband}")
    print(f"{'Num. of hole bands:':>40} {hole_nband}")
    print(f"{'Valence band minimum (VBM) (eV):':>40} {VBM:.4f}")
    print(f"{'Conduction band maximum (CBM) (eV):':>40} {CBM:.4f}")
    print(f"{'Band gap (Eg) (eV):':>40} {bandgap:.4f}")
    print("")

    elec_occs_amplitude = np.zeros_like(elec_energy_array)
    hole_occs_amplitude = np.zeros_like(hole_energy_array)

    # A pre-factor for the pump pulse
    pump_factor = 1.0

    print('Computing the optically excited occupations...')
    t_occs = TimingGroup('Setup occupations')
    t_occs.add('total', level=3).start()

    # Here, we find the same k points for electrons and holes
    # one-to-one correspondence between elec and hole k points
    # We transform the 3D k-point arrays into 1D arrays of tuples
    # Then, intersect1d function is used to find the same k points
    # for both electrons and holes
    ekidx, hkidx = np.intersect1d(
        elec_kpoint_array.view('float64,float64,float64').reshape(-1),
        hole_kpoint_array.view('float64,float64,float64').reshape(-1),
        return_indices=True)[1:]

    # Iteratre over electron and hole bands
    # Even though, the for loops are inefficient in Python,
    # the number of bands is rarely more than 10, therefore
    # the vectorization is not necessary
    for iband in range(elec_nband):
        for jband in range(hole_nband):
            # diff. between elec and hole for a given elec branch iband and hole branch jband
            delta = pump_factor * \
                gaussian(elec_energy_array[ekidx, iband] - hole_energy_array[hkidx, jband],
                         pump_energy, pump_energy_broadening, hole_nband, elec_nband)

            # Only for the intersected k points, we add the delta occupation
            elec_occs_amplitude[ekidx, iband] += delta
            hole_occs_amplitude[hkidx, jband] += delta

    t_occs.timings['total'].stop()

    print(f"{'OCCUPATION SETUP':*^70}")
    print(f"{'Occupations setup time:':>40} {t_occs.timings['total'].t_delta:.4f} s")
    print(f"{'Intersect k-points:':>40} {ekidx.shape[0]} (total: {elec_kpoint_array.shape[0]} elec; {hole_kpoint_array.shape[0]} hole)")
    print(f"{'Max Electron Occupancy:':>40} {max(elec_occs_amplitude.ravel()):.4f}")
    print(f"{'Max Hole Occupancy:':>40} {max(hole_occs_amplitude.ravel()):.4f}")
    print(f"{'Electron concentration (a.u.):':>40} {sum(elec_occs_amplitude.ravel()):.4f}")
    print(f"{'Hole concentration (a.u.):':>40} {sum(hole_occs_amplitude.ravel()):.4f}")
    print(f"{'Difference:':>40} {sum(elec_occs_amplitude.ravel()) - sum(hole_occs_amplitude.ravel()):.4e}")
    print("")

    # Write to HDF5 file, replacing snap_t_1
    # Electron
    if os.path.exists(elec_pump_pulse_path):
        warnings.warn(f'Overwriting the pump_pulse file {elec_pump_pulse_path}.', RuntimeWarning)
    if os.path.exists(hole_pump_pulse_path):
        warnings.warn(f'Overwriting the pump_pulse file {hole_pump_pulse_path}.', RuntimeWarning)

    time_grid = np.arange(0, pump_time_window + pump_time_step, pump_time_step)
    num_steps = time_grid.shape[0]

    elec_pump_pulse_file = open_hdf5(elec_pump_pulse_path, mode='w')
    hole_pump_pulse_file = open_hdf5(hole_pump_pulse_path, mode='w')

    for h5f in [elec_pump_pulse_file, hole_pump_pulse_file]:
        h5f.create_group('pump_pulse_snaps')

        h5f.create_dataset('pump_energy', data=pump_energy)
        h5f['pump_energy'].attrs['units'] = 'eV'

        h5f.create_dataset('pump_energy_broadening', data=pump_energy_broadening)
        h5f['pump_energy_broadening'].attrs['units'] = 'eV'

        h5f.create_dataset('finite_width', data=finite_width)
        if finite_width:
            h5f.create_dataset('pump_fwhm', data=pump_fwhm)
            h5f.create_dataset('pump_time_window', data=pump_time_window)
            h5f.create_dataset('pump_num_steps', data=num_steps)
            h5f.create_dataset('pump_time_step', data=pump_time_step)
            h5f.create_dataset('pump_time_grid', data=time_grid)

        else:
            h5f.create_dataset('pump_fwhm', data=0.0)
            h5f.create_dataset('pump_time_window', data=0.0)
            h5f.create_dataset('pump_num_steps', data=0)
            h5f.create_dataset('pump_time_step', data=0.0)
            h5f.create_dataset('pump_time_grid', data=np.array([0.0]))

        h5f['pump_fwhm'].attrs['units'] = 'fs'
        h5f['pump_time_window'].attrs['units'] = 'fs'
        h5f['pump_time_step'].attrs['units'] = 'fs'
        h5f['pump_time_grid'].attrs['units'] = 'fs'

    gaussian_excitation(elec_pump_pulse_file, elec_occs_amplitude,
                        time_grid,
                        pump_time_window, pump_fwhm, pump_time_step,
                        hole=False, finite_width=finite_width)

    gaussian_excitation(hole_pump_pulse_file, hole_occs_amplitude,
                        time_grid,
                        pump_time_window, pump_fwhm, pump_time_step,
                        hole=True, finite_width=finite_width)

    # Close
    close_hdf5(elec_pump_pulse_file)
    close_hdf5(hole_pump_pulse_file)

    print('\nPlotting...')
    plot_occ_ampl(elec_occs_amplitude, elec_kpoint_array, elec_energy_array,
                    hole_occs_amplitude, hole_kpoint_array,
                    hole_energy_array, pump_energy)
