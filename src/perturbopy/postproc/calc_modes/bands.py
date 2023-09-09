import numpy as np
from scipy.optimize import curve_fit
from perturbopy.postproc.calc_modes.calc_mode import CalcMode
from perturbopy.postproc.utils.constants import energy_conversion_factor, length_conversion_factor
from perturbopy.postproc.dbs.units_dict import UnitsDict
from perturbopy.postproc.dbs.recip_pt_db import RecipPtDB
from perturbopy.postproc.utils.plot_tools import plot_dispersion, plot_recip_pt_labels
from perturbopy.postproc.utils.lattice import reshape_points, cryst2cart


class Bands(CalcMode):
    """
    Class representation of a Perturbo bands calculation.

    Parameters
    ----------
    pert_dict : dict
    Dictionary containing the inputs and outputs from the bands calculation.

    Attributes
    ----------
    kpt : RecipPtDB
       Database for the k-points used in the bands calculation.
    bands : UnitsDict
       Database for the band energies computed by the bands calculation.

    """

    def __init__(self, pert_dict):
        """
        Constructor method

        """
        super().__init__(pert_dict)

        if self.calc_mode != 'bands':
            raise ValueError('Calculation mode for a BandsCalcMode object should be "bands"')

        kpath_units = self._pert_dict['bands'].pop('k-path coordinate units')
        kpath = np.array(self._pert_dict['bands'].pop('k-path coordinates'))
        kpoint_units = self._pert_dict['bands'].pop('k-point coordinate units')
        kpoint = np.array(self._pert_dict['bands'].pop('k-point coordinates'))

        energies_dict = self._pert_dict['bands'].pop('band index')
        num_bands = self._pert_dict['bands'].pop('number of bands')
        energy_units = self._pert_dict['bands'].pop('band units')

        self.kpt = RecipPtDB.from_lattice(kpoint, kpoint_units, self.lat, self.recip_lat, kpath, kpath_units)
        self.bands = UnitsDict.from_dict(energies_dict, energy_units)

    def indirect_bandgap(self, n_lower, n_upper):
        """
        Method to compute the indirect bandgap between two bands.

        Parameters
        ----------
        n_lower, n_upper : int
           Band number of the lower and upper bands.

        Returns
        -------
        gap: float
           The indirect bandgap, computed as the energy difference between the minimum of
           the upper band and the maximum of the lower band.
        lower_kpoint, upper_kpoint : array
           k-points corresponding to the minimum of the upper band and the maximum of the lower band.

        Raises
        ------
        ValueError
           If the upper and lower band numbers provided are not valid band indices from the bands database, or
           if n_lower is greater than n_upper.

        """

        if n_lower not in self.bands.keys() or n_upper not in self.bands.keys():
            raise ValueError("n_lower and n_upper must be valid band numbers.")

        if n_lower > n_upper:
            raise ValueError("n_lower must be less than or equal to n_upper.")

        gap = np.min(self.bands[n_upper]) - np.max(self.bands[n_lower])

        lower_kpoint = self.kpt.points[:, np.argmax(self.bands[n_lower])]
        upper_kpoint = self.kpt.points[:, np.argmin(self.bands[n_upper])]

        return gap, lower_kpoint, upper_kpoint

    def direct_bandgap(self, n_lower, n_upper):
        """
        Method to compute the direct bandgap between two bands.

        Parameters
        ----------
        n_lower, n_upper : int
           Band number of the lower and upper bands.

        Returns
        -------
        gap: float
           The direct bandgap, computed as the minimum energy difference between two bands
           at the same k-point.
        kpoint: array
           The k-point corresponding to the direct bandgap.

        Raises
        ------
        ValueError
           If the upper and lower band numbers provided are not valid band indices from the bands database, or
           if n_lower is greater than n_upper.

        """
        if n_lower not in self.bands.keys() or n_upper not in self.bands.keys():
            raise ValueError("n_lower and n_upper must be valid band numbers")

        if n_lower > n_upper:
            raise ValueError("n_lower must be less than or equal to n_upper.")

        transitions = self.bands[n_upper] - self.bands[n_lower]
        gap = np.min(transitions)
        kpoint = self.kpt.points[:, np.argmin(transitions)]

        return gap, kpoint

    def effective_mass(self, n, kpoint, max_distance, direction=None, ax=None, c='r'):
        """
        Method to compute the effective mass at a k-point, approximated with a parabolic fit.

        Parameters
        ----------
        n : int
           Index of the band for which to calculate the effective mass.

        kpoint : list
           The k-point on which to center the calculation.

        max_distance : float
           Maximum distance between the center k-point and k-points to include in the parabolic approximation.

        direction : array_like, optional
           The k-point specifying the direction of the effective mass. Defaults to the same value as kpoint,
           i.e. the longitudinal effective mass.

        ax : matplotlib.axes.Axes
           Axis on which to plot the bands and approximated parabolic curve

        c : str
           Color for plotting the approximated parabolic curve

        Returns
        -------
        effective_mass : float
           The longitudinal effective mass at band n and the inputted kpoint, computed by a parabolic fit.

        """

        # Default direction is longitudinal, i.e. in same direction as central k-point
        if direction is None:
            direction = kpoint
        else:
            direction = reshape_points(direction)

        kpoint = reshape_points(kpoint)

        energies = self.bands[n] * energy_conversion_factor(self.bands.units, 'hartree')
        alat = self.alat * length_conversion_factor(self.alat_units, 'bohr')
        E_0 = energies[self.kpt.find(kpoint)][0]

        def get_fit_data(max_fit_distance, kpoint, direction, max_points=None, epsilon=1e-6):

            kpoint_distances = np.linalg.norm(self.kpt.points - np.array(kpoint), axis=0)
            kpoint_mag_squared = np.linalg.norm(self.kpt.points, axis=0)

            # Find all k-points parallel to the direction within a tolerance, epsilon
            kpoint_parallel = abs(np.divide(np.dot(np.reshape(direction, (3,)), self.kpt.points), (np.linalg.norm(direction) * kpoint_mag_squared),
                                            where=kpoint_mag_squared != 0) - 1) < epsilon

            if max_points is None:
                kpoint_indices = np.where(np.logical_and(kpoint_distances < max_fit_distance, kpoint_parallel))[0]
                kpoint_indices = np.sort(kpoint_indices)
            else:
                kpoint_indices = np.where(kpoint_parallel)[0]
                kpoint_idx = self.kpt.find(kpoint)[0]
                kpoint_indices = np.where(abs(kpoint_indices - kpoint_idx) <= max_points)[0]

            kpoint_idx = self.kpt.find(kpoint)[0]

            if kpoint_idx not in kpoint_indices.flatten():
                kpoint_indices = np.append(kpoint_indices, kpoint_idx)

            kpt_points = self.kpt.points[:, kpoint_indices]

            kpt_points = cryst2cart(kpt_points, self.lat, self.recip_lat, forward=True, real_space=False)
            kpoint = cryst2cart(kpoint, self.lat, self.recip_lat, forward=True, real_space=False)

            kpoint_distances_squared = np.sum(np.square(kpt_points - kpoint), axis=0) * (np.pi * 2 / self.alat) ** 2

            return kpoint_indices, kpoint_distances_squared

        def parabolic_approx(kpoint_dist_squared, prefactor):
            return prefactor * kpoint_dist_squared + E_0

        fit_indices, fit_distances_squared = get_fit_data(max_distance, kpoint, direction)
        fit_energies = energies[fit_indices]
        fit_params, pcov = curve_fit(parabolic_approx, fit_distances_squared, fit_energies)

        effective_mass = 1 / (fit_params[0] * 2)

        if ax is not None:
            ax = self.plot_bands(ax, 'k')

            plot_indices, plot_distances_squared = get_fit_data(max_distance * 1.8, kpoint, direction)
            energies_fitted = (fit_params[0] * plot_distances_squared + E_0) * energy_conversion_factor('hartree', self.bands.units)

            ax.plot(self.kpt.path[plot_indices], energies_fitted, c, marker=None, ls='--')
            ax.plot(self.kpt.path[fit_indices], energies[fit_indices] * energy_conversion_factor('hartree', self.bands.units), c, marker='o')

        return effective_mass

    def plot_bands(self, ax, show_kpoint_labels=True, c='k', ls='-', energy_window=None):
        """
        Method to plot the band structure.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
           Axis on which to plot the bands.

        energy_window : tuple of int, optional
           The range of band energies to be shown on the y-axis.

        show_kpoint_labels : bool, optional
           If true, the k-point labels stored in the labels attribute will be shown on the plot. Default true.

        Returns
        -------
        ax: matplotlib.axes.Axes
           Axis with the plotted bands.

        """
        ax = plot_dispersion(ax, self.kpt.path, self.bands, self.bands.units, c, ls, energy_window)

        if show_kpoint_labels:
            ax = plot_recip_pt_labels(ax, self.kpt.labels, self.kpt.points, self.kpt.path)

        return ax
