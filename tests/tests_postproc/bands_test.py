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
ge_bands_calc = ppy.BandsCalcMode.from_yaml(os.path.join('tests', 'refs_postproc', 'ge_bands.yml'))

###### TEST CONSTANTS #######

# Test prefix_exp
assert(ppy.constants.prefix_exp('m') == -3)
assert(ppy.constants.prefix_exp('M') == 6)
assert(ppy.constants.prefix_exp('mu') == -6)
assert(ppy.constants.prefix_exp('Y') == 24)
assert(ppy.constants.prefix_exp('') == 0)

# Test prefix_conversion_exp
assert(ppy.constants.prefix_conversion_exp('m') == 3)
assert(ppy.constants.prefix_conversion_exp('M') == -6)
assert(ppy.constants.prefix_conversion_exp('mu') == 6)
assert(ppy.constants.prefix_conversion_exp('Y') == -24)
assert(ppy.constants.prefix_conversion_exp('') == 0)

# Test find_prefix_and_base_units

test_dict = {'bohr':['bohr', 'a.u', 'atomic units', 'au'], 'angstrom':['angstrom, a'], 'm':['m', 'meter'] }

assert(ppy.constants.find_prefix_and_base_units('a.u', test_dict) == ('', 'bohr'))
assert(ppy.constants.find_prefix_and_base_units('A.U', test_dict) == ('', 'bohr'))
assert(ppy.constants.find_prefix_and_base_units('bohr', test_dict) == ('', 'bohr'))
assert(ppy.constants.find_prefix_and_base_units('Bohr', test_dict) == ('', 'bohr'))
assert(ppy.constants.find_prefix_and_base_units('nm', test_dict) == ('n', 'm'))


# Test standardize_units_name
assert(ppy.constants.standardize_units_name('a.u', test_dict) == 'bohr')
assert(ppy.constants.standardize_units_name('A.U', test_dict) == 'bohr')
assert(ppy.constants.standardize_units_name('bohr', test_dict) == 'bohr')
assert(ppy.constants.standardize_units_name('Bohr', test_dict) == 'bohr')
assert(ppy.constants.standardize_units_name('nm', test_dict) == 'nm')

# Test conversion_factor
test_vals = {'bohr': (1, 0), 'angstrom': (0.529177249, 0), 'm': (5.29177249, -11)}
assert(isclose(ppy.constants.conversion_factor('a.u', 'bohr', test_dict, test_vals), 1))
assert(isclose(ppy.constants.conversion_factor('a.u', 'nm', test_dict, test_vals), 5.29177249e-2))
assert(isclose(ppy.constants.conversion_factor('cm', 'fm', test_dict, test_vals), 1e13))
assert(isclose(ppy.constants.conversion_factor('fm', 'cm', test_dict, test_vals), 1e-13))

# Test energy_conversion_factor

# Test length_conversion_factor

# Test hbar


####### TEST LATTICE UTILS #######

# Test reshape_kpts
kpts = [[1,2,3],[0,0,0],[4,5,6]]
assert(np.all(ppy.lattice.reshape_kpts(kpts)==np.array(kpts)))

kpts=np.array(kpts)
assert(np.all(ppy.lattice.reshape_kpts(kpts)==kpts))

kpts = ([[1,2,3],[0,0,0],[4,5,6],[1,1,1],[2,2,2]])
assert(np.shape(ppy.lattice.reshape_kpts(kpts))==(3,5))
assert(np.all(ppy.lattice.reshape_kpts(kpts)==np.transpose(np.array(kpts))))

kpts = ([[1,2,3,3,2,1,4],[0,0,0,0,0,0,0],[1,2,1,1,1,1,1]])
np.shape(ppy.lattice.reshape_kpts(kpts))==(3,7)
assert(np.all(ppy.lattice.reshape_kpts(kpts)==(np.array(kpts))))

# Test cryst_to_cart

vectors_cryst = [[1,0.3],[1,0],[1,0.4]]
vectors_cart = [[1,   0.15], [1,   0.2 ], [1,   0.35]]
assert(np.all(ppy.lattice.cryst_to_cart(vectors_cryst, ge_bands_calc.lat, ge_bands_calc.recip_lat, forward=True, real_space=True) == vectors_cart))
# assert(np.all(cryst_to_cart(vectors_cart, ge_bands_calc.lat, ge_bands_calc.recip_lat, forward=False, real_space=True) == vectors_cryst))

lat = [[0.5, 0.5, 0.0], [0.0, 0.5, 0.5], [0.5, 0.0, 0.5]]
recip_lat = [[1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, 1.0]]
vectors_cryst = [[0,0,0.5,0.25,0.25,0.375], [0,0.5,0.5,0.75,0.625,0.75], [0,0.5,0.5,0.5,0.625,0.375]]	
vectors_cart = [[0, 0, 0.5, 0.5,  0.25, 0.75], [0, 1, 0.5, 1,   1,   0.75], [0,   0,   0.5, 0,   0.25,0.]]
assert(np.all(ppy.lattice.cryst_to_cart(vectors_cryst, ge_bands_calc.lat, ge_bands_calc.recip_lat, forward=True, real_space=False) == vectors_cart))
assert(np.all(ppy.lattice.cryst_to_cart(vectors_cart, ge_bands_calc.lat, ge_bands_calc.recip_lat, forward=False, real_space=False) == vectors_cryst))

####### TEST KPT LIST #######
# Test constructor
kpts_cart = vectors_cart
kpts_cryst = vectors_cryst
units = 'cryst'

lat = [[0.5, 0.5, 0.0], [0.0, 0.5, 0.5], [0.5, 0.0, 0.5]]
recip_lat = [[1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, 1.0]]

