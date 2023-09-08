import numpy as np
from perturbopy.postproc.calc_modes.calc_mode import CalcMode
from perturbopy.postproc.dbs.units_dict import UnitsDict
from perturbopy.postproc.dbs.recip_pt_db import RecipPtDB
from perturbopy.postproc.utils.plot_tools import plot_dispersion, plot_recip_pt_labels, plot_vals_on_bands


class Ephmat(CalcMode):
    """
    Class representation of a Perturbo ephmat calculation.

    Attributes
    ----------


    """

    def __init__(self, pert_dict):
        """
        Constructor method

        Parameters
        ----------
        pert_dict : dict
        Dictionary containing the inputs and outputs from the ephmat calculation.

        """
        super().__init__(pert_dict)

        if self.calc_mode != 'ephmat':
            raise ValueError('Calculation mode for a ephmatCalcMode object should be "ephmat"')

        phdisp_units = self._pert_dict['ephmat'].pop('phonon energy units')
        defpot_units = self._pert_dict['ephmat'].pop('deformation potential units')
        ephmat_units = self._pert_dict['ephmat'].pop('e-ph matrix elements units')
        nmode = self._pert_dict['ephmat'].pop('number of phonon modes')

        kpath_units = self._pert_dict['ephmat'].pop('k-path coordinate units')
        kpath = np.array(self._pert_dict['ephmat'].pop('k-path coordinates'))
        kpoint_units = self._pert_dict['ephmat'].pop('k-point coordinate units')
        kpoint = np.array(self._pert_dict['ephmat'].pop('k-point coordinates'))
        
        qpath_units = self._pert_dict['ephmat'].pop('q-path coordinate units')
        qpath = np.array(self._pert_dict['ephmat'].pop('q-path coordinates'))
        qpoint_units = self._pert_dict['ephmat'].pop('q-point coordinate units')
        qpoint = np.array(self._pert_dict['ephmat'].pop('q-point coordinates'))

        ephmat_dat = self._pert_dict['ephmat'].pop('phonon mode')
        
        self.kpt = RecipPtDB.from_lattice(kpoint, kpoint_units, self.lat, self.recip_lat, kpath, kpath_units)
        self.qpt = RecipPtDB.from_lattice(qpoint, qpoint_units, self.lat, self.recip_lat, qpath, qpath_units)

        phdisp = {}
        defpot = {}
        ephmat = {}

        for phidx in ephmat_dat.keys():
            phdisp[phidx] = ephmat_dat[phidx].pop('phonon energy')
            defpot[phidx] = ephmat_dat[phidx].pop('deformation potential')
            ephmat[phidx] = ephmat_dat[phidx].pop('e-ph matrix elements')

            # in the case of multiple k-points and q-points, need to make defpot and ephmat two-dimensional
            if len(kpath) > 1 and len(qpath) > 1:
                defpot[phidx] = np.array(defpot).reshape(len(kpath), len(qpath))
                ephmat[phidx] = np.array(ephmat).reshape(len(kpath), len(qpath))

        self.phdisp = UnitsDict.from_dict(phdisp, phdisp_units)
        self.defpot = UnitsDict.from_dict(defpot, defpot_units)
        self.ephmat = UnitsDict.from_dict(ephmat, ephmat_units)

    def plot_phdisp(self, ax, show_qpoint_labels=True, c='k', ls='-', energy_window=None):
        """
        Method to plot the phonon dispersion.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
           Axis on which to plot the phdisp.

        energy_window : tuple of int, optional
           The range of band energies to be shown on the y-axis.

        show_qpoint_labels : bool, optional
           If true, the q-point labels stored in the labels attribute will be shown on the plot. Default true.

        Returns
        -------
        ax: matplotlib.axes.Axes
           Axis with the plotted bands.

        """
        ax = plot_dispersion(ax, self.qpt.path, self.phdisp.energies, self.phdisp.units, c, ls, energy_window)

        if show_qpoint_labels:
            ax = plot_recip_pt_labels(ax, self.qpt.labels, self.qpt.points, self.qpt.path)

        return ax

    def plot_defpot(self, ax, show_qpoint_labels=True, cmap='RdBu', energy_window=None):
        """
        Method to plot the phonon dispersion.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
           Axis on which to plot the phdisp.

        energy_window : tuple of int, optional
           The range of band energies to be shown on the y-axis.

        show_qpoint_labels : bool, optional
           If true, the q-point labels stored in the labels attribute will be shown on the plot. Default true.

        Returns
        -------
        ax: matplotlib.axes.Axes
           Axis with the plotted bands.

        """
        ax = plot_vals_on_bands(ax, self.qpt.path, self.phdisp.energies, self.phdisp.units, values=self.defpot.energies, energy_window=energy_window, cmap=cmap)

        if show_qpoint_labels:
            ax = plot_recip_pt_labels(ax, self.qpt.labels, self.qpt.points, self.qpt.path)

        return ax

    def plot_ephmat(self, ax, show_qpoint_labels=True, cmap='RdBu', energy_window=None):
        """
        Method to plot the phonon dispersion.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
           Axis on which to plot the phdisp.

        energy_window : tuple of int, optional
           The range of band energies to be shown on the y-axis.

        show_qpoint_labels : bool, optional
           If true, the q-point labels stored in the labels attribute will be shown on the plot. Default true.

        Returns
        -------
        ax: matplotlib.axes.Axes
           Axis with the plotted bands.

        """
        ax = plot_vals_on_bands(ax, self.qpt.path, self.phdisp.energies, self.phdisp.units, values=self.ephmat.energies, energy_window=energy_window, cmap=cmap)

        if show_qpoint_labels:
            ax = plot_recip_pt_labels(ax, self.qpt.labels, self.qpt.points, self.qpt.path)

        return ax
