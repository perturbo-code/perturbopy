import numpy as np
from perturbopy.postproc.calc_modes.calc_mode import CalcMode
from perturbopy.postproc.dbs.units_dict import UnitsDict
from perturbopy.postproc.dbs.recip_pt_db import RecipPtDB
from perturbopy.postproc.utils.plot_tools import plot_recip_pt_labels, plot_vals_on_bands


class Spins(CalcMode):
    """
    Class representation of a Perturbo spins calculation.

    Parameters
    ----------
    pert_dict : dict
    Dictionary containing the inputs and outputs from the spins calculation.

    Attributes
    ----------
    kpt : RecipPtDB
       Database for the k-points used in the spins calculation.
    bands : UnitsDict
       Database for the band energies computed by the spins calculation.
    spins : UnitsDict
       Database for the spin and band energies computed by the spins calculation.

    """

    def __init__(self, pert_dict):
        """
        Constructor method

        """
        super().__init__(pert_dict)

        if self.calc_mode != 'spins':
            raise ValueError('Calculation mode for a SpinsCalcMode object should be "spins"')

        kpath_units = self._pert_dict['spins'].pop('k-path coordinate units')
        kpath = np.array(self._pert_dict['spins'].pop('k-path coordinates'))
        kpoint_units = self._pert_dict['spins'].pop('k-point coordinate units')
        kpoint = np.array(self._pert_dict['spins'].pop('k-point coordinates'))

        energies_dict = self._pert_dict['spins'].pop('band index')
        num_bands = self._pert_dict['spins'].pop('number of bands')
        energy_units = self._pert_dict['spins'].pop('band units')

        spins_dict = self._pert_dict['spins'].pop('band index (spins)')
        spin_units = self._pert_dict['spins'].pop('<n|sigma_z|n> units')

        self.kpt = RecipPtDB.from_lattice(kpoint, kpoint_units, self.lat, self.recip_lat, kpath, kpath_units)
        self.bands = UnitsDict.from_dict(energies_dict, energy_units)
        self.spins = UnitsDict.from_dict(spins_dict, spin_units)

    def plot_spins(self, ax, kpoint_idx=0, show_kpoint_labels=True, log=True, **kwargs):
        """
        Method to plot the <n|sigma_z|n> values over the band structure.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
           Axis on which to plot the bands.
        
        kpoint_idx : int, optional
           Index of the k-point to plot the <n|sigma_z|n> values for. <n|sigma_z|n> elements will be plotted along k-points, at this k-point
           By default, it will be the first k-point.

        show_kpoint_labels : bool, optional
           If true, the k-point labels stored in the labels attribute will be shown on the plot. Default true.

        log : bool, optional
           If true, the plot will normalize values on a log scale. If false, the plot will normalize values linearly.
           By default, it will be true.

        Returns
        -------
        ax: matplotlib.axes.Axes
           Axis with the plotted bands.

        """
        values = {}

        values = {key: 1 - val for key, val in self.spins.items()}

        ax = plot_vals_on_bands(ax, self.kpt.path, self.bands, self.bands.units, values=values, log=log, label=r'$|\langle n|\sigma_z|n\rangle |$', **kwargs)

        if show_kpoint_labels:
            ax = plot_recip_pt_labels(ax, self.kpt.labels, self.kpt.points, self.kpt.path)

        return ax
