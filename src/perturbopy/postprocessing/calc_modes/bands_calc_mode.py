import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from perturbopy.postprocessing.calc_modes.calc_mode import CalcMode

class BandsCalcMode(CalcMode):
   """
   This is a class representation of a bands calculation.

   Parameters
   ----------
   pert_dict : dict
      dictionary containing inputs and outputs from a bands calculation

   """

   def __init__(self, pert_dict):
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
      self.band_units = self._pert_dict['bands'].pop('band units')
      self.bands = self._pert_dict['bands'].pop('band index')

   def convert_band_units(self, new_units):
      """
      Method to convert the energy units of the band structure.

      Parameters
      ----------
      new_units : str
         Energy units to which the band structure will be converted. 

      Returns
      -------
      None

      """

      ###
      # conversion_factor = convert_units(self.band_units, new_units)

      for band_idx in self.bands.keys():
         self.bands[band_idx] = self.bands[band_idx] * conversion_factor

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

      # for i, k_path_coordinate in enumerate(self.k_path_coordinates):
      #    self.k_path_coordinate[i] = prefactor * k_path_coordinate

   def find_kpt_indices(self, kpt, instance = None):

      kpt_indices = np.where(np.all(self.kpt_coordinates == kpt, axis=1))[0]
      
      if len(kpt_indices) == 0:
         raise Exception("k point coordinate is not in the list of coordinates")
      
      if instance is not None:
         if len(kpt_indices) < instance:
            raise Exception("Fewer k point coordinates were found than match the instance number")
            kpt_indices = kpt_indices[instance - 1]

      return kpt_indices

   # def convert_kpt_units(self, new_units, crystal_basis, alat):


   def compute_effective_mass(self, n, center_kpt, num_points_around_center, center_kpt_instance=1):
      """
      Method to approximate the effective mass of a carrier at a particular k point and band,
      assuming the band is approximately parabolic near the k point. The k point is specified
      by coordinate.

      Parameters
      ----------
      band_idx: int
         Band number 
      k_center: 
      ####

      range_around_center:
      ###


      Returns
      -------
      effective mass: float
         The approximate effective mass

      """

      ###

      # Currently hard coded to work for Ge
      hbar = 1
      a = 10.69
      energy_conversion = 0.0367493 
      energies = []
      kpt_distance_squared = []

      center_kpt_idx = self.find_kpt_indices(center_kpt, center_kpt_instance)

      for kpt_idx, kpt in enumerate(self.kpt_coordinates):

         if abs(center_kpt_idx - kpt_idx) > num_points_around_center:
            continue
         energies = energies + [self.bands[n][kpt_idx]*energy_conversion]
         kpt = self.kpt_coordinates[kpt_idx]
         k_diff_squared = (kpt[0] - center_kpt[0])**2 + (kpt[1] - center_kpt[1])**2 + (kpt[2] - center_kpt[2])**2 

      def f(x, slope):
         return slope*x

      fit_params, pcov = curve_fit(f, k_diff_squared, energies)
      
      effective_mass = a**2 * hbar**2 / (2 * fit_params[0])

      return effective_mass

   def compute_indirect_bandgap(self, n_initial, n_final):
      """
      Method to compute the indirect bandgap between two bands
   
      Parameters
      ----------

      """
      gap = np.min(self.bands[n_final]) - np.max(self.bands[n_initial]) 
      initial_kpt = self.kpt_coordinates[np.argmax(self.bands[n_initial])]
      final_kpt = self.kpt_coordinates[np.argmin(self.bands[n_final])]

      return gap, initial_kpt, final_kpt

   def compute_transitions(self, n_initial, n_final):
   
      transitions = []

      for i, kpt in enumerate(self.kpt_coordinates):
         transitions = transitions + [self.bands[n_final][i] - self.bands[n_initial][i]]

      return transitions

   def compute_direct_bandgap(self, n_initial, n_final):
      transitions = self.compute_transitions(n_initial, n_final)
      gap = np.min(transitions)
      kpt = self.kpt_coordinates[np.argmin(transitions)]
      return gap, kpt

   def plot_bands(self):
      fig = plt.figure(figsize=(12, 12), dpi=80)
      ax = fig.add_subplot(111)

      for band_idx in self.bands:
         ax.plot(self.k_path_coordinates, self.bands[band_idx])

      #for high_symm_point in high_symm_points.keys():
       #   plt.axvline(x = high_symm_points[high_symm_point]['xq'], label = high_symm_point, c='grey', ls = '--')
        #  plt.text(x = high_symm_points[high_symm_point]['xq'] - 0.04,y = -7, s = high_symm_point, fontsize= 35)

      plt.ylabel('Electron energy (' + self.band_units + ')', fontsize = 35)
      plt.show()

