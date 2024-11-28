import numpy as np
import pytest
import os

import perturbopy.postproc as ppy


@pytest.fixture()
def gaas_phdisp():
    """
    Method to generate the PhdispCalcMode object corresponding to GaAs YAML file.

    Returns
    -------
    phdisp : ppy.PhdispCalcMode

    """
    yml_path = os.path.join("refs", "gaas_phdisp.yml")
    return ppy.Phdisp.from_yaml(yml_path)

@pytest.mark.parametrize("show_qpoint_labels", [
                        (False), (True)
])
def test_plot_phdisp(gaas_phdisp, plt, show_qpoint_labels, with_plt):
    """
    Method to test Phdisp.plot_phdisp function
    
    Method to plot the phonon dispersion.

    Parameters
    ----------
    show_qpoint_labels : bool, optional
        If true, the q-point labels stored in the labels attribute will be shown on the plot. Default true.

    """
    
    if not with_plt:
        pytest.skip("Test requires pytest-plt")

    fig, ax = plt.subplots()
    ppy.Phdisp.plot_phdisp(gaas_phdisp, ax, show_qpoint_labels)
