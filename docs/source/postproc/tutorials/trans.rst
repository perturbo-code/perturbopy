Trans tutorial
==============

.. code-block :: python

	import perturbopy.postproc as ppy

	si_trans = ppy.TransCalcMode.from_yaml('si_trans_ita_electron.yml')

Accessing the data
~~~~~~~~~~~~~~~~~~

A typical transport calculation solves the BTE for several different configurations, where each configuration corresponds to a temperature, chemical potential, and carrier concentration. The data for each configuration are stored in :py:class:`.TransConfig` objects that can be accessed by indexing the `si_trans` object.

.. code-block :: python
	
	# Access the first configuration of si_trans
	si_trans[1].temperature
	>> 300.00

	si_trans[1].chem_potential
	>> 6.5504824219

	si_trans[1].concentration
	>> 9.945835e+17

We can also access the results with :py:attr:`.TransConfig.conductivity`, :py:attr:`.TransConfig.mobility`, :py:attr:`.TransConfig.seebeck_coeff`, and :py:attr:`.TransConfig.thermal_conductivity`. These are all stored as tensors; i.e.  For example, here are the results for the conductivity tensor:

.. code-block :: python

	# Access the conductivity results for the first configuration of si_trans
	si_trans[1].conductivity
	>> [[ 2.5389272e+04 -3.1056698e-02 -2.0778462e-01]
		[-3.1056698e-02  2.5390489e+04  5.9898721e-02]
		[-2.0778462e-01  5.9898721e-02  2.5389500e+04]]

	# Access the 'xy' component
	si_trans[1].conductivity[0, 1]


Additionally, if we are using ITA rather than RTA, we can access the convergence of the conductivity tensor for each iteration of solving the BTE. 

.. code-block :: python

	# Get the conductivity at each iteration of the BTE
	si_trans[1].conductivity_iter

	>> {1: array([[ 2.4817300e+04, -1.0178186e-01, -7.9157444e-02],
       [-1.0178186e-01,  2.4817960e+04,  3.9313206e-02],
       [-7.9157444e-02,  3.9313206e-02,  2.4817360e+04]]), 2: array([[ 2.5288733e+04, -2.5526387e-02, -1.2887813e-01],
       [-2.5526387e-02,  2.5289902e+04,  5.8570355e-02],
       [-1.2887813e-01,  5.8570355e-02,  2.5288974e+04]]), 3: array([[ 2.5401491e+04, -3.4944053e-02, -2.0791663e-01],
       [-3.4944053e-02,  2.5402694e+04,  5.9040028e-02],
       [-2.0791663e-01,  5.9040028e-02,  2.5401714e+04]]), 4: array([[ 2.5389272e+04, -3.1056698e-02, -2.0778462e-01],
       [-3.1056698e-02,  2.5390489e+04,  5.9898721e-02],
       [-2.0778462e-01,  5.9898721e-02,  2.5389500e+04]])}

Finally, we can use :py:attr:`.TransCalcMode.units` to see the units of various quantities:

.. code-block :: python
	
	si_trans.units

	>> {'temperature': 'K', 'chemical potential': 'eV', 'concentration': 'cm-3', 'conductivity': '1/Ohm/m', 'mobility': 'cm2/V/s', 'Seebeck coefficient': 'mV/K', 'thermal conductivity': 'W/m/K'}

It is often convenient to get an array of all the temperatures, all the mobilities, etc. In this case, we can use the ``:py:meth:.TransCalcMode.get_temperatures()`` method.

To do: plotting, plotting with experiments, finalize data storage, units conversion 