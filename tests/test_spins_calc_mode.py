import numpy as np
import pytest
import os

import perturbopy.postproc as ppy


@pytest.fixture()
def gaas_spins():
    """
    Method to generate the SpinsCalcMode object corresponding to GaAs YAML file.

    Returns
    -------
    spins : ppy.SpinsCalcMode

    """
    yml_path = os.path.join("refs", "gaas_spins.yml")
    return ppy.Spins.from_yaml(yml_path)

@pytest.mark.parametrize("kpoint_idx, show_kpoint_labels, log", [
                        (2, False, False),
                        (0, True, True),
                        (1, True, False)
])
def test_plot_spins(gaas_spins, plt, kpoint_idx, show_kpoint_labels, log, with_plt):
    """
    Method to plot the <n|Sigma_z|n> values over the band structure.

    Parameters
    ----------
    kpoint_idx : int, optional
        Index of the k-point to plot the <n|Sigma_z|n> values for. <n|Sigma_z|n> elements will be plotted along k-points, at this k-point.
        By default, it will be the first k-point.

    show_kpoint_labels : bool, optional
        If true, the k-point labels stored in the labels attribute will be shown on the plot. Default true.
    
    log : bool, optional
        If true, the plot will normalize values on a log scale. If false, the plot will normalize values linearly.
        By default, true.

    """
    
    if not with_plt:
        pytest.skip("Test requires pytest-plt")

    fig, ax = plt.subplots()
    ppy.Spins.plot_spins(gaas_spins, ax, kpoint_idx, show_kpoint_labels, log)
