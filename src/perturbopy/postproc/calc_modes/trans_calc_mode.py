import numpy as np
from perturbopy.postproc.calc_modes.calc_mode import CalcMode
from perturbopy.postproc.calc_modes.trans_config import TransConfig


class TransCalcMode(CalcMode):
    """
    Class representation of a Perturbo imsigma calculation.

    Parameters
    ----------
    pert_dict : dict
        Dictionary containing the inputs and outputs from the transport calculation.

    """

    def __init__(self, pert_dict):
        """
        Constructor method

        """
        super().__init__(pert_dict)

        if self.calc_mode.split('-')[0] != 'trans':
            raise ValueError('Calculation mode for a TransCalcMode object should begin with "trans-"')

        self.units = {}
        self._dat = {}

        for key in ['temperature', 'chemical potential', 'concentration', 'conductivity',
                    'mobility', 'Seebeck coefficient', 'thermal conductivity']:
            self.units[key] = self._pert_dict['trans'].pop(f'{key} units')

        num_config = self._pert_dict['trans'].pop('number of configurations')
        trans_dat = self._pert_dict['trans'].pop('configuration index')

        for config_idx in trans_dat.keys():
            temperature = trans_dat[config_idx].pop('temperature')
            chem_potential = trans_dat[config_idx].pop('chemical potential')
            concentration = trans_dat[config_idx].pop('concentration')
            conductivity = trans_dat[config_idx].pop('conductivity')['tensor']
            mobility = trans_dat[config_idx].pop('mobility')['tensor']
            seebeck_coeff = trans_dat[config_idx].pop('Seebeck coefficient')['tensor']
            thermal_conductivity = trans_dat[config_idx].pop('thermal conductivity')['tensor']

            num_iter = trans_dat[config_idx].pop('number of iterations')
            iteration_dat = trans_dat[config_idx].pop('iteration')
            conductivity_iter = {}

            for iteration in iteration_dat.keys():
                conductivity_iter[iteration] = iteration_dat[iteration]['conductivity']['tensor']

            self._dat[config_idx] = TransConfig(temperature, chem_potential, concentration, conductivity,
                                                mobility, seebeck_coeff, thermal_conductivity, conductivity_iter)

    def __getitem__(self, index):
        """
        Method to index the TransCalcMode object

        Parameters
        ----------
        index : int
            The configuration number requested

        Returns
        -------
        trans_config: TransConfig
           Object containing information pertaining to the configuration being indexed

        """
        return self._dat[index]
