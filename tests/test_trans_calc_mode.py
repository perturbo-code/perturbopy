import numpy as np
import pytest
import os

import perturbopy.postproc as ppy


@pytest.fixture()
def gaas_trans():
    """
    Method to generate the TransCalcMode object corresponding to GaAs YAML file.

    Returns
    -------
    trans : ppy.TransCalcMode

    """
    yml_path = os.path.join("refs", "gaas_trans-ita.yml")
    return ppy.Trans.from_yaml(yml_path)
