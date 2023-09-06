import numpy as np
from perturbopy.postproc.utils.constants import conversion_factor, standardize_units_name


class UnitsDict(dict):
    """
    This is a class representation of a set of physical quantities with units organized in a dictionary.

    Attributes
    ----------
    data : dict
       Dictionary of floats or arrays of physical quantities
    units : str {}
       The units of the physical quantities

    """
    def __init__(self, units, *args, **kwargs):
        """
        Constructor method

        """
        super().__init__(*args, **kwargs)
        
        self.units = units

    @classmethod
    def from_dict(cls, input_dict, units):
        """
        Class method to create a UnitsDict object from a Python dictionary and a set of units.

        """

        units_dict = cls(units)
        units_dict.update(input_dict)
        
        return units_dict

    def convert_units(self, new_units, in_place=True):
        """
        Method to convert the stored values to new units.
        The converted units may or may not be stored.

        Parameters
        ----------
        new_units : str
           Units to which the values will be converted.
        in_place : bool, optional
           Whether or not to store the converted units.

        Returns
        -------
        converted_vals: dict
           The values in the new units.

        """
        new_units = standardize_units_name(new_units)

        conversion_factor = conversion_factor(self.units, new_units)
        converted_vals = {}

        for key in self:
            converted_val = self[key] * conversion_factor
            converted_vals[key] = converted_val

            if in_place:
                self[key] = converted_val

        if in_place:
            self.units = new_units

        return converted_vals
