Trans tutorial
==============

In this section, we describe how to use Perturbopy to process a Perturbo transport calculation. The possible calculation modes are: ``trans``, ``trans-rta``, ``trans-ita``, ``trans-mag-rta``, ``trans-mag-ita``, and ``trans-pp``. Any of these calculation modes can be processed with the :py:class:`.Trans` object described below.

The transport calculation modes solve the Boltzmann transport equation (BTE) to compute the electrical conductivity, carrier mobility tensors as well as the Seebeck coefficient and thermal conductivity. For more information, please refer to the `Perturbo website <https://perturbo-code.github.io/mydoc_trans.html>`_. We first run the Perturbo calculation following the instructions on the Perturbo website (running ``trans-rta`` as an example) and obtain the YAML file, *si_trans-rta.yml*.

Next, we create the :py:class:`.Trans` object using the YAML file as an input. This object contains all of the information from the YAML file.

.. code-block :: python

	import perturbopy.postproc as ppy

	si_trans = ppy.Trans.from_yaml('si_trans-rta.yml')

Accessing the data
~~~~~~~~~~~~~~~~~~

The main results of the results are stored in two parts: 

* information defining the configuration of the transport calculation (temperature, chemical potential, carrier concentration)
* computed transport properties (electrical conductivity, carrier mobility tensors as well as the Seebeck coefficient and thermal conductivity)

See :ref:tutorials_intro for information on accessing data from ``si_trans`` that is general for all calculation modes, such as input parameters and the material's crystal structure.

Configuration data
------------------

Transport calculations are run for various system configurations, i.e. the temperature, chemical potential, and carrier concentration. Information about the configuration(s), are stored in the following attributes:

* :py:attr:`.Trans.temperature`
* :py:attr:`.Trans.chem_pot`
* :py:attr:`.Trans.conc`

All of these attributes are :py:class:`.UnitsDict` objects, which are Python dictionaries with an additional attribute that stores the units. The keys of the dictionary represent the configuration number. The values are floats representing the temperature, chemical potential, or carrier concentration of that configuration.

For example, let's look at the temperatures.

.. code-block :: python

	# Keys are configuration number, values are temperatures
	si_trans.temperature
	>> {1: 150.0, 2: 200.0, 3: 250.0, 4: 300.0, 5: 350.0}
	
	# Units are in Kelvin
	si_trans.temperature.units
	>> 'K'

Please see the section :ref:`physical_quantities` for details on working with :py:class:`UnitsDict` objects.

Transport results
-----------------

The following transport results are stored: 

* :py:attr:`.Trans.cond`
* :py:attr:`.Trans.mob`
* :py:attr:`.Trans.seebeck`
* :py:attr:`.Trans.therm_cond`

All of these attributes are also :py:class:`.UnitsDict` objects. The keys of the dictionary represent the configuration number. The values are 3x3 numpy arrays, which represent the computed tensors for conductivity, mobility, seebeck coefficient, and thermal conductivity.

For example, let's look at the mobilities.

.. code-block :: python

	# Get the mobility tensor for the 4th configuration
	si_trans.mob[4]

	>> array([[ 1.5574091e+03, -6.3873187e-03, -4.9675237e-03],
       [-6.3873187e-03,  1.5574506e+03,  2.4670994e-03],
       [-4.9675237e-03,  2.4670994e-03,  1.5574129e+03]])

    # Get the units
    si_trans.mob.units
    >> 'cm2/V/s'

Please see the section :ref:`physical_quantities` for details on working with :py:class:`UnitsDict` objects.


Plotting the data
~~~~~~~~~~~~~~~~~

Below is an example for plotting the 'xx' component of mobility as a function of temperature.

.. code-block :: python

	import perturbopy.postproc as ppy
	import matplotlib.pyplot as plt
	import numpy as np

	fig, ax  = plt.subplots()

	# Optional
	plt.rcParams.update(ppy.plot_tools.plotparams)

	temperatures = np.array(list(si_trans.temperatures.values()))

	# Get xx components of mobilities
	mobilities = np.array(list(si_trans.mob.values()))[:, 0, 0]

	ax.plot(temperatures, mobilities)

	ax.set_xlabel(f"Temperature ({si_trans.temperature.units})")
	ax.set_ylabel(f"Mobility ({si_trans.mob.units})")

	plt.show()

.. image:: figures/si_mob_vs_T.png
	:width: 450
	:align: center