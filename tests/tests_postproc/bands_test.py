import os
from subprocess import call
import matplotlib.pyplot as plt

repo_dir = 'C:/Users/shael/github/perturbopy'
conda_path = 'C:/Users/shael/Anaconda3/Scripts/conda.exe'

os.chdir(repo_dir)
call(['pip','install','.'])

from perturbopy.postproc.calc_modes.bands_calc_mode import BandsCalcMode

ge_bands_calc = BandsCalcMode.from_yaml(os.path.join('tests', 'refs_postproc', 'ge_bands.yml'))

#### Test convert_energy_units function ###

print(ge_bands_calc.energy_units)
print(ge_bands_calc.bands[1][:5])

ge_bands_calc.convert_energy_units('hartree')
print(ge_bands_calc.energy_units)
print(ge_bands_calc.bands[1][:5])

### Test convert k points function ###

print(ge_bands_calc.kpt_coordinate_units)
print(ge_bands_calc.kpt_coordinates[100:105,:])
ge_bands_calc.convert_kpt_units('Cartesian')
print(ge_bands_calc.kpt_coordinate_units)
print(ge_bands_calc.kpt_coordinates[100:105,:])

# ### Test cryst_to_cart function ### 

vectors = [[0,0,0.5,0.25,0.25,0.375], [0,0.5,0.5,0.75,0.625,0.75], [0,0.5,0.5,0.5,0.625,0.375]]	
print(ge_bands_calc.cryst_to_cart(vectors, forward=True, real_space=False))

vectors = ge_bands_calc.cryst_to_cart(vectors, forward=True, real_space=False)
print(ge_bands_calc.cryst_to_cart(vectors, forward=False, real_space=False))

vectors = [[1,0.3],[1,0],[1,0.4]]
print(ge_bands_calc.cryst_to_cart(vectors, forward=True, real_space=True))

vectors = ge_bands_calc.cryst_to_cart(vectors, forward=True, real_space=True)
print(ge_bands_calc.cryst_to_cart(vectors, forward=False, real_space=True))

### Test scale_k_path_coordinates ###
print(ge_bands_calc.k_path_coordinates[:20])
ge_bands_calc.scale_k_path_coordinates(-1,1)
print(ge_bands_calc.k_path_coordinates[:20])

print(ge_bands_calc.compute_direct_bandgap(8,9))
print(ge_bands_calc.compute_indirect_bandgap(8,9))

### Test find k-point
idx = ge_bands_calc.find_kpt([0,0,0])
print(idx)
print(ge_bands_calc.kpt_coordinates[idx])
print(ge_bands_calc.kpt_coord_to_kpath_coord([0,0,0]))
print(ge_bands_calc.kpath_coord_to_kpt_coord(-0.23))

fig, ax = plt.subplots(1,1)
ge_bands_calc.label_kpt([0,0,0],r'$\Gamma$')
ge_bands_calc.label_kpt([.5,.5,.5],'L')

ge_bands_calc.plot_bands(ax)

plt.show()

print(ge_bands_calc.compute_effective_mass(9,[0.5,0.5,0.5], 0.05))

