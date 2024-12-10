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


def gaussian_excitation(pump_pulse_file, occs_amplitude, time_window, pulse_fwhm, time_step, hole=False, finite_width=True):
    """
    The Gaussian pulse excitation for the Perturbo dynamics.
    Pump pulses for electrons and holes must be dumped into separate HDF5 files.
    In Perturbop, set `pump_pulse = .true.` and `pump_pulse_fname = ...` in pert.in.

    TODO: if gaussian_pulse is False, create only one snap in this function
    TODO: change the name of the function, pass the gaussian_pulse var

    TODO FORTRAN:
    Warning if norm dist is turned on with pump pulse

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

    pump_pulse_file.create_group('pump_pulse')

    # Time grid for the pulse
    t_grid = np.arange(0, time_window + time_step, time_step)

    num_steps = t_grid.shape[0]

    # Compute the Gaussian sigma from the full width at half maximum (FWHM)
    sigma = sigma_from_fwhm(pulse_fwhm)

    num_k, num_bands = occs_amplitude.shape

    delta_occs_array = np.zeros((num_bands, num_steps, num_k))

    # t - time, j - band, k - k-point
    delta_occs_array[:, :, :] = np.einsum('t,jk->ktj',
                                          delta_occs_pulse_coef(
                                              t_grid[:], time_step, time_window, sigma),
                                          occs_amplitude[:, :])

    get_size(delta_occs_array, 'delta(fnk(t))', dump=True)

    # Dump also the static occupations
    if 'pump_pulse' in pump_pulse_file:
        print('Warning: overwriting the pump_pulse group')
        del pump_pulse_file['pump_pulse']

    pulse_group = pump_pulse_file.create_group('pump_pulse')

    pulse_group.create_dataset('pulse_num_steps', data=num_steps - 1)
    pulse_group.create_dataset('time_step', data=time_step)

    if not hole:
        sign = 1
    else:
        sign = -1

    for itime in range(num_steps):
        pulse_group.create_dataset(f'pulse_snap_t_{itime}',
                                   data=sign * delta_occs_array[:, itime, :].T)

    if 'static_occupations' in pump_pulse_file:
        print('Warning: overwriting the static_occupations group')
        del pump_pulse_file['static_occupations']

    static_group = pump_pulse_file.create_group('static_occupations')

    if not hole:
        static_group.create_dataset('static_snap', data=occs_amplitude)
    else:
        static_group.create_dataset('static_snap', data=1.0 - occs_amplitude)

    t_dataset.timings['total'].stop()
    print(t_dataset)


def plot_static_occ(e_occs, elec_kpoint_array, elec_energy_array, h_occs, hole_kpoint_array, hole_energy_array, pump_energy):
    """
    Plot occupation on bands
    """
    # find where kz == 0
    idx = np.where((elec_kpoint_array[:, 1] == 0) & (elec_kpoint_array[:, 0] == 0))
    fig = plt.figure()
    plt.scatter(elec_kpoint_array[idx, 2], elec_energy_array[idx], s=0.5, c='black', alpha=0.5)
    plt.scatter(elec_kpoint_array[idx, 2], elec_energy_array[idx], s=e_occs[idx]
                * 1000 + 1e-10, c='red', alpha=0.5)
    idx = np.where((hole_kpoint_array[:, 1] == 0) & (hole_kpoint_array[:, 0] == 0))
    for i in range(np.size(hole_energy_array, axis=1)):
        plt.scatter(hole_kpoint_array[idx, 2], hole_energy_array[idx, i], s=0.5, c='black', alpha=0.5)
        plt.scatter(hole_kpoint_array[idx, 2], hole_energy_array[idx, i], s=h_occs[idx, i][0] * 1000 + 1e-10, c='red',
                    alpha=0.5)

    plt.savefig('2D_{:5.3f}.png'.format(pump_energy))
    plt.show()


def setup_pump_pulse(elec_pump_pulse_path, hole_pump_pulse_path,
                     elec_dyna_run, hole_dyna_run,
                     pump_energy,
                     pump_time_step=1.0,
                     pump_fwhm=20.0,
                     pump_energy_broadening=0.040,
                     pump_time_window=50.0,
                     gaussian_pulse=True):
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

    gaussian_pulse : bool, optional
        If True, the Gaussian pulse will be generated.
        If False, the pulse will be a step function.
    """

    print(f"{'PUMP PULSE PARAMETERS':*^70}")
    print(f"{'Pump pulse energy (eV):':>40} {pump_energy:.3f}")
    print(f"{'Pump pulse time step (fs):':>40} {pump_time_step:.3f}")
    print(f"{'Pump pulse FWHM (fs):':>40} {pump_fwhm:.3f}")
    print(f"{'Pump pulse energy broadening (eV):':>40} {pump_energy_broadening:.4f}")
    print(f"{'Pump pulse time window (fs):':>40} {pump_time_window:.3f}")
    print(f"{'Setup Gaussian pulse:':>40} {gaussian_pulse}")
    print("")

    # Check electron and hole time steps
    elec_dyna_time_step = elec_dyna_run[1].time_step
    hole_dyna_time_step = hole_dyna_run[1].time_step

    if np.abs(elec_dyna_time_step - pump_time_step) > 1e-6:
        warnings.warn(f'Electron dynamics time step ({elec_dyna_time_step:.3f} fs) '
                      f'is different from the pump pulse time step ({pump_time_step:.3f} fs).',
                      UserWarning)

    if np.abs(hole_dyna_time_step - pump_time_step) > 1e-6:
        warnings.warn(f'Hole dynamics time step ({hole_dyna_time_step:.3f} fs) '
                      f'is different from the pump pulse time step ({pump_time_step:.3f} fs).',
                      UserWarning)

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

    bandgap = CBM - VBM        # band gap (eV)

    print(f"{'BAND STRUCTURE PARAMETERS':*^70}")
    print(f"{'Valence band minimum (VBM) (eV):':>40} {VBM:.4f}")
    print(f"{'Conduction band maximum (CBM) (eV):':>40} {CBM:.4f}")
    print(f"{'Band gap (Eg) (eV):':>40} {bandgap:.4f}")
    print("")

    elec_nband = len(elec_dyna_run.bands)
    hole_nband = len(hole_dyna_run.bands)

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

    num_kpoints = ekidx.shape[0]

    print(f'\n---Intersect k-points: {num_kpoints} (among {elec_kpoint_array.shape[0]}'
          f' elec and {hole_kpoint_array.shape[0]} hole k-points)---\n')

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
            elec_occs_amplitude[ekidx, iband] += delta
            hole_occs_amplitude[hkidx, jband] += delta

    t_occs.timings['total'].stop()

    print(f"{'OCCUPATION SETUP':*^70}")
    print(f"{'Occupations setup time:':>40} {t_occs.timings['total'].t_delta:.4f} s")
    print(f"{'Electron bands:':>40} {elec_nband}")
    print(f"{'Hole bands:':>40} {hole_nband}")
    print(f"{'Max Electron Occupancy:':>40} {max(elec_occs_amplitude.ravel()):.4f}")
    print(f"{'Max Hole Occupancy:':>40} {max(hole_occs_amplitude.ravel()):.4f}")
    print(f"{'Electron concentration (a.u.):':>40} {sum(elec_occs_amplitude.ravel()):.4f}")
    print(f"{'Hole concentration (a.u.):':>40} {sum(hole_occs_amplitude.ravel()):.4f}")
    print(f"{'Difference:':>40} {sum(elec_occs_amplitude.ravel()) - sum(hole_occs_amplitude.ravel()):.4e}")
    print("")

    # Write to HDF5 file, replacing snap_t_1
    # Electron
    if os.path.exists(elec_pump_pulse_path):
        warnings.warn(f'Overwriting the pump_pulse file {elec_pump_pulse_path}.', UserWarning)
    if os.path.exists(hole_pump_pulse_path):
        warnings.warn(f'Overwriting the pump_pulse file {hole_pump_pulse_path}.', UserWarning)

    elec_pump_pulse_file = open_hdf5(elec_pump_pulse_path, mode='w')
    hole_pump_pulse_file = open_hdf5(hole_pump_pulse_path, mode='w')


    #gaussian_excitation(cdyna_file_elec, elec_occs_amplitude,
    #                    exit_time_window, pulse_fwhm, time_step)



    # Close
    close_hdf5(elec_pump_pulse_file)
    close_hdf5(hole_pump_pulse_file)

    exit()

    # TODO: check that time_step from gaas_cdyna.h5/dynamics_run_1/time_step_fs
    # is the same as time_step
    data = cdyna_file_elec['dynamics_run_1/snap_t_1']

    if gaussian_pulse:
        # for the Gaussian pulse, the initial step, which is snap_t_1 is zero
        data[...] = np.zeros_like(elec_occs_amplitude)
        gaussian_excitation(cdyna_file_elec, elec_occs_amplitude,
                            exit_time_window, pulse_fwhm, time_step)

    else:
        data[...] = elec_occs_amplitude

    exit()

    cdyna_file_elec.close()

    # Hole (need to write 1-f since Perturbo treats holes and electrons the same)
    cdyna_file_hole = h5py.File(os.path.join(
        cdyna_hole_path, prefix + '_cdyna.h5'), 'r+')

    # TODO: check that time_step from gaas_cdyna.h5/dynamics_run_1/time_step_fs
    # is the same as time_step
    data = cdyna_file_hole['dynamics_run_1/snap_t_1']

    print('\nVALUES:')
    print(np.max(np.ravel(elec_occs_amplitude)))
    print(np.max(np.ravel(hole_occs_amplitude)))
    if gaussian_pulse:
        data[...] = np.ones_like(hole_occs_amplitude)
        gaussian_excitation(cdyna_file_hole, hole_occs_amplitude,
                            exit_time_window, pulse_fwhm, time_step, hole=True)

    else:
        data[...] = 1.0 - hole_occs_amplitude

    cdyna_file_hole.close()

    print('\nPlotting...')
    plot_static_occ(elec_occs_amplitude, elec_kpoint_array, elec_energy_array, hole_occs_amplitude, hole_kpoint_array, hole_energy_array, pump_energy)


