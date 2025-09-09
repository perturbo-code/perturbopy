import os
import numpy as np
import warnings
from perturbopy.postproc.calc_modes.calc_mode import CalcMode
from perturbopy.postproc.dbs.recip_pt_db import RecipPtDB
from perturbopy.postproc.calc_modes.dyna_indiv_run import DynaIndivRun
from perturbopy.io_utils.io import open_yaml, open_hdf5, close_hdf5
from perturbopy.postproc.utils.timing import Timing, TimingGroup
from perturbopy.postproc.dbs.units_dict import UnitsDict

# for plotting
import matplotlib.pyplot as plt
from perturbopy.postproc.utils.spectra_plots import find_fwhm
from perturbopy.postproc.utils.plot_tools import plotparams
plt.rcParams.update(plotparams)


class DynaRun(CalcMode):
    """
    Class representation of a Perturbo dynamics-run calculation.

    TODO: better handling with snaps. Make it as property.
    Print a sensible message if snaps is None and access is attempted.
    Implement a getter and setter for snaps linked to HDF5 file.

    Attributes
    ----------
    kpt : RecipPtDB
       Database for the k-points used in the bands calculation.
    bands : UnitsDict
       Database for the band energies computed by the bands calculation.
    num_runs : int
        Number of separate simulations performed
    _cdyna_file : h5py.File
        HDF5 file containing the results of the dynamics-run calculation.
        We cannot store in RAM the whole file, so we will access the data as needed.
    _tet_file : h5py.File
        HDF5 file containing the results of the setup calculation required before the dynamics-run calculation.
    _kpoints : array
        Raw array of k-points. Shape (num_kpoints, 3)
    _energies : array
        Raw array of band energies. Shape (num_kpoints, num_bands)
    _dat : dict
        Python dictionary of DynaIndivRun objects containing results from each simulation
    """

    def __init__(self, cdyna_file, tet_file, pert_dict, read_snaps=True):
        """
        Constructor method

        Parameters
        ----------
        cdyna_file : h5py.File
            HDF5 file containing the results of the dynamics-run calculation.
            The file is kept open after the object is created.

        tet_file : h5py.File
            Tetrahedron HDF5 file obtained from the setup calculation.

        pert_dict : dict
            Dictionary containing the information from the dynamics-run YAML file.

        read_snaps : bool, optional
            Flag to read the snapshots from the HDF5 file.
            Reading the snapshots can be time-consuming and memory-intensive.

        """

        self.timings = TimingGroup("dynamics-run")

        self.read_snaps = read_snaps

        super().__init__(pert_dict)

        if self.calc_mode != 'dynamics-run':
            raise ValueError('Calculation mode for a DynamicsRunCalcMode object should be "dynamics-run"')

        self._cdyna_file = cdyna_file
        self._tet_file = tet_file

        self.pump_pulse = self._pert_dict['input parameters']['after conversion']['pump_pulse']

        if self.pump_pulse:
            if 'pump pulse' not in self._pert_dict['dynamics-run'].keys():
                raise ValueError('pump_pulse was set to .true. but no "pump pulse" key'
                                 ' was found in the dynamics-run section of the YAML file')

            pump_dict = self._pert_dict['dynamics-run']['pump pulse']
            self.pump_pulse = PumpPulse(pump_dict)

        kpoint = np.array(tet_file['kpts_all_crys_coord'][()])

        self.kpt = RecipPtDB.from_lattice(kpoint, "crystal", self.lat, self.recip_lat)

        energies = np.array(cdyna_file['band_structure_ryd'][()])
        energies_dict = {i + 1: np.array(energies[:, i]) for i in range(0, energies.shape[1])}
        self.bands = UnitsDict.from_dict(energies_dict, 'Ry')

        # k- and q-point grids
        self.boltz_kdim = np.array(self._pert_dict['input parameters']['after conversion']['boltz_kdim'])
        self.boltz_qdim = np.array(self._pert_dict['input parameters']['after conversion']['boltz_qdim'])

        # Raw arrays
        self._kpoints = kpoint
        self._energies = energies

        self._data = {}

        self.num_runs = cdyna_file['num_runs'][()]

        with self.timings.add('iterate_dyna') as t:

            for irun in range(1, self.num_runs + 1):
                dyn_str = f'dynamics_run_{irun}'

                num_steps = cdyna_file[dyn_str]['num_steps'][()]
                time_step = cdyna_file[dyn_str]['time_step_fs'][()]

                # a dynamics run must have at least one snap
                numk, numb = cdyna_file[dyn_str]['snap_t_1'][()].shape

                if read_snaps:
                    print(f'Reading snapshots for {dyn_str}...')
                    snap_t = np.zeros((numb, numk, num_steps), dtype=np.float64)

                    for itime in range(num_steps):
                        snap_t[:, :, itime] = cdyna_file[dyn_str][f'snap_t_{itime + 1}'][()].T
                else:
                    snap_t = None

                # Get E-field, which is only present if nonzero
                if "efield" in cdyna_file[dyn_str].keys():
                    efield = cdyna_file[dyn_str]["efield"][()]
                else:
                    efield = np.array([0.0, 0.0, 0.0])

                self._data[irun] = DynaIndivRun(num_steps, time_step, snap_t, time_units='fs', efield=efield)

    @classmethod
    def from_hdf5_yaml(cls, cdyna_path, tet_path, yaml_path='pert_output.yml', read_snaps=True):
        """
        Class method to create a DynamicsRunCalcMode object from the HDF5 file and YAML file
        generated by a Perturbo calculation

        Parameters
        ----------
        cdyna_path : str
           Path to the HDF5 file generated by a dynamics-run calculation
        tet_path : str
           Path to the HDF5 file generated by the setup calculation required before the dynamics-run calculation
        yaml_path : str, optional
           Path to the YAML file generated by a dynamics-run calculation

        Returns
        -------
        dyanamics_run : DynamicsRunCalcMode
           The DynamicsRunCalcMode object generated from the HDF5 and YAML files

        """

        if not os.path.isfile(yaml_path):
            raise FileNotFoundError(f'File {yaml_path} not found')
        if not os.path.isfile(cdyna_path):
            raise FileNotFoundError(f'File {cdyna_path} not found')
        if not os.path.isfile(tet_path):
            raise FileNotFoundError(f'File {tet_path} not found')

        yaml_dict = open_yaml(yaml_path)
        cdyna_file = open_hdf5(cdyna_path)
        tet_file = open_hdf5(tet_path)

        return cls(cdyna_file, tet_file, yaml_dict, read_snaps=read_snaps)

    def close_hdf5_files(self):
        """
        Method to close the HDF5 files: _cdyna_file and _tet_file.
        After the DynaRun object is created, the HDF5 files are kept open.
        One has to close them manually.
        """

        # Check if cdyan_file is open
        if self._cdyna_file:
            print(f'Closing {self._cdyna_file.filename}')
            close_hdf5(self._cdyna_file)

        # Check if tet_file is open
        if self._tet_file:
            print(f'Closing {self._tet_file.filename}')
            close_hdf5(self._tet_file)

    def __getitem__(self, index):
        """
        Method to index the DynamicsRunCalcMode object

        Parameters
        ----------
        index : int
            The dynamics run requested, indexing starting at 1

        Returns
        -------
        dynamics_run: DynamicsRun
           Object containing information for the dynamics run

        """
        if index <= 0 or index > len(self._data):
            raise IndexError("Index out of range")

        return self._data[index]

    def __len__(self):
        """
        Method to get the number of runs in DynamicsRunCalcMode object

        Returns
        -------
        num_runs : int
            Number of runs
        """

        return self.num_runs

    def __str__(self):
        """
        Method to print the dynamics run information
        """

        title = f' dynamics-run: {self.prefix} '
        text = f"{title:*^60}\n"

        text += f"{'Read snaps at init':>30}: {self.read_snaps}\n"
        text += f"{'Number of k-points':>30}: {self.kpt.points_cart.shape[1]}\n"
        nband = self._pert_dict['input parameters']['after conversion']['band_max'] - \
                self._pert_dict['input parameters']['after conversion']['band_min'] + 1
        text += f"{'Number of bands':>30}: {nband}\n"
        text += f"{'Hole':>30}: {self._pert_dict['input parameters']['after conversion']['hole']}\n"
        text += "\n"

        text += f"{'Number of runs':>30}: {self.num_runs}\n"

        for irun, dynamics_run in self._data.items():
            text += f"{'Dynamics run':>30}: {irun}\n"
            text += f"{'Number of steps':>30}: {dynamics_run.num_steps}\n"
            text += f"{'Time step (fs)':>30}: {dynamics_run.time_step}\n"
            text += f"{'Electric field (V/cm)':>30}: {dynamics_run.efield}\n"

        return text

    def extract_steady_drift_vel(self, dyna_pp_yaml_path):
        """
        Method to extract the drift velocities and equilibrium carrier concentrations

        Returns
        -------
        num_runs : int
            Number of runs
        """

        if not os.path.isfile(dyna_pp_yaml_path):
            raise FileNotFoundError(f'File {dyna_pp_yaml_path} not found')

        dyna_pp_dict = open_yaml(dyna_pp_yaml_path)

        vels = dyna_pp_dict['dynamics-pp']['velocity']
        concs = dyna_pp_dict['dynamics-pp']['concentration']

        step_number = 0

        steady_drift_vel = []
        steady_conc = []

        for irun, dynamics_run in self._data.items():

            step_number += dynamics_run.num_steps

            if np.allclose(dynamics_run.efield, np.array([0.0, 0.0, 0.0])):
                steady_drift_vel.append(None)
                steady_conc.append(concs[step_number])
            else:
                steady_drift_vel.append((-1.0) * vels[step_number])
                steady_conc.append(concs[step_number])

        return steady_drift_vel, steady_conc

    @staticmethod
    def to_cdyna_h5(prefix, band_structure_ryd, snap_array, time_step_fs,
                    path='.', new=True, overwrite=False, num_runs=1):
        """
        Write the dynamics data into the prefix_cdyna.h5 HDF5 file.
        Follows the script format of the Perturbo dynamics-run calculation.
        Currently implemented as a static method. The idea is that if we need to write an HDF5 cdyna
        file, it is forcfully different from an existing one, therefore, one or more
        attributes are different from the original cdyna file.

        Parameters
        ----------

        prefix : str
            Prefix of the HDF5 file. Same as prefix in any Perturbo calculation.

        band_structure_ryd : np.ndarray
            Band structure in Rydberg units. Shape: num_kpoints x num_bands

        snap_array : np.ndarray
            Array of carrier occupations. Shape: (num_steps, num_kpoints, num_bands)

        time_step_fs : float or np.ndarray
            Time step in fs. If float, the same time step is used for all runs.
            If np.ndarray, the time steps for each run are specified.

        path : str
            Path to the directory where the HDF5 file is saved. Default is the current directory.

        new : bool
            Flag to indicate if the file is new. Default is True.

        overwrite : bool
            Flag to indicate if the file is overwritten. Default is False.

        num_runs : int
            Number of dynamics_run runs. Default is 1.
        """

        trun = TimingGroup('write cdyna')
        trun.add('total', level=3).start()

        if not new:
            raise NotImplementedError("Only new files are supported")
        if num_runs != 1:
            raise NotImplementedError("Only num_runs=1 is supported")

        if isinstance(time_step_fs, (float, np.floating)):
            time_step_fs = np.array([time_step_fs])
        if time_step_fs.shape[0] != num_runs:
            raise ValueError("The number of time steps must be equal to num_runs")

        if path != '.':
            os.makedirs(path, exist_ok=True)

        new_cdyna_filename = os.path.join(path, f'{prefix}_cdyna.h5')

        if os.path.isfile(new_cdyna_filename):
            if overwrite:
                warnings.warn(f'File {new_cdyna_filename} already exists. Overwriting it.')
            else:
                raise FileExistsError(f'File {new_cdyna_filename} already exists. Set overwrite=True to overwrite it.')

        if snap_array.ndim != 3:
            raise ValueError("snap_array must be 3D. Shape: (num_steps, num_kpoints, num_bands)")
        else:
            num_steps_read, num_kpoints_read, num_bands_read = snap_array.shape
            print("Occupations shape to write:")
            print(f"num_steps: {num_steps_read}, num_kpoints: {num_kpoints_read}, num_bands: {num_bands_read}")

            if num_kpoints_read < num_steps_read or num_kpoints_read < num_bands_read:
                warnings.warn("The number of k-points of snap array to write is smaller "
                              "than the number of time steps or bands.")

        new_cdyna_file = open_hdf5(new_cdyna_filename, 'w')

        new_cdyna_file.create_dataset('band_structure_ryd', data=band_structure_ryd)
        new_cdyna_file['band_structure_ryd'].attrs['ryd2ev'] = 13.605698066

        new_cdyna_file.create_dataset('num_runs', data=num_runs)

        for irun in range(1, num_runs + 1):

            # In Perturbo, in dynamics_run_1, snap_t_ start from 0, where snap_t_0 is the initial state
            # In dynamics_run_2 and onwards, snap_t_ start from
            if irun == 1:
                offset = 0

                if snap_array.shape[0] == 1:
                    # duplicate the initial state
                    snap_array = np.vstack((snap_array, snap_array))
                num_steps = snap_array.shape[0] - 1

            else:
                offset = 1
                num_steps = snap_array.shape[0]

            dyn_str = f'dynamics_run_{irun}'
            new_cdyna_file.create_group(dyn_str)
            new_cdyna_file[dyn_str].create_dataset('num_steps', data=num_steps)
            new_cdyna_file[dyn_str].create_dataset('time_step_fs', data=time_step_fs[irun - 1])

            for itime in range(snap_array.shape[0]):
                new_cdyna_file[dyn_str].create_dataset(f'snap_t_{itime + offset}', data=snap_array[itime, :, :])

        close_hdf5(new_cdyna_file)

        trun.timings['total'].stop()
        print(f'{"Total time to write cdyna":>30}: {trun.timings["total"].total_runtime} s')
        print()


