"""
This is a module for working with constants, including storing values for different units and finding conversion factors.

"""

import pint
import re 


ureg = pint.UnitRegistry()
ureg.define('hartree = 2.0 Ry = Ha')

def conversion_factor(from_units, to_units):
    
    return ureg(from_units).to(ureg(to_units)).magnitude

def standardize_units_name(units):

    number_pattern = r'(-?\d+(\.\d+)?)'
    units = re.sub(number_pattern, r'^\1', units)

    try:
        return ureg(units)

    except pint.errors.UndefinedUnitError:
        
        print(f"'{units}' is not defined in the UnitRegistry.")
        return None

def hbar(units):
    """
    Calculate the reduced Planck constant (h-bar) in the specified units using Pint.

    Parameters
    ----------
    units : str
        The desired units for the result.

    Returns
    -------
    Quantity
        The value of h-bar in the specified units.

    """
    hbar_value = 1.0545718e-34  # Planck constant in J·s

    # Use Pint to convert the Planck constant to the desired units
    hbar_in_units = hbar_value * ureg.joule * ureg.second

    return hbar_in_units.to(units).magnitude
