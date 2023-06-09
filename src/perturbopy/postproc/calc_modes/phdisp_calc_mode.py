import numpy as np
from perturbopy.postproc.calc_modes.calc_mode import CalcMode
from perturbopy.postproc.dbs.energy_db import EnergyDB
from perturbopy.postproc.dbs.recip_pt_db import RecipPtDB
from perturbopy.postproc.utils.plot_tools import plot_dispersion, plot_recip_pt_labels


class PhdispCalcMode(CalcMode):
   """
   Class representation of a Perturbo phonon dispersion (phdisp) calculation.

   Parameters
   ----------
   pert_dict : dict
      Dictionary containing the inputs and outputs from the phdisp calculation.

   Attributes
   ----------
   qpt : RecipPtDB
      Database for the q-points used in the phdisp calculation.
   phdisp : EnergiesDB
      Database for the phonon energies computed by the phdisp calculation.

   """

   def __init__(self, pert_dict):
      """
      Constructor method

      """
      super().__init__(pert_dict)
      
      if self.calc_mode != 'bands':
         raise ValueError('Calculation mode for a BandsCalcMode object should be "bands"')
      
      qpath_units = self._pert_dict['bands'].pop('k-path coordinate units')
      qpath = np.array(self._pert_dict['bands'].pop('k-path coordinates'))
      qpoint_units = self._pert_dict['bands'].pop('k-point coordinate units')
      qpoint = np.array(self._pert_dict['bands'].pop('k-point coordinates'))

      energies_dict = self._pert_dict['bands'].pop('band index')
      num_modes = self._pert_dict['bands'].pop('number of bands')
      energy_units = self._pert_dict['bands'].pop('band units')

      self.qpt = RecipPtDB.from_lattice(qpoint, qpoint_units, self.lat, self.recip_lat, qpath, qpath_units)
      self.phdisp = EnergyDB(energies_dict, energy_units, num_modes)

   def plot_phdisp(self, ax, energy_window=None, show_qpoint_labels=True, **kwargs):
      """
      Method to plot the phonon dispersion.

      Parameters
      ----------
      ax : matplotlib.axes.Axes
         Axis on which to plot the phonons.

      energy_window : tuple of int, optional
         The range of phonon energies to be shown on the y-axis.

      show_qpoint_labels : bool, optional
         If true, the k-point labels stored in the labels attribute will be shown on the plot.

      Returns
      -------
      ax: matplotlib.axes.Axes
         Axis with the plotted phonons.

      """
      ax = plot_dispersion(ax, self.qpt.path, self.phdisp.energies, self.phdisp.units, energy_window, **kwargs)

      if show_qpoint_labels:
         ax = plot_recip_pt_labels(ax, self.qpt.labels, self.qpt.points, self.qpt.path, **kwargs)
      
      return ax
