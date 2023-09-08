Trans tutorial
==============

In this section, we describe how to use Perturbopy to process a Perturbo transport calculation. The possible calculation modes are: ``trans``, ``trans-rta``, ``trans-ita``, ``trans-mag-rta``, ``trans-mag-ita``, and ``trans-pp``. Any of these calculation modes can be processed with the :py:class:`.Trans` object described below.

The transport calculation modes solve the Boltzmann transport equation (BTE) to compute the electrical conductivity, carrier mobility tensors as well as the Seebeck coefficient and thermal conductivity. For more information, please refer to the `Perturbo website <https://perturbo-code.github.io/mydoc_interpolation#electronic-bandscalc_mode--phdisp>`_. We first run the Perturbo calculation following the instructions on the Perturbo website (running ``trans-rta`` as an example) and obtain the YAML file, *si_trans-rta.yml*.

Next, we create the :py:class:`.Trans` object using the YAML file as an input. This object contains all of the information from the YAML file.

.. code-block :: python

	import perturbopy.postproc as ppy

	si_trans-rta = ppy.Trans.from_yaml('si_trans-rta.yml')



