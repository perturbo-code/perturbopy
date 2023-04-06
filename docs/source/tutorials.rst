Testing Perturbo
================

.. contents::
   :depth: 3

Exporting data to python
------------------------

Perturbopy can be used to export data from a perturbo calculation to Python for further analysis.

.. code-block :: python

	import perturbopy.postproc as ppy

	bands = ppy.BandsCalcMode.from_yaml("pert_output.yml")

.. program-output:: python

	import perturbopy.postproc as ppy

	bands = ppy.BandsCalcMode.from_yaml("pert_output.yml")