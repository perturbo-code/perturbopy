import numpy as np
from perturbopy.postproc.calc_modes.calc_mode import CalcMode
from perturbopy.postproc.calc_modes.imsigma_config import ImsigmaConfig
from perturbopy.postproc.dbs.energy_db import EnergyDB
from perturbopy.postproc.dbs.recip_pt_db import RecipPtDB


class ImsigmaCalcMode(CalcMode):
    """
    Class representation of a Perturbo imsigma calculation.

    Parameters
    ----------
    pert_dict : dict
    Dictionary containing the inputs and outputs from the imsigma calculation.

    Attributes
    ----------


    """

    def __init__(self, pert_dict):
        """
        Constructor method

        """
        super().__init__(pert_dict)

        if self.calc_mode.split('-')[0] != 'imsigma':
            raise ValueError('Calculation mode for an ImsigmaCalcMode object should be "imsigma"')

        kpoint_units = self._pert_dict['imsigma'].pop('k-point coordinate units')
        num_kpoints = self._pert_dict['imsigma'].pop('number of k-points')
        kpoint = np.array(self._pert_dict['imsigma'].pop('k-point coordinates'))
        self.kpt = RecipPtDB.from_lattice(kpoint, kpoint_units, self.lat, self.recip_lat)
        
        energy_units = self._pert_dict['imsigma'].pop('energy units')
        num_bands = self._pert_dict['imsigma'].pop('number of bands')
        energies_dict = self._pert_dict['imsigma']['energy'].pop('band index')
        self.bands = EnergyDB(energies_dict, energy_units)

        self.units = {}
        self._dat = {}

        num_config = self._pert_dict['imsigma'].pop('number of configurations')
        config_dat = self._pert_dict['imsigma'].pop('configuration index')
        num_modes = self._pert_dict['imsigma'].pop('number of phonon modes')

        for key in ['temperature', 'chemical potential', 'Im(Sigma)']:
            self.units[key] = self._pert_dict['imsigma'].pop(f'{key} units')

        for config_idx in config_dat.keys():
            temperature = config_dat[config_idx].pop('temperature')
            chem_potential = config_dat[config_idx].pop('chemical potential')
            imsigma_dat = config_dat[config_idx].pop('band index')

            imsigma = {}
            imsigma_mode = {}

            for mode in np.arange(1, num_modes + 1):
                imsigma_mode[mode] = {}

            for band_index in imsigma_dat.keys():
                imsigma[band_index] = imsigma_dat[band_index]['Im(Sigma)']['total']
                for mode in np.arange(1, num_modes + 1):
                    imsigma_mode[mode][band_index] = imsigma_dat[band_index]['Im(Sigma)']['phonon mode'][mode]

            self._dat[config_idx] = ImsigmaConfig(temperature, chem_potential, imsigma, imsigma_mode)

    def __getitem__(self, index):
        """
        Method to index the ImsigmaCalcMode object

        Parameters
        ----------
        index : int
            The configuration number requested

        Returns
        -------
        imsigma_config: ImsigmaConfig
           Object containing information pertaining to the configuration being indexed

        """
        return self._dat[index]
