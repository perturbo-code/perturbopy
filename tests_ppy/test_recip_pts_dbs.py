import numpy as np
import os
import pytest
import math

import perturbopy.postproc as ppy

@pytest.fixture()
def recip_dbs():
    points_cryst = [[0,0,0.5,0.25,0.25,0.375], [0,0.5,0.5,0.75,0.625,0.75], [0,0.5,0.5,0.5,0.625,0.375]]
    points_cart = [[0, 0, 0.5, 0.5,  0.25, 0.75], [0, 1, 0.5, 1,   1,   0.75], [0,   0,   0.5, 0,   0.25,0.]]
    return ppy.RecipPtDB(points_cryst, points_cart)

@pytest.mark.parametrize("test_min, test_max, expected", [
	(0,1,[0,0.2,0.4,0.6,0.8,1])
	])

def test_scale_path(recip_dbs, test_min, test_max, expected):
	recip_dbs.scale_path(test_min, test_max)
	print(recip_dbs.path)
	assert(np.all(recip_dbs.path == expected))
# # test constructor and class method! properties, (units?), scale_kpath

# # Test constructor

# kpts_cart = vectors_cart
# kpts_cryst = vectors_cryst
# lat = [[0.5, 0.5, 0.0], [0.0, 0.5, 0.5], [0.5, 0.0, 0.5]]
# recip_lat = [[1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, 1.0]]

# kpts_db = KptsDB(kpts_cart, kpts_cryst, units='crystal', kpath=None, kpath_units='arbitrary', labels=None)
# kpts_db = ppy.KptsDB(kpts_cart, kpts_cryst, units='crystal', kpath=None, kpath_units='arbitrary', labels=None)
# assert(np.all(kpts_db.kpts_cart == vectors_cart))
# assert(np.all(kpts_db.kpts_cryst == vectors_cryst))
# assert(kpts_db.units == 'crystal')
# assert(len(kpts_db.kpath==7))

# # Test from_lattice
# kpts_db2 = KptsDB.from_lattice(kpts_cryst, 'cryst', lat, recip_lat)
# kpts_db2 = ppy.KptsDB.from_lattice(kpts_cryst, 'cryst', lat, recip_lat)
# assert(np.all(kpts_db2.kpts_cryst == vectors_cryst))
# assert(np.all(kpts_db2.kpts_cart == vectors_cart))
# assert(kpts_db2.units == 'crystal')   # def from_lattice(self, kpts, units, lat, recip_lat, kpath=None, kpath_units='arbitrary', labels=None):
# assert(kpts_db.units == 'crystal')
# assert(kpts_db._units == 'crystal')
# kpts_db.units = 'cart'
# assert(kpts_db.units == 'tpiba')
# assert(kpts_db.units == 'cartesian')

# # Test kpts property
# kpts_db.units = 'cryst'
# assert(kpts_db.units == 'crystal')
# assert(np.all(kpts_db.kpts == kpts_db.kpts_cryst))
# kpts_db.units = 'Cartesian'
# assert(kpts_db.units == 'tpiba')
# assert(kpts_db.units == 'cartesian')
# assert(np.all(kpts_db.kpts == kpts_db.kpts_cart))

# # Test scale_kpath(self, range_min, range_max):

# @pytest.mark.parametrize("test_input1, test_input2")

# assert(np.all(kpts_db.kpath_to_kpt(0.3) == [0.5,1,0]))

# @pytest.mark.parametrize("test_input1, test_input2, expected", [

# 	([3,3,1],[3,3,1], 0),
# 	([[3],[2],[1]],[3,2,1], 0),
# 	([[3,2,1]],[3,2,1], 0),
# 	([1,1,1],[0,2,0], math.sqrt(3)),
# 	([[1,2,3],[4,5,6]], [1,2,3,], [0, math.sqrt(27)]),
# 	([[1,4],[2,5],[3,6]], [1,2,3,], [0, math.sqrt(27)]),
# 	([[1,2,3],[4,5,6]], [[2,3,4],[5,6,7]], [math.sqrt(3), math.sqrt(3)]),
# 	([[1,4],[2,5],[3,6]], [[2,3,4],[5,6,7]], [math.sqrt(3), math.sqrt(3)])

# 	])

# def test_compute_distances(test_input1, test_input2, expected):
# 	assert(np.all(np.isclose(ppy.lattice.compute_distances(test_input1, test_input2), expected)))
# 	assert(np.all(np.isclose(ppy.lattice.compute_distances(test_input2, test_input1), expected)))


# @pytest.mark.parametrize("test_point, test_points_array, atol, expected", [
# 	([1,1,1],[[1,1,1],[1,1,1],[1,1,1]], None, [0,1,2]),
# 	([1,1,1],[[1,1,1],[1,1,1],[.96,.96,.96]], None, [0,1,2]),
# 	([1,1,1],[[1,1,1],[1,1,1],[.9,.9,.9]], None, None),
# 	([1,1,1],[[1,1,1],[1,1,1],[.9,.9,.9]], 0.2, [0,1,2]),
# 	([[1],[1],[1]],[[1,1,1],[1,1,1],[.9,.9,.9]], 0.2, [0,1,2]),
# 	([1,1,1],[[1,1,1],[1,1,1],[1,.96,.96]], None, [0])
# 	])

# def test_where(test_point, test_points_array, atol, expected):
# 	if atol is None:
# 		assert(np.all(ppy.lattice.where(test_point, test_points_array) == expected))
# 	else:
# 		assert(np.all(ppy.lattice.where(test_point, test_points_array, atol=atol) == expected))

# @pytest.mark.parametrize("test_point, test_points_array, test_path_array, atol, expected", [
# 	([1,2,0],[[1,1,1],[1,5,6],[1,2,0], [3,3,3]], [1,2,3,4], None, 3),
# 	([1,2,0],[[1,1,1],[1,5,6],[1.02,2.01,0.04], [3,3,3]], [1,2,3,4], None, 3),
# 	([1,2,0],[[1,1,1],[1,2,0],[1,2,0], [3,3,3]], [0.1,0.2,0.3,0.4], None, [0.2,0.3]),
# 	([1,2,0],[[1,1,1],[1,5,6],[1,2.1,0], [3,3,3]], [1,2,3,4], None, None),
# 	([1,2,0],[[1,1,1],[1,5,6],[1,2.1,0], [3,3,3]], [1,2,3,4], 0.12, 3),
# 	([1,2,0],[[1,1,1],[1,2,0],[1,2.1,0], [3,3,3]], [1,2,3,4], 0.12, 2)
# 	])

# def test_point_to_path(test_point, test_points_array, test_path_array, atol, expected):
# 	if atol is None:
# 		assert(np.all(ppy.lattice.point_to_path(test_point, test_points_array, test_path_array) == expected))
# 	else:
# 		assert(np.all(ppy.lattice.point_to_path(test_point, test_points_array, test_path_array, atol=atol) == expected))

# @pytest.mark.parametrize("test_path, test_points_array, test_path_array, atol, expected", [
# 	(3,[[1,1,1],[1,5,6],[1,2,0], [3,3,3]], [1,2,3,4], None, [1,2,0]),
# 	])
# def test_path_to_point(test_path, test_points_array, test_path_array, atol, expected):
#     assert(ppy.lattice.path_to_point(test_path, test_points_array, test_path_array))
