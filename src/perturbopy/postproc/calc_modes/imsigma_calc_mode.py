import numpy as np
from perturbopy.postproc.calc_modes.calc_mode import CalcMode
from perturbopy.postproc.dbs.phys_quantity_array import PhysQuantityArray
from perturbopy.postproc.dbs.recip_pt_db import RecipPtDB
from perturbopy.postproc.utils.plot_tools import plot_dispersion, plot_recip_pt_labels, plot_vals_on_bands

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

        if self.calc_mode != 'imsigma':
            raise ValueError('Calculation mode for a ImsigmaCalcMode object should be "imsigma"')

        T_units = self._pert_dict['imsigma'].pop('temperature units')
        imsigma_units = self._pert_dict['imsigma'].pop('Im(Sigma) units')
        chem_pot_units = self._pert_dict['imsigma'].pop('chemical potential units')
        num_config = self._pert_dict['imsigma'].pop('number of configurations')
        num_modes = self._pert_dict['imsigma'].pop('number of phonon modes')

        kpoint_units = self._pert_dict['imsigma'].pop('k-point coordinate units')
        num_kpoints = self._pert_dict['imsigma'].pop('number of k-points')
        kpoint = np.array(self._pert_dict['imsigma'].pop('k-point coordinates'))
        self.kpt = RecipPtDB.from_lattice(kpoint, kpoint_units, self.lat, self.recip_lat)
        

        energy_units = self._pert_dict['imsigma'].pop('energy units')
        num_bands = self._pert_dict['imsigma'].pop('number of bands')
        energies_dict = self._pert_dict['imsigma'].pop('band index')
        self.bands = EnergyDB(energies_dict, energy_units)

        imsigma_dat = self._pert_dict['imsigma'].pop('configuration index')
        temperatures = {}
        chem_potentials = {}
        imsigmas = {}

        for config_idx in imsigma_dat.keys():
            temperatures[config_idx] = imsigma_dat[config_idx].pop('temperature')
            chem_potentials[config_idx] = imsigma_dat[config_idx].pop('chemical potential')
            imsigmas[config_idx] = imsigma_dat[config_idx].pop('band index')

        self.imsigmas = PhysQuantityArray(phdisp, imsigmas_units)
        self.defpot = PhysQuantityArray(defpot, defpot_units)
        self.ephmat = PhysQuantityArray(imsigmas, ephmat_units)

# find temperature and chemical potential corresponding
# include unit conversion 
   