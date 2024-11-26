import numpy as np
from perturbopy.postproc.calc_modes.calc_mode import CalcMode
from perturbopy.postproc.dbs.units_dict import UnitsDict
from perturbopy.postproc.dbs.recip_pt_db import RecipPtDB
from perturbopy.postproc.utils.constants import hbar


class ImsigmaSpin(CalcMode):
    """
    Class representation of a Perturbo imsigma_spin calculation.

    Attributes
    ----------
    kpt : RecipPtDB
       Database for the k-points used in the imsigma calculation, containing N points.
    
    bands : UnitsDict
       Database for the band energies computed by the imsigma calculation. The keys are
       the band index, and the values are an array (of length N) containing the energies at each k-point
       with units bands.units

    temper : UnitsDict
        Dictionary of temperatures used in each configuration. The keys give the configuration number,
        and the values are floats giving the temperature (with units temper.units)
    
    chem_pot : UnitsDict
        Dictionary of chemical potentials used in each configuration. The keys
        give the configuration number, and the values are floats giving the
        chemical potential (with units chem_pot.units)
    
    imsigma_flip : UnitsDict
        Dictionary of spin flip imaginary self-energies computed for each configuration. The top level keys are the
        configuration number, and the second level keys are the band index. The values are arrays of length N giving the
        imaginary self-energies along all the k-points at that band index for the configuration. Units are in imsigma.units.

    imsigma_flip_mode : UnitsDict
        Dictionary of spin flip imaginary self-energies resolved by phonon mode computed. The top level keys are the
        configuration number, and the second level keys are the band index. The third level keys are
        the phonon mode. Finally,the values are arrays of length N giving the imaginary self-energies along all the k-points
        due to the given phonon mode at that band index for the configuration. Units are in imsigma_mode.units.
    
    """

    def __init__(self, pert_dict):
        """
        Constructor method

        Parameters
        ----------
        pert_dict : dict
            Dictionary containing the inputs and outputs from the imsigma calculation.

        """
        super().__init__(pert_dict)

        if self.calc_mode.split('-')[0] != 'imsigma_spin':
            raise ValueError('Calculation mode for an ImsigmaSpinCalcMode object should be "imsigma_spin"')

        kpoint_units = self._pert_dict['imsigma_spin'].pop('k-point coordinate units')
        num_kpoints = self._pert_dict['imsigma_spin'].pop('number of k-points')
        kpoint = np.array(self._pert_dict['imsigma_spin'].pop('k-point coordinates'))
        self.kpt = RecipPtDB.from_lattice(kpoint, kpoint_units, self.lat, self.recip_lat)
        
        energy_units = self._pert_dict['imsigma_spin'].pop('energy units')
        num_bands = self._pert_dict['imsigma_spin'].pop('number of bands')
        energies_dict = self._pert_dict['imsigma_spin']['energy'].pop('band index')
        self.bands = UnitsDict.from_dict(energies_dict, energy_units)

        num_config = self._pert_dict['imsigma_spin'].pop('number of configurations')
        config_dat = self._pert_dict['imsigma_spin'].pop('configuration index')
        num_modes = self._pert_dict['imsigma_spin'].pop('number of phonon modes')

        self.temper = UnitsDict(units=self._pert_dict['imsigma_spin'].pop('temperature units'))
        self.chem_pot = UnitsDict(units=self._pert_dict['imsigma_spin'].pop('chemical potential units'))
        self.imsigma_flip = UnitsDict(units=self._pert_dict['imsigma_spin'].pop('Im(Sigma) units'))
        self.imsigma_flip_mode = UnitsDict(units=self.imsigma_flip.units)
        
        for config_idx in config_dat.keys():
            self.imsigma_flip[config_idx] = {}
            self.imsigma_flip_mode[config_idx] = {}
            self.temper[config_idx] = config_dat[config_idx].pop('temperature')
            self.chem_pot[config_idx] = config_dat[config_idx].pop('chemical potential')
            
            imsigma_dat = config_dat[config_idx].pop('band index')

            for mode in np.arange(1, num_modes + 1):
                self.imsigma_flip_mode[config_idx][mode] = {}

            for band_index in imsigma_dat.keys():
                self.imsigma_flip[config_idx][band_index] = np.array(imsigma_dat[band_index]['Im(Sigma)']['total'])

                for mode in np.arange(1, num_modes + 1):
                    self.imsigma_flip_mode[config_idx][mode][band_index] = np.array(imsigma_dat[band_index]['Im(Sigma)']['phonon mode (total)'][mode])
