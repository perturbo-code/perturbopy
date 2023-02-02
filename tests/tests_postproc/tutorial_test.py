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

fig, ax = plt.subplots(1,1)
ge_bands_calc.plot_bands(ax)
plt.show()

indirect_bg,init_kpt,final_kpt = ge_bands_calc.compute_indirect_bandgap(8,9)
direct_bg,direct_kpt = ge_bands_calc.compute_direct_bandgap(8,9)

print(f"The indirect bandgap is {indirect_bg} \nfrom kpt {init_kpt} to kpt {final_kpt}\n\n")
print(f"The direct bandgap is {direct_bg} at \nkpt {direct_kpt}")

# effective_mass = ge_bands_calc.compute_effective_mass(9,[0.5,0.5,0.5], 0.1)
# print(f"The effective_mass is {effective_mass}")

si_phdisp_calc = ppy.PhdispCalcMode.from_yaml(os.path.join('tests','refs_postproc','si_phdisp.yml'))

# si_phdisp_calc.label_qpts(special_kpts)
si_phdisp_calc.plot_phdisp(ax)

plotparams = ppy.plot_tools.plotparams
plotparams['font.size'] = 25
plt.rcParams.update(plotparams)

plt.show()