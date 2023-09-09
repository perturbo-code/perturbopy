import numpy as np
from perturbopy.postproc.dbs.units_dict import UnitsDict
from perturbopy.postproc.calc_modes.calc_mode import CalcMode


class Trans(CalcMode):
    """
    Class representation of a Perturbo imsigma calculation.

    Attributes
    ----------
    temper : UnitsDict
        Dictionary of temperatures used in each configuration. The keys give the configuration number,
        and the values are floats giving the temperature (with units temper.units)
    
    chem_pot : UnitsDict
        Dictionary of chemical potentials used in each configuration. The keys
        give the configuration number, and the values are floats giving the 
        chemical potential (with units chem_pot.units)
    
    conc : UnitsDict
        Dictionary of carrier concentrations used in each configuration. The keys
        give the configuration number, and the values are floats giving the 
        concentration (with units conc.units)
    
    cond : UnitsDict
        Dictionary of conductivity tensors computed for each configuration. The keys are the 
        configuration number, and the values are 3x3 arrays giving the
        conductivity tensor (with units cond.units)
    
    mob : UnitsDict
        Dictionary of mobility tensors computed for each configuration. The keys give the
        configuration number, and the values are 3x3 arrays for the mobility tensor (with units mob.units)
    
    seebeck : UnitsDict
        Dictionary of Seebeck coefficient tensors computed for each configuration. The keys give the
        configuration number, and the values are 3x3 arrays giving theSeebeck coefficient tensor
        (with units seebeck.units). If not computed, this field will be None.
    
    thermal_cond : UnitsDict
        Dictionary of thermal conductivity tensors computed for each configuration. The keys give
        the configuration number, and the values are 3x3 arrays giving the thermal conductivity tensor
        (with units thermal_cond.units) If not computed, this field will be None.
    
    bfield : UnitsDict
        Dictionary of magnetic fields used in each configuration, if running a magnetic field transport
        calculation (if not, this field will be None). The keys are the configuration number, and the values
        are the 3-dimensional magnetic field (with units of bfield.units)
    
    cond_iter : UnitsDict
        Dictionary of dictionaries giving conductivity tensor computed at each iteration when solving
        the iterative BTE, if running an ITA calculation (if not, this field will be None).
        The keys of the top level dictionary are the configuration number, and the values are
        additional dictionaries with keys giving the iteration number and values giving the conductivity tensor
        at that iteration.

    """

    def __init__(self, pert_dict):
        """
        Constructor method

        Parameters
        ----------
        pert_dict : dict
            Dictionary containing the inputs and outputs from the transport calculation.

        """
        super().__init__(pert_dict)

        if self.calc_mode.split('-')[0] != 'trans':
            raise ValueError('Calculation mode for a Trans object should begin with "trans-"')

        self.temper = UnitsDict(units = self._pert_dict['trans'].pop('temperature units'))
        self.chem_pot = UnitsDict(units = self._pert_dict['trans'].pop('chemical potential units'))
        self.conc = UnitsDict(units = self._pert_dict['trans'].pop('concentration units'))
        self.cond = UnitsDict(units = self._pert_dict['trans'].pop('conductivity units'))
        self.mob = UnitsDict(units = self._pert_dict['trans'].pop('mobility units'))

        if 'Seebeck coefficient units' in self._pert_dict['trans'].keys():
            self.seebeck = UnitsDict(units = self._pert_dict['trans'].pop('Seebeck coefficient units'))
        else:
            self.seebeck = None

        if 'thermal conductivity units' in self._pert_dict['trans'].keys():
            self.thermal_cond = UnitsDict(units = self._pert_dict['trans'].pop('thermal conductivity units'))
        else:
            self.thermal_cond = None

        if 'magnetic field units' in self._pert_dict['trans'].keys():
            self.bfield = UnitsDict(units = self._pert_dict['trans'].pop('magnetic field units'))
        else:
            self.bfield = None

        num_config = self._pert_dict['trans'].pop('number of configurations')
        trans_dat = self._pert_dict['trans'].pop('configuration index')

        if 'number of iterations' in trans_dat[1].keys():
            self.cond_iter = UnitsDict(units = self.cond.units)
        else:
            self.cond_iter = None

        for config_idx in trans_dat.keys():
            self.temper[config_idx] = trans_dat[config_idx].pop('temperature')
            self.chem_pot[config_idx] = trans_dat[config_idx].pop('chemical potential')
            self.conc[config_idx] = trans_dat[config_idx].pop('concentration')
            self.cond[config_idx] = np.array(trans_dat[config_idx].pop('conductivity')['tensor'])
            self.mob[config_idx] = np.array(trans_dat[config_idx].pop('mobility')['tensor'])

            if self.seebeck != None:
                self.seebeck[config_idx] = np.array(trans_dat[config_idx].pop('Seebeck coefficient')['tensor'])
            
            if self.thermal_cond != None:
                self.seebeck[config_idx] = np.array(trans_dat[config_idx].pop('thermal conductivity')['tensor'])

            if self.bfield != None:
                self.bfield[config_idx] = np.array(trans_dat[config_idx].pop('magnetic field'))

            if self.cond_iter != None:
                num_iter = trans_dat[config_idx].pop('number of iterations')
                iteration_dat = trans_dat[config_idx].pop('iteration')
                conductivity_iter = {}

                for iteration in iteration_dat.keys():
                    conductivity_iter[iteration] = iteration_dat[iteration]['conductivity']['tensor']

                self.cond_iter[config_idx] = conductivity_iter
