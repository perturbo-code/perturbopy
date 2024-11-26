import numpy as np
from perturbopy.postproc.calc_modes.calc_mode import CalcMode
from perturbopy.postproc.dbs.units_dict import UnitsDict
from perturbopy.postproc.dbs.recip_pt_db import RecipPtDB
from perturbopy.postproc.utils.plot_tools import plot_dispersion, plot_recip_pt_labels, plot_vals_on_bands


class EphmatSpin(CalcMode):
    """
    Class representation of a Perturbo ephmat_spin calculation.

    Attributes
    ----------
    kpt : RecipPtDB
       Database for the k-points used in the ephmat_spin calculation, containing N points.
    
    qpt : RecipPtDB
       Database for the q-points used in the ephmat_spin calculation, containing M points.
    
    phdisp : UnitsDict
       Database for the phonon energies computed by the ephmat_spin calculation. The keys are
       the phonon mode, and the values are an array (of length M) containing the energies at each q-point
       with units phdisp.units
    
    ephmat : UnitsDict
       Database for the e-ph spin flip matrix elements computed by the ephmat_spin calculation. The keys are
       the phonon mode, and the values are an array (of length NxM) where element (n, m)
       is the e-ph spin flip matrix element (units ephmat.units) between an electron at k-point n and phonon at q-point m
    
    defpot : UnitsDict
       Database for the deformation potentials computed by the phdisp calculation. The keys are
       the phonon mode, and the values are an array (of length NxM) where element (n, m)
       is the deformation potential (units defpot.units) of an electron at k-point n and phonon at q-point m.

    """

    def __init__(self, pert_dict):
        """
        Constructor method

        Parameters
        ----------
        pert_dict : dict
            Dictionary containing the inputs and outputs from the ephmat_spin calculation.

        """
        super().__init__(pert_dict)

        if self.calc_mode != 'ephmat_spin':
            raise ValueError('Calculation mode for a EphmatSpin object should be "ephmat_spin"')

        phdisp_units = self._pert_dict['ephmat_spin'].pop('phonon energy units')
        defpot_units = self._pert_dict['ephmat_spin'].pop('deformation potential units')
        ephmat_units = self._pert_dict['ephmat_spin'].pop('e-ph matrix elements units')
        nmode = self._pert_dict['ephmat_spin'].pop('number of phonon modes')

        kpath_units = self._pert_dict['ephmat_spin'].pop('k-path coordinate units')
        kpath = np.array(self._pert_dict['ephmat_spin'].pop('k-path coordinates'))
        kpoint_units = self._pert_dict['ephmat_spin'].pop('k-point coordinate units')
        kpoint = np.array(self._pert_dict['ephmat_spin'].pop('k-point coordinates'))
        
        qpath_units = self._pert_dict['ephmat_spin'].pop('q-path coordinate units')
        qpath = np.array(self._pert_dict['ephmat_spin'].pop('q-path coordinates'))
        qpoint_units = self._pert_dict['ephmat_spin'].pop('q-point coordinate units')
        qpoint = np.array(self._pert_dict['ephmat_spin'].pop('q-point coordinates'))

        ephmat_dat = self._pert_dict['ephmat_spin'].pop('phonon mode')
        
        self.kpt = RecipPtDB.from_lattice(kpoint, kpoint_units, self.lat, self.recip_lat, kpath, kpath_units)
        self.qpt = RecipPtDB.from_lattice(qpoint, qpoint_units, self.lat, self.recip_lat, qpath, qpath_units)

        phdisp = {}
        defpot = {}
        ephmat = {}

        N = len(self.kpt.path)
        M = len(self.qpt.path)

        for phidx in ephmat_dat.keys():
            phdisp[phidx] = ephmat_dat[phidx].pop('phonon energy')
            defpot[phidx] = np.array(ephmat_dat[phidx].pop('deformation potential')).reshape(N, M)
            ephmat[phidx] = np.array(ephmat_dat[phidx].pop('e-ph matrix elements')).reshape(N, M)

        self.phdisp = UnitsDict.from_dict(phdisp, phdisp_units)
        self.defpot = UnitsDict.from_dict(defpot, defpot_units)
        self.ephmat = UnitsDict.from_dict(ephmat, ephmat_units)

    def plot_phdisp(self, ax, show_qpoint_labels=True, **kwargs):
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
        ax = plot_dispersion(ax, self.qpt.path, self.phdisp, self.phdisp.units, **kwargs)

        if show_qpoint_labels:
            ax = plot_recip_pt_labels(ax, self.qpt.labels, self.qpt.points, self.qpt.path)

        return ax

    def plot_defpot(self, ax, kpoint_idx=0, show_qpoint_labels=True, **kwargs):
        """
        Method to plot the phonon dispersion.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
           Axis on which to plot the phdisp.

        kpoint_idx : int, optional
            Index of the k-point to plot the deformation potentials for. Deformation potentials will be plotted along q-points, at this k-point
            By default, it will be the first k-point.

        energy_window : tuple of int, optional
           The range of band energies to be shown on the y-axis.

        show_qpoint_labels : bool, optional
           If true, the q-point labels stored in the labels attribute will be shown on the plot. Default true.

        Returns
        -------
        ax: matplotlib.axes.Axes
           Axis with the plotted bands.

        """

        values = {}

        for key, val in self.defpot.items():
            values[key] = self.defpot[key][kpoint_idx, :]

        ax = plot_vals_on_bands(ax, self.qpt.path, self.phdisp, self.phdisp.units, values=values, label=r'$\Phi$', **kwargs)

        if show_qpoint_labels:
            ax = plot_recip_pt_labels(ax, self.qpt.labels, self.qpt.points, self.qpt.path)

        return ax

    def plot_ephmat(self, ax, kpoint_idx=0, show_qpoint_labels=True, **kwargs):
        """
        Method to plot the phonon dispersion.

        Parameters
        ----------
        ax : matplotlib.axes.Axes
           Axis on which to plot the phdisp.

        kpoint_idx : int, optional
            Index of the k-point to plot the e-ph elements for. E-ph elements will be plotted along q-points, at this k-point
            By default, it will be the first k-point.
        energy_window : tuple of int, optional
           The range of band energies to be shown on the y-axis.

        show_qpoint_labels : bool, optional
           If true, the q-point labels stored in the labels attribute will be shown on the plot. Default true.

        Returns
        -------
        ax: matplotlib.axes.Axes
           Axis with the plotted bands.

        """

        values = {}

        for key, val in self.ephmat.items():
            values[key] = self.ephmat[key][kpoint_idx, :]

        ax = plot_vals_on_bands(ax, self.qpt.path, self.phdisp, self.phdisp.units, values=values, label=r'$|g flip|$', **kwargs)

        if show_qpoint_labels:
            ax = plot_recip_pt_labels(ax, self.qpt.labels, self.qpt.points, self.qpt.path)

        return ax
