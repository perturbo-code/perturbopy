"""
Utils for ultrafast spectroscopy: transient absorption calculations
based on electron-phonon and hole-phonon dynamics simulations.
"""

import numpy as np
import warnings

from .memory import get_size
from .timing import TimingGroup
from .constants import energy_conversion_factor


def gaussian_delta(x, mu, sig):
    """
    Gaussian delta-function normalized to 1.

    Parameters
    ----------
    x : array
        Array of x-values.
    mu : float
        Mean of the Gaussian.
    sig : float
        Standard deviation of the Gaussian.
    """

    return np.exp(-0.5 * ((x - mu) / sig)**2) / (sig * np.sqrt(2 * np.pi))


def compute_trans_abs(elec_dyna_run,
                      hole_dyna_run,
                      de_grid=0.02,
                      energy_grid_max=None,
                      eta=0.02,
                      save_npy=True,
                      tr_dipoles_sqr=None):
    """
    Compute the transient absorption spectrum from the electron and hole dynamics simulations.
    The data is saved in the current directory as numpy binary files (.npy).

    Parameters
    ----------

    elec_dyna_run : DynaRun
        Object containing the results of the electron dynamics simulation.

    hole_dyna_run : DynaRun
        Object containing the results of the hole dynamics simulation.

    de_grid : float
        Energy grid spacing for the transient absorption spectrum. Affects the calculation time.

    energy_grid_max : float
        Maximum probe energy for the spectrum. If None, the maximum band energy difference (condunction-valence) is used.
        Minimum probe energy is always the bandgap.

    eta : float
        Broadening parameter for the Gaussian delta functions applied to the energy grid.

    save_npy : bool
        Save the data as numpy binary files (.npy).

    Returns
    -------

    time_grid : np.ndarray
        Time grid for the transient absorption spectrum.

    trans_abs_energy_grid : np.ndarray
        Energy grid for the transient absorption spectrum.

    dA_elec : np.ndarray
        Electron contribution to the transient absorption spectrum. Shape (num_energy_points, num_steps).

    dA_hole : np.ndarray
        Hole contribution to the transient absorption spectrum. Shape (num_energy_points, num_steps).

    tr_dipoles_sqr : np.ndarray
        Transition dipoles squared, valence-to-conduction for each k-point and band.
        Currently, the k-grid for dipoles must match the one for electrons.
        Experimental feature.
    """

    trun = TimingGroup('trans. abs.')
    trun.add('total', level=3).start()

    # Check the consistency of the two DynaRun objects

    # 1. Check the k-grids. q-grids can be different
    if not np.all(elec_dyna_run.boltz_kdim == hole_dyna_run.boltz_kdim):
        raise ValueError('The k-grids of the electron and hole simulations are different.')

    # 2. Check the simulation times
    if elec_dyna_run[1].num_steps != hole_dyna_run[1].num_steps:
        raise ValueError('The number of time steps of the electron and hole simulations are different.')
    if not np.allclose(elec_dyna_run[1].time_step, hole_dyna_run[1].time_step):
        raise ValueError('The time steps of the electron and hole simulations are different.')

    # 3. Check if the HDF5 cdyna files are still open
    if not elec_dyna_run._cdyna_file:
        raise ValueError('The electron dynamics HDF5 file (prefix_cdyna.h5) is closed.')
    if not hole_dyna_run._cdyna_file:
        raise ValueError('The hole dynamics HDF5 file (prefix_cdyna.h5) is closed.')

    time_step = elec_dyna_run[1].time_step
    num_steps = elec_dyna_run[1].num_steps
    time_grid = np.arange(0, num_steps * time_step, time_step)

    # Energy arrays
    elec_energy_array = elec_dyna_run._energies
    hole_energy_array = hole_dyna_run._energies

    # K-point arrays
    elec_kpoint_array = elec_dyna_run._kpoints
    hole_kpoint_array = hole_dyna_run._kpoints

    # Convert from Ry to eV
    elec_energy_array *= energy_conversion_factor('Ry', 'eV')
    hole_energy_array *= energy_conversion_factor('Ry', 'eV')

    # Number of bands
    elec_nband = len(elec_dyna_run.bands)
    hole_nband = len(hole_dyna_run.bands)

    # Band quantities
    VBM = np.max(hole_energy_array.ravel())
    CBM = np.min(elec_energy_array.ravel())
    bandgap = CBM - VBM

    energy_band_max = np.max(elec_energy_array.ravel())
    energy_band_min = np.min(hole_energy_array.ravel())

    if energy_grid_max is None:
        energy_grid_max = energy_band_max - energy_band_min
    elif energy_grid_max < bandgap:
        warnings.warn(f'The maximum probe energy specified ({energy_grid_max}) is smaller than the bandgap ({bandgap}).'
                      f' The maximum probe energy is set to max(cond)-min(val) {energy_band_max - energy_band_min}.')
        energy_grid_max = energy_band_max - energy_band_min

    # Energy grid for the transient absorption spectrum, affect the calculation time
    trans_abs_energy_grid = np.arange(bandgap, energy_grid_max, de_grid)
    num_energy_points = trans_abs_energy_grid.shape[0]
    print(f"{'Number of energy grid points':>30}: {num_energy_points}\n")

    # Find the interection between the electron and hole k-points
    print('Finding intersect k-points...')
    with trun.add('intersect kpoints') as t:
        ekidx, hkidx = np.intersect1d(
            elec_kpoint_array.view('float64,float64,float64').reshape(-1),
            hole_kpoint_array.view('float64,float64,float64').reshape(-1),
            return_indices=True)[1:]

        assert ekidx.size == hkidx.size, 'The number of intersect k-points is different.'

        num_intersect_kpoints = ekidx.size

    # Currently, the number of k-points of the transition dipoles
    # must be the same as the number of k-points of the electron energy array
    # In a future development, we will interpolate the transition dipoles on the fly
    if tr_dipoles_sqr is not None:
        elec_nband_tr_dip, hole_nband_tr_dip, num_k_tr_dip = tr_dipoles_sqr.shape

        if elec_nband_tr_dip != elec_nband or hole_nband_tr_dip != hole_nband \
                or num_k_tr_dip != elec_kpoint_array.shape[0]:
            raise ValueError(f'Wrong shape of the transition dipoles array: {tr_dipoles_sqr.shape}')
        else:
            print('\nTransition dipoles are provided.')
            print(f"{'Tr. dip. shape (num. elec. bands, num. hole bands, num. k points)':>30}: {tr_dipoles_sqr.shape}\n")

    # Compute all the Gaussian deltas on the intersect grid
    print('Computing Gaussian deltas...')
    with trun.add('compute deltas') as t:
        ALL_DELTAS = np.zeros((elec_nband, hole_nband, num_intersect_kpoints, num_energy_points))

        # Here, we vectorize over the k-points (ekidx, hkidx), the most expensive operation
        # Computation can still be vectorized for the energy points
        for iband in range(elec_nband):
            for jband in range(hole_nband):
                for ienergy in range(num_energy_points):
                    # Factor of two from spin.
                    ALL_DELTAS[iband, jband, :, ienergy] = \
                        gaussian_delta(elec_energy_array[ekidx, iband] -
                                       hole_energy_array[hkidx, jband],
                                       trans_abs_energy_grid[ienergy], eta)

                    if tr_dipoles_sqr is not None:
                        ALL_DELTAS[iband, jband, :, ienergy] *= 0.5 * tr_dipoles_sqr[iband, jband, :]
                    else:
                        ALL_DELTAS[iband, jband, :, ienergy] *= 2.0

        get_size(ALL_DELTAS, 'ALL_DELTAS', dump=True)
        print('')

    # Compute the transient absorption spectrum first for electrons and holes separately
    print('Computing transient absorption spectrum...')
    with trun.add('compute trans. abs.') as t:

        # Store all the occupations at once in numpy arrays
        # If the memory consumption is too high, one has to setup an explicit time loop for transient absorption
        e_occs_time_array = np.zeros((num_steps, num_intersect_kpoints, elec_nband))
        h_occs_time_array = np.zeros((num_steps, num_intersect_kpoints, hole_nband))

        # number of dynamics run
        ndyna = 1
        for istep in range(num_steps):

            # HDF5 dataset names
            elec_dset_name = f'dynamics_run_{ndyna}/snap_t_{istep}'
            hole_dset_name = f'dynamics_run_{ndyna}/snap_t_{istep}'

            # Read the occupations
            # We read them directly from the HDF5 files. Usually, this data is not stored in memory.
            elec_occs = elec_dyna_run._cdyna_file[elec_dset_name][()]
            # Minus sign for transient absorption, store only on the intersect grid, hence ekidx
            elec_occs = -elec_occs[ekidx, :]

            hole_occs = 1.0 - hole_dyna_run._cdyna_file[hole_dset_name][()]
            hole_occs = -hole_occs[hkidx, :]

            # Second index of elec_occs is band, one can select specific bands here
            e_occs_time_array[istep, :, :] = elec_occs[:, :]
            h_occs_time_array[istep, :, :] = hole_occs[:, :]

        get_size(e_occs_time_array, 'e_occs_time_array', dump=True)
        get_size(h_occs_time_array, 'h_occs_time_array', dump=True)
        print('')

        # Compute the transient absorption spectrum
        dA_elec = np.zeros((num_energy_points, num_steps))
        dA_hole = np.zeros((num_energy_points, num_steps))
        for iband in range(elec_nband):
            for jband in range(hole_nband):

                # Sum over intersect k-points
                dA_elec[:, :] += (np.tensordot(e_occs_time_array[:, :, iband],
                                  ALL_DELTAS[iband, jband, :, :], axes=((1), (0))) / num_intersect_kpoints).T

                dA_hole[:, :] += (np.tensordot(h_occs_time_array[:, :, jband],
                                  ALL_DELTAS[iband, jband, :, :], axes=((1), (0))) / num_intersect_kpoints).T

    # Save the data
    print('Saving the data...')
    with trun.add('save data') as t:
        pump_energy = elec_dyna_run.pump_pulse.pump_energy
        ending = f'_Epump_{pump_energy:.4f}'
        # Total transient absorption
        np.save(f'trans_abs_dA{ending}', dA_elec + dA_hole)
        # Electron contribution
        np.save(f'trans_abs_dA_elec{ending}', dA_elec)
        # Hole contribution
        np.save(f'trans_abs_dA_hole{ending}', dA_hole)
        # Time grid
        np.save(f'trans_abs_T{ending}', time_grid)
        # Energy grid
        np.save(f'trans_abs_E{ending}', trans_abs_energy_grid)

    trun.timings['total'].stop()
    print(trun)

    return time_grid, trans_abs_energy_grid, dA_elec, dA_hole
