import numpy as np
import pytest
import os

import perturbopy.postproc as ppy


@pytest.fixture()
def sto_spectral_cum():
    """
    Method to generate the spectral_cum object corresponding to spectralhdf5.

    Returns
    -------
    phdisp : ppy.PhdispCalcMode

    """
    yml_path = os.path.join("refs", "sto_spectral-cum.yml")
    spectral_path = os.path.join("refs", "sto_spectral_cumulant.h5")
    return ppy.SpectralCumulant.from_hdf5_yaml(spectral_path, yml_path)

def test_plot_spectral_cum(sto_spectral_cum, plt, with_plt):
    """
    Method to test SpectralCumulant.plot_Aw function

    Method to plot the spectral function A(ω)

    Parameters
    ----------
    show_qpoint_labels : bool, optional
        If true, the q-point labels stored in the labels attribute will be shown on the plot. Default true.

    """

    if not with_plt:
        pytest.skip("Test requires pytest-plt")

    fig, ax = plt.subplots()
    ppy.SpectralCumulant.plot_Aw(sto_spectral_cum, ax)

def test_spectral_cum():
    """
    Method to test SpectralCumulant.plot_Aw function array shape

    Parameters
    ----------

    """

    yml_path = os.path.join("refs", "sto_spectral-cum.yml")
    spectral_path = os.path.join("refs", "sto_spectral_cumulant.h5")
    model = ppy.SpectralCumulant.from_hdf5_yaml(spectral_path, yml_path)
    np.testing.assert_equal(model.Akw.shape, (1, 3, 2, 3001))
    np.testing.assert_equal(model.freq_array.shape, (3001,))

