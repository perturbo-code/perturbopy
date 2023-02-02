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
si_bands_calc = ppy.BandsCalcMode.from_yaml(os.path.join('tests', 'refs_postproc', 'si_bands.yml'))
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

# Test reshape_points
kpoints = [[1,2,3],[0,0,0],[4,5,6]]
assert(np.all(ppy.lattice.reshape_points(kpoints)==np.array(kpoints)))

kpoints=np.array(kpoints)
assert(np.all(ppy.lattice.reshape_points(kpoints)==kpoints))

kpoints = ([[1,2,3],[0,0,0],[4,5,6],[1,1,1],[2,2,2]])
assert(np.shape(ppy.lattice.reshape_points(kpoints))==(3,5))
assert(np.all(ppy.lattice.reshape_points(kpoints)==np.transpose(np.array(kpoints))))

kpoints = ([[1,2,3,3,2,1,4],[0,0,0,0,0,0,0],[1,2,1,1,1,1,1]])
np.shape(ppy.lattice.reshape_points(kpoints))==(3,7)
assert(np.all(ppy.lattice.reshape_points(kpoints)==(np.array(kpoints))))

# Test cryst_to_cart

vectors_cryst = [[1,0.3],[1,0],[1,0.4]]
vectors_cart = [[-1,   -0.35], [1,   0.2 ], [1,   0.15]]
assert(np.all(ppy.lattice.cryst_to_cart(vectors_cryst, ge_bands_calc.lat, ge_bands_calc.recip_lat, forward=True, real_space=True) == vectors_cart))
# assert(np.all(cryst_to_cart(vectors_cart, ge_bands_calc.lat, ge_bands_calc.recip_lat, forward=False, real_space=True) == vectors_cryst))

lat = [[0.5, 0.5, 0.0], [0.0, 0.5, 0.5], [0.5, 0.0, 0.5]]
recip_lat = [[1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, 1.0]]
vectors_cryst = [[0,0,0.5,0.25,0.25,0.375], [0,0.5,0.5,0.75,0.625,0.75], [0,0.5,0.5,0.5,0.625,0.375]]	
# vectors_cart = [[0, 0, 0.5, 0.5,  0.25, 0.75], [0, 1, 0.5, 1,   1,   0.75], [0,   0,   0.5, 0,   0.25,0.]]
vectors_cart = [[ 0, -0.25, -0.5, -0.375, -0.4375, -0.375 ], [ 0., 0.5, 0.5, 0.625, 0.625, 0.5625], [ 0, 0.25, 0.5, 0.5, 0.4375,  0.5625],]
vectors_cart = [[ 0., 0.,-0.5,0.,-0.25,0.,], [ 0., 1., 0.5,1., 1., 0.75], [ 0., 0., 0.5,0.5,0.25,0.75]]

assert(np.all(ppy.lattice.cryst_to_cart(vectors_cryst, ge_bands_calc.lat, ge_bands_calc.recip_lat, forward=True, real_space=False) == vectors_cart))
assert(np.all(ppy.lattice.cryst_to_cart(vectors_cart, ge_bands_calc.lat, ge_bands_calc.recip_lat, forward=False, real_space=False) == vectors_cryst))

####### TEST kpoint LIST #######
# Test constructor
kpoints_cart = vectors_cart
kpoints_cryst = vectors_cryst
units = 'cryst'

lat = [  -0.50000,     0.00000,    -0.50000,  ], [   0.00000,     0.50000,     0.50000,  ], [   0.50000,     0.50000,     0.00000,  ]
recip_lat = [  -1.00000,     1.00000,    -1.00000,  ], [  -1.00000,     1.00000,     1.00000,  ], [   1.00000,     1.00000,    -1.00000,  ]

kpoints_db = ppy.RecipPtDB(kpoints_cart, kpoints_cryst, units='crystal', path=None, path_units='arbitrary', labels=None)
assert(np.all(kpoints_db.coords_cart == vectors_cart))
assert(np.all(kpoints_db.coords_cryst == vectors_cryst))
assert(kpoints_db.units == 'crystal')
assert(len(kpoints_db.path==7))

# Test from_lattice
kpoints_db2 = ppy.RecipPtDB.from_lattice(kpoints_cryst, 'cryst', lat, recip_lat)
assert(np.all(kpoints_db2.coords_cryst == vectors_cryst))
print(kpoints_db2.coords_cart)
assert(np.all(kpoints_db2.coords_cart == vectors_cart))
assert(kpoints_db2.units == 'crystal')   # def from_lattice(self, kpoints, units, lat, recip_lat, kpath=None, kpath_units='arbitrary', labels=None):

# # Test kpoints_from_units and kpoints
# assert(np.all(kpoints_db.kpt_from_units('cart') == kpoints_db.kpt_cart))
# assert(np.all(kpoints_db.kpt_from_units('tpiba') == kpoints_db.kpt_cart))
# assert(np.all(kpoints_db.kpt_from_units('frac') == kpoints_db.kpt_cryst))
# assert(np.all(kpoints_db.kpt_from_units('crystal') == kpoints_db.kpt_cryst))

# Test units property and setter
assert(kpoints_db.units == 'crystal')
kpoints_db.units = 'frac'
assert(kpoints_db.units == 'crystal')
assert(kpoints_db._units == 'crystal')
kpoints_db.units = 'cart'
assert(kpoints_db.units == 'cartesian')

