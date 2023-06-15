import pytest
import math

import perturbopy.postproc as ppy

test_dict = {'bohr': ['bohr', 'a.u', 'atomic units', 'au'], 'angstrom': ['angstrom, a'], 'm': ['m', 'meter']}
test_vals = {'bohr': (1, 0), 'angstrom': (0.529177249, 0), 'm': (5.29177249, -11)}


@pytest.mark.parametrize("test_prefix, expected_exponent", [
                        ('m', -3), ('M', 6), ('mu', -6), ('Y', 24), ('', 0)
])
def test_prefix_exp(test_prefix, expected_exponent):
    """
    Method to test the constants.prefix_exp function

    Parameters
    ----------
    test_prefix : str
       The prefix to be converted to an exponent
    expected_exponent : int
       The expected exponent that the function should return

    """
    assert(ppy.constants.prefix_exp(test_prefix) == expected_exponent)


@pytest.mark.parametrize("test_units, expected", [
                        ('a.u', ('', 'bohr')), ('A.U', ('', 'bohr')), ('Bohr', ('', 'bohr')),
                        ('nm', ('n', 'm'))
])
def test_find_prefix_and_base_units(test_units, expected):
    """
    Method to test the constants.find_prefix_and_base_units function

    Parameters
    ----------
    test_units : str
       The units to be decomposed into prefix and base
    expected : tuple
       The expected prefix and base units to be returned

    """
    assert(ppy.constants.find_prefix_and_base_units(test_units, test_dict) == expected)


@pytest.mark.parametrize("test_units, expected_units", [
                        ('a.u', 'bohr'), ('A.U', 'bohr'), ('Bohr', 'bohr'),
                        ('nm', 'nm')
])
def test_standardize_units_name(test_units, expected_units):
    """
    Method to test the constants.find_prefix_and_base_units function

    Parameters
    ----------
    test_units : str
       The units to be converted to a standard units name
    expected_units : str
       The expected standardized units to be returned

    """
    assert(ppy.constants.standardize_units_name(test_units, test_dict) == expected_units)


@pytest.mark.parametrize("test_units1, test_units2, expected_factor", [
                        ('a.u', 'bohr', 1), ('a.u', 'nm', 5.29177249e-2),
                        ('cm', 'fm', 1e13), ('fm', 'cm', 1e-13),
                        ('a.u', 'bohr', 1), ('a.u', 'nm', 5.29177249e-2),
                        ('cm', 'fm', 1e13), ('fm', 'cm', 1e-13)
])
def test_conversion_factor(test_units1, test_units2, expected_factor):
    """
    Method to test the constants.conversion_factor function

    Parameters
    ----------
    test_units1, test_units2 : str
       The units between which to find a conversion factor
    expected_factor : float
       The expected conversion factor

    """
    assert(math.isclose(ppy.constants.conversion_factor(test_units1, test_units2, test_dict, test_vals), expected_factor))


@pytest.mark.parametrize("test_units1, test_units2, expected_factor", [
                        ('a.u', 'bohr', 1), ('a.u', 'nm', 5.29177249e-2),
                        ('cm', 'fm', 1e13), ('fm', 'cm', 1e-13),
                        ('a.u', 'bohr', 1), ('a.u', 'nm', 5.29177249e-2),
                        ('cm', 'fm', 1e13), ('fm', 'cm', 1e-13)
])
def test_length_conversion_factor(test_units1, test_units2, expected_factor):
    """
    Method to test the constants.length_conversion_factor function

    Parameters
    ----------
    test_units1, test_units2 : str
       The units between which to find a conversion factor
    expected_factor : float
       The expected conversion factor

    """
    assert(math.isclose(ppy.constants.length_conversion_factor(test_units1, test_units2), expected_factor))


@pytest.mark.parametrize("test_units, expected_hbar", [
                        ('ev*fs', 0.6582119569), ('atomic', 1)
])
def test_hbar(test_units, expected_hbar):
    """
    Method to test the constants.conversion_factor function

    Parameters
    ----------
    test_units : str
       The units for hbar
    expected_hbar : float
       The expected value of hbar in the corresponding units

    """
    assert(math.isclose(ppy.constants.hbar(test_units), expected_hbar))
