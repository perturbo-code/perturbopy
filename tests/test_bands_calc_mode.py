import numpy as np
import pytest
import os

import perturbopy.postproc as ppy


@pytest.fixture()
def gaas_bands():
   """
   Method to generate the BandsCalcMode object corresponding to GaAs YAML file.

   Returns
   -------
   bands : ppy.BandsCalcMode

   """
   print("HELLO")
   print(os.path.dirname(os.getcwd()))
   print(os.getcwd())
   yml_path = os.path.join("refs", "gaas_bands.yml")
   return ppy.BandsCalcMode.from_yaml(yml_path)


@pytest.mark.parametrize("n_lower, n_upper, expected_gap, expected_kpoint", [
                         [4, 5, 0.29572179519999864, [0.01442, 0.01442, 0.02885]],
                         [8, 9, 0.44878296240000104, [0., 0., 0.]]
])
def test_compute_direct_bandgap(gaas_bands, n_lower, n_upper, expected_gap, expected_kpoint):
   """
   Method to test compute_direct_bandgap
 
   Parameters
   ----------
   n_lower, n_upper : int
      Band number of the lower and upper bands.
   
   expected_gap : float

   expected_kpoint : array_like

   """
   gap, kpoint = gaas_bands.compute_direct_bandgap(n_lower, n_upper)
   assert(np.isclose(expected_gap, gap))
   assert(np.allclose(expected_kpoint, kpoint))


@pytest.mark.parametrize("n_lower, n_upper, expected_gap, expected_kpoint_lower, expected_kpoint_upper", [
                         [8, 9, 0.44878296240000104, [0., 0., 0.], [0., 0., 0.]],
                         [10, 11, -0.2976607195999996, [0.21635, 0.21635, 0.43269], [0.5, 0., 0.5]]
])
def test_compute_indirect_bandgap(gaas_bands, n_lower, n_upper, expected_gap, expected_kpoint_lower, expected_kpoint_upper):
   """
   Method to test compute_indirect_bandgap
 
   Parameters
   ----------
   n_lower, n_upper : int
      Band number of the lower and upper bands.
   
   expected_gap : float

   expected_kpoint_lower, expected_kpoint_upper : array_like

   """
   gap, kpoint_lower, kpoint_upper = gaas_bands.compute_indirect_bandgap(n_lower, n_upper)
   assert(np.isclose(expected_gap, gap))
   assert(np.allclose(expected_kpoint_lower, kpoint_lower))
   assert(np.allclose(expected_kpoint_upper, kpoint_upper))


@pytest.mark.parametrize("n, kpoint, max_distance, direction, expected_m", [
                         [9, [0, 0, 0], 0.1, [0.5, 0.5, 0.5], 0.11826539850425859]
])
def test_compute_effective_mass(gaas_bands, n, kpoint, max_distance, direction, expected_m):
   """
   Method to test compute_effective_mass
 
   Parameters
   ----------
   n : int
      Index of the band for which to calculate the effective mass.
   
   kpoint : list
      The k-point on which to center the calculation.

   max_distance : float
      Maximum distance between the center k-point and k-points to include in the parabolic approximation.

   direction : array_like
      The k-point specifying the direction of the effective mass. Defaults to the same value as kpoint,
      i.e. the longitudinal effective mass.

   expected_m : float
      The expected effective mass computed

   """
   m, _ = gaas_bands.compute_effective_mass(n, kpoint, max_distance, direction)
   print(m)
   assert(np.isclose(expected_m, m))
