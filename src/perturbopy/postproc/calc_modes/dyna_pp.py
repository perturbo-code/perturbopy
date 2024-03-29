import numpy as np
import os
from perturbopy.postproc.calc_modes.calc_mode import CalcMode
from perturbopy.io_utils.io import open_yaml, open_hdf5, close_hdf5


class DynaPP(CalcMode):
    """
    Class representation of a Perturbo dynamics-pp calculation.
    
    Attributes
    ----------

    times : np.ndarray
        Array of all the times from the dynamics-run simulations.
    
    time_units : str
        units for the times attribute

    energy_grid : np.ndarray
        Array of energies in the energy window for the calculation
    
    energy_units : str
        Units for the energy_grid attribute

    popu : np.ndarray
        Array of shape num_times x num_energies containing carrier populations over the energy_grid and times.

    """

    def __init__(self, popu_file, pert_dict):
        """
        Constructor method
        
        Parameters
        ----------
        pert_dict : dict
            Dictionary containing the inputs and outputs from the dynamics-pp calculation.
        """
        super().__init__(pert_dict)

        if self.calc_mode != 'dynamics-pp':
            raise ValueError('Calculation mode for a DynamicsPPCalcMode object should be "dynamics-pp"')

        self.time_units = 'fs'
        self.times = popu_file['times_fs'][()]
        self.energy_units = 'ev'
        self.energy_grid = popu_file['energy_grid_ev'][()]

        self.popu = np.zeros((len(self.energy_grid), len(self.times)))

        for itime, time in enumerate(self.times):
            self.popu[:, itime] = popu_file['energy_distribution'][f'popu_t{itime}'][()]

        if 'concentration' in pert_dict['dynamics-pp'].keys():
            self.conc = pert_dict['dynamics-pp'].pop('concentration')
            self.conc_units = pert_dict['dynamics-pp'].pop('concentation units')
        else:
            self.conc = None
            self.conc_units = None

        if 'velocity' in pert_dict['dynamics-pp'].keys():
            self.drift_vel = pert_dict['dynamics-pp'].pop('velocity')
            self.drift_vel_units = pert_dict['dynamics-pp'].pop('velocity units')
        else:
            self.drift_vel = None
            self.drift_vel_units = None

    @classmethod
    def from_hdf5_yaml(cls, popu_path, yaml_path='pert_output.yml'):
        """
        Class method to create a DynamicsRunCalcMode object from the HDF5 file and YAML file
        generated by a Perturbo calculation

        Parameters
        ----------
        popu_path : str
           Path to the HDF5 file generated by a dynamics-pp calculation
        yaml_path : str, optional
           Path to the YAML file generated by a dynamics-pp calculation

        Returns
        -------
        dyanamics_pp : DynaPP
           The DynaPP object generated from the HDF5 and YAML files

        """

        if not os.path.isfile(popu_path):
            raise FileNotFoundError(f'File {popu_path} not found')
        if not os.path.isfile(yaml_path):
            raise FileNotFoundError(f'File {yaml_path} not found')

        popu_file = open_hdf5(popu_path)
        yaml_dict = open_yaml(yaml_path)

        return cls(popu_file, yaml_dict)
