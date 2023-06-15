import numpy as np
import pytest

import perturbopy.postproc as ppy

points_cryst = [[0, 0, 0.5, 0.25, 0.25, 0.375], [0, 0.5, 0.5, 0.75, 0.625, 0.75], [0, 0.5, 0.5, 0.5, 0.625, 0.375]]
points_cart = [[0, 0, 0.5, 0.5, 0.25, 0.75], [0, 1, 0.5, 1, 1, 0.75], [0, 0, 0.5, 0, 0.25, 0.]]


@pytest.fixture()
def recip_dbs():
    """
    Fixture to generate a RecipPtDB object

    """
    return ppy.RecipPtDB(points_cart, points_cryst, units='cryst')


@pytest.mark.parametrize("units_input, expected_units, expected_points", [
                        ('cryst', 'crystal', points_cryst), ('Cartesian', 'cartesian', points_cart),
])
def test_units(recip_dbs, units_input, expected_units, expected_points):
    """
    Method to test the conversion between different units

    Parameters
    ----------
    units_input : str
       The units to convert the points to
    expected_units : str
       The expected units to be stored, according to standardized units names
    expected_points : array
       The points expected to be stored in recip_dbs after conversion

    """
    recip_dbs.convert_units(units_input)
    assert(recip_dbs.units == expected_units)
    assert(np.all(recip_dbs.points == expected_points))


@pytest.mark.parametrize("test_min, test_max, expected", [
                        (0, 1, [0, 0.2, 0.4, 0.6, 0.8, 1])
])
def test_scale_path(recip_dbs, test_min, test_max, expected):
    """
    Method to test the recip_pt_db.scale_path function

    Parameters
    ----------
    test_min, test_max : float
       The min and max value in the range the path should be scaled to
    expected : list
       The expected, rescaled path
    """
    recip_dbs.scale_path(test_min, test_max)
    print(type(recip_dbs))
    assert(np.all(recip_dbs.path == expected))


@pytest.mark.parametrize("point, expected", [
                        ([[0, 0, 0.5, 0.25, 0.25, 0.375], [0, 0.5, 0.5, 0.75, 0.625, 0.75], [0, 0.5, 0.5, 0.5, 0.625, 0.375]], [0, 0, 0, 0, 0, 0]),
])
def test_compute_distances(recip_dbs, point, expected):
    """
    Method to test the recip_pt_db.compute_distances function

    Parameters
    ----------
    point : array_like
       The point to compute the distances between (compared to all the points in recip_dbs)
    expected : list
       The expected distances between the points in recip_dbs and the inputted point
    """
    print(recip_dbs.distances(point))
    assert(np.all(np.isclose(recip_dbs.distances(point), expected)))


@pytest.mark.parametrize("test_point, max_dist, expected", [
                        ([0, 0, 0], None, 0), ([0.25, 0.625, 0.625], None, 4),
                        ([0.25, 0.625, 0.56], None, []), ([0.25, 0.625, 0.56], 0.1, 4),
                        ([0, 0.5, 0.5], None, [1]),
])
def test_find(recip_dbs, test_point, max_dist, expected):
    """
    Method to test the recip_pt_db.find function

    Parameters
    ----------
    test_point : array_like
       The point to search recip_dbs
    max_dist : float
       The maximum distance between the point to locate and the points identified as matches
    expected : list
       The expected indices to be found

    """
    print(recip_dbs.distances(test_point))
    print(recip_dbs.find(test_point))
    if max_dist is None:
        assert(np.all(recip_dbs.find(test_point) == expected))
    else:
        assert(np.all(recip_dbs.find(test_point, max_dist=max_dist) == expected))


@pytest.mark.parametrize("test_point, max_dist, expected", [
                        ([0, 0, 0], None, 0), ([0.25, 0.625, 0.625], None, 4),
                        ([0.25, 0.625, 0.56], None, None), ([0.25, 0.625, 0.56], 0.1, 4),
])
def test_point2path(recip_dbs, test_point, max_dist, expected):
    """
    Method to test the recip_pt_db.point2path function

    Parameters
    ----------
    test_point : array_like
       The point to search recip_dbs
    max_dist : float
       The maximum distance between the point to locate and the points identified as matches
    expected : float
       The expected path coordinate(s) to be found

    """
    if max_dist is None:
        assert(np.all(recip_dbs.point2path(test_point) == expected))
    else:
        assert(np.all(recip_dbs.point2path(test_point, max_dist=max_dist) == expected))


@pytest.mark.parametrize("test_path, atol, expected", [
                        (0, None, [0, 0, 0]), (4, None, [0.25, 0.625, 0.625]), (4.1, None, None),
                        (4.1, 0.1, [0.25, 0.625, 0.625])
])
def test_path2point(recip_dbs, test_path, atol, expected):
    """
    Method to test the recip_pt_db.path2point function

    Parameters
    ----------
    test_path : float
       The path coordinate to search recip_dbs
    atol : float
       The maximum difference between the path coordinate to locate and the coordinates identified as matches
    expected : array
       The expected point(s) to be found

    """
    if atol is None:
        assert(np.all(recip_dbs.path2point(test_path) == expected))
    else:
        assert(np.all(recip_dbs.path2point(test_path, atol=atol) == expected))


@pytest.mark.parametrize("test_path, atol, expected", [
                        (0, None, [0, 0, 0]), (4, None, [0.25, 1, 0.25]), (4.1, None, None),
                        (4.1, 0.1, [0.25, 1, 0.25])
])
def test_path2point_cart(recip_dbs, test_path, atol, expected):
    """
    Method to test the recip_pt_db.path2point function after converting units

    Parameters
    ----------
    test_path : float
       The path coordinate to search recip_dbs
    atol : float
       The maximum difference between the path coordinate to locate and the coordinates identified as matches
    expected : array
       The expected point(s) to be found

    """
    recip_dbs.convert_units("cart")
    if atol is None:
        assert(np.all(recip_dbs.path2point(test_path) == expected))
    else:
        assert(np.all(recip_dbs.path2point(test_path, atol=atol) == expected))
