Imsigma tutorial
================

In this section, we describe how to use Perturbopy to process a Perturbo imsigma calculation.

The imsigma calculation mode computes the e-ph self-energy for a list of electronic crystal momenta. We first run the Perturbo calculation following the instructions on the Perturbo website and obtain the YAML file, *'si_imsigma.yml'*. For more information, please refer to the `Perturbo website <https://perturbo-code.github.io/mydoc_scattering.html#imaginary-part-of-e-ph-self-energycalc_mode--imsigma>`_.

Next, we create the :py:class:`.Imsigma` object using the YAML file as an input. This object contains all of the information from the YAML file.

.. code-block :: python

    import perturbopy.postproc as ppy

    # Example using the imsigma calculation mode
    si_imsigma = ppy.Imsigma.from_yaml('si_imsigma.yml')


Accessing the data
------------------

The main results of the results are categorized below: 

* the k-points the e-ph self energies are computed for and the band energies corresponding to these k-points
* information defining the configuration of the imsigma calculation (temperature, chemical potential, carrier concentration)
* The e-ph self energies for each electronic state, given in total and broken up by phonon mode

See :ref:`exporting_data` to learn how to access data from ``si_imsigma`` that is general for all calculation modes, such as input parameters and the material's crystal structure. # ERROR

Bands data
~~~~~~~~~~

The k-points used for the bands calculation are stored in the :py:attr:`.Imsigma.kpt` attribute, which is of type :py:class:`.RecipPtDB`. For example, to access the k-point coordinates and their units:

.. code-block :: python
  
  si_imsigma.kpt.points[:, 0]

  >> array([0.    , 0.2875, 0.3   ])

  si_imsigma.kpt.units

  >> 'crystal'

Please see the section :ref:`handling_kpt_qpt` for details on accessing the k-points through this attribute.

The  band energies are stored in the :py:attr:`.Imsigma.bands` attribute, which is a :py:class:`.UnitsDict` object. The keys represent the band index, and the values are arrays containing the band energies corresponding to each k-point. 

.. code-block :: python

  si_imsigma.bands.keys()
  >> dict_keys([1, 2])

  si_imsigma.bands[1][:10]
  >> array([6.95536966, 6.91545084, 6.93285883, 6.89499322, 6.9498133 ,
       6.92969695, 6.89402423, 6.96254005, 6.94493518, 6.91144529])

Please see the section :ref:`physical_quantities` for details on accessing the bands and their units.

Configuration data
~~~~~~~~~~~~~~~~~~

Imsigmaport calculations are run for various system configurations, i.e. the temperature, chemical potential, and carrier concentration. Information about the configuration(s), are stored in the following attributes:

* :py:attr:`.Imsigma.temper`
* :py:attr:`.Imsigma.chem_pot`

All of these attributes are :py:class:`.UnitsDict` objects, which are Python dictionaries with an additional attribute that stores the units. The keys of the dictionary represent the configuration number. The values are floats representing the temperature or chemical potential.

For example, let's look at the temperatures.

.. code-block :: python

    # Keys are configuration number, values are temperatures
    si_imsigma.temperature
    >> {1: 25.85203}
    
    # Units are in meV
    si_imsigma.temperature.units
    >> 'meV'


Please see the section :ref:`physical_quantities` for details on working with :py:class:`UnitsDict` objects.

Imsigma results
~~~~~~~~~~~~~~~

The e-ph self energies are stored in the :py:attr:`.Imsigma.imsigma` object, which is of type :py:class:`.UnitsDict`. There are two levels in this dictionary. The first level gives the configuration number. The second level gives the band index. The values are arrays of the e-ph self energies computed along all the k-points, at that configuration and band index.

.. code-block :: python

	# The first key is the configuration number. Here we have one configuration.
	si_imsigma.imsigma.keys()
	>> dict_keys([1])

	# The second key is the band index. Here we are looking at configuration 1, and we have 2 bands (matching the si_imsigma.bands attribute)
	si_imsigma.imsigma[1].keys()
	>> dict_keys([1, 2])

	# The e-ph self energy array for configuration 1 and band index 2.
	# There are 450 values in the array because we have 450 k-points.
	si_imsigma.imsigma[1][1].shape
	>> (450,)

	# The e-ph self energies for configuration 1, band index 2, and the first 5 k-points
	si_imsigma.imsigma[1][1][:5]
	>> array([12.37084914, 11.40051791, 12.08165333, 11.20097615, 12.26688231])

	# The units are meV
	si_imsigma.imsigma.units
	>> 'meV'


.. code-block :: python

	# The first key is the configuration number. Here we have one configuration.
	si_imsigma.imsigma_mode.keys()
	>> dict_keys([1])
	
	# The second key is the phonon mode. Here we have 6 modes for configuration 1.
	si_imsigma.imsigma_mode[1].keys()
	>> dict_keys([1, 2, 3, 4, 5, 6])

	# The third key is the band index. Here we are looking at configuration 1, phonon mode 3, and we see
	# we have 2 bands (matching the si_imsigma.bands attribute)
	si_imsigma.imsigma_mode[1][3].keys()
	>> dict_keys([1, 2])

	# The e-ph self energy array for configuration 1, phonon mode 3, and band index 2.
	# There are 450 values in the array because we have 450 k-points.
	si_imsigma.imsigma_mode[1][3][2].shape
	>> (450,)

	# The e-ph self energies for configuration 1, phonon mode 3, band index 2, and the first 5 k-points
	si_imsigma.imsigma_mode[1][3][2][:5]
	>> array([18.14712596, 20.83056571, 20.4743665 , 21.94419049, 20.38251006])

	# The units are meV
	si_imsigma.imsigma_mode.units
	>> 'meV'