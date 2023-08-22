import numpy as np
from perturbopy.postproc.utils.constants import energy_conversion_factor, length_conversion_factor, standardize_units_name


class PhysQuantityArray(np.ndarray):
    """
    This is a class representation of a set of physical quantities with associated units organized in an array. It is
    a subclass of np.ndarray extended to account for the units associated with physical quantities.

    """

    def __new__(cls, input_array, units, phys_quantity_type):
        """

        Parameters
        ----------
        input_array : array_like
            The array of physical quantities to be stored.
        units : str
            The units of the physical quantities.
        phys_quantity_type : str
            The type of physical quantity (i.e. energy, length) that is being stored

        Attributes
        ----------
        energies : dict
            Dictionary of arrays of energies, with keys labelling the band number or phonon mode.
        units : str
            Units for the stored energies
        num_indices : int
            The number of keys in the energies dict
        """
        
        obj = np.asarray(input_array).view(cls)
        obj.units = units
        obj.phys_quantity_type = phys_quantity_type

        return obj
    
    def __array_finalize__(self, obj):

        if obj is None:
            return
        
        self.units = getattr(obj, 'units', None)
        self.phys_quantity_type = getattr(obj, 'phys_quantity_type', None)

    def convert_units(self, new_units, in_place=True):
        """
        Method to convert the units of the stored physical quantities.
        The converted units may or may not be stored.

        Parameters
        ----------
        new_units : str
           Units to which the physical quantities will be converted.
        in_place : bool, optional
           Whetherh or not to store the converted units.

        Returns
        -------
        converted_quantities: dict
           The physical quantities in the new units.

        """
        new_units = standardize_units_name(new_units)

        # need to modify this to account for energy_conversion_factor and more
        conversion_factor = energy_conversion_factor(self.units, new_units)
        converted_quantities = {}

        for idx in np.arange(0, len(self)):
            converted_quantities[idx] = self[idx] * conversion_factor

        if conversion_factor != 1 and in_place:
            self.units = new_units
            self = converted_quantities
            print(f"Quantities have been converted to {new_units}.")

        return converted_quantities
