import numpy as np
from perturbopy.postproc.utils.constants import ureg, conversion_factor, standardize_units_name


class UnitsDict(dict):
    """
    This is a class representation of a set of physical quantities with units organized in a dictionary.
    The physical quantities may either be arrays or floats.

    Attributes
    ----------
    data : dict
       Dictionary of floats or array_like types of physical quantities
    units : str {}
       The units of the physical quantities

    """
    def __init__(self, units, *args, **kwargs):
        """
        Constructor method

        """
        super().__init__(*args, **kwargs)

        self.units = standardize_units_name(units)
        
        self.apply_recursive(lambda x: np.array(x) if isinstance(x, list) else x)

    
    def convert_units(self, target_units, in_place=True):
        """
        Convert all quantities to the specified target units using Pint.

        Parameters
        ----------
        target_units : str 
            The target units for conversion.

        Returns
        -------
        UnitsDict: A new UnitsDict object with quantities converted to the target units.
        
        """

        factor = conversion_factor(self.units, target_units)

        self.units = standardize_units_name(target_units)

        return self.apply_recursive(lambda x: x * factor, in_place)


    def apply_recursive(self, function, in_place=True):
        """
        Recursively perform operations on any array in the dictionary

        """
        def apply_recursive_helper(data_tmp):
            if isinstance(data_tmp, dict):
                return {key: apply_recursive_helper(value) for key, value in data_tmp.items()}
            else:
                return function(data_tmp)

        if in_place:
            # Update values in the original dictionary
            for key, value in self.items():
                self[key] = apply_recursive_helper(value)
            return self
        else:
            # Create a new object with updated values
            new_dict = {key: apply_recursive_helper(value) for key, value in self.items()}
            return UnitsDict(self.units, new_dict)

    