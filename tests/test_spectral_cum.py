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
    prefix='refs/sto'
    return ppy.SpectralCumulant(prefix)


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
    ppy.SpectralCumulant.plot_Aw_(sto_spectral_cum, plt, ax)