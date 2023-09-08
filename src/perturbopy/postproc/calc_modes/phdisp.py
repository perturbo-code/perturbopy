import numpy as np
from perturbopy.postproc.calc_modes.calc_mode import CalcMode
from perturbopy.postproc.dbs.units_dict import UnitsDict
from perturbopy.postproc.dbs.recip_pt_db import RecipPtDB
from perturbopy.postproc.utils.plot_tools import plot_dispersion, plot_recip_pt_labels


class Phdisp(CalcMode):
    """
    Class representation of a Perturbo phonon dispersion (phdisp) calculation.

   
    Attributes
    ----------
    qpt : RecipPtDB
       Database for the q-points used in the phdisp calculation.
    phdisp : UnitsDict
       Database for the phonon energies computed by the phdisp calculation.

    """

    def __init__(self, pert_dict):
        """
        Constructor method

         Parameters
        ----------
        pert_dict : dict
           Dictionary containing the inputs and outputs from the phdisp calculation.

        """
        super().__init__(pert_dict)

        if self.calc_mode != 'phdisp':
            raise ValueError('Calculation mode for a PhdispCalcMode object should be "phdisp"')

        qpath_units = self._pert_dict['phdisp'].pop('q-path coordinate units')
        qpath = np.array(self._pert_dict['phdisp'].pop('q-path coordinates'))
        qpoint_units = self._pert_dict['phdisp'].pop('q-point coordinate units')
        qpoint = np.array(self._pert_dict['phdisp'].pop('q-point coordinates'))

        energies_dict = self._pert_dict['phdisp'].pop('phonon mode')

        for mode_idx in energies_dict.keys():
            energies_dict[mode_idx] = np.array(energies_dict[mode_idx])

        num_modes = self._pert_dict['phdisp'].pop('number of modes')
        energy_units = self._pert_dict['phdisp'].pop('phdisp units')

        self.qpt = RecipPtDB.from_lattice(qpoint, qpoint_units, self.lat, self.recip_lat, qpath, qpath_units)
        self.phdisp = UnitsDict.from_dict(energies_dict, energy_units)

    def plot_phdisp(self, ax, show_qpoint_labels=True, c='k', ls='-', energy_window=None):
        """
        Method to plot the phonon dispersion.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
           Axis on which to plot the phonons.

        show_qpoint_labels : bool, optional
           If true, the q-point labels stored in the labels attribute will be shown on the plot.

        c : str, list
            See plot_tools.plot_dispersion function

        ls : str, list
            See plot_tools.plot_dispersion function 

        energy_window : tuple of float, optional
           The range of phonon energies to be shown on the y-axis.

        Returns
        -------
        ax: matplotlib.axes.Axes
           Axis with the plotted phonons.

        """
        ax = plot_dispersion(ax, self.qpt.path, self.phdisp.energies, self.phdisp.units, energy_window)

        if show_qpoint_labels:
            ax = plot_recip_pt_labels(ax, self.qpt.labels, self.qpt.points, self.qpt.path)

        return ax
