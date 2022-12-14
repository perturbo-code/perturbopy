import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.optimize import curve_fit
from perturbopy.postproc.calc_modes.calc_mode import CalcMode
from perturbopy.postproc.utils.constants import energy_conversion_factor, standard_units_name


#probably move to a plotting tools class
def choose_plotting_attribute(default, attribute_names, **kwargs):
   
   for attribute_name in attribute_names:
      if attribute_name in kwargs.keys():
         attribute = kwargs.pop(attribute_name)

   else:
      attribute = default

   if not isinstance(attribute, list):
      attribute = [attribute]

   return attribute, kwargs


class BandsCalcMode(CalcMode):
   """
   This is a class representation of a bands calculation.

   Parameters
   ----------
   pert_dict : dict
      dictionary containing inputs and outputs from a bands calculation

   """

   def __init__(self, pert_dict, labeled_kpts=None):
      """
      Constructor method

      """
      super().__init__(pert_dict)
      
      if self.calc_mode != 'bands':
         raise Exception('Calculation mode for a BandsCalcMode object should be "bands"')

      self.nbands = self._pert_dict['bands'].pop('number of bands')
      self.k_path_coordinate_units = self._pert_dict['bands'].pop('k-path coordinate units')
      self.k_path_coordinates = np.array(self._pert_dict['bands'].pop('k-path coordinates'))
      self.kpt_coordinate_units = self._pert_dict['bands'].pop('k-point coordinate units')
      self.kpt_coordinates = np.array(self._pert_dict['bands'].pop('k-point coordinates'))
      self.energy_units = self._pert_dict['bands'].pop('band units')
      self.bands = self._pert_dict['bands'].pop('band index')

      for band_idx in self.bands.keys():
         self.bands[band_idx] = np.array(self.bands[band_idx])

      self.labeled_kpts = {}

   def convert_energy_units(self, new_units, save=True):
      """
      Method to convert the energy units of the band structure.

      Parameters
      ----------
      new_units : str
         Energy units to which the band structure will be converted.
      save : bool
         Whether or not to store the new units and converted band structure
         in the energy_units and bands attributes.

      Returns
      -------
      converted_bands: dict
         The band structure in the new units.

      """

      conversion_factor = energy_conversion_factor(self.energy_units, new_units)
      converted_bands = {}

      if conversion_factor == 1:
         return self.bands

      for band_idx in self.bands.keys():
         converted_bands[band_idx] = self.bands[band_idx] * conversion_factor

      if save:
         self.bands = converted_bands
         self.energy_units = new_units

      return converted_bands

   def convert_kpt_units(self, new_units, save=True):
      """
      Method to convert the k-point units or basis.

      Parameters
      ----------
      new_units : str
         K-point units to which the k-points will be converted.
      save : bool
         Whether or not to store the new units and converted k-points
         in the kpt_coordinate_units and kpt_coordinates attributes.

      Returns
      -------
      converted_bands: dict
         The k-points in the new units.

      """

      kpt_units_names = {'cartesian': ['cart'], 'crystal': ['cryst', 'frac', 'fractional']}
      new_units = standard_units_name(new_units, kpt_units_names)

      if new_units == self.kpt_coordinate_units:
         return self.kpt_coordinates

      forward = new_units == 'crystal'

      converted_kpt_coordinates = self.cryst_to_cart(self.kpt_coordinates, forward=True, real_space=False, col_oriented=False)

      if save:
         self.kpt_coordinates = converted_kpt_coordinates
         self.kpt_coordinate_units = new_units

      return converted_kpt_coordinates

   def scale_k_path_coordinates(self, range_min, range_max):
      """
      Method to scale the arbitrary k path plotting coordinates to a certain range.

      Parameters
      ----------
      range_min: float
         Lower limit of the range to which the k path coordinates will be scaled. 
      range_max: float
         Upper limit of the range to which the k path coordinates will be scaled.

      Returns
      -------
      None

      """

      self.k_path_coordinates = (self.k_path_coordinates - min(self.k_path_coordinates)) \
                                 / (max(self.k_path_coordinates) - min(self.k_path_coordinates)) \
                                 * (range_max - range_min) \
                                 + range_min

   def find_kpt(self, kpt, nearest=True):
      """
      Method to find the index or indices of a particular k-point coordinate

      Parameters
      ----------
      kpt: list
         The k-point to be searched
      nearest: bool
         If true, the index of the closest k-point will be returned

      Returns
      -------
      kpt_indices: list
         The indices of the matching k-points

      """

      kpt_indices = np.where(np.all(self.kpt_coordinates == kpt, axis=1))[0]
      
      if len(kpt_indices) == 0:
         if nearest:
            distances = np.sqrt(np.sum(np.square(self.kpt_coordinates - np.array(kpt)), axis=1))
            min_distance = np.amin(distances)
            kpt_indices = np.where(distances == min_distance)[0]

            print(f"Nearest k-point to {kpt} is {self.kpt_coordinates[kpt_indices]}")
         else:
            raise Exception("k point coordinate is not in the list of coordinates")

      return kpt_indices

   def kpt_coord_to_kpath_coord(self, kpt, nearest=True):
      """
      Method to find the k-path coordinate of a particular k-point coordinate

      Parameters
      ----------
      kpt: list
         The k-point to be searched
      nearest: bool
         If true, the k-path coordinate of the closest k-point will be returned

      Returns
      -------
      kpath_coord: list
         The k-path coordinates of the corresponding k-points

      """

      kpath_coord = self.k_path_coordinates[self.find_kpt(kpt, nearest)]

      return kpath_coord

   def kpath_coord_to_kpt_coord(self, kpath, nearest=True):
      """
      Method to find the k-point of a particular k-path coordinate

      Parameters
      ----------
      kpt: list
         The k-path to be searched
      nearest: bool
         If true, the k-point of the closest k-path coordinate will be returned

      Returns
      -------
      kpath_coord: list
         The k-points of the corresponding k-path coordinate

      """

      if kpath in self.k_path_coordinates:
         kpath_idx = np.where(self.k_path_coordinates == kpath)
      else:
         if nearest:
            distances = np.abs(self.k_path_coordinates - kpath)
            min_distance = np.amin(distances)
            kpath_idx = np.where(distances == min_distance)[0]
         else:
            raise Exception("k path coordinate is not in the list of coordinates")

      return self.kpt_coordinates[kpath_idx]

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

      if n_initial not in self.bands.keys() or n_final not in self.bands.keys():
         raise Exception("n_initial and n_final must be valid band numbers")

      gap = np.min(self.bands[n_final]) - np.max(self.bands[n_initial])
      initial_kpt = self.kpt_coordinates[np.argmax(self.bands[n_initial])]
      final_kpt = self.kpt_coordinates[np.argmin(self.bands[n_final])]

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
      if n_initial not in self.bands.keys() or n_final not in self.bands.keys():
         raise Exception("n_initial and n_final must be valid band numbers")

      transitions = self.bands[n_final] - self.bands[n_initial]
      gap = np.min(transitions)
      kpt = self.kpt_coordinates[np.argmin(transitions)]

      return gap, kpt

   def label_kpt(self, kpt_coordinate, kpt_label, nearest=True, **kwargs):
      kpt_units = kwargs.pop('kpt_units', self.kpt_coordinate_units)
      
    #  if not kpt_units == self.kpt_units:
     #    kpt_units = self.c
      self.labeled_kpts[kpt_label] = kpt_coordinate

   def plot_kpt_labels(self, ax, line=True, **kwargs):
      default_y = ax.get_ylim()[0] - (ax.get_ylim()[1] - ax.get_ylim()[0]) *0.1
      
      label_y = kwargs.pop('label_y', default_y)
      fontsize = kwargs.pop('fontsize', 20)
      color = kwargs.pop('color', 'k')

      for label in self.labeled_kpts:
         for x in self.kpt_coord_to_kpath_coord(self.labeled_kpts[label]):
            label_x = kwargs.pop('label_x', x)
            if line:
               ax.axvline(x, color=color, **kwargs)
            ax.text(x=label_x, y=label_y, s=label, fontsize=fontsize, **kwargs)

      return ax

   def plot_bands(self, ax, show_kpt_labels=True, **kwargs):
      """
      Method to plot the band structure.
   
      Parameters
      ----------
      ax: matplotlib.axes.Axes
         Axis on which to plot band structure
      show_kpt_labels: bool
         Whether or not to label the special k-points
      
      Returns
      -------
      ax: matplotlib.axes.Axes
         Axis with the plotted band structure

      """

      n_min = kwargs.pop('nmin', 1)
      n_max = kwargs.pop('nmax', self.nbands)

      # Colors, labels and linestyles can be inputted as lists,
      # as one value to be applied to all bands,
      # or set to the default value

      default_colors = ['b', 'k', 'g', 'r', 'c', 'm', 'y']
      default_linewidths = 4
      default_labels = None
      default_linestyles = ['-']
      default_ylabel = f'Energy ({self.energy_units})'

      colors, kwargs = choose_plotting_attribute(default_colors, ['c', 'colors'], **kwargs)
      linewidths, kwargs = choose_plotting_attribute(default_linewidths, ['lw', 'linewidth'], **kwargs)
      linestyles, kwargs = choose_plotting_attribute(default_linestyles, ['ls', 'linestyle'], **kwargs)
      labels, kwargs = choose_plotting_attribute(default_labels, ['labels', 'label'], **kwargs)

      ylabel = kwargs.pop('ylabel', default_ylabel)
      ylabel_fontsize = kwargs.pop('ylabel_fontsize', 20)
      for n in range(n_min, n_max):

         ax.plot(self.k_path_coordinates, self.bands[n],
                 color=colors[n % len(colors)],
                 linestyle=linestyles[n % len(linestyles)],
                 label=labels[n % len(labels)],
                 linewidth=linewidths[n % len(labels)], **kwargs)

      if show_kpt_labels:
         ax = self.plot_kpt_labels(ax)

      ax.set_xticks([])
      ax.set_ylabel(ylabel, fontsize=ylabel_fontsize)

      return ax

   def compute_effective_mass(self, n, kpt, max_distance):
      kpt_coordinates =  self.convert_kpt_units(new_units='cartesian', save=False)
      energies = self.bands[n] * energy_conversion_factor(self.energy_units, 'hartree')
      alat = self.alat # * distance_conversion_factor(self.alat, 'bohr')

      # assume kpt in cartesian coords
      E_0 = energies[self.find_kpt(kpt)]
      print(f'E_0: {E_0}')

      kpt_distances_squared = np.sum(np.square(kpt_coordinates - np.array(kpt)),axis=1)
      print(kpt_coordinates[200])
      print(kpt)
      print(kpt_distances_squared[200])
      kpt = np.array(kpt)
      kpt_indices = np.where(kpt_distances_squared < max_distance)


      energies = energies[kpt_indices]
      kpt_distances_squared = kpt_distances_squared[kpt_indices] * (2 * math.pi / alat)**2

      def f(prefactor, kpt_dist_squared, energy):
         return prefactor * kpt_dist_squared + E_0

      print(kpt_distances_squared)
      print(energies)

      fit_params, pcov = curve_fit(f, kpt_distances_squared, energies)

      # make sure atomic units hbar=1 me=1 energy in hartrees kpts in cartesian

      effective_mass = fit_params[0] / 2
      print(fit_params[0])
      plt.scatter(self.k_path_coordinates[kpt_indices], energies)
      plt.plot(self.k_path_coordinates[kpt_indices], fit_params[0] * kpt_distances_squared+E_0, 'k')
      plt.show()

      return effective_mass
