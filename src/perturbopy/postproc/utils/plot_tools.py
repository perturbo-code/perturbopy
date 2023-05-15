"""
This is a module for creating plots based on Perturbo calculation results

"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from perturbopy.postproc.utils import lattice
from matplotlib import colors
plotparams = {'figure.figsize': (16, 9),
                     'axes.grid': False,
                     'lines.linewidth': 2.5,
                     'axes.linewidth': 1.1,
                     'lines.markersize': 10,
                     'xtick.bottom': True,
                     'xtick.top': True,
                     'xtick.direction': 'in',
                     'xtick.minor.visible': True,
                     'ytick.left': True,
                     'ytick.right': True,
                     'ytick.direction': 'in',
                     'ytick.minor.visible': True,
                     'figure.autolayout': False,
                     'mathtext.fontset': 'dejavusans',
                     'mathtext.default': 'it',
                     'xtick.major.size': 4.5,
                     'ytick.major.size': 4.5,
                     'xtick.minor.size': 2.5,
                     'ytick.minor.size': 2.5,
                     'legend.handlelength': 3.0,
                     'legend.shadow': False,
                     'legend.markerscale': 1.0,
                     'font.size': 20}


def plot_recip_pt_labels(ax, labels, point_array, path_array, label_height="lower", show_line=True):
   """"
   Method to add reciprocal point labels to the plot

   Parameters
   ----------
   ax : matplotlib.axes.Axes
         Axis with plotted dispersion

   recip_pt : RecipPtDB
         The database of points in reciprocal space to plot

   line : bool
         If true, a line will be plotted to mark labeled reciprocal points

   Returns
   -------
   ax: matplotlib.axes.Axes
       Axis with the plotted dispersion and labeled reciprocal points

   """

   if label_height == "upper":
      label_height = ax.get_ylim()[1] + (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.1

   elif label_height == "lower":
      label_height = ax.get_ylim()[0] - (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.1
   
   for label in labels.keys():
      path_to_label = lattice.convert_point2path(labels[label], point_array, path_array)
      
      if path_to_label is None:
         continue
      for x in path_to_label:
         if show_line:
            ax.axvline(x)
            ax.text(x=x, y=label_height, s=label)

   return ax


def set_energy_window(ax, energy_window):
   ax.set_ylim((float(energy_window[0]) * 1.01, float(energy_window[1]) * .99))
   return ax


def plot_dispersion(ax, path, energies, energy_units, c='k', ls='-', energy_window=None):
   """
   Method to plot the dispersion (phonon dispersion or band structure).

   Parameters
   ----------
   ax: matplotlib.axes.Axes
         Axis on which to plot the dispersion

   : RecipPtDB
         The database of reciprocal points to be plotted

   energy_db : EnergiesDB
         The database of energies to be plotted

   show_reicp_pts_labels: bool
         Whether or not to show the reciprocal point labels stored in 
   Returns
   -------
   ax: matplotlib.axes.Axes
         Axis with the plotted dispesion

   """

   if isinstance(c, str):
      c = [c]
   if isinstance(ls, str):
      ls = [ls]

   print(c)

   for n in energies.keys():
      x = path
      y = energies[n]
      ax.plot(x, y, c='k')#,
                  # color=c[n % len(c)],
                  # linestyle=ls[n % len(ls)])

   if energy_window is not None:
      ax = set_energy_window(ax, energy_window)

   ax.set_xticks([])
   ax.set_ylabel(f'Energy ({energy_units})')

   return ax


def plot_vals_on_bands(ax, path, energies, energy_units, values, cmap='RdBu', energy_window=None):
   """
   Method to plot the dispersion (phonon dispersion or band structure).

   Parameters
   ----------
   ax: matplotlib.axes.Axes
         Axis on which to plot the dispersion

   : RecipPtDB
         The database of reciprocal points to be plotted

   energy_db : EnergiesDB
         The database of energies to be plotted

   show_reicp_pts_labels: bool
         Whether or not to show the reciprocal point labels stored in 
   Returns
   -------
   ax: matplotlib.axes.Axes
         Axis with the plotted dispesion

   """

   # Create a continuous norm to map from data points to colors
   vmin = min([min(values[key]) for key in values.keys()])
   vmax = max([max(values[key]) for key in values.keys()])

   print(vmin)
   print(vmax)
   
   norm = plt.Normalize(vmin, vmax)
   #norm = colors.LogNorm(vmin,vmax)
   for n in energies.keys():

      x = np.array(path)
      y = np.array(energies[n])

      points = np.array([x, y]).T.reshape(-1, 1, 2)
      segments = np.concatenate([points[: -1], points[1:]], axis=1)
   
      lc = LineCollection(segments, cmap=cmap, norm=norm)
      
      lc.set_array(values[n])
      lc.set_linewidth(2)
      line = ax.add_collection(lc)

      if ax.get_xlim()[0] > x.min():
         ax.set_xlim(ax.min(), ax.get_xlim()[1])
      if ax.get_xlim()[1] < x.max():
         ax.set_xlim(ax.get_xlim()[0], x.max())
   
      if ax.get_ylim()[0] > y.min():
         ax.set_ylim(y.min(), ax.get_ylim()[1])
      if ax.get_ylim()[1] < y.max():
         ax.set_ylim(ax.get_ylim()[0], y.max())

   plt.colorbar(line, ax=ax)

   if energy_window is not None:
      ax = set_energy_window(ax, energy_window)

   ax.set_xticks([])
   ax.set_ylabel(f'Energy ({energy_units})')

   return ax
