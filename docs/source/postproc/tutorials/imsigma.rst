Imsigma tutorial
================

.. code-block :: python

	import perturbopy.postproc as ppy

	si_imsigma = ppy.ImsigmaCalcMode.from_yaml('si_imsigma_electron.yml')

Accessing the data
~~~~~~~~~~~~~~~~~~

The imsigma calculation computes the e-ph self-energies for electrons at various k-points and in various bands. To see the electron band information, please see the :doc:bands tutorial. The data is stored analogously in :py:attr:`ImsigmaCalcMode.kpt` and :py:attr:`ImsigmaCalcMode.bands` attributes. For example,

.. code-block :: python
	
	# Access the k-points and units
	si_imsigma.kpt.points
	si_imsigma.kpt.units

	# Access the band energies and units
	si_imsigma.bands.energies
	si_imsigma.bands.units

A typical imsigma calculation computes the e-ph self-energies for multiple configurations, where each configuration corresponds to a temperature, chemical potential, and carrier concentration. The data for each configuration are stored in :py:class:`.ImsigmaConfig` objects that can be accessed by indexing the `si_imsigma` object.

.. code-block :: python
	
	# Access the first configuration of si_imsigma
	si_imsigma[1].temperature
	>> 300.00

	si_imsigma[1].chem_potential
	>> 6.5504824219

	si_imsigma[1].concentration
	>> 9.945835e+17

We can also access the e-ph self energy results, stored in :py:attr:`.ImsigmaConfig.imsigma` as a dictionary. The keys of the dictionary represent the electron band index, and the arrays give the e-ph self energy at that band index for each of the k-points.

.. code-block :: python

	# Access the imsigma results for the first configuration of si_imsigma
	si_imsigma[1].imsigma


Additionally, we can get the e-ph self energies for each phonon mode with :py:attr:`.ImsigmaConfig.imsigma_mode`, which is another dictionary. Each key of the dictionary represents the phonon mode and corresponds to a dictionary similar in format to :py:attr:`.ImsigmaConfig.imsigma`, but only showing the e-ph self energies due to the particular phonon mode.

.. code-block :: python

	# Access the imsigma results for the second phonon mode
	si_imsigma[1].imsigma_mode[2]

Finally, we can use :py:attr:`.ImsigmaCalcMode.units` to see the units of various quantities:

.. code-block :: python
	
	si_imsigma.units

