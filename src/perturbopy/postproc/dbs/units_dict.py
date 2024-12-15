import numpy as np
from perturbopy.postproc.utils.constants import conversion_factor, standardize_units_name


class UnitsDict(dict):
    """
    This is a class representation of a set of physical quantities with units organized in a dictionary.
    The physical quantities may either be arrays or floats.

    Attributes
    ----------
    data : dict
       TODO: UnitsDict DOES NOT HAVE A data ATTRIBUTE
       Dictionary of floats or array_like types of physical quantities
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

        def convert_lists_to_numpy(data):
            """
            Helper function to recursively convert any lists in the dictionary to arrays

            """
            if isinstance(data, list):
                return np.array(data)
            if isinstance(data, dict):
                return {key: convert_lists_to_numpy(value) for key, value in data.items()}
            return data

        input_dict = convert_lists_to_numpy(input_dict)
        units_dict = cls(units)
        units_dict.update(input_dict)

        return units_dict
