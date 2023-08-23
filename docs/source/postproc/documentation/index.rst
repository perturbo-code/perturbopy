

For developers
==============

.. toctree::
    :maxdepth: 1

    utils

In this section, we provide notes for developers on how the code is structured. For full documentation, please refer to the API (link). 

The code is organized in three main folders: the ``utils`` folder, the ``dbs`` folder, and the ``calc_modes`` folder. 

The ``utils`` folder contains modules that encode functions useful to several calculation modes. 

* The ``constants`` module stores commonly used constants, as well as functions for converting between units.
* The ``lattice`` module contains functions for working with crystal lattices, such as converting between crystal and cartesian coordinates.
* The ``plot_tools`` contains functions for plotting.

The ``dbs`` folder contains classes that represent databases common to several calculation modes. For example, several calculation modes store information about k-points or q-points, so we have a ``RecipPtDB`` that represents sets of reciprocal points. These ``dbs`` classes typically use functions from the ``utils`` modules.

* The ``RecipPtDB`` class represents sets of reciprocal points, such as k-points or q-points. Its methods correspond strongly to the ``lattice`` module.
* The ``EnergyDB`` class represents a dispersion, such as a band structure or phonon dispersion. It contains methods for unit conversion.

Finally, the ``calc_modes`` folder contains classes that represent each Perturbo calculation mode. These ``calc_modes`` classes typically have attributes of ``dbs`` classes, and they may use functions from the ``utils`` modules, particularly the ``plot_tools`` module.