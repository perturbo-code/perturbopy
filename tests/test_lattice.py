import numpy as np
import pytest
import math
import perturbopy.postproc as ppy


@pytest.mark.parametrize("test_points, expected_points", [

                        ([3, 3, 2], np.array([[3], [3], [2]])),
                        (np.array([3, 3, 2]), np.array([[3], [3], [2]])),
                        ([[1, 1, 1], [2, 2, 2], [3, 3, 3]], np.array([[1, 1, 1], [2, 2, 2], [3, 3, 3]])),
                        ([[1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4]], np.array([[1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]])),
                        ([[1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]], np.array([[1, 2, 3, 4], [1, 2, 3, 4], [1, 2, 3, 4]])),
                        ([[1, 1], [2, 2], [3, 3]], np.array([[1, 1], [2, 2], [3, 3]])),
                        ([[1, 2, 3], [1, 2, 3]], np.array([[1, 1], [2, 2], [3, 3]]))

])
def test_reshape_points(test_points, expected_points):
   """"
   Method to test lattice.reshape_points function

   Parameters
   ----------
   test_points : array_like
      The array of points to reshape
   expected_points : array
      The expected reshaped array of points
      
   """
   test_points = ppy.lattice.reshape_points(test_points)

   assert(np.all(test_points == expected_points))
   assert(isinstance(test_points, np.ndarray))

   if len(np.shape(test_points)) == 1:
     assert(np.shape(test_points) == (3, 1))
   elif np.shape(test_points)[0] == 3:
     assert(np.shape(test_points) == (3, np.shape(test_points)[1]))
   elif np.shape(test_points)[1] == 3:
     assert(np.shape(test_points) == (3, np.shape(test_points)[0]))


@pytest.mark.parametrize("test_points_cart, test_points_cryst, test_lat, test_recip_lat", [
                        ([[0, 0, 0.5, 0.25, 0.25, 0.375], [0, 0.5, 0.5, 0.75, 0.625, 0.75], [0, 0.5, 0.5, 0.5, 0.625, 0.375]],
                         [[0, 0, 0.5, 0.5, 0.25, 0.75], [0, 1, 0.5, 1, 1, 0.75], [0, 0, 0.5, 0, 0.25, 0.]],
                         np.array([[0.5, 0.5, 0.0], [0.0, 0.5, 0.5], [0.5, 0.0, 0.5]]).T,
                         np.array([[1.0, 1.0, -1.0], [-1.0, 1.0, 1.0], [1.0, -1.0, 1.0]]).T)

])
def test_cryst2cart(test_points_cart, test_points_cryst, test_lat, test_recip_lat):
   """"
   Method to test lattice.cryst2cart function

   Parameters
   ----------
   test_points_cart : array_like
      The points in cartesian coordinates
   test_points_cryst : array_like
      The points in crystal coordinates
   test_lat : array_like
      The lattice vectors assumed in the conversion
   test_recip_lat : array_like
      The reciprocal lattice vectors assumed in the conversion
      
   """
   assert(np.allclose(ppy.lattice.cryst2cart(test_points_cryst, test_lat, test_recip_lat, real_space=True, forward=True), test_points_cart))
   assert(np.allclose(ppy.lattice.cryst2cart(test_points_cart, test_lat, test_recip_lat, real_space=True, forward=False), test_points_cryst))


@pytest.mark.parametrize("test_points1, test_points2, expected_distances", [

                        ([3, 3, 1], [3, 3, 1], 0),
                        ([[3], [2], [1]], [3, 2, 1], 0),
                        ([[3, 2, 1]], [3, 2, 1], 0),
                        ([1, 1, 1], [0, 2, 0], math.sqrt(3)),
                        ([[1, 2, 3], [4, 5, 6]], [1, 2, 3], [0, math.sqrt(27)]),
                        ([[1, 4], [2, 5], [3, 6]], [1, 2, 3], [0, math.sqrt(27)]),
                        ([[1, 2, 3], [4, 5, 6]], [[2, 3, 4], [5, 6, 7]], [math.sqrt(3), math.sqrt(3)]),
                        ([[1, 4], [2, 5], [3, 6]], [[2, 3, 4], [5, 6, 7]], [math.sqrt(3), math.sqrt(3)])

])
def test_compute_distances(test_points1, test_points2, expected_distances):
   """"
   Method to test lattice.compute_distances function

   Parameters
   ----------
   test_points1, test_points2 : array_like
      Arrays of test points between which to compute distances
   expected_distances : list
      The expected distances between the two arrays of test points
      
   """
   assert(np.all(np.isclose(ppy.lattice.compute_distances(test_points1, test_points2), expected_distances)))
   assert(np.all(np.isclose(ppy.lattice.compute_distances(test_points2, test_points1), expected_distances)))


