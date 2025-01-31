"""
Suite of Python scripts for the Perturbo code testing and postprocessing.
"""

from .calc_modes.calc_mode import CalcMode
from .calc_modes.bands import Bands
from .calc_modes.spectral_cumulant import SpectralCumulant
from .calc_modes.spins import Spins
from .calc_modes.phdisp import Phdisp
from .calc_modes.ephmat import Ephmat
from .calc_modes.ephmat_spin import EphmatSpin
from .calc_modes.trans import Trans
from .calc_modes.imsigma import Imsigma
from .calc_modes.imsigma_spin import ImsigmaSpin
from .calc_modes.dyna_run import DynaRun
from .calc_modes.dyna_pp import DynaPP

from .dbs.units_dict import UnitsDict
from .dbs.recip_pt_db import RecipPtDB

from .utils import constants, plot_tools, lattice, spectra_generate_pulse, \
    timing, spectra_trans_abs, spectra_plots

# import warnings
# import os


# # Define a custom format for warnings
# def custom_formatwarning(message, category, filename, lineno, line=None):
#     basename = os.path.basename(filename)
#     return f"{category.__name__} in {basename} at line {lineno}: {message}\n"


# # Apply the custom format
# warnings.formatwarning = custom_formatwarning
