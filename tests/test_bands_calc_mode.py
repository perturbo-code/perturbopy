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
    yml_path = os.path.join("refs", "gaas_bands.yml")
    return ppy.Bands.from_yaml(yml_path)


@pytest.mark.parametrize("n_lower, n_upper, expected_gap, expected_kpoint", [
                         [4, 5, 0.29572179519999864, [0.01442, 0.01442, 0.02885]],
                         [8, 9, 0.44878296240000104, [0., 0., 0.]]
])
def test_direct_bandgap(gaas_bands, n_lower, n_upper, expected_gap, expected_kpoint):
    """
    Method to test direct_bandgap

    Parameters
    ----------
    n_lower, n_upper : int
       Band number of the lower and upper bands.

    expected_gap : float

    expected_kpoint : array_like

    """
    gap, kpoint = gaas_bands.direct_bandgap(n_lower, n_upper)
    assert(np.isclose(expected_gap, gap))
    assert(np.allclose(expected_kpoint, kpoint))

@pytest.mark.parametrize("n_lower, n_upper, expected_gap, expected_kpoint_lower, expected_kpoint_upper", [
                         [8, 9, 0.44878296240000104, [0., 0., 0.], [0., 0., 0.]],
                         [10, 11, -0.2976607195999996, [0.21635, 0.21635, 0.43269], [0.5, 0., 0.5]]
])
def test_indirect_bandgap(gaas_bands, n_lower, n_upper, expected_gap, expected_kpoint_lower, expected_kpoint_upper):
    """
    Method to test indirect_bandgap

    Parameters
    ----------
    n_lower, n_upper : int
       Band number of the lower and upper bands.

    expected_gap : float

    expected_kpoint_lower, expected_kpoint_upper : array_like

    """
    gap, kpoint_lower, kpoint_upper = gaas_bands.indirect_bandgap(n_lower, n_upper)
    assert(np.isclose(expected_gap, gap))
    assert(np.allclose(expected_kpoint_lower, kpoint_lower))
    assert(np.allclose(expected_kpoint_upper, kpoint_upper))


@pytest.mark.parametrize("n, kpoint, max_distance, direction, expected_m", [
                         [9, [0, 0, 0], 0.1, [0.5, 0.5, 0.5], 0.11826539850425859]
])
def test_effective_mass(gaas_bands, n, kpoint, max_distance, direction, expected_m):
    """
    Method to test effective_mass

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
    print(gaas_bands.bands)
    m = gaas_bands.effective_mass(n, kpoint, max_distance, direction)
    assert(np.isclose(expected_m, m))

@pytest.mark.parametrize("show_kpoint_labels", [
                        (False), (True)
])
def test_plot_bands(gaas_bands, plt, show_kpoint_labels, with_plt):
    """
    Method to test bands.plot_bands function.

    Method to plot the band structure.

    Parameters
    ----------
    show_kpoint_labels : bool, optional
        If true, the k-point labels stored in the labels attribute will be shown on the plot. Default true.

    """
    
    if not with_plt:
        pytest.skip("Test requires pytest-plt")

    fig, ax = plt.subplots()
    ppy.Bands.plot_bands(gaas_bands, ax, show_kpoint_labels)