@pytest.mark.parametrize("test_point, test_points_array, max_dist, nearest, expected", [
                        ([1, 1, 1], [[1, 1, 1], [1, 1, 1], [1, 1, 1]], None, True, [0, 1, 2]),
                        ([1, 1, 1], [[1, 1, 1], [1, 1, 1], [.96, 0.96, 0.96]], None, True, []),
                        ([1, 1, 1], [[1, 1, 1], [1, 1, 1], [.96, 0.96, 0.96]], 0.0401, True, [0, 1, 2]),
                        ([1, 1, 1], [[1, 1, 1], [1, 1, 1], [.9, 0.9, 0.9]], None, True, []),
                        ([1, 1, 1], [[1, 1, 1], [1, 1, 1], [.9, 0.9, 0.9]], 0.2, True, [0, 1, 2]),
                        ([[1], [1], [1]], [[1, 1, 1], [1, 1, 1], [.9, 0.9, 0.9]], 0.2, True, [0, 1, 2]),
                        ([1, 1, 1], [[1, 1, 1], [1, 1, 1], [1, 0.995, 0.995]], None, True, [0]),
                        ([1, 1, 1], [[1, 1, 1], [1, 1, 1], [1, 0.995, 0.995]], None, False, [0, 1, 2])
])
def test_find_point(test_point, test_points_array, max_dist, nearest, expected):
   """"
   Method to test lattice.find_point function

   Parameters
   ----------
   test_point : array_like
      The point to search
   test_points_array : array_like
      The array of points to be searched for matches
   max_dist : float
      The maximum distances between points to be considered a match
   nearest : bool
      Whether or not to return just the matches that are closest in distance, or all matches within max_dist
   expected : list
      The expected list of indices corresponding to points in test_points_array matching test_point
      
   """
   if max_dist is None:
     assert(np.all(ppy.lattice.find_point(test_point, test_points_array, nearest=nearest) == expected))
   else:
     assert(np.all(ppy.lattice.find_point(test_point, test_points_array, max_dist=max_dist, nearest=nearest) == expected))


@pytest.mark.parametrize("test_point, test_points_array, test_path_array, max_dist, expected", [
                        ([1, 2, 0], [[1, 1, 1], [1, 5, 6], [1, 2, 0], [3, 3, 3]], [1, 2, 3, 4], None, 3),
                        ([1, 2, 0], [[1, 1, 1], [1, 5, 6], [1.02, 2.01, 0.04], [3, 3, 3]], [1, 2, 3, 4], None, 3),
                        ([1, 2, 0], [[1, 1, 1], [1, 2, 0], [1, 2, 0], [3, 3, 3]], [0.1, 0.2, 0.3, 0.4], None, [0.2, 0.3]),
                        ([1, 2, 0], [[1, 1, 1], [1, 5, 6], [1, 2.1, 0], [3, 3, 3]], [1, 2, 3, 4], None, None),
                        ([1, 2, 0], [[1, 1, 1], [1, 5, 6], [1, 2.1, 0], [3, 3, 3]], [1, 2, 3, 4], 0.12, 3),
                        ([1, 2, 0], [[1, 1, 1], [1, 2, 0], [1, 2.1, 0], [3, 3, 3]], [1, 2, 3, 4], 0.12, 2)
])
def test_convert_point2path(test_point, test_points_array, test_path_array, max_dist, expected):
   """"
   Method to test lattice.convert_point2path function

   Parameters
   ----------
   test_point : array_like
      The point to convert to a path coordinate
   test_points_array : array_like
      The array of points
   test_path_array : array_like
      The path coordinates corresponding to points in test_points_array
   max_dist : float
      The maximum distances between test_point and a point in test_points_array to be considered a match
   expected : int
      The expected path coordinate or list of coordinates corresponding to the test_point
      
   """
   if max_dist is None:
     assert(np.all(ppy.lattice.convert_point2path(test_point, test_points_array, test_path_array) == expected))
   else:
     assert(np.all(ppy.lattice.convert_point2path(test_point, test_points_array, test_path_array, max_dist=max_dist) == expected))


@pytest.mark.parametrize("test_path, test_points_array, test_path_array, atol, expected", [
                        (3, [[1, 1, 1], [1, 5, 6], [1, 2, 0], [3, 3, 3]], [1, 2, 3, 4], None, [1, 2, 0]),
])
def test_convert_path2point(test_path, test_points_array, test_path_array, atol, expected):
   """"
   Method to test lattice.path2point function

   Parameters
   ----------
   test_path : float
      The point to convert to a path coordinate
   test_points_array : array_like
      The array of points
   test_path_array : array_like
      The path coordinates corresponding to points in test_points_array
   atol : float
      The maximum distances between test_path and the coordinates in test_path_array to be considered a match
   expected : array_like
      The expected point coordinates corresponding to the test_path coordinate
      
   """
   print(ppy.lattice.convert_path2point(test_path, test_points_array, test_path_array))
   assert(np.all(np.isclose(ppy.lattice.convert_path2point(test_path, test_points_array, test_path_array), expected)))
