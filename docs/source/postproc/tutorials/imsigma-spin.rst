ImsigmaSpin tutorial
====================

In this section, we describe how to use Perturbopy to process a Perturbo ``'imsigma_spin'`` calculation.

The ``'imsigma_spin'`` calculation mode computes the e-ph spin-flip self-energy for a list of electronic crystal momenta. We first run the Perturbo calculation following the instructions on the Perturbo website and obtain the YAML file, *'diam_imsigma_spin.yml'*. For more information, please refer to the `Perturbo website <https://perturbo-code.github.io/mydoc_spin.html#imaginary-part-of-e-ph-spin-flip-self-energycalc_mode--imsigma_spin>`_.

Next, we create the :py:class:`.ImsigmaSpin` object using the YAML file as an input. This object contains all of the information from the YAML file.

.. code-block :: python

    import perturbopy.postproc as ppy

    # Example using the imsigma_spin calculation mode.
    diam_imsigma_spin = ppy.ImsigmaSpin.from_yaml('diam_imsigma_spin.yml')


Accessing the data
------------------

The attributes in an :py:class:`.ImsigmaSpin` object have the same name and format as an object from the :py:class:`.Imsigma`. The main results of the results are categorized below: 

* The k-points for which the e-ph self energies are computed and the corresponding band energies
* Configuration information (temperature, chemical potential, carrier concentration)
* The e-ph self energies for each electronic state, given both in total and by phonon mode

See :ref:`exporting_data` to learn how to access data from ``diam_imsigma_spin`` that is general for all calculation modes, such as input parameters and the material's crystal structure.

Bands data
~~~~~~~~~~

The k-points used for the ``'ephmat_spin'`` calculation are stored in the :py:attr:`.ImsigmaSpin.kpt` attribute, which is of type :py:class:`.RecipPtDB`. For example, to access the k-point coordinates and their units,

.. code-block :: python
  
    # The first k-point (points are stored column-oriented).
    diam_imsigma_spin.kpt.points[:, 0]
    >> array([0.    , 0.25  , 0.2625])

    # The points are in crystal coordinates.
    diam_imsigma_spin.kpt.units
    >> 'crystal'

Please see the section :ref:`handling_kpt_qpt` for more details on accessing information from :py:attr:`.ImsigmaSpin.kpt`, such as labeling the k-points and converting to Cartesian coordinates.

The  band energies are stored in the :py:attr:`.ImsigmaSpin.bands` attribute, which is a :py:class:`.UnitsDict` object. The keys represent the band index, and the values are arrays containing the band energies corresponding to each k-point. 

.. code-block :: python

    # There are two bands used in this calculation.
    diam_imsigma_spin.bands.keys()
    >> dict_keys([1, 2])

    # Band energies of the first band corresponding to the first 10 k-points.
    diam_imsigma_spin.bands[1][:10]
    >> array([17.84019125, 17.75059409, 17.78470674, 17.69665692, 17.81793713,
              17.76517492, 17.67960317, 17.83014117, 17.7809763 , 17.69861557])

Please see the section :ref:`physical_quantities` for details on accessing the bands and their units.

Configuration data
~~~~~~~~~~~~~~~~~~

The ``'imsigma_spin'`` calculations can be run for various system configurations, i.e. the temperature, chemical potential, and carrier concentration. Information about the configuration(s), are stored in the following attributes:

* :py:attr:`.ImsigmaSpin.temper`
* :py:attr:`.ImsigmaSpin.chem_pot`

These attributes are :py:class:`.UnitsDict` objects, which are Python dictionaries with an additional attribute that stores the units. The keys of the dictionary represent the configuration number. The values are floats representing the temperature or chemical potential.

For example, let's look at the temperatures.

.. code-block :: python

    # Keys are configuration number, values are temperatures.
    diam_imsigma_spin.temper
    >> {1: 25.85203}
    
    # Units are in meV.
    diam_imsigma_spin.temper.units
    >> 'meV'

Please see the section :ref:`physical_quantities` for details on working with :py:class:`UnitsDict` objects.

ImsigmaSpin results
~~~~~~~~~~~~~~~~~~~

The e-ph self energies are stored in the :py:attr:`.ImsigmaSpin.imsigma` object, which is of type :py:class:`.UnitsDict`. There are two levels in this dictionary. The first level gives the configuration number. The second level gives the band index. The values are arrays of the e-ph self energies computed along all the k-points, at that configuration and band index.

.. code-block :: python

    # The first key is the configuration number.
    # Here we have one configuration.
    diam_imsigma_spin.imsigma.keys()
    >> dict_keys([1])

    # The second key is the band index. Here we are looking at configuration 1,
    # and we have 2 bands (matching the diam_imsigma_spin.bands attribute).
    diam_imsigma_spin.imsigma[1].keys()
    >> dict_keys([1, 2])

    # The e-ph spin-flip self-energy array for configuration 1 and
    # band index 2. The array size matches the number of k-points.
    diam_imsigma_spin.imsigma[1][2].shape
    >> (815,)

    # The e-ph spin-flip self-energies for configuration 1, band index 2,
    # and the first 4 k-points.
    diam_imsigma_spin.imsigma[1][2][:4]
    >> array([1.29425589e-05, 7.97155145e-06, 1.06093255e-05, 8.78246442e-06])

    # The units are meV.
    diam_imsigma_spin.imsigma.units
    >> 'meV'

We can also get the e-ph spin-flip self energies for each phonon mode through the :py:attr:`.ImsigmaSpin.imsigma_mode` object. This dictionary is similar, but there is an additional level that identifies the phonon mode.

.. code-block :: python

    # The first key is the configuration number.
    diam_imsigma_spin.imsigma_mode.keys()
    >> dict_keys([1])
    
    # The second key is the phonon mode. Here we have 6 modes.
    diam_imsigma_spin.imsigma_mode[1].keys()
    >> dict_keys([1, 2, 3, 4, 5, 6])

    # The third key is the band index. Here we are looking at configuration 1,
    # phonon mode 3, and we see we have 2 bands. Note that this matches
    # the diam_imsigma_spin.bands attribute.
    diam_imsigma_spin.imsigma_mode[1][3].keys()
    >> dict_keys([1, 2])

    # The e-ph spin-flip self-energy array for configuration 1, phonon mode 3,
    # and band index 2. The array size matches the number of k-points.
    diam_imsigma_spin.imsigma_mode[1][3][2].shape
    >> (2445,)

    # The e-ph spin-flip self-energies for configuration 1, phonon mode 3,
    # band index 2, and the first 4 k-points.
    diam_imsigma_spin.imsigma_mode[1][3][2][:4]
    >> array([2.71039146e-06, 0.00000000e+00, 0.00000000e+00, 1.83641809e-06])

    # The units are meV.
    diam_imsigma_spin.imsigma_mode.units
    >> 'meV'
