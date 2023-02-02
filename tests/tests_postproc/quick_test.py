import os
from subprocess import call
import numpy as np
import matplotlib.pyplot as plt
from math import isclose

repo_dir = 'C:/Users/shael/github/perturbopy'
conda_path = 'C:/Users/shael/Anaconda3/Scripts/conda.exe'

os.chdir(repo_dir)
call(['pip','install','.'])

import perturbopy as ppy
import matplotlib.pyplot as plt

ge_bands_calc = ppy.BandsCalcMode.from_yaml(os.path.join('tests','refs_postproc','ge_bands.yml'))
print(ge_bands_calc.kpath_units)
ge_bands_calc.kpts_db.path_coords_units = 'not arbitrary'
print(ge_bands_calc.kpath_units)
