import numpy as np
import pytest
import os

import perturbopy.postproc as ppy


@pytest.fixture()
def si_ephmat():
    """
    Method to generate the EphmatCalcMode object corresponding to Si YAML file.

    Returns
    -------
    ephmat : ppy.EphmatCalcMode

    """
    yml_path = os.path.join("refs", "si_ephmat.yml")
    return ppy.EphmatCalcMode.from_yaml(yml_path)