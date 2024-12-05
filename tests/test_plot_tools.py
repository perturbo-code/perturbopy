import pytest
import perturbopy.postproc as ppy
import numpy as np


@pytest.mark.parametrize("labels, point_array, path_array, label_height, show_line", [
                        ({'L': [1, 1, 1], 'X': [1, 2, 0], 'W': [1, 5, 6]}, [[1, 1, 1], [1, 2, 0], [1, 5, 6], [3, 3, 3]], [1, 2, 3, 4], 'lower', True),
                        ({'L': [1, 1, 1], 'X': [1, 2, 0], 'K': [3, 3, 3]}, [[1, 1, 1], [1, 2, 0], [1, 5, 6], [3, 3, 3]], [1, 2, 3, 4], 'upper', True),
                        ({'L': [1, 1, 1], 'X': [1, 2, 0], 'K': [3, 3, 3]}, [[1, 1, 1], [1, 2, 0], [1, 5, 6], [3, 3, 3]], [1, 2, 3, 4], 'upper', False)
])
def test_plot_recip_pt_labels(plt, labels, point_array, path_array, label_height, show_line, with_plt):
    """"
    Method to test plot_tools.plot_recip_pt_labels function

    Method to add reciprocal point labels to the plot

    Parameters
    ----------
    labels : dict
       Dictionary with keys corresponding to reciprocal point labels as strings, and values
       corresponding to array_like reciprocal points

    point_array : array_like
       Array of points corresponding to the x-axis of the plot

    path_array : array_like
       The path coordinates corresponding to the point_array

    label_height : str
       Can either be "upper" or "lower" to specify if labels should be above or below the plot

    show_line : bool
       If true, a line will be plotted to mark labeled reciprocal points

    """

    if not with_plt:
        pytest.skip("Test requires pytest-plt")

    fig, ax = plt.subplots()
    ppy.plot_tools.plot_recip_pt_labels(ax, labels, point_array, path_array, label_height, show_line)

@pytest.mark.parametrize("energy_window", [
                        ([0.2, 1]), ([-1, 10])
])
def test_set_energy_window(plt, energy_window, with_plt):
    """"
    Method to test plot_tools.set_energy_window function

    Method to set the energy window (y-axis) of the plot

    Parameters
    ----------
    energy_window : tuple
       Tuple with the lower and upper bound of the chosen energy window

    """
    
    if not with_plt:
        pytest.skip("Test requires pytest-plt")
    
    fig, ax = plt.subplots()
    ppy.plot_tools.set_energy_window(ax, energy_window)


@pytest.mark.parametrize("path, energies, energy_units, c, ls, energy_window", [
                        ([1, 2, 3, 4, 5], {1: [0.1, 0.2, 0.25, 0.3, 0.2], 2: [1.1, 1.2, 1.25, 1.3, 1.2]}, 'eV', 'k', '--', None),
                        ([1, 2, 3, 4, 5], {1: [0.1, 0.2, 0.25, 0.3, 0.2], 2: [1.1, 1.2, 1.25, 1.3, 1.2]}, 'eV', ['b', 'g'], '--', None),
                        ([1, 2, 3, 4, 5], {1: [0.1, 0.2, 0.25, 0.3, 0.2], 2: [1.1, 1.2, 1.25, 1.3, 1.2]}, 'eV', ['b', 'k'], ['-', '--'], None),
                        ([1, 2, 3, 4, 5], {1: [0.1, 0.2, 0.25, 0.3, 0.2], 2: [1.1, 1.2, 1.25, 1.3, 1.2]}, 'eV', 'k', '--', [0.2, 1]),
                        ([1, 2, 3, 4, 5], {1: [0.1, 0.2, 0.25, 0.3, 0.2], 2: [1.1, 1.2, 1.25, 1.3, 1.2], 3: [2, 2.3, 2.4, 2, 2]},
                            'eV', ['b', 'g'], ['--', ':'], None)
])
def test_plot_dispersion(plt, path, energies, energy_units, c, ls, energy_window, with_plt):
    """"
    Method to test plot_tools.plot_dispersion function

    Method to plot the dispersion (phonon dispersion or band structure).

    Parameters
    ----------
    path : array_like
       The array or list of path coordinates to be plotted on the x-axis

    energies : dict
       Dictionary of arrays of energies to plot, with keys labelling the band number or phonon mode.

    energy_units : str

    c : str, list
       Matplotlib color for plotting. If a list, different colors will be iterated through as each band is plotted.

    ls : str, list
       Matplotlib linestyle for plotting. If a list, different linestyles will be iterated through as each band is plotted.

    energy_window : tuple, optional
       Tuple with the lower and upper bound of the chosen energy window

    """

    if not with_plt:
        pytest.skip("Test requires pytest-plt")

    fig, ax = plt.subplots()
    ppy.plot_tools.plot_dispersion(ax, path, energies, energy_units, c, ls, energy_window)

