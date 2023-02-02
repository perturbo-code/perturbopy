import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.optimize import curve_fit
from perturbopy.postproc.calc_modes.calc_mode import CalcMode
from perturbopy.postproc.utils.constants import energy_conversion_factor, length_conversion_factor
from perturbopy.postproc.dbs.energies_db import EnergiesDB
from perturbopy.postproc.dbs.recip_pt_db import RecipPtDB
from perturbopy.postproc.utils.plot_tools import plot_dispersion
from perturbopy.postproc.utils.lattice import cryst_to_cart, reshape_points

class PhdispCalcMode(CalcMode):
   """
   This is a class representation of a bands calculation.

   Parameters
   ----------
   pert_dict : dict
      dictionary containum_ing inputs and outputs from a bands calculation

   """

   def __init__(self, pert_dict):
      """
      Constructor method

      """
      super().__init__(pert_dict)
      
      if self.calc_mode != 'bands':
         raise ValueError('Calculation mode for a BandsCalcMode object should be "bands"')
      
      kpath_units = self._pert_dict['bands'].pop('k-path coordinate units')
      kpath = np.array(self._pert_dict['bands'].pop('k-path coordinates'))
      qpoint_units = self._pert_dict['bands'].pop('k-point coordinate units')
      qpoint = np.array(self._pert_dict['bands'].pop('k-point coordinates'))

      energies_dict = self._pert_dict['bands'].pop('band index')
      num_bands = self._pert_dict['bands'].pop('number of bands')
      energy_units = self._pert_dict['bands'].pop('band units')

      self.qpt = RecipPtDB.from_lattice(qpoint, qpoint_units, self.lat, self.recip_lat, kpath, kpath_units)
      self.phdisp = EnergiesDB(energies_dict, energy_units, num_bands)

 
   @property
   def num_bands(self):
      return self.phdisp.num_indices
   @property
   def energy_units(self):
      return self.phdisp.units

   @property
   def band_indices(self):
      return self.phdisp.indices

   def convert_energy_units(self, new_units):
      return self.phdisp.convert_units(new_units)

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
      initial_qpt: array
         k-point of the lower band
      final_qpt: array
         k-point of the upper band

      """

      if n_initial not in self.band_indices or n_final not in self.band_indices:
         raise ValueError("n_initial and n_final must be valid band numbers")

      gap = np.min(self.phdisp[n_final]) - np.max(self.phdisp[n_initial])

      initial_qpt = self.qpt.coords[:, np.argmax(self.phdisp[n_initial])]
      final_qpt = self.qpt.coords[:, np.argmin(self.phdisp[n_final])]

      return gap, initial_qpt, final_qpt

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
      qpt: array
         k-point of the gap

      """
      if n_initial not in self.band_indices or n_final not in self.band_indices:
         raise ValueError("n_initial and n_final must be valid band numbers")

      transitions = self.phdisp[n_final] - self.phdisp[n_initial]
      gap = np.min(transitions)
      qpt = self.qpt.coords[:, np.argmin(transitions)]

      return gap, qpt

   def compute_effective_mass(self, n, qpt, max_distance):
      """
      Method to compute the effective mass approximated by a fitting a parabola
      around a k-point
   
      Parameters
      ----------
      n : int
         Index of the band to perform the calculation on
      
      qpt : int
         The k-point to center the calculation on

      max_distance : float
         Maximum distance between the center k-point and k-points
         to include in the calculation

      Returns
      -------
      effective_mass : float
         The effective mass computed by the parabolic approximation

      """
      epsilon = 1e-2

      qpt = reshape_points(qpt)

      self.qpt_units = 'cartesian'
      print(self.qpt.coords)

      energies = self.phdisp[n] * energy_conversion_factor(self.energy_units, 'hartree')
      alat = self.alat * length_conversion_factor(self.alat_units, 'bohr')

      # assume qpt in cartesian coords
      E_0 = energies[self.find_qpt(qpt)]

      qpoint_distances = np.linalg.norm(self.qpt - np.array(qpt), axis=0)
      qpoint_parallel = np.dot(np.reshape(qpt, (3,)), self.qpt) / (np.linalg.norm(qpt) * np.linalg.norm(self.qpt, axis=0)) -1 < epsilon

      print(self.qpt.coords)
      print(qpoint_distances[:2])
      print(qpoint_parallel)
      qpt = np.array(qpt)
      qpoint_indices = np.where(np.logical_and(qpoint_distances < max_distance, qpoint_parallel))

      energies = energies[qpoint_indices]

      qpoint_coordinates = self.qpt.coords[:,qpoint_indices][:,0,:]
      qpoint_distances_squared = np.sum(np.square(qpoint_coordinates - qpt), axis=0)*(math.pi *2/self.alat)**2


      def f(prefactor, qpoint_dist_squared, energy):
         return prefactor * qpoint_dist_squared + E_0

      fit_params, pcov = curve_fit(f, qpoint_distances_squared, energies)

      # make sure atomic units hbar=1 me=1 energy in hartrees qpoint in cartesian

      effective_mass = fit_params[0] / 2
      plt.scatter(self.kpath[qpoint_indices], energies)
      plt.plot(self.kpath[qpoint_indices], fit_params[0] * qpoint_distances_squared + E_0, 'k')
      plt.show()

      return effective_mass

   def plot_bands(self, ax, energy_window=None, show_qpoint_labels=True, **kwargs):
      """
      Method to plot the band structure.

      Parameters
      ----------
      ax: matplotlib.axes.Axes
         Axis on which to plot band structure

      show_qpoint_labels: bool
         Whether or not to show the k-point labels stored in the labels attribute

      Returns
      -------
      ax: matplotlib.axes.Axes
         Axis with the plotted band structure

      """
      return plot_dispersion(ax, self.qpt_db, self.phdisp, energy_window, show_qpoint_labels, **kwargs) # add options for energy window, bands
