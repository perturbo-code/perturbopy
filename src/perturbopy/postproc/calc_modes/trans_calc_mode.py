import numpy as np
from perturbopy.postproc.calc_modes.calc_mode import CalcMode
from perturbopy.postproc.dbs.phys_quantity_array import PhysQuantityArray, TensorPhysQuantityArray
from perturbopy.postproc.dbs.recip_pt_db import RecipPtDB
from perturbopy.postproc.utils.plot_tools import plot_dispersion, plot_recip_pt_labels, plot_vals_on_bands

class TransCalcMode(CalcMode):
    """
    Class representation of a Perturbo imsigma calculation.

    Parameters
    ----------
    pert_dict : dict
    Dictionary containing the inputs and outputs from the transport calculation.

    Attributes
    ----------


    """

    def __init__(self, pert_dict):
        """
        Constructor method

        """
        super().__init__(pert_dict)

        if self.calc_mode.split('-')[0] != 'trans':
            raise ValueError('Calculation mode for a TransCalcMode object should begin with "trans-"')

        temperature_units = self._pert_dict['trans'].pop('temperature units')
        chem_potential_units = self._pert_dict['trans'].pop('chemical potential units')
        concentration_units = self._pert_dict['trans'].pop('concentration units')
        conductivity_units = self._pert_dict['trans'].pop('conductivity units')
        mobility_units = self._pert_dict['trans'].pop('mobility units')
        seebeck_coeff_units = self._pert_dict['trans'].pop('Seebeck coefficient units')
        thermal_conductivity_units = self._pert_dict['trans'].pop('thermal conductivity units')

        num_config = self._pert_dict['trans'].pop('number of configurations')

        trans_dat = self._pert_dict['trans'].pop('configuration index')

        temperature = {}
        chem_potential = {}
        concentration = {}
        conductivity = {}
        mobility = {}
        seebeck_coeff = {}
        thermal_conductivity = {}

        num_iter = {}
        conductivity_convergence = {}

        for config_idx in trans_dat.keys():
            temperature[config_idx] = trans_dat[config_idx].pop('temperature')
            chem_potential[config_idx] = trans_dat[config_idx].pop('chemical potential')
            concentration[config_idx] = trans_dat[config_idx].pop('concentration')
            conductivity[config_idx] = trans_dat[config_idx].pop('conductivity')['tensor']
            mobility[config_idx] = trans_dat[config_idx].pop('mobility')['tensor']
            seebeck_coeff[config_idx] = trans_dat[config_idx].pop('Seebeck coefficient')['tensor']
            thermal_conductivity[config_idx] = trans_dat[config_idx].pop('thermal conductivity')['tensor']

            num_iter[config_idx] = trans_dat[config_idx].pop('number of iterations')
            conductivity_convergence_dat = trans_dat[config_idx].pop('iteration')
            conductivity_convergence[config_idx] = {}

            for iteration in np.arange(1, num_iter[config_idx] + 1):
                conductivity_iterations.append()

            conductivity_convergence[config_idx] = trans_dat[config_idx].pop('iteration')['tensor']

        self.temperature = PhysQuantityArray(temperature, temperature_units, "temperature")
        self.chem_potential = PhysQuantityArray(chem_potential, chem_potential_units, "chem_potential")
        self.concentration = PhysQuantityArray(concentration, concentration_units, "concentration")
        
        self.conductivity = TensorPhysQuantityArray(conductivity, conductivity_units, "conductivity")
        self.mobility = TensorPhysQuantityArray(mobility, mobility_units, "mobility")
        self.seebeck_coeff = TensorPhysQuantityArray(seebeck_coeff, seebeck_coeff_units, "seebeck_coeff")
        self.thermal_conductivity = TensorPhysQuantityArray(thermal_conductivity, thermal_conductivity_units, "thermal_conductivity")


# Ideas for methods:
# plot convergence
# simple plots
# find temperature and chemical potential corresponding
# include unit conversion 
   