@pytest.mark.parametrize("path, energies, energy_units, values, cmap, label, log, energy_window", [
                        ([1, 2, 3, 4, 5], {1: [0.1, 0.2, 0.25, 0.3, 0.2], 2: [1.1, 1.2, 1.25, 1.3, 1.2]}, 'eV',
                            {1: np.array([0.1, 0.9, 0.4, 2, 3]), 2: np.array([0.001, -1, 1.3, 1.4, 3])}, 'YlOrRd', 'Values1', False, None),
                        ([1, 2, 3, 4, 5], {1: [0.1, 0.2, 0.25, 0.3, 0.2], 2: [1.1, 1.2, 1.25, 1.3, 1.2]}, 'eV', 
                            {1: np.array([0.1, 0.9, 0.4, 2, 3]), 2: np.array([1, 1, 1.3, 1.4, 3])}, 'YlOrBr', 'Values2', True, None),
                        ([1, 2, 3, 4, 5], {1: [0.1, 0.2, 0.25, 0.3, 0.2], 2: [1.1, 1.2, 1.25, 1.3, 1.2]}, 'eV',
                            {1: np.array([0.1, 0.9, 0.4, 2, 3]), 2: np.array([0.001, -1, 1.3, 1.4, 3])}, 'YlOrRd', 'Values3', False, [0.2, 1]),
                        ([1, 2, 3, 4, 5], {1: [0.1, 0.2, 0.25, 0.3, 0.2], 2: [1.1, 1.2, 1.25, 1.3, 1.2]}, 'eV',
                            {1: np.array([0.1, 0.9, 0.4, 2, 3]), 2: np.array([1, 1, 1.3, 1.4, 3])}, 'YlOrBr', 'Values4', True, [0.2, 1]),
                        ([1, 2, 3, 4, 5], {1: [0.1, 0.2, 0.25, 0.3, 0.2], 2: [1.1, 1.2, 1.25, 1.3, 1.2], 3: [2, 2.3, 2.4, 2, 2]}, 'eV',
                            {1: np.array([0.1, 0.9, 0.4, 2, 3]), 2: np.array([0, -1, 3, 3.2, 3.1]), 3: np.array([0.01, 0.7, 0.2, 1, 3])}, 'PuBuGn', 'Values5', False, None)
])
def test_plot_vals_on_bands(plt, path, energies, energy_units, values, cmap, label, log, energy_window, with_plt):
    """
    Method to test plot_tools.plot_vals_on_bands function

    Method to plot normalized colormap overlaid on the dispersion (phonon dispersion or band structure).

    Parameters
    ----------
    path : array_like
       The array or list of path coordinates to be plotted on the x-axis

    energies : dict
       Dictionary of arrays of energies to plot, with keys labelling the band number or phonon mode.

    energy_units : str

    values : dict
       Dictionary of arrays of values to plot on the bands by color

    cmap : str
       Matplotlib cmap for plotting values.

    label : str
       Label for the values mapped on the colormap

    log : bool, optional
       If true, values will be normalized using log scale. If false, values will be normalized using linear scale.
       By default, true.

    energy_window : tuple, optional
       Tuple with the lower and upper bound of the chosen energy window

    """

    if not with_plt:
        pytest.skip("Test requires pytest-plt")

    fig, ax = plt.subplots()
    ppy.plot_tools.plot_vals_on_bands(ax, path, energies, energy_units, values, cmap, label, log, energy_window)
