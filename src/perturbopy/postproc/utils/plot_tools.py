"""
This is a module for creating plots based on Perturbo calculation results

"""

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


def plot_kpt_labels(ax, kpt_db, line=True, **kwargs):
  """"
  Method to add k-point labels to the plot

  Parameters
  ----------
  ax : matplotlib.axes.Axes
      Axis with plotted band structure

  kpt_db : KptsDB
      The database of k-points in the plot (also contains the k-point labels)

  line : bool
      If true, a line will be plotted to mark labeled k-points

  Returns
  -------
  ax: matplotlib.axes.Axes
     Axis with the plotted band structure and labeled k-points

  """
  default_y = ax.get_ylim()[0] - (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.1

  label_y = kwargs.pop('label_y', default_y)
  fontsize = kwargs.pop('fontsize', 20)
  color = kwargs.pop('color', 'k')

  labeled_kpts = kpt_db.labels

  for label in labeled_kpts:
    for x in kpt_db.kpt_to_kpath(labeled_kpts[label]):
       label_x = kwargs.pop('label_x', x)
       if line:
          ax.axvline(x, color=color, **kwargs)
          ax.text(x=label_x, y=label_y, s=label, fontsize=fontsize, **kwargs)

          return ax


def plot_bands(ax, kpt_db, bands_db, show_kpt_labels=True, **kwargs):
   """
   Method to plot the band structure.

   Parameters
   ----------
   ax: matplotlib.axes.Axes
      Axis on which to plot band structure

   kpt_db : KptsDB
      The database of k-points to be plotted

   bands_db : EnergiesDB
      The database of energies to be plotted

   show_kpt_labels: bool
      Whether or not to show the k-point labels stored in kpt_db

   Returns
   -------
   ax: matplotlib.axes.Axes
      Axis with the plotted band structure

   """

   default_colors = ['b', 'k', 'g', 'r', 'c', 'm', 'y']
   default_linestyles = ['-']
   default_ylabel = f'Energy ({bands_db.units})'
   default_band_indices = bands_db.band_indices

   band_indices = kwargs.pop('band_indices', default_band_indices)
   colors = kwargs.pop('c', kwargs.pop('color', default_colors))
   linestyles = kwargs.pop('ls', kwargs.pop('linestyle', default_linestyles))

   if not isinstance(colors, list):
      colors = [colors]
   if not isinstance(linestyles, list):
      linestyles = [linestyles]

   ylabel = kwargs.pop('ylabel', default_ylabel)

   for n in band_indices:

      ax.plot(kpt_db.kpath, bands_db.energies[n],
              color=colors[n % len(colors)],
              linestyle=linestyles[n % len(linestyles)])

   if show_kpt_labels:
      ax = plot_kpt_labels(ax, kpt_db)

   ax.set_xticks([])
   ax.set_ylabel(ylabel)

   return ax
