import pytest
import numpy as np

import perturbopy.postproc as ppy


@pytest.mark.parametrize("test_units, expected_hbar", [
                        ('eV*fs', 0.65821)
])
def test_hbar(test_units, expected_hbar):
    """
    Test the constants.conversion_factor function

    Parameters
    ----------
    test_units : str
       The units for hbar
    expected_hbar : float
       The expected value of hbar in the corresponding units

    """
    print(ppy.constants.hbar(test_units))
    assert(np.isclose(ppy.constants.hbar(test_units), expected_hbar))


@pytest.mark.parametrize("test_units1, test_units2, expected_factor", [
                        ('bohr', 'bohr', 1), ('bohr', 'nm', 5.29177249e-2),
                        ('cm', 'fm', 1e13), ('fm', 'cm', 1e-13),
                        ('meV', 'Ha', 3.674930882447527e-05), ('Ry', 'Ha', 0.5)
])
def test_conversion_factor(test_units1, test_units2, expected_factor):
    """
    Test the constants.conversion_factor function

    Parameters
    ----------
    test_units1, test_units2 : str
       The units between which to find a conversion factor
    expected_factor : float
       The expected conversion factor

    """
    assert(np.isclose(ppy.constants.conversion_factor(test_units1, test_units2), expected_factor))
