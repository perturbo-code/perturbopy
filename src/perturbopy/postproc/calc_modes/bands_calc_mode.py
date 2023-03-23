import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.optimize import curve_fit
from perturbopy.postproc.calc_modes.calc_mode import CalcMode
from perturbopy.postproc.utils.constants import energy_conversion_factor, length_conversion_factor
from perturbopy.postproc.dbs.energy_db import EnergyDB
from perturbopy.postproc.dbs.recip_pt_db import RecipPtDB
from perturbopy.postproc.utils.plot_tools import plot_dispersion
from perturbopy.postproc.utils.lattice import cryst_to_cart, reshape_points


class BandsCalcMode(CalcMode):
   """
   Class representation of a Perturbo bands calculation.

   Parameters
   ----------
   pert_dict : dict
      Dictionary containing the inputs and outputs from the bands calculation.

   Attributes
   ----------
   kpt : RecipPtDB
      Database for the k-points used in the phdisp calculation.
   bands : EnergiesDB
      Database for the band energies computed by the bands calculation.

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
      kpoint_units = self._pert_dict['bands'].pop('k-point coordinate units')
      kpoint = np.array(self._pert_dict['bands'].pop('k-point coordinates'))

      energies_dict = self._pert_dict['bands'].pop('band index')
      num_bands = self._pert_dict['bands'].pop('number of bands')
      energy_units = self._pert_dict['bands'].pop('band units')

      self.kpt = RecipPtDB.from_lattice(kpoint, kpoint_units, self.lat, self.recip_lat, kpath, kpath_units)
      self.bands = EnergiesDB(energies_dict, energy_units)

   def compute_indirect_bandgap(self, n_lower, n_upper):
      """
      Method to compute the indirect bandgap between two bands.
   
      Parameters
      ----------
      n_lower, n_upper : int
         Number of the lower and upper bands.

      Returns
      -------
      gap: float
         The indirect bandgap, computed as the energy difference between the maximum of
         the upper band and the minimum of the lower band.
      lower_kpt, upper_kpt : array_like
         k-points corresponding to the maximum of the upper band and the minimum of the lower band.

      Raises
      ------
      ValueError
         If the upper and lower band numbers provided are not band indices as stored in the bands database.

      """

      if n_lower not in self.bands.indices or n_upper not in self.bands.indices:
         raise ValueError("n_lower and n_upper must be valid band numbers")

      gap = np.min(self.bands.energies[n_upper]) - np.max(self.bands.energies[n_lower])

      initial_kpt = self.kpt.points[:, np.argmax(self.bands.energies[n_lower])]
      final_kpt = self.kpt.points[:, np.argmin(self.bands.energies[n_upper])]

      return gap, initial_kpt, final_kpt

   def compute_direct_bandgap(self, n_lower, n_upper):
      """
      Method to compute the direct bandgap between two bands.
   
      Parameters
      ----------
      n_lower: int
         Number of the lower band
      n_upper: int
         Number of the upper band
      
      Returns
      -------
      gap: float
         The direct bandgap, computed as the minimum energy difference between two bands
         at the same k-point.
      kpoint: array_like
         The k-point corresponding to the direct bandgap.

      """
      if n_lower not in self.band_indices or n_upper not in self.band_indices:
         raise ValueError("n_lower and n_upper must be valid band numbers")

      transitions = self.bands.indices[n_upper] - self.bands.indices[n_lower]
      gap = np.min(transitions)
      kpoint = self.kpt.points[:, np.argmin(transitions)]

      return gap, kpoint

   def compute_effective_mass(self, n, kpoint, max_distance, show_plot=True):
      """
      Method to compute the longitudinal effective mass at a k-point, approximated with a parabolic fit.
      Parameters
      ----------
      n : int
         Index of the band to calculate the effective mass on.
      
      kpoint : int
         The k-point to center the calculation on.

      max_distance : float
         Maximum distance between the center k-point and k-points to include in the parabolic approximation.

      Returns
      -------
      effective_mass : float
         The longitudinal effective mass at band n and the inputted kpoint, computed by a parabolic fit.

      """
      epsilon = 1e-2

      kpoint = reshape_points(kpoint)

      energies = self.bands.energies[n] * energy_conversion_factor(self.energy_units, 'hartree')
      alat = self.alat * length_conversion_factor(self.alat_units, 'bohr')
      E_0 = energies[self.kpt.where(kpoint)]

      kpt_distances = np.linalg.norm(self.kpt.points - np.array(kpoint), axis=0)
      kpt_parallel = np.dot(np.reshape(kpoint, (3,)), self.kpt.points) / (np.linalg.norm(kpoint) * np.linalg.norm(self.kpt.points, axis=0)) - 1 < epsilon

      kpt_indices = np.where(np.logical_and(kpt_distances < max_distance, kpt_parallel))
      energies = energies[kpoint_indices]

      kpt_points = self.kpt.points[:, kpoint_indices][:, 0, :]
      kpoint_distances_squared = np.sum(np.square(kpt_points - kpoint), axis=0) * (math.pi * 2/self.alat) ** 2

      def parabolic_approx(prefactor, kpoint_dist_squared, energy):
         return prefactor * kpoint_dist_squared + E_0
      
      fit_params, pcov = curve_fit(parabolic_approx, kpoint_distances_squared, energies)

      effective_mass = 1 / (fit_params[0] * 2)

      if show_plot():
         plt.scatter(self.kpt.path[kpoint_indices], energies)
         plt.plot(self.kpt.path[kpoint_indices], fit_params[0] * kpoint_distances_squared + E_0, 'k')
         plt.show()

      return effective_mass

   def plot_bands(self, ax, energy_window=None, show_kpoint_labels=True, **kwargs):
      """
      Method to plot the band structure.

      Parameters
      ----------
      ax : matplotlib.axes.Axes
         Axis on which to plot the bands.

      energy_window : tuple of int
         The range of band energies to be shown on the y-axis.

      show_kpoint_labels : bool
         If true, the k-point labels stored in the labels attribute will be shown on the plot.

      **kwargs, optional
         Extra arguments to plot_dispersion. Refer to plot_dispersion documentation for a list of all possible arguments.

      Returns
      -------
      ax: matplotlib.axes.Axes
         Axis with the plotted bands.

      """
      return plot_dispersion(ax, self.kpt, self.bands, energy_window, show_kpoint_labels, **kwargs)
