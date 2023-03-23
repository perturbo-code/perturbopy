import numpy as np
from perturbopy.postproc.utils.constants import energy_conversion_factor, standardize_units_name, energy_units_names


class EnergiesDB():
   """
   This is a class representation of a set of energies organized in bands.

   Parameters
   ----------
   energies : dict
      Dictionary of arrays of energies, with keys corresponding to the band number.
   units : str {}
      The energy units.

   Attributes
   ----------
   energies : dict
      Dictionary of arrays of energies, with keys corresponding to the band number.
   _units : dict
      The energy units.
   num_indices : 
      The number of bands in the energies dict.
      
   """
   def __init__(self, energies_dict, units):
      """
      Constructor method

      """
      self.energies = energies_dict
      self.units = units

      for idx in self.energies.keys():
         self.energies[idx] = np.array(self.energies[idx])

      self.num_indices = len(self.energies.keys())

   @property
   def indices(self):
      """
      Property storing the indices, i.e. the keys of the energies dict.

      Returns
      -------
      indices : list
         The list of indices.

      """
      return list(self.energies.keys())

   def convert_units(self, new_units, in_place=True):
      """
      Method to convert the energy units of the stored energies.
      Does not store the changes.

      Parameters
      ----------
      new_units : str
         Energy units to which the energies will be converted.
      in_place : bool, default : True
         Whetherh or not to store the converted units.

      Returns
      -------
      converted_energies: dict
         The energies in the new units.

      """
      new_units = standardize_units_name(new_units)

      conversion_factor = energy_conversion_factor(self.units, new_units)
      converted_energies = {}

      for idx in self.energies.keys():
         converted_energies[idx] = self.energies[idx] * conversion_factor

      if conversion_factor != 1 and in_place:
         self.units = new_units
         self.energies = converted_energies
         print(f"Energies have been converted to {new_units}.")

      return converted_energies

   def __getitem__(self, key):
      return self.energies[key]

   def __str__(self):
      return str(self.energies)