# Test kpoints property
kpoints_db.units = 'cryst'
assert(kpoints_db.units == 'crystal')
assert(np.all(kpoints_db.coords == kpoints_db.coords_cryst))
kpoints_db.units = 'Cartesian'
assert(kpoints_db.units == 'cartesian')
assert(np.all(kpoints_db.coords == kpoints_db.coords_cart))

# Test scale_kpath(self, range_min, range_max):
kpoints_db.scale_path(0,0.5)
assert(np.all(kpoints_db.path == [0,0.1,0.2,0.3,0.4,0.5]))

#Test compute_kpt_distances(self, kpoint, units):

assert(np.all(np.isclose(kpoints_db.distances_from(kpoints_db.coords), [0., 0., 0, 0., 0., 0.])))
# assert(np.all(np.isclose(kpoints_db.compute_kpt_distances([0.5,0.5,0.5]), [0.8660254, 0.8660254, 0, 0.70710678, 0.61237244, 0.61237244])))

# # Test find_kpt(self, kpoint, nearest=True, **kwargs):
# assert(kpoints_db.find_kpt([0,0,0]) == 195)
# assert(kpoints_db.find_kpt([0.5,1,0]) == 3)
# assert(kpoints_db.find_kpt([0.499,1,0]) == 3)
# # assert(kpoints_db.find_kpt([0.55,1,0]) == ValueError)

# # Test kpoint_to_kpath(self, kpoint, units, nearest=True):
# assert(kpoints_db.kpt_to_kpath([0.5,1,0]) == 0.3)
# assert(kpoints_db.kpt_to_kpath([0.499,1,0]) == 0.3)

# # Test kpath_coord_to_kpt_coord(self, kpath, nearest=True, **kwargs):
# assert(np.all(kpoints_db.kpath_to_kpt(0.3) == [0.5,1,0]))

##### TEST ENERGIES ######
# Test constructor
energies_db = ppy.EnergiesDB({1:[0.1,0.2,0.3], 2:[0.3,0.4,0.5]}, 'meV')
assert(energies_db.num_indices == 2)

# Test band_indices property
assert(energies_db.indices == [1,2])

# Test convert_units
assert(np.all(energies_db.convert_units('eV')[1] == [0.0001,0.0002,0.0003]))
assert(np.all(energies_db.convert_units('electronvolt')[2] == [0.0003,0.0004,0.0005]))
assert(np.all(energies_db.energies_dict[1] == [0.1,0.2,0.3]))
assert(np.all(energies_db.energies_dict[2] == [0.3,0.4,0.5]))
assert(energies_db.units == 'meV')

# Test units property and setter
energies_db.units = 'eV'
assert(np.all(energies_db.energies_dict[1] == [0.0001,0.0002,0.0003]))
assert(np.all(energies_db.energies_dict[2] == [0.0003,0.0004,0.0005]))
assert(energies_db.units == 'eV')


###### TEST PLOT UTILS ########

###### TEST BANDS CALC MODE ########

# Test constructor

ge_bands_calc = ppy.BandsCalcMode.from_yaml(os.path.join('tests', 'refs_postproc', 'ge_bands.yml'))

# Test compute_indirect_bandgap and compute_direct_bandgap
print(ge_bands_calc.compute_indirect_bandgap(8,9))
print(ge_bands_calc.compute_direct_bandgap(8,9))


si_bands_calc = ppy.BandsCalcMode.from_yaml(os.path.join('tests', 'refs_postproc', 'si_bands.yml'))

# Test compute_indirect_bandgap and compute_direct_bandgap
print(si_bands_calc.compute_indirect_bandgap(4,5))
print(si_bands_calc.compute_direct_bandgap(4,5))

# Test compute_effective_mass(self, n, kpoint, max_distance):
# print(ge_bands_calc.compute_effective_mass(9, [0,0,0], 0.01))

# Test plot_bands(self, ax, show_kpt_labels=True, **kwargs):
# ppy.plot_tools.plot_bands(ax)

plt.rcParams.update(ppy.plot_tools.plotparams)

fig, ax = plt.subplots(1,1)

special_kpoints = [ [0.5  , 0.5  , 0.5 ],
				 [0.5  , 0.0  , 0.5 ],
				 [0.5  , 0.25 , 0.75],
				 [0.375, 0.375, 0.75] ]

special_kpoints_labels = ['L','X','W','K']


si_bands_calc.kpt.add_label([0,0,0],r'$\Gamma$')
si_bands_calc.kpt.add_label([0.5,0.5,0.5], 'test')
si_bands_calc.kpt.add_labels({'l':[0.5,0.5,0.5],'gamma':[0,0,0],})

print(si_bands_calc.kpt.labels)
si_bands_calc.plot_bands(ax)

#plt.show()

# # print(ge_bands_calc.compute_effective_mass(9,[0.5,0.5,0.5], 0.05))

# ###### TEST PHDISP CALC MODE ########

# # Test constructor
# si_phdisp_calc = ppy.PhdispCalcMode.from_yaml(os.path.join('tests', 'refs_postproc', 'si_phdisp.yml'))

# # Test renaming branches

# plt.rcParams.update(ppy.plot_tools.plotparams)

# fig, ax = plt.subplots(1,1)

# special_qpts = ppy.utils.constants.special_recip_pts
# si_phdisp_calc.label_qpts(special_qpts)
# si_phdisp_calc.plot_phdisp(ax)

plt.show()