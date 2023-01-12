import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.optimize import curve_fit
from perturbopy.postproc.calc_modes.calc_mode import CalcMode
from perturbopy.postproc.utils.constants import energy_conversion_factor, length_conversion_factor
from perturbopy.postproc.dbs.energies_db import EnergiesDB
from perturbopy.postproc.dbs.kpts_db import KptsDB
from perturbopy.postproc.utils.plotting_utils import plot_bands


class BandsCalcMode(CalcMode):
   """
   This is a class representation of a bands calculation.

   Parameters
   ----------
   pert_dict : dict
      dictionary containing inputs and outputs from a bands calculation

   """

   def __init__(self, pert_dict, kpt_labels={}):
      """
      Constructor method

      """
      super().__init__(pert_dict)
      
      if self.calc_mode != 'bands':
         raise ValueError('Calculation mode for a BandsCalcMode object should be "bands"')
      
      kpath_units = self._pert_dict['bands'].pop('k-path coordinate units')
      kpath = np.array(self._pert_dict['bands'].pop('k-path coordinates'))
      kpt_units = self._pert_dict['bands'].pop('k-point coordinate units')
      kpts = np.array(self._pert_dict['bands'].pop('k-point coordinates'))

      bands = self._pert_dict['bands'].pop('band index')
      nbands = self._pert_dict['bands'].pop('number of bands')
      energy_units = self._pert_dict['bands'].pop('band units')

      self.kpt_db = KptsDB.from_lattice(kpts, kpt_units, self.lat, self.recip_lat, kpath, kpath_units, kpt_labels)
      self.bands = EnergiesDB(bands, energy_units, nbands)

   def compute_indirect_bandgap(self, n_initial, n_final):
      """
      Method to compute the indirect bandgap between two bands
   
      Parameters
      ----------
      n_initial: int
         Number of the lower band
      n_final: int
         Number of the upper band
      
      Returns
      -------
      gap: float
         minimum energy gap between the two bands
      initial_kpt: array
         k-point of the lower band
      final_kpt: array
         k-point of the upper band

      """

      if n_initial not in self.bands.band_indices or n_final not in self.bands.band_indices:
         raise ValueError("n_initial and n_final must be valid band numbers")

      gap = np.min(self.bands.energies[n_final]) - np.max(self.bands.energies[n_initial])

      initial_kpt = self.kpt_db.kpts[:, np.argmax(self.bands.energies[n_initial])]
      final_kpt = self.kpt_db.kpts[:, np.argmin(self.bands.energies[n_final])]

      return gap, initial_kpt, final_kpt

   def compute_direct_bandgap(self, n_initial, n_final):
      """
      Method to compute the direct bandgap between two bands
   
      Parameters
      ----------
      n_initial: int
         Number of the lower band
      n_final: int
         Number of the upper band
      
      Returns
      -------
      gap: float
         minimum energy gap between the two bands
      kpt: array
         k-point of the gap

      """
      if n_initial not in self.bands.band_indices or n_final not in self.bands.band_indices:
         raise ValueError("n_initial and n_final must be valid band numbers")

      transitions = self.bands.energies[n_final] - self.bands.energies[n_initial]
      gap = np.min(transitions)
      kpt = self.kpt_db.kpts[:, np.argmin(transitions)]

      return gap, kpt

   def compute_effective_mass(self, n, kpt, max_distance):
      kpt_coordinates = self.kpt_db.kpts_cart
      energies = self.bands.energies[n] * energy_conversion_factor(self.bands.units, 'hartree')
      alat = self.alat * length_conversion_factor(self.alat_units, 'bohr')

      # assume kpt in cartesian coords
      E_0 = energies[self.kpt_db.find_kpt(kpt)]

      kpt_distances_squared = np.sum(np.square(kpt_coordinates - np.reshape(np.array(kpt), (3,1))), axis=0)

      kpt = np.array(kpt)
      kpt_indices = np.where(kpt_distances_squared < max_distance)

      energies = energies[kpt_indices]
      kpt_distances_squared = kpt_distances_squared[kpt_indices] * (2 * math.pi / alat)**2

      def f(prefactor, kpt_dist_squared, energy):
         return prefactor * kpt_dist_squared + E_0

      fit_params, pcov = curve_fit(f, kpt_distances_squared, energies)

      # make sure atomic units hbar=1 me=1 energy in hartrees kpts in cartesian

      effective_mass = fit_params[0] / 2
      plt.scatter(self.kpt_db.kpath[kpt_indices], energies)
      plt.plot(self.kpt_db.kpath[kpt_indices], fit_params[0] * kpt_distances_squared + E_0, 'k')
      plt.show()

      return effective_mass

   def plot_bands(self, ax, show_kpt_labels=True, **kwargs):
      return plot_bands(ax, self.kpt_db, self.bands, show_kpt_labels, **kwargs)
      