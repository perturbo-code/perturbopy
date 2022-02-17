# perturpy
Suite of Python scripts for Perturbo testing and postprocessing 

To do:
* testsuite (that can be launched as a separate script)
* read and print data and system from epwan
* plot band structure/phonon dispersion
* read plot the cdyna HDF5

Quick Start (how to run tests):
* navigate to perturbopy/
$ pip install .
* start an interactive mode (if you use tempo run the following and naviagte back to perturbopy/)
$ qsub -I test perturbopy/tests/test_utils/tempo.pbs
* navigate to perturbopy/tests
$ cd perturbopy/tests
* run pytest
$ pytest
* To run a specific test just pass the file as an arg
$ pytest test_epwan-setup.py
