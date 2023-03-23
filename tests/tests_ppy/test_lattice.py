import numpy as np
import os
import pytest
import math

import perturbopy.postproc as ppy

@pytest.mark.parametrize("test_input, expected", [

	([3,3,2], np.array([[3],[3],[2]])),
	(np.array([3,3,2]), np.array([[3],[3],[2]])),
	([[1,1,1],[2,2,2],[3,3,3]], np.array([[1,1,1],[2,2,2],[3,3,3]])),
	([[1,1,1],[2,2,2],[3,3,3],[4,4,4]], np.array([[1,2,3,4],[1,2,3,4],[1,2,3,4]])),
	([[1,2,3,4],[1,2,3,4],[1,2,3,4]], np.array([[1,2,3,4],[1,2,3,4],[1,2,3,4]])),
	([[1,1],[2,2],[3,3]], np.array([[1,1],[2,2],[3,3]])),
	([[1,2,3],[1,2,3]], np.array([[1,1],[2,2],[3,3]]))

	])

def test_reshape_points(test_input, expected):
	test_result = ppy.lattice.reshape_points(test_input)

	assert(np.all(test_result == expected))
	assert(isinstance(test_result, np.ndarray))

	if len(np.shape(test_input)) == 1:
		assert(np.shape(test_result) == (3,1))
	elif np.shape(test_input)[0] == 3:
		assert(np.shape(test_result) == (3, np.shape(test_input)[1]))
	elif np.shape(test_input)[1] == 3:
		assert(np.shape(test_result) == (3, np.shape(test_input)[0]))

@pytest.mark.parametrize("test_points_cart, test_points_cryst, test_lat, test_recip_lat", [

	# [0.5, 0.5, 0], [0, 0.5, 0.5], [0.5, 0, 0.5]

	([[0,0,0.5,0.25,0.25,0.375], [0,0.5,0.5,0.75,0.625,0.75], [0,0.5,0.5,0.5,0.625,0.375]],
	 [[0, 0, 0.5, 0.5,  0.25, 0.75], [0, 1, 0.5, 1,   1,   0.75], [0,   0,   0.5, 0,   0.25,0.]],
	 np.array([[0.5, 0.5, 0.0], [0.0, 0.5, 0.5], [0.5, 0.0, 0.5]]).T,
	 np.array([[1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, 1.0]]).T)

	])

def test_cryst_to_cart(test_points_cart, test_points_cryst, test_lat, test_recip_lat):
	print(test_points_cart)
	print(ppy.lattice.cryst_to_cart(test_points_cart, test_lat, test_recip_lat, real_space=True, forward=True))
	assert(np.allclose(ppy.lattice.cryst_to_cart(test_points_cryst, test_lat, test_recip_lat, real_space=True, forward=True), test_points_cart))
	assert(np.allclose(ppy.lattice.cryst_to_cart(test_points_cart, test_lat, test_recip_lat, real_space=True, forward=False),  test_points_cryst))

	# assert(np.allclose(ppy.lattice.cryst_to_cart(test_points_cart, test_lat, test_recip_lat, real_space=False, forward=True), test_points_cryst))
	# assert(np.allclose(ppy.lattice.cryst_to_cart(test_points_cryst, test_lat, test_recip_lat, real_space=False, forward=False),  test_points_cart))

@pytest.mark.parametrize("test_input1, test_input2, expected", [

	([3,3,1],[3,3,1], 0),
	([[3],[2],[1]],[3,2,1], 0),
	([[3,2,1]],[3,2,1], 0),
	([1,1,1],[0,2,0], math.sqrt(3)),
	([[1,2,3],[4,5,6]], [1,2,3,], [0, math.sqrt(27)]),
	([[1,4],[2,5],[3,6]], [1,2,3,], [0, math.sqrt(27)]),
	([[1,2,3],[4,5,6]], [[2,3,4],[5,6,7]], [math.sqrt(3), math.sqrt(3)]),
	([[1,4],[2,5],[3,6]], [[2,3,4],[5,6,7]], [math.sqrt(3), math.sqrt(3)])

	])

def test_compute_distances(test_input1, test_input2, expected):
	assert(np.all(np.isclose(ppy.lattice.compute_distances(test_input1, test_input2), expected)))
	assert(np.all(np.isclose(ppy.lattice.compute_distances(test_input2, test_input1), expected)))


@pytest.mark.parametrize("test_point, test_points_array, atol, expected", [
	([1,1,1],[[1,1,1],[1,1,1],[1,1,1]], None, [0,1,2]),
	([1,1,1],[[1,1,1],[1,1,1],[.96,.96,.96]], None, [0,1,2]),
	([1,1,1],[[1,1,1],[1,1,1],[.9,.9,.9]], None, None),
	([1,1,1],[[1,1,1],[1,1,1],[.9,.9,.9]], 0.2, [0,1,2]),
	([[1],[1],[1]],[[1,1,1],[1,1,1],[.9,.9,.9]], 0.2, [0,1,2]),
	([1,1,1],[[1,1,1],[1,1,1],[1,.96,.96]], None, [0])
	])

def test_where(test_point, test_points_array, atol, expected):
	if atol is None:
		assert(np.all(ppy.lattice.where(test_point, test_points_array) == expected))
	else:
		assert(np.all(ppy.lattice.where(test_point, test_points_array, atol=atol) == expected))

@pytest.mark.parametrize("test_point, test_points_array, test_path_array, atol, expected", [
	([1,2,0],[[1,1,1],[1,5,6],[1,2,0], [3,3,3]], [1,2,3,4], None, 3),
	([1,2,0],[[1,1,1],[1,5,6],[1.02,2.01,0.04], [3,3,3]], [1,2,3,4], None, 3),
	([1,2,0],[[1,1,1],[1,2,0],[1,2,0], [3,3,3]], [0.1,0.2,0.3,0.4], None, [0.2,0.3]),
	([1,2,0],[[1,1,1],[1,5,6],[1,2.1,0], [3,3,3]], [1,2,3,4], None, None),
	([1,2,0],[[1,1,1],[1,5,6],[1,2.1,0], [3,3,3]], [1,2,3,4], 0.12, 3),
	([1,2,0],[[1,1,1],[1,2,0],[1,2.1,0], [3,3,3]], [1,2,3,4], 0.12, 2)
	])

def test_point_to_path(test_point, test_points_array, test_path_array, atol, expected):
	if atol is None:
		assert(np.all(ppy.lattice.point_to_path(test_point, test_points_array, test_path_array) == expected))
	else:
		assert(np.all(ppy.lattice.point_to_path(test_point, test_points_array, test_path_array, atol=atol) == expected))

@pytest.mark.parametrize("test_path, test_points_array, test_path_array, atol, expected", [
	(3,[[1,1,1],[1,5,6],[1,2,0], [3,3,3]], [1,2,3,4], None, [1,2,0]),
	])
def test_path_to_point(test_path, test_points_array, test_path_array, atol, expected):
    print(ppy.lattice.path_to_point(test_path, test_points_array, test_path_array))
    assert(np.all(np.isclose(ppy.lattice.path_to_point(test_path, test_points_array, test_path_array), expected)))
