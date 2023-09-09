Tutorials
=========
    
Here, we provide tutorials for Perturbo postprocessing. For each tutorial, we first must perform a Perturbo calculation, described `here <https://perturbo-code.github.io/mydoc_running_perturbo.html>`_. Perturbo offers several **calculation modes**, which compute different properties of a material. The results are outputted to a YAML file, which is used as an input to Perturbopy.

First, we give an overview on the workflow to use Perturbopy. In additional sections linked below, we provide tutorials explaining how to process the outputs of each calculation mode:

.. toctree::
    :maxdepth: 1

    bands
    phdisp
    ephmat
    trans
    imsigma
    dynamics-run
    dynamics-pp

.. _perturbo_calculation:

Perturbo calculation
-----------------------

All Perturbo calculations output a YAML file (default name **<prefix>_<calc_mode>.yml.**). This YAML file structure is described on the `Perturbo website <https://perturbo-code.github.io/mydoc_running_perturbo.html#yaml-file-structure>`_. It contains the following information:

* inputs to the Perturbo calculation (the *input parameters* field in the YAML file)
* information about the material (the *basic data* field in the YAML file), such as the lattice parameter and lattice vectors. 
* outputs from the Perturbo calculation (fields that are specific to each ``calc_mode``, described in individual tutorials)

We will use this YAML file to export the data to Python with Perturbopy.

.. _exporting_data:

Exporting data
--------------

The first step is to create a object containing the data. All of the data from the YAML file is stored in Perturbopy objects, which have a datatype specific to their ``calc_mode``. For example, let's say the ``calc_mode`` = ``bands``. To postprocess the results, we should create a :py:class:`.Bands` object called ``si_bands``, using the YAML file as an input. The ``si_bands`` object contains all the data stored in the YAML file, **'si_bands.yml'**. 

.. code-block :: python

	import perturbopy.postproc as ppy

	si_bands = ppy.Bands.from_yaml('si_bands.yml')

.. note ::
	Some Perturbo calculation modes output results that are too large to be stored in a YAML file. These results are stored instead in an HDF5 file. If a particular calculation mode requires an HDF5 file, it will be stated in the respective tutorial.


Material information
~~~~~~~~~~~~~~~~~~~~

The *basic data* field of the YAML file stores information about the material from the **'prefix'_epr.h5** file generated in the ``qe2pert`` step. Each entry of the *basic data* is stored in separate attributes in the Perturbopy object. For example, here we obtain the lattice parameter (alat) and lattice vectors (lat) used for silicon:

.. code-block :: python

	si_bands.alat

	>> 10.264

	si_bands.lat

	>> array([[-0.5,  0. , -0.5],
              [ 0. ,  0.5,  0.5],
              [ 0.5,  0.5,  0. ]])

For full details on all the *basic data* entries stored as attributes in ``si_bands``, please refer to the parameters of :py:class:`.CalcMode`. 

Perturbo inputs and outputs
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Perturbo outputs are stored in attributes that are specific to their ``calc_mode``, Please refer to the individual tutorials for more details. Two important databases are used to store :ref:`k-points and q-points <Handling k-points and q-points>`, and to store other :ref:`physical quantities <Physical quantities>` such as band energies, temperatures, etc.

Remaining data from the YAML file are stored in the :py:attr:`.CalcMode._pert_dict` attribute. For example, calculation inputs are stored in the *inputs* field of the :py:attr:`.CalcMode._pert_dict` dictionary in every Perturbopy object.

.. code-block :: python

	gaas_bands._pert_dict['input parameters']['after conversion']['sampling']

    >> 'uniform'

Perturbo outputs that are not physically relevant (such as timing information and parallelization information) are also stored in :py:attr:`.CalcMode._pert_dict`. 


.. _handling_kpt_qpt:

Handling k-points and q-points
------------------------------

In several calculation modes, we work with sets of points in reciprocal space, such as k-points and q-points. These are stored in  objects. For example, let's look at the ``kpt`` attribute of the :py:class:`.Bands`, which stores the k-points used in the ``bands`` calculation.

The N coordinates are stored as a 3xN array in the :py:attr:`.RecipPtDB.points` attribute of ``kpt``. For example, to access the first k-point:

.. code-block :: python
	
	si_bands.kpt.points[:, 0]

	>> array([0.5, 0.5, 0.5])

The units of :py:attr:.RecipPtDB.points can either be:

* *crystal*: coordinates are in relative coordinates of the reciprocal lattice vectors
* *cartesian*: coordinates are in units of :math:`\frac{2\pi}{a}`

To see the units, 

.. code-block :: python
	
	si_bands.kpt.units

	>> 'crystal'

To change the units,

.. code-block :: python
	
	si_bands.kpt.convert_units("cartesian")
	si_bands.units

	>> 'cartesian'

The ``kpt`` attribute also stores the k-path coordinates, which are the one-dimensional coordinates assigned to each k-point. These would be the x-coordinates on a plot of the band structure.

.. code-block :: python
	
	si_bands.kpt.path

	>> array([0., 0.0169809, 0.0339618, ... 3.7386444, 3.7594417, 3.780239])

It is also possible to rescale the k-path, which has arbitrary units.

