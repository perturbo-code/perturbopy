import numpy as np
import pytest
import os

import perturbopy.postproc as ppy


@pytest.fixture()
def gaas_imsigma():
    """
    Method to generate the ImsigmaCalcMode object corresponding to GaAs YAML file.

    Returns
    -------
    imsigma : ppy.ImsigmaCalcMode

    """
    yml_path = os.path.join("refs", "gaas_imsigma.yml")
    return ppy.Imsigma.from_yaml(yml_path)