kpts_db = ppy.KptsDB(kpts_cart, kpts_cryst, units='crystal', kpath=None, kpath_units='arbitrary', labels=None)
assert(np.all(kpts_db.kpts_cart == vectors_cart))
assert(np.all(kpts_db.kpts_cryst == vectors_cryst))
assert(kpts_db.units == 'crystal')
assert(len(kpts_db.kpath==7))

# Test from_lattice
kpts_db2 = ppy.KptsDB.from_lattice(kpts_cryst, 'cryst', lat, recip_lat)
assert(np.all(kpts_db2.kpts_cryst == vectors_cryst))
assert(np.all(kpts_db2.kpts_cart == vectors_cart))
assert(kpts_db2.units == 'crystal')   # def from_lattice(self, kpts, units, lat, recip_lat, kpath=None, kpath_units='arbitrary', labels=None):

# Test kpts_from_units and kpts
assert(np.all(kpts_db.kpts_from_units('cart') == kpts_db.kpts_cart))
assert(np.all(kpts_db.kpts_from_units('tpiba') == kpts_db.kpts_cart))
assert(np.all(kpts_db.kpts_from_units('frac') == kpts_db.kpts_cryst))
assert(np.all(kpts_db.kpts_from_units('crystal') == kpts_db.kpts_cryst))

# Test units property and setter
assert(kpts_db.units == 'crystal')
kpts_db.units = 'frac'
assert(kpts_db.units == 'crystal')
assert(kpts_db._units == 'crystal')
kpts_db.units = 'cart'
assert(kpts_db.units == 'cartesian')

# Test kpts property
kpts_db.units = 'cryst'
assert(kpts_db.units == 'crystal')
assert(np.all(kpts_db.kpts == kpts_db.kpts_cryst))
kpts_db.units = 'Cartesian'
assert(kpts_db.units == 'cartesian')
assert(np.all(kpts_db.kpts == kpts_db.kpts_cart))

# Test scale_kpath(self, range_min, range_max):
kpts_db.scale_kpath(0,0.5)
assert(np.all(kpts_db.kpath == [0,0.1,0.2,0.3,0.4,0.5]))

# Test compute_kpt_distances(self, kpt, units):

assert(np.all(np.isclose(kpts_db.compute_kpt_distances(kpts_db.kpts), [0., 0., 0, 0., 0., 0.])))
assert(np.all(np.isclose(kpts_db.compute_kpt_distances([0.5,0.5,0.5]), [0.8660254, 0.8660254, 0, 0.70710678, 0.61237244, 0.61237244])))

# Test find_kpt(self, kpt, nearest=True, **kwargs):
assert(kpts_db.find_kpt([0,0,0]) == 0)
assert(kpts_db.find_kpt([0.5,1,0]) == 3)
assert(kpts_db.find_kpt([0.499,1,0]) == 3)
# assert(kpts_db.find_kpt([0.55,1,0]) == ValueError)

# Test kpt_to_kpath(self, kpt, units, nearest=True):
assert(kpts_db.kpt_to_kpath([0.5,1,0]) == 0.3)
assert(kpts_db.kpt_to_kpath([0.499,1,0]) == 0.3)

# Test kpath_coord_to_kpt_coord(self, kpath, nearest=True, **kwargs):
assert(np.all(kpts_db.kpath_to_kpt(0.3) == [0.5,1,0]))

##### TEST ENERGIES ######
# Test constructor
energies_db = ppy.EnergiesDB({1:[0.1,0.2,0.3], 2:[0.3,0.4,0.5]}, 'meV')
assert(energies_db.nbands == 2)

# Test band_indices property
assert(energies_db.band_indices == [1,2])

# Test convert_units
assert(np.all(energies_db.convert_units('eV')[1] == [0.0001,0.0002,0.0003]))
assert(np.all(energies_db.convert_units('electronvolt')[2] == [0.0003,0.0004,0.0005]))
assert(np.all(energies_db.energies[1] == [0.1,0.2,0.3]))
assert(np.all(energies_db.energies[2] == [0.3,0.4,0.5]))
assert(energies_db.units == 'meV')

# Test units property and setter
energies_db.units = 'eV'
assert(np.all(energies_db.energies[1] == [0.0001,0.0002,0.0003]))
assert(np.all(energies_db.energies[2] == [0.0003,0.0004,0.0005]))
assert(energies_db.units == 'eV')


###### TEST PLOT UTILS ########

###### TEST BANDS CALC MODE ########

# Test constructor
ge_bands_calc = ppy.BandsCalcMode.from_yaml(os.path.join('tests', 'refs_postproc', 'ge_bands.yml'))

# Test compute_indirect_bandgap and compute_direct_bandgap
print(ge_bands_calc.compute_indirect_bandgap(8, 9))
print(ge_bands_calc.compute_direct_bandgap(8, 9))

# Test compute_effective_mass(self, n, kpt, max_distance):
# print(ge_bands_calc.compute_effective_mass(9, [0,0,0], 0.01))

# Test plot_bands(self, ax, show_kpt_labels=True, **kwargs):
# ppy.plot_tools.plot_bands(ax)

plt.rcParams.update(ppy.plot_tools.plotparams)
print(plotparams)

fig, ax = plt.subplots(1,1)
ge_bands_calc.kpt_db.label_kpt([0,0,0],r'$\Gamma$')
ge_bands_calc.kpt_db.label_kpt([.5,.5,.5],'L')
ge_bands_calc.plot_bands(ax)

plt.show()

# # print(ge_bands_calc.compute_effective_mass(9,[0.5,0.5,0.5], 0.05))

