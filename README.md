# perturbopy - Python suite for Perturbo postprocessing and testing

This package provides utilities to postprocess and test the Perturbo code, which is an open-source software to compute from first principles the scattering processes between charge carriers (electrons and holes) and phonons, defects, and photons in solid state materials, including metals, semiconductors, oxides, and insulators. Perturbo is written in modern Fortran, including efficient MPI and OpenMP parallelization, allowing to perform calculations efficient on supercomputers using up to ~100,000 cores. Read more about the main code Perturbo [here](https://perturbo-code.github.io/index.html).

Perturbopy provides a user-friendly object-oriented environment to postprocess Perturbo calculations, such as band structure interpolation, electron transport, ultrafast carrier dynamics, and many more. Using Perturbopy, a user can easily load the Perturbo output files (HDF5 or YAML) into Python objects, perform calculations, and visualize data.

The second purpose of the Perturbopy package is to test the main Perturbo code. After a compilation of the Perturbo code on a new machine or after a new implementation, it is always a good practice to run the testsuite, verifying that the existing functionality was not affected, and add new test cases to ensure that the newly implemented features will be compatible with future implementations. Perturbopy, using the `pytest` package, provides extensive testing of Perturbo, allowing for both serial and parallel runs.

Find more about Perturbopy on its [documentation website](https://perturbopy.readthedocs.io). We are open to collaboration! Please create a fork and submit a pull request with detailed description of your work, and we will be happy to discuss and include your contribution.



