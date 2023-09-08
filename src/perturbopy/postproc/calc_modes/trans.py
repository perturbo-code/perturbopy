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

        self.temperature = UnitsDict(units = self._pert_dict['trans'].pop('temperature units'))
        self.chem_pot = UnitsDict(units = self._pert_dict['trans'].pop('chemical potential units'))
        self.conc = UnitsDict(units = self._pert_dict['trans'].pop('concentration units'))
        self.cond = UnitsDict(units = self._pert_dict['trans'].pop('conductivity units'))
        self.mob = UnitsDict(units = self._pert_dict['trans'].pop('mobility units'))
        self.seebeck = UnitsDict(units = self._pert_dict['trans'].pop('Seebeck coefficient units'))
        self.thermal_cond = UnitsDict(units = self._pert_dict['trans'].pop('thermal conductivity units'))
        
        num_config = self._pert_dict['trans'].pop('number of configurations')
        trans_dat = self._pert_dict['trans'].pop('configuration index')

        if 'number of iterations' in trans_dat[1].keys():
            self.cond_iter = UnitsDict(units = self.cond.units)

        for config_idx in trans_dat.keys():
            self.temperature[config_idx] = trans_dat[config_idx].pop('temperature')
            self.chem_pot[config_idx] = trans_dat[config_idx].pop('chemical potential')
            self.conc[config_idx] = trans_dat[config_idx].pop('concentration')
            self.cond[config_idx] = np.array(trans_dat[config_idx].pop('conductivity')['tensor'])
            self.mob[config_idx] = np.array(trans_dat[config_idx].pop('mobility')['tensor'])
            self.seebeck[config_idx] = np.array(trans_dat[config_idx].pop('Seebeck coefficient')['tensor'])
            self.thermal_cond[config_idx] = np.array(trans_dat[config_idx].pop('thermal conductivity')['tensor'])

            if hasattr(self, 'cond_iter'):
                num_iter = trans_dat[config_idx].pop('number of iterations')
                iteration_dat = trans_dat[config_idx].pop('iteration')
                conductivity_iter = {}

                for iteration in iteration_dat.keys():
                    conductivity_iter[iteration] = iteration_dat[iteration]['conductivity']['tensor']

                self.cond_iter[config_idx] = conductivity_iter
