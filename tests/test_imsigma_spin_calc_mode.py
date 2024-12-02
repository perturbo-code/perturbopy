import numpy as np
import pytest
import os

import perturbopy.postproc as ppy


@pytest.fixture()
def gaas_imsigma_spin():
    """
    Method to generate the ImsigmaSpinCalcMode object corresponding to GaAs YAML file.

    Returns
    -------
    imsigma_spin : ppy.ImsigmaSpinCalcMode

    """
    yml_path = os.path.join("refs", "gaas_imsigma_spin.yml")
    return ppy.ImsigmaSpin.from_yaml(yml_path)