class PumpPulse():
    """
    Class for pump pulse excitation.

    Attributes
    ----------

    pump_energy : float
        Energy of the pump pulse excitation in eV.

    spectral_width_fwhm : float
        Energy broadening FWHM of the pump pulse excitation in eV.

    pump_duration_fwhm : float
        Duration FWHM of the pump pulse excitation in fs.

    num_steps : int
        Number of steps in the pump pulse excitation.

    pump_factor : float
        Factor for the pump pulse excitation.

    pump_time_step : float
        Time step of the pump pulse excitation in fs.

    num_bands : int
        Number of bands in the pump pulse excitation. Tailored for the Perturbo dynamics-run calculation.

    num_kpoints : int
        Number of k-points in the pump pulse excitation. Tailored for the Perturbo dynamics-run calculation.

    carrier_number_array : np.ndarray
        Additional carrier number array for the pump pulse excitation.

    optional_params : dict
        Optional parameters for the pump pulse excitation.
        Specific to the pulse shape. 10 parameters allocated.

    hole : bool
        Flag to indicate if the pump pulse excitation is for the hole.
        Must be the same as in the ultrafast simulation.

    time_profile : np.ndarray
        Array of time profile for the pump pulse excitation. First column is time in fs, second column is the time profile.

    energy_profile : np.ndarray
        Array of energy profile for the pump pulse excitation. First column is energy in eV, second column is the energy profile
    """

    def __init__(self, pump_dict):
        """
        Constructor method

        Parameters
        ----------
        pump_dict : dict
            Dictionary containing the pump pulse excitation parameters.
        """

        # TODO: use UnitsDict for entries in pump_dict
        # CURRENTLY, UnitsDict seems to be ill-suited for floats with units
        # input_dict = {'pump_energy': pump_dict['pump_energy']}
        # self.pump_energy = UnitsDict.from_dict(input_dict, units='eV')

        self.pump_energy = pump_dict['pump_energy']
        self.pump_energy_units = pump_dict['pump_energy units']

        self.spectral_width_fwhm = pump_dict['pump_spectral_width_fwhm']
        self.spectral_width_fwhm_units = pump_dict['pump_spectral_width_fwhm units']

        self.pump_duration_fwhm = pump_dict['pump_duration_fwhm']
        self.pump_duration_fwhm_units = pump_dict['pump_duration_fwhm units']

        self.num_steps = pump_dict['num_steps']

        self.pump_factor = pump_dict['pump_factor']

        self.pump_time_step = pump_dict['pump_time_step']
        self.pump_time_step_units = pump_dict['pump_time_step units']

        self.num_bands = pump_dict['num_bands']
        self.num_kpoints = pump_dict['num_kpoints']

        self.carrier_number_array = \
            np.array(pump_dict['pump pulse carrier number'])
        self.carrier_number_units = pump_dict['carrier_number units']

        # Optional parameters are specific to the pump pulse excitation
        # 10 parameters allocated
        self.optional_params = pump_dict['optional_params']

        self.hole = pump_dict['hole']

        # arrays of time and energy profile
        self.time_profile = np.array(pump_dict['time_profile'])
        self.energy_profile = np.array(pump_dict['energy_profile'])

    def __str__(self):
        """
        Method to print the pump pulse excitation parameters.
        """

        carrier = 'hole' if self.hole else 'electron'
        title = f'Pump pulse parameters ({carrier})'
        text = f'{title:*^60}\n'
        text += f"{f'Pump energy ({self.pump_energy_units})':>30}: {self.pump_energy:.4f}\n"
        text += f"{f'Energy broadening FWHM ({self.spectral_width_fwhm_units})':>30}: {self.spectral_width_fwhm:.4f}\n"
        text += f"{f'Pulse duration FWHM ({self.pump_duration_fwhm_units})':>30}: {self.pump_duration_fwhm:.4f}\n"
        text += f"{'Pump factor':>30}: {self.pump_factor:.3e}\n"
        text += f"{'Number of steps':>30}: {self.num_steps}\n"
        text += f"{f'Time step ({self.pump_time_step_units})':>30}: {self.pump_time_step}\n"
        text += f"{'Hole':>30}: {self.hole}\n"

        return text

    def plot_time_profile(self, ax=None):
        """
        Plot the pump pulse time profile.
        """

        if self.time_profile is None:
            warnings.warn('No time profile found for the pump pulse')
            return None

        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(10, 8))

        # Find the FWHM and half-maximum of the time profile
        time_left_FWHM, time_right_FWHM, time_half_max = find_fwhm(self.time_profile[:, 0], self.time_profile[:, 1])

        ax.plot(self.time_profile[:, 0], self.time_profile[:, 1])
        ax.plot([time_left_FWHM, time_right_FWHM], [time_half_max, time_half_max], marker='o', color='tab:red', lw=3, label='FWHM')
        ax.set_xlabel('Time (fs)', fontsize=24)
        ax.set_ylabel('Time Gaussian', fontsize=24)
        ax.set_title(f'Time profile (FWHM = {time_right_FWHM - time_left_FWHM:.4f} fs)')
        ax.legend()
        ax.grid()

        return ax

    def plot_energy_profile(self, ax=None):
        """
        Plot the pump pulse energy profile.
        """

        if self.energy_profile is None:
            warnings.warn('No energy profile found for the pump pulse')
            return None

        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(10, 8))

        # Find the FWHM and half-maximum of the energy profile
        energy_left_FWHM, energy_right_FWHM, energy_half_max = find_fwhm(self.energy_profile[:, 0], self.energy_profile[:, 1])

        ax.plot(self.energy_profile[:, 0], self.energy_profile[:, 1])
        ax.plot([energy_left_FWHM, energy_right_FWHM], [energy_half_max, energy_half_max], marker='o', color='tab:red', lw=3, label='FWHM')
        ax.axvline(self.pump_energy, color='gray', lw=3, label='Pump energy')
        ax.set_xlabel('Energy (eV)', fontsize=24)
        ax.set_ylabel('Energy Gaussian', fontsize=24)
        ax.set_title(f'Energy profile (FWHM = {energy_right_FWHM - energy_left_FWHM:.4f} eV)')
        ax.legend(loc='upper right')
        ax.grid()

        return ax
