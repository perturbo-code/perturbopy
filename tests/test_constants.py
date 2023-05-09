import pytest
import math

import perturbopy.postproc as ppy

test_dict = {'bohr': ['bohr', 'a.u', 'atomic units', 'au'], 'angstrom': ['angstrom, a'], 'm': ['m', 'meter']}
test_vals = {'bohr': (1, 0), 'angstrom': (0.529177249, 0), 'm': (5.29177249, -11)}


@pytest.mark.parametrize("test_input, expected", [
                        ('m', -3), ('M', 6), ('mu', -6), ('Y', 24), ('', 0)
])
def test_prefix_exp(test_input, expected):
   assert(ppy.constants.prefix_exp(test_input) == expected)


@pytest.mark.parametrize("test_input, expected", [
                        ('a.u', ('', 'bohr')), ('A.U', ('', 'bohr')), ('Bohr', ('', 'bohr')),
                        ('nm', ('n', 'm'))
])
def test_find_prefix_and_base_units(test_input, expected):
   assert(ppy.constants.find_prefix_and_base_units(test_input, test_dict) == expected)


@pytest.mark.parametrize("test_input, expected", [
                        ('a.u', 'bohr'), ('A.U', 'bohr'), ('Bohr', 'bohr'),
                        ('nm', 'nm')
])
def test_standardize_units_name(test_input, expected):
   assert(ppy.constants.standardize_units_name(test_input, test_dict) == expected)


@pytest.mark.parametrize("test_input1, test_input2, expected", [
                        ('a.u', 'bohr', 1), ('a.u', 'nm', 5.29177249e-2),
                        ('cm', 'fm', 1e13), ('fm', 'cm', 1e-13),
                        ('a.u', 'bohr', 1), ('a.u', 'nm', 5.29177249e-2),
                        ('cm', 'fm', 1e13), ('fm', 'cm', 1e-13)
])
def test_conversion_factor(test_input1, test_input2, expected):
   assert(math.isclose(ppy.constants.conversion_factor(test_input1, test_input2, test_dict, test_vals), expected))


@pytest.mark.parametrize("test_input1, test_input2, expected", [
                        ('a.u', 'bohr', 1), ('a.u', 'nm', 5.29177249e-2),
                        ('cm', 'fm', 1e13), ('fm', 'cm', 1e-13),
                        ('a.u', 'bohr', 1), ('a.u', 'nm', 5.29177249e-2),
                        ('cm', 'fm', 1e13), ('fm', 'cm', 1e-13)
])
def test_length_conversion_factor(test_input1, test_input2, expected):
   assert(math.isclose(ppy.constants.length_conversion_factor(test_input1, test_input2), expected))


@pytest.mark.parametrize("test_input, expected", [
                        ('ev*fs', 0.6582119569), ('atomic', 1)
])
def test_hbar(test_input, expected):
   print(ppy.constants.hbar(test_input))
   assert(math.isclose(ppy.constants.hbar(test_input), expected))
