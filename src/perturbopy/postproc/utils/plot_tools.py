"""
This is a module for creating plots based on Perturbo calculation results

"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

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

def plot_recip_pt_labels(ax, recip_pt_db, line=True, **kwargs):
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
  default_y = ax.get_ylim()[0] - (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.1

  label_y = kwargs.pop('label_y', default_y)
  fontsize = kwargs.pop('fontsize', 20)
  color = kwargs.pop('color', 'lightgray')

  labeled_recip_pt = recip_pt_db.labels

  for label in labeled_recip_pt.keys():
    for x in recip_pt_db.point_to_path(labeled_recip_pt[label]):
       label_x = kwargs.pop('label_x', x)
       if line:
          ax.axvline(x, color=color, linestyle='--',**kwargs, zorder=1)
          ax.text(x=label_x, y=label_y, s=label, fontsize=fontsize, **kwargs)

  return ax


def plot_dispersion(ax, recip_pt_db, energies_db, energy_window=None, show_recip_pt_labels=True, **kwargs):
   """
   Method to plot the dispersion (phonon dispersion or band structure).

   Parameters
   ----------
   ax: matplotlib.axes.Axes
      Axis on which to plot the dispersion

   recip_pt_db : RecipPtDB
      The database of reciprocal points to be plotted

   energies_db : EnergiesDB
      The database of energies to be plotted

   show_reicp_pts_labels: bool
      Whether or not to show the reciprocal point labels stored in recip_pt_db

   Returns
   -------
   ax: matplotlib.axes.Axes
      Axis with the plotted dispesion

   """

   default_colors = ['b', 'k', 'g', 'r', 'c', 'm', 'y']
   default_linestyles = ['-']
   default_ylabel = f'Energy ({energies_db.units})'
   default_dispersion_band_indices = energies_db.indices

   dispersion_band_indices = kwargs.pop('band_indices', default_dispersion_band_indices)
   colors = kwargs.pop('c', kwargs.pop('color', default_colors))
   linestyles = kwargs.pop('ls', kwargs.pop('linestyle', default_linestyles))
   band_labels = kwargs.pop('label', kwargs.pop('labels', None))

   if not isinstance(colors, list):
      colors = [colors]
   if not isinstance(linestyles, list):
      linestyles = [linestyles]
   if not isinstance(band_labels, list):
      band_labels = [band_labels]

   ylabel = kwargs.pop('ylabel', default_ylabel)

   for dispersion_band_idx, n in enumerate(dispersion_band_indices):
      x = np.array(recip_pt_db.path)
      y = np.array(energies_db.energies_dict[n])

      if energy_window is not None:
        above_min = np.where(y>energy_window[0])
        x = x[above_min]
        y = y[above_min]
        if len(x) == 0:
          continue

        below_max = np.where(y<energy_window[1])
        x = x[below_max]
        y = y[below_max]
        if len(x) == 0:
          continue

        ax.set_ylim((energy_window[0]*1.01, energy_window[1]*.99))
      ax.plot(x,y,
              color=colors[n % len(colors)],
              linestyle=linestyles[n % len(linestyles)],
              label = band_labels[n % len(band_labels)], zorder=2)
    
   if show_recip_pt_labels:
      ax = plot_recip_pt_labels(ax, recip_pt_db)

   ax.set_xticks([])
   ax.set_ylabel(ylabel)

   return ax

def plot_vals_on_bands(ax, recip_pt_db, energies_db, values, energy_window=None, show_recip_pt_labels=True, **kwargs):
   """
   Method to plot the dispersion (phonon dispersion or band structure).

   Parameters
   ----------
   ax: matplotlib.axes.Axes
      Axis on which to plot the dispersion

   recip_pt_db : RecipPtDB
      The database of reciprocal points to be plotted

   energies_db : EnergiesDB
      The database of energies to be plotted

   show_reicp_pts_labels: bool
      Whether or not to show the reciprocal point labels stored in recip_pt_db

   Returns
   -------
   ax: matplotlib.axes.Axes
      Axis with the plotted dispesion

   """

   default_ylabel = f'Energy ({energies_db.units})'
   dispersion_band_indices = energies_db.indices
   ylabel = kwargs.pop('ylabel', default_ylabel)

   # Create a continuous norm to map from data points to colors
   vmin = min([min(values[key]) for key in values.keys()])
   vmax = max([max(values[key]) for key in values.keys()])
   norm = plt.Normalize(vmin, vmax)

   for n in dispersion_band_indices:

      x = np.array(recip_pt_db.path)
      y = np.array(energies_db.energies_dict[n])
      points = np.array([x, y]).T.reshape(-1, 1, 2)
      segments = np.concatenate([points[:-1], points[1:]], axis=1)
      lc = LineCollection(segments, cmap='RdBu', norm=norm)

      lc.set_array(values[n])
      lc.set_linewidth(2)
      line = ax.add_collection(lc)

   energies_dict = energies_db.energies_dict
   ax.set_ylim(min([min(energies_dict[key]) for key in energies_dict.keys()]), max([max(energies_dict[key]) for key in energies_dict.keys()]))
      
   if show_recip_pt_labels:
      ax = plot_recip_pt_labels(ax, recip_pt_db)
      
   plt.colorbar(line, ax=ax)

   ax.set_xticks([])
   ax.set_ylabel(ylabel)

   return ax
