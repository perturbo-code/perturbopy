import numpy as np
import warnings

fcc_points = {'L': [0.5, 0.5, 0.5], 'X': [0.5, 0.0, 0.5], 'W': [0.5, 0.25, 0.75], 'K': [0.375, 0.375, 0.75], 'G': [0, 0, 0]}

def reshape_points(point_array):
    """
    Method to reshape reciprocal points into a 2d array of shape (3, N)
    such that reciprocal points are column-oriented
       - a list of reciprocal points will be transformed to an array
       - an array of reciprocal points with shape (N, 3) will be reshaped
         to shape (3, N) if N != 3
       - Note that reciprocal points with shape (3, 3) will be assumed to
         have the correct shape

    Parameters
    ----------
    point_array: array_like
       An array or list of reciprocal points with shape (3,N), (N,3), or (3,)

    Returns
    -------
    point_array: array
       An array of reciprocal points with shape (3,N)

    Raises
    ------
    ValueError
        If the shape of `point_array` is not (3, N), (N, 3), or (3,)

    Warns
    -----
    UserWarning
        If `point_array` is a 3x3 array, a warning is issued that the points are
        assumed to be column-oriented already.

    """
    point_array = np.array(point_array)
    point_array_shape = np.shape(point_array)

    if 3 not in point_array_shape:
        raise ValueError('Reciprocal points should be inputted as a 3xN array, where N is the number of points.')

    if len(point_array_shape) == 1:
        return np.reshape(point_array, (3, 1))

    elif point_array_shape[0] == 3:
        if point_array_shape[1] == 3:
            warnings.warn('Reciprocal points are 3x3 array; assume points are already column-oriented', UserWarning)
        return point_array

    else:
        return np.transpose(point_array)


def cryst2cart(point_array, lat, recip_lat, forward=True, real_space=True):
    """
    Method to convert points in real space or reciprocal space
    between crystal and cartesian coordinates, given the crystal
    lattice. Real space points in cartesian units have units of alat.
    Reciprocal points in cartesian coordinates have units of 2pi/alat.

    Parameters
    ----------
    point_array : array
       3xN Array of vectors [v1, v2, v3 ...] to be converted

    lat : array
       3x3 array of lattice vectors [v1, v2, v3] in units of alat

    recip_lat : array
       3x3 array of reciprocal lattice vectors [v1, v2, v3 in units of
       2pi/a

    forward : bool, optional
       If true, vectors will be converted from crystal to cartesian
       coordinates. If false, vectors will be converted from
       cartesian to crystal coordinates

    real_space : bool, optional
       If true, vectors are assumed to be in real space
       (i.e. atomic positions). If false, vectors are assumed to
       be in reciprocal space (i.e. reciprocal points).

    Returns
    -------
    converted_point_array : array
       Array containing the converted vectors [v1, v2, v3, ...]

    """

    if forward:
        if real_space:
            conversion_mat = lat
        else:
            conversion_mat = recip_lat

    else:
        if real_space:
            conversion_mat = np.transpose(recip_lat)
        else:
            conversion_mat = np.transpose(lat)

    converted_point_array = np.tensordot(conversion_mat, point_array, axes=1)

    return converted_point_array


def compute_distances(point_array1, point_array2):
    """
    Method to compute the distances between points

    Parameters
    ----------
    point_array1, point_array2 : array_like
       The points between which distances will be computed. They should have the same
       shape. Both will be reshaped to assume column-oriented points if needed. For
       example, arrays of shape (N, 3) will be reshaped to (3, N) if N != 3.

    Returns
    -------
    distances : array
       An array of distances between points in point_array1 and point_array2, computed
       across the columns.

    """
    point_array1 = reshape_points(point_array1)
    point_array2 = reshape_points(point_array2)

    if np.shape(point_array1) != np.shape(point_array2) and np.shape(point_array1) != (3, 1) and np.shape(point_array2) != (3, 1):
        print(np.shape(point_array1))
        print(np.shape(point_array2))
        raise ValueError("Shape of arrays should be the same, or one array should only contain one k-point.")

    distances = np.linalg.norm(point_array1 - point_array2, axis=0)

    return distances


def find_point(point, point_array, max_dist=0.025, nearest=True):
    """
    Method to find the index or indices of a particular point in an array of points.

    Parameters
    ----------
    point : array_like
       The point to be located in an array of points

    point_array : array_like
       The set of points that will be searched through

    max_dist : float, optional
       The maximum distance between the point to locate and the points identified as matches

    narest : bool, optional
       If True, only the nearest point, or points in the case of duplicate points, are returned (even if
       other points are within the max_dist)


    Returns
    -------
    points_indices: list
       The index or indices of the matching points in point_array

    """
    point = reshape_points(point)
    point_array = reshape_points(point_array)

    distances = compute_distances(point_array, point)

    if nearest:
        min_distance = np.min(distances)
        point_indices = np.where(np.isclose(distances, min_distance))[0]

        if min_distance <= max_dist:
            return point_indices
        else:
            return []

    else:
        return np.arange(len(distances))[distances <= max_dist]


def convert_point2path(point, point_array, path_array, max_dist=0.025, nearest=True):
    """
    Method to find the path coordinate corresponding to a particular point

    Parameters
    ----------
    point: array_like
       The point to be converted to a path coordinate

    point_array: array_like
       A set of points

    path_array: array_like
       The path corresponding to the points

    max_dist : float, optional
       The maximum distance between the point to locate and the matching points

    nearest : bool, optional
       If True, only the nearest point, or points in the case of repeated points, are returned (even if
       other points are within the max_dist)

    Returns
    -------
    path_coord: array
       The path coordinate(s) of the corresponding reciprocal space point(s)

    """
    point = reshape_points(point)
    point_array = reshape_points(point_array)
    path_array = np.array(path_array)

    point_indices = find_point(point, point_array, max_dist, nearest)

    if len(point_indices) == 0:
        return np.array([])
    else:
        path_coord = path_array[point_indices]
        return path_coord


def convert_path2point(path_coord, point_array, path_array, atol=1e-8, rtol=1e-5, nearest=True):
    """
    Method to find the point corresponding to a path coordinate

    Parameters
    ----------
    path_coord : float
       The path coordinate to be converted to a point

    point_array: array_like
       A set of points

    path_array: array_like
       The path corresponding to the points

    atol : float, optional
       The absolute tolerance between the path coordinate to locate and the matching path coordinates

    rtol : float, optional
       The relative tolerance between the path coordinate to locate and the matching path coordinates

    nearest : bool, optional
       If True, only the nearest path coordinate, or coordinates in the case of repeats, are returned (even if
       other points are within the absolute and relative tolerance)

    Returns
    -------
    point_array: list
       The reciprocal space point(s) of the corresponding path coordinate

    """
    point_array = reshape_points(point_array)
    path_array = np.array(path_array)

    distances = np.abs(path_array - path_coord)
    min_distance = np.amin(distances)

    if min_distance <= atol + rtol * min_distance:
        path_indices = np.where(np.isclose(distances, min_distance))[0]
        return np.reshape(point_array[:, path_indices], (3,))
    else:
        return np.array([])
