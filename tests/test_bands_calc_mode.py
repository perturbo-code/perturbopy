import numpy as np
import pytest
import os

import perturbopy.postproc as ppy


@pytest.fixture()
def gaas_bands():
   yml_path = os.path.join(os.path.dirname(os.getcwd()), "tests_f90", "refs_perturbo", "epwan1-bands", "pert_output.yml")
   return ppy.BandsCalcMode.from_yaml(yml_path)

@pytest.mark.parametrize("n_lower, n_upper, expected_gap, expected_kpoint", [
   [4, 5, 0.29572179519999864, [0.01442, 0.01442, 0.02885]],
   [8, 9, 0.44878296240000104, [0., 0., 0.]]
])
def test_compute_direct_bandgap(gaas_bands, n_lower, n_upper, expected_gap, expected_kpoint):
   gap, kpoint = gaas_bands.compute_direct_bandgap(n_lower, n_upper)
   assert(np.isclose(expected_gap, gap))
   assert(np.allclose(expected_kpoint, kpoint))

@pytest.mark.parametrize("n_lower, n_upper, expected_gap, expected_kpoint_lower, expected_kpoint_upper", [
   [8, 9, 0.44878296240000104, [0., 0., 0.], [0., 0., 0.]],
   [10, 11, -0.2976607195999996, [0.21635, 0.21635, 0.43269], [0.5, 0., 0.5]] 
])
def test_compute_indirect_bandgap(gaas_bands, n_lower, n_upper, expected_gap, expected_kpoint_lower, expected_kpoint_upper):
   gap, kpoint_lower, kpoint_upper = gaas_bands.compute_indirect_bandgap(n_lower, n_upper)
   assert(np.isclose(expected_gap, gap))
   assert(np.allclose(expected_kpoint_lower, kpoint_lower))
   assert(np.allclose(expected_kpoint_upper, kpoint_upper))
# def test_compute_effective_mass(n_lower, n_upper, expected):
   
# def test_compute_direct_gap(n_lower, n_upper, expected):
