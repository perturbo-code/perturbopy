import numpy as np
from perturbopy.postproc.dbs.units_dict import UnitsDict
from perturbopy.postproc.calc_modes.calc_mode import CalcMode


class Trans(CalcMode):
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

        self.temperatures = UnitsDict(units = self._pert_dict['trans'].pop('temperature units'))
        self.chem_potentials = UnitsDict(units = self._pert_dict['trans'].pop('chemical potential units'))
        self.concentrations = UnitsDict(units = self._pert_dict['trans'].pop('concentration units'))
        self.conductivities = UnitsDict(units = self._pert_dict['trans'].pop('conductivity units'))
        self.mobilities = UnitsDict(units = self._pert_dict['trans'].pop('mobility units'))
        self.seebeck_coeffs = UnitsDict(units = self._pert_dict['trans'].pop('Seebeck coefficient units'))
        self.thermal_conductivities = UnitsDict(units = self._pert_dict['trans'].pop('thermal conductivity units'))
        
        num_config = self._pert_dict['trans'].pop('number of configurations')
        trans_dat = self._pert_dict['trans'].pop('configuration index')

        if 'number of iterations' in trans_dat[1].keys():
            self.conductivities_iter = UnitsDict(units = self.conductivities.units)

        for config_idx in trans_dat.keys():
            self.temperatures[config_idx] = trans_dat[config_idx].pop('temperature')
            self.chem_potentials[config_idx] = trans_dat[config_idx].pop('chemical potential')
            self.concentrations[config_idx] = trans_dat[config_idx].pop('concentration')
            self.conductivities[config_idx] = np.array(trans_dat[config_idx].pop('conductivity')['tensor'])
            self.mobilities[config_idx] = np.array(trans_dat[config_idx].pop('mobility')['tensor'])
            self.seebeck_coeffs[config_idx] = np.array(trans_dat[config_idx].pop('Seebeck coefficient')['tensor'])
            self.thermal_conductivities[config_idx] = np.array(trans_dat[config_idx].pop('thermal conductivity')['tensor'])

            if hasattr(self, 'conductivities_iter'):
                num_iter = trans_dat[config_idx].pop('number of iterations')
                iteration_dat = trans_dat[config_idx].pop('iteration')
                conductivity_iter = {}

                for iteration in iteration_dat.keys():
                    conductivity_iter[iteration] = iteration_dat[iteration]['conductivity']['tensor']

                self.conductivities_iter[config_idx] = conductivity_iter
