Dynamics-run tutorial
=====================

In this section, we describe how to use Perturbopy to process a Perturbo ``dynamics-run`` calculation.

The ultrafast dynamics calculation solves the real-time Boltzman transport equation (rt-BTE). Please see the `Perturbo website <https://perturbo-code.github.io/mmydoc_dynamics.html>`_ for more details. We first run the Perturbo calculation following the instructions on the Perturbo website and obtain the YAML file, *si_dynamics-run.yml*. We also obtain two other important files: the tet HDF5 file *si_tet.h5* (from the setup calculation), and the cdyna HDF5 file *si_cdyna.h5*. These files store data on the k-points and the dynamics results which are too large to be outputted to the YAML file.

Next, we create the :py:class:`.DynaRun` object using the YAML file, cdyna HDF5 file, and tet HDF5 file as inputs. This :py:class:`.DynaRun` object contains all of the information from those three files.

.. code-block :: python

	import perturbopy.postproc as ppy

	cdyna_path = "si_cdyna.h5"
	tet_path = "si_tet.h5"
	yaml_path = "si_dynamics_run.yml"
	si_dyna_run = ppy.DynaRun.from_hdf5_yaml(cdyna_path, tet_path, yaml_path)


Accessing the data
~~~~~~~~~~~~~~~~~~

We can get information on the number of runs, (total number of performed simulations), the number of time steps and their increment for each run, and the electric field for each run.

..code-block :: python
	
	si_dyna_run.num_runs

	>> 1

	si_dyna_run.get_info()

	>> This simulation has 1 runs
        
        Dynamics run: 1
        Number of steps: 25
        Time step (fs): 2.0
        Electric field (V/cm): [0. 0. 0.]

Below, we describe how to access information on a particular run. The ``si_dyna_run`` object contains information on the k-points and band structure, stored in :py:attr:`DynaRun.kpt` and :py:attr:`DynaRun.bands`. These are also described below.


Individual runs
---------------

We can index the ``si_dyna_run`` object to obtain information on a particular run (stored in :py:class:`.DynaIndivRun` objects. For example, to obtain information on configuration 1,

.. code-block :: python

	si_dyna_run[1]

.. note ::
	Indexing starts at 1 to match with Perturbo indices.

For each run, we can obtain the distribution function at each time using the :py:attr:`DynaIndivRun.snap_t` attribute. The shape of this attribute is num_bands x num_kpoints x num_time_steps.

.. code-block :: python

	si_dyna_run[1].snap_t.shape # num_bands x num_kpoints x num_time_steps
	>> (2, 15975, 25)

	# Get the distribution function at band 1, k-point 1000, and all time steps.
	si_dyna_run[1].snap_t[1, 1000, :]

	>> [1.38367179e-88 1.38343669e-88 1.38319133e-88 3.72746507e-87
		 3.56916995e-70 7.02520666e-62 3.31911718e-58 2.37911270e-56
		 5.62502833e-55 7.23131136e-54 6.24468845e-53 4.05880934e-52
		 2.12845401e-51 9.42992232e-51 3.64547874e-50 1.25909889e-49
		 3.95524208e-49 1.14578759e-48 3.09467415e-48 7.86225317e-48
		 1.89254866e-47 4.34236821e-47 9.54505383e-47 2.01865321e-46
		 4.12256762e-46]

	si_dyna_run[1].num_steps
	>> 25
	si_dyna_run[1].time_step
	>> 2.0
	si_dyna_run[1].efield
	>> array([0., 0., 0.])


K-points
--------

The k-points used for the bands calculation are stored in the :py:attr:`.DynaRun.kpt` attribute, which is of type :py:class:`.RecipPtDB`. For example, to access the k-point coordinates and their units:

.. code-block :: python
	
	si_dyna_run.kpt.points[:, 0]

	>> array([0.5, 0.5, 0.5])

	si_dyna_run.kpt.units

	>> 'crystal'

Please see the section :ref:`handling_kpt_qpt` for details on accessing the k-points through this attribute.

Band energies
-------------

The  band energies are stored in the :py:attr:`.DynaRun.bands` attribute, which is a :py:class:`.UnitsDict` object. The keys represent the band index, and the values are arrays containing the band energies corresponding to each k-point. 

.. code-block :: python

	si_dyna_run.bands.keys()
	>> dict_keys([1, 2])

	si_dyna_run.bands[2]
	>> array([0.51121006, 0.51080167, 0.51173707, ..., 0.50932315, 0.50955554, 0.51121006])

Please see the section :ref:`physical_quantities` for details on accessing the bands and their units.
