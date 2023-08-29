Ephmat tutorial
===============

.. code-block :: python

	import perturbopy.postproc as ppy

	si_ephmat = ppy.EphmatCalcMode.from_yaml('si_ephmat.yml')

Accessing the data
~~~~~~~~~~~~~~~~~~

The ephmat calculation computes the e-ph elements between electrons in states defined by a k-point and band index, and phonons in states defined by . To see the electron band information, please see the :doc:bands tutorial. The data for the phonons is stored analogously in :py:attr:`EphmatCalcMode.qpt` and :py:attr:`EphmatCalcMode.phdisp` attributes. For example,

.. code-block :: python
	
	# Access the k-points, q-points and units
	si_ephmat.kpt.points
	si_ephmat.kpt.units

	si_ephmat.qpt.points
	si_ephmat.qpt.units

	# Access the band energies and units
	si_ephmat.phdisp.energies
	si_ephmat.phdisp.units

The ephmat calculation interpolates the deformation potentials and e-ph elements which are stored in dictionaries :py:attr:`EphmatCalcMode.defpot` and :py:attr:`EphmatCalcMode.ephmat`, respectively. The keys represent the phonon mode, and the values are the elements (these are flattened to a 1d array if the number of k-points and number of q-points are both greater than one)

.. code-block :: python
	si_ephmat.ephmat
	si_ephmat.defpot