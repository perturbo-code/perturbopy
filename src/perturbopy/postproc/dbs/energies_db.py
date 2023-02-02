import numpy as np
from perturbopy.postproc.utils.constants import energy_conversion_factor, standardize_units_name, energy_units_names


class EnergiesDB():
   """
   This is a class representation of a set of energies organized in a dictionary.

   """
   def __init__(self, energies_dict, units, num_indices=None):
      """
      Constructor method

      """
      self.energies_dict = energies_dict
      self._units = units

      for idx in self.energies_dict.keys():
         self.energies_dict[idx] = np.array(self.energies_dict[idx])

      if num_indices is not None and num_indices != len(energies_dict.keys()):
         raise ValueError("nindices input is inconsistent with the number of energies")
      self.num_indices = len(energies_dict.keys())

   @property
   def indices(self):
      """
      Property storing the indices, i.e. the keys of the energies

      Returns
      -------
      indices : list
         The list of indices

      """
      return list(self.energies_dict.keys())
   
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
      converted_energies_dict: dict
         The stored energies in the new units.

      """

      conversion_factor = energy_conversion_factor(self.units, new_units)
      converted_energies_dict = {}

      for idx in self.energies_dict.keys():
         converted_energies_dict[idx] = self.energies_dict[idx] * conversion_factor

      return converted_energies_dict

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
      self.energies_dict = self.convert_units(new_units)
      self._units = standardize_units_name(new_units, energy_units_names)

   def __getitem__(self, key):
      return self.energies_dict[key]

   def __str__(self):
      return str(self.energies_dict)