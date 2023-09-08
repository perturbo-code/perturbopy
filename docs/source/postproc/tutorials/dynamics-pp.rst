Dynamics-run tutorial
=====================

In this section, we describe how to use Perturbopy to process a Perturbo ``dynamics-pp`` calculation.

The ultrafast dynamics calculation solves the real-time Boltzman transport equation (rt-BTE). Please see the `Perturbo website <https://perturbo-code.github.io/mmydoc_dynamics.html>`_ for more details. We first run the Perturbo calculation following the instructions on the Perturbo website and obtain the YAML file, *si_dynamics-pp.yml*. We also obtain the popu HDF5 file *si_popu.h5*, which stores results from the ``dynamics-pp`` calculation too lage to be outputted to the YAML file.