import pytest
import perturbopy.postproc as ppy

points_cryst = [[0, 0, 0.5, 0.25, 0.25, 0.375], [0, 0.5, 0.5, 0.75, 0.625, 0.75], [0, 0.5, 0.5, 0.5, 0.625, 0.375]]
points_cart = [[0, 0, 0.5, 0.5, 0.25, 0.75], [0, 1, 0.5, 1, 1, 0.75], [0, 0, 0.5, 0, 0.25, 0.]]


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