.. code-block :: python
	
	# Rescale the k-path to a range between 0 and 10
	si_bands.kpt.scale_path(0, 10)

	si_bands.kpt.path

	>> array([0., 0.04492018,  0.08984035, ... 9.88996833,  9.94498417, 10.])

The :py:class`RecipPtDB` dataype also provides methods to:

* search an array of k-points for a particular k-point, and return the indices of the matches (:py:meth:`.RecipPtDB.find`)
* find the k-path coordinate corresponding to a k-point coordinate (:py:meth:`.RecipPtDB.point2path`)
* find the k-point coordinate corresponding to a k-path coordinate (:py:meth:`.RecipPtDB.path2point`)

.. code-block :: python

	# Finds the index or indices of the k-point [0.5, 0.25, 0.75]
	si_bands.kpt.find([0.5, 0.25, 0.75])

	>> array([123], dtype=int64)

	# Check that this index is correct
	si_bands.kpt.points[:, 123]

	>> array([0.5 , 0.25, 0.75])

	# Find the k-path coordinate corresponding to k-point [0.5, 0.25, 0.75]
	si_bands.kpt.point2path([0.5, 0.25, 0.75])

	>> array([6.25893072])

	# Check that this k-path coordinate is correct
	si_bands.kpt.path[123]

	>> 6.258930718401667

	# Do the reverse: convert from k-path coordinate to k-point 
	si_bands.kpt.path2point(6.25893072)

	>> array([0.5 , 0.25, 0.75])

Note that, in the case of repeated k-points, both indices will be returned:

.. code-block :: python

	# Find the index of the gamma point, which is in the k-points twice
	si_bands.kpt.find([0,0,0])

	>> array([ 51, 195], dtype=int64)

	# Check this result
	si_bands.kpt.points[:, 51]
	si_bands.kpt.points[:, 195]

	>> array([0., 0., 0.])
	   array([0., 0., 0.])

Note that all three of these functions take two additional inputs: `max_dist` and `nearest`. The `max_dist` (default 0.025) specifies the maximum distance between two k-points to consider them a match. For example, 

.. code-block :: python

	# Find the index of [0.01, 0.01, 0.01], which is not one of the k-points stored in kpt.points.
	# However, its distance from [0,0,0] is 0.017 < 0.025, so the results for [0, 0, 0] are returned.
	si_bands.kpt.find([0.01, 0.01, 0.01])

	>> array([ 51, 195], dtype=int64)

	# Check this result
	si_bands.kpt.points[:, 51]
	si_bands.kpt.points[:, 195]

	>> array([0., 0., 0.])
	>> array([0., 0., 0.])

If `nearest` (default True) is True, only the k-point(s) that are closest to a requested k-point is considered a match, even if other k-points are within the `max_dist` range. For example, if `max_dist` = 0.05, then both [0.01, 0.01, 0.01] and [0.02, 0.02, 0.02] lie within that distance from [0, 0, 0]. If `nearest` = True, only [0.01, 0.01, 0.01] is considered a match. If `nearest` is False, both are considered matches. 

We can also add labels to the k-points. For example, the FCC Brillouin zone identifies [0.5, 0.5, 0.5] as the L point, and [0.5, 0.0, 0.5] as the X point. To add these labels,

.. code-block :: python
	
	si_bands.kpt.add_labels({"L": [0.5, 0.5, 0.5], "X": [0.5, 0.0, 0.5]})
	si_bands.kpt.labels

	>> {'L': [0.5, 0.5, 0.5], 'X': [0.5, 0.0, 0.5]}

Note these labels can be removed with `kpt.remove_labels`.

.. code-block :: python

	si_bands.kpt.remove_labels(["L"])
	si_bands.kpt.labels

	>> {'X': [0.5, 0.0, 0.5]}

A dictionary of labels for the FCC lattice can be found in ``ppy.lattice.points_fcc``.

.. code-block :: python
	
	si_bands.kpt.add_labels(ppy.lattice.points_fcc)
	si_bands.kpt.labels

	>> {'L': [0.5, 0.5, 0.5],
	>>	'X': [0.5, 0.0, 0.5],
	>>	'W': [0.5, 0.25, 0.75],
	>>	'K': [0.375, 0.375, 0.75],
	>>	'$\\Gamma$': [0, 0, 0]}

For more details on the RecipPtDB and its attributes, refer to the API :py:class:`.RecipPtDB`.

.. _physical_quantities:

Physical quantities
-------------------

Physical quantities such as energies, temperatures, mobilities, conductivities, etc are stored in :py:class:`UnitsDict` objects. These objects inherit from and function as Python dictionaries. They have an additional attribute to store the units.

For example in ``si_bands``, the band energies are stored in the :py:attr:`.Bands.bands` attribute. This is a :py:class:`UnitsDict`, with keys corresponding to band index and values corresponding to the energies of that band along the k-point path. It functions as a Python dictionary:

.. code-block :: python

	si_bands.bands.keys()
	>> dict_keys([1, 2, 3, 4, 5, 6, 7, 8])

	si_bands.bands[8]
	>> array([13.69848506, 13.70154719, ..., 9.47676028, 9.46081004])


We can also access the energy units.

.. code-block :: python

	si_bands.bands.units
	>> 'eV'

