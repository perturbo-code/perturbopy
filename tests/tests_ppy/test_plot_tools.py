import pytest
import perturbopy.postproc as ppy

points_cryst = [[0, 0, 0.5, 0.25, 0.25, 0.375], [0, 0.5, 0.5, 0.75, 0.625, 0.75], [0, 0.5, 0.5, 0.5, 0.625, 0.375]]
points_cart = [[0, 0, 0.5, 0.5, 0.25, 0.75], [0, 1, 0.5, 1, 1, 0.75], [0, 0, 0.5, 0, 0.25, 0.]]


@pytest.fixture()
def recip_dbs():
   return ppy.RecipPtDB(points_cart, points_cryst, units='cryst')


@pytest.mark.parametrize("path, energies, energy_units, c, ls, energy_window", [
                        ([1, 2, 3, 4, 5], {1: [0.1, 0.2, 0.25, 0.3, 0.2], 2: [1.1, 1.2, 1.25, 1.3, 1.2]}, 'eV', 'k', '--', None),
                        ([1, 2, 3, 4, 5], {1: [0.1, 0.2, 0.25, 0.3, 0.2], 2: [1.1, 1.2, 1.25, 1.3, 1.2]}, 'eV', ['b', 'g'], '--', None),
                        ([1, 2, 3, 4, 5], {1: [0.1, 0.2, 0.25, 0.3, 0.2], 2: [1.1, 1.2, 1.25, 1.3, 1.2]}, 'eV', ['b', 'k'], ['-', '--'], None),
                        ([1, 2, 3, 4, 5], {1: [0.1, 0.2, 0.25, 0.3, 0.2], 2: [1.1, 1.2, 1.25, 1.3, 1.2]}, 'eV', 'k', '--', [0.2, 1]),
                        ([1, 2, 3, 4, 5], {1: [0.1, 0.2, 0.25, 0.3, 0.2], 2: [1.1, 1.2, 1.25, 1.3, 1.2], 3: [2, 2.3, 2.4, 2, 2]},
                            'eV', ['b', 'g'], ['--', ':'], None)
])
def test_plot_dispersion(plt, path, energies, energy_units, c, ls, energy_window):
   fig, ax = plt.subplots()
   ppy.plot_tools.plot_dispersion(ax, path, energies, energy_units, c, ls, energy_window)


@pytest.mark.parametrize("path, energies, energy_units, values", [
                        ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], {1: [0.1, 0.2, 0.25, 0.3, 0.2, 1.1, 1.2, 1.25, 1.3, 1.2]},
                            'eV', {1: [10, 11, 2, 12, 13, 10, 12, 11.5, 14, 12]})
])
def test_plot_vals_on_bands(plt, path, energies, energy_units, values):
   fig, ax = plt.subplots()
   ppy.plot_tools.plot_vals_on_bands(ax, path, energies, energy_units, values)
