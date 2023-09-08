import numpy as np
import os
from perturbopy.postproc.calc_modes.calc_mode import CalcMode
from perturbopy.io_utils.io import open_yaml, open_hdf5, close_hdf5

class DynPP(CalcMode):
    """
    Class representation of a Perturbo dynamics-pp calculation.

    Parameters
    ----------
    pert_dict : dict
        Dictionary containing the inputs and outputs from the transport calculation.

    """

    def __init__(self, popu_file, pert_dict):
        """
        Constructor method

        """
        super().__init__(pert_dict)

        if self.calc_mode != 'dynamics-pp':
            raise ValueError('Calculation mode for a DynamicsPPCalcMode object should be "dynamics-pp"')

        self._dat = {}
        self.time_units = 'fs'
        self.times = popu_file['times_fs'][()]
        self.energy_units = 'ev'
        self.energy_grid = popu_file['energy_grid_ev'][()]

        self.popu = np.zeros((len(self.energy_grid), len(self.times)))

        for itime, time in enumerate(self.times):
            self.popu[:, itime] = popu_file['energy_distribution'][f'popu_t{itime}'][()]


    @classmethod
    def from_hdf5_yaml(cls, popu_path, yaml_path='pert_output.yml'):
        """
        Class method to create a DynamicsRunCalcMode object from the HDF5 file and YAML file
        generated by a Perturbo calculation

        Parameters
        ----------
        yaml_path : str
           Path to the HDF5 file generated by a dynamics-run calculation
        yaml_path : str, optional
           Path to the YAML file generated by a dynamics-run calculation

        Returns
        -------
        dyanamics_run : DynamicsRunCalcMode
           The DynamicsRunCalcMode object generated from the HDF5 and YAML files

        """

        if not os.path.isfile(popu_path):
            raise FileNotFoundError(f'File {cdyna_path} not found')
        if not os.path.isfile(yaml_path):
            raise FileNotFoundError(f'File {yaml_path} not found')

        cdyna_file = open_hdf5(popu_path)
        yaml_dict = open_yaml(yaml_path)

        return cls(cdyna_file, yaml_dict)


    def popu_vs_t():
        """

        """
