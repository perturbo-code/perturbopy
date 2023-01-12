import numpy as np
import matplotlib.pyplot as plt
import math
from scipy.optimize import curve_fit
from perturbopy.postproc.calc_modes.calc_mode import BandsCalcMode
from perturbopy.postproc.utils.constants import energy_conversion_factor, standard_units_name

class PhdispCalcMode(BandsCalcMode):

	def __init__(self, pert_dict, labeled_kpts=None):
      """
      Constructor method

      """
      super().__init__(pert_dict)
      
      if self.calc_mode != 'phdisp':
         raise Exception('Calculation mode for a PhdispCalcMode object should be "phdisp"')
