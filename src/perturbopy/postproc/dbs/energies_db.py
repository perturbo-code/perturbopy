import numpy as np
from perturbopy.postproc.utils.constants import energy_conversion_factor, standardize_units_name, energy_units_names


class EnergiesDB():
   """
   This is a class representation of a set of energies organized in bands.

   """
   def __init__(self, energies, units, nbands=None):
      """
      Constructor method

      """
      self.energies = energies
      self._units = units

      for band_idx in self.energies.keys():
         self.energies[band_idx] = np.array(self.energies[band_idx])

      if nbands is not None and nbands != len(energies.keys()):
         raise ValueError("nbands input is inconsistent with the number of energies")
      self.nbands = len(energies.keys())

   @property
   def band_indices(self):
      """
      Property storing the band indices, i.e. the keys of the energies

      Returns
      -------
      band_indices : list
         The list of band indices

      """
      return list(self.energies.keys())
   
   @property
   def units(self):
      """
      Property storing the energy units of the stored energies

      Returns
      -------
      units : str
         The energy units

      """
      return self._units

   def convert_units(self, new_units):
      """
      Method to convert the energy units of the stored energies.
      Does not store the changes.

      Parameters
      ----------
      new_units : str
         Energy units to which the energies will be converted.

      Returns
      -------
      converted_energies: dict
         The stored energies in the new units.

      """

      conversion_factor = energy_conversion_factor(self.units, new_units)
      converted_energies = {}

      for band_idx in self.energies.keys():
         converted_energies[band_idx] = self.energies[band_idx] * conversion_factor

      return converted_energies

   @units.setter
   def units(self, new_units):
      """
      Setter for the units property. Changes the _units attribute as well
      as converting the energies attribute to new_units.

      Parameters
      ----------
      new_units : str
         Energy units to which the energies will be converted.
      """
      self.energies = self.convert_units(new_units)
      self._units = standardize_units_name(new_units, energy_units_names)
