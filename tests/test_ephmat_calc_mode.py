import numpy as np
import pytest
import os

import perturbopy.postproc as ppy


@pytest.fixture()
def gaas_ephmat():
    """
    Method to generate the EphmatCalcMode object corresponding to GaAs YAML file.

    Returns
    -------
    ephmat : ppy.EphmatCalcMode

    """
    yml_path = os.path.join("refs", "gaas_ephmat.yml")
    return ppy.Ephmat.from_yaml(yml_path)

@pytest.mark.parametrize("show_qpoint_labels", [
                        (False), (True)
])
def test_plot_phdisp(gaas_ephmat, plt, show_qpoint_labels, with_plt):
    """
    Method to test Ephmat.plot_phdisp function
    
    Method to plot the phonon dispersion.

    Parameters
    ----------
    show_qpoint_labels : bool, optional
        If true, the q-point labels stored in the labels attribute will be shown on the plot. Default true.

    """
    
    if not with_plt:
        pytest.skip("Test requires pytest-plt")

    fig, ax = plt.subplots()
    ppy.Ephmat.plot_phdisp(gaas_ephmat, ax, show_qpoint_labels)

@pytest.mark.parametrize("kpoint_idx, show_qpoint_labels", [
                        (0, False),
                        (2, True)
])
def test_plot_defpot(gaas_ephmat, plt, kpoint_idx, show_qpoint_labels, with_plt):
    """
    Method to test Ephmat.plot_defpot function
    
    Method to plot the deformation potential as a colormap overlaid on the phonon dispersion.

    kpoint_idx : int, optional
        Index of the k-point to plot the deformation potentials for. Deformation potentials will be plotted along q-points, at this k-point
        By default, it will be the first k-point.

    show_qpoint_labels : bool, optional
        If true, the q-point labels stored in the labels attribute will be shown on the plot. Default true.

    """
    
    if not with_plt:
        pytest.skip("Test requires pytest-plt")

    fig, ax = plt.subplots()
    ppy.Ephmat.plot_defpot(gaas_ephmat, ax, kpoint_idx, show_qpoint_labels)

@pytest.mark.parametrize("kpoint_idx, show_qpoint_labels", [
                        (0, False),
                        (2, True)
])
def test_plot_ephmat(gaas_ephmat, plt, kpoint_idx, show_qpoint_labels, with_plt):
    """
    Method to test Ephmat.plot_ephmat function
    
    Method to plot the e-ph matrix elements as a colormap overlaid on the phonon dispersion.

    kpoint_idx : int, optional
        Index of the k-point to plot the deformation potentials for. Deformation potentials will be plotted along q-points, at this k-point
        By default, it will be the first k-point.

    show_qpoint_labels : bool, optional
        If true, the q-point labels stored in the labels attribute will be shown on the plot. Default true.

    """
    
    if not with_plt:
        pytest.skip("Test requires pytest-plt")

    fig, ax = plt.subplots()
    ppy.Ephmat.plot_ephmat(gaas_ephmat, ax, kpoint_idx, show_qpoint_labels)
