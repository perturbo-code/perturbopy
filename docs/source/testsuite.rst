Testing Perturbo
================

.. contents::
   :depth: 3

To test Perturbo (``qe2pert.x`` and ``perturbo.x`` executables), we provide a testsuite within the `perturbopy` package. We recommend to run the testsuite:

* to verify that the code runs correctly after download and installation;
* if some modifications to the source code have been made;
* if you want to commit the changes into the Perturbo project (int this case, this is an obligatory step).

For the Perturbo code download and installation, please refer to `this page <https://perturbo-code.github.io/mydoc_installation.html>`_. Also, you can use and test Perturbo from the `Docker image <https://perturbo-code.github.io/mydoc_docker.html>`_.

Running testsuite
-----------------

Basic run
~~~~~~~~~

We assume that the `pertpy` Python environment is :ref:`activated <Conda activate>` and `perturbopy` is :ref:`installed <Installation>`.

The testuite work consists of three parts:

1. Run ``perturbo.x`` for several configurations of input files and check that the results obtained are the same as the reference;
2. Perform ab initio calculations from scratch (with self-consitent calculation, more on that `here <https://perturbo-code.github.io/mydoc_qe2pert.html>`_), and use ``qe2pert.x`` to get a new epr file;
3. Using the resulting epr files, run the same calculations as in step 1 again, and compare them with the reference ones.

We need step 3 because we have no way to compare the epr files directly due to gauge freedom. Therefore, we need to use ``perturbo.x``, whose correctness we confirmed in step 1, to use it to determine whether ``qe2pert.x`` worked correctly.

At the same time, the ``qe2pert.x`` test can be disabled and not run every time (this calculations are computationally expensive). This is governed by the parameterization of the tests, discussed below.

To be able to run the calculations on a specific device, you need to make changes to the configuration file. You can find it in the ``config_machine`` folder. It is a YAML-file, which structure you can understand by the example:

.. code-block:: python

    PERT_SCRATCH: tmp
    prel_coms:
        - module load perturbo
        - module load qe
    comp_info:
        scf: 
            exec: srun -n 64 pw.x -npools 8
        phonon:
            exec: srun -n 64 ph.x -npools 8
        nscf:
            exec: srun -n 64 pw.x -npools 8
        wannier90:
            exec: srun -n 2 wannier90.x
        pw2wannier90:
            exec: srun -n 1 pw2wannier90.x
        qe2pert:
            prel_coms:
                - export OMP_NUM_THREADS=8
            exec: srun -n 8 qe2pert -npools 8
        perturbo:
            exec: srun -n 8 perturbo.x -npools 8

			
Let's analyze the meaning of each of the blocks:

* ``PERT_SCRATCH`` is the address of the folder where the auxiliary files in the tests will be located. This is an optional parameter, in case of its absence the ``PERT_SCRATCH`` address will be used; 
* ``prel_coms`` is a set of commands to be executed before each of the computational steps. This could be loading packages, specifying any environment variables, and so on;
* ``comp_info`` - this block stores information about each computational step. If you only want to test ``perturbo.x``, you only need a block named ``perturbo``. In the case of full testing, you must prescribe blocks for each of the steps. Each block in ``comp_info`` may contain 2 more blocks - ``prel_coms`` and ``exec``.  The first one also specifies the preliminary commands, but they will be executed before a particular calculation step (optional block). The second one contains how to perform calculations for each step (mandatory block).

.. note::

   The ``config_machine.yaml`` must contain information about the execution of each step, which you make during the stesting


Once, the ``config_machine.yaml`` is set up, navigate to the `perturbopy/tests_f90` folder and run:

.. code-block:: console

   (pertpy) $ pytest

In the case of successful run of all tests, one will see **<n> passed** as the final line of the output, where <n> is the number of tests.

By default, the tests wil be run in the *perturbopy/tests_f90/PERTURBO_SCRATCH* directory. If all tests are passed, this directory will be empty after the pytest run. In the case of a failure of one or more tests, the corresponding test folder(s) will be not removed from the *tests_f90/PERTURBO_SCRATCH* directory.

On clusters and supercomputers, the testsuite can be launched both in the interactive mode and as a job. 

Parametrization of testsuite
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using the command-line options and environmental variables, one can parametrize running the testsuite.

To see a verbose output, run:
   
  
   
.. option:: -s

   Print output of the testing functions.
   
.. option:: --durations

   Show times for tests and setup and teardown. If `--durations=0`, show all times, if `--durations=1` - for the slowest one, `--durations=2` - for the two slowest, etc.
   
.. option:: --devel

   Additionally run the tests in the development stage.
   
.. option:: --tags

   List of tags to include in this testsuite run.
   
.. option:: --exclude-tags

   List of tags to exclude from this testsuite run.
   
.. option:: --ephr_tags

   List of ephr_tags to include in this testsuite run.
  
.. option:: --exclude-ephr_tags

   List of ephr_tags to exclude from this testsuite run.
   
.. option:: --epwan

   List of epwan files to test.


.. option:: --test-names

   List of test folder names to include in this testsuite run.
   
.. option:: --run_qe2pert

   Include the qe2pert tests.
   
.. option:: --config_machine

   Name of file with computational information for qe2pert computation. Should be in the folder tests_f90/comp_qe2pert.

.. option:: --keep_perturbo

   Save all the materials related to perturbo tests.

.. option:: --keep_ephr

   Save all ephr-files from the qe2pert testing.
   
.. option:: --keep_preliminary

   Save all preliminary files for ephr calculation.



Running testsuite on NERSC
--------------------------

In this section, we provide examples to run the testsuite on `NERSC <https://www.nersc.gov>`_. However, for other supercomputers, the commands are similar. 

.. _Job scripts:

The example scripts and job submission files are in the `test_scripts` folder:

* `env_setup_examples.sh`
* `nersc_cori_haswell_job_example.slurm`
* `nersc_cori_knl_job_example.slurm`

.. note::

   Copy and modify these files to make them consistent with your **paths**, 
   number of **MPI tasks**, **OpenMP threads**, **job parameters** etc.
   
.. warning ::

   On NERSC Cori, the testsuite must be run in the $SCRATCH directory (not $HOME).
   The HDF5 file locking must be disabled. 
   Both issues are addressed in the `nersc_cori_knl_job_example.slurm` script.

Job submission
..............

#. Navigate to the tests folder:

   .. code-block:: console

      $ cd perturbopy/tests

#. Modify the submission and environment setup :ref:`scripts <Job scripts>`.

#. Submit the job: 

   .. code-block:: console

      $ # for Cori KNL
      $ sbatch test_scripts/nersc_cori_knl_job_example.slurm
      $
      $ # for Cori Haswell
      $ sbatch test_scripts/nersc_cori_haswell_job_example.slurm

#. The testsuite output will be written into the `pytest_output` file.

Note that the job must be submitted from the `tests` folder and the `pertpy` environment is not activated manually (it is activated from the submission script).

Interactive mode
................

Here are the commands to run the Perturbo testsuite on Cori in the `interactive mode <https://docs.nersc.gov/jobs/interactive/>`_.

#. Navigate to the tests folder:

   .. code-block:: console

      $ cd perturbopy/tests

#. Load the ``python`` module:

   .. code-block:: console

      $ module load python

#. Activate the `pertpy` environment (to create the environment, see :ref:`this page <Conda activate>`)

   .. code-block:: console

      $ conda activate pertpy

#. Launch the `interactive mode <https://docs.nersc.gov/jobs/interactive/>`_:

   .. code-block:: console

      (pertpy) $ # for Cori KNL
      (pertpy) $ salloc -N 1 -C knl -q interactive -t 00:20:00
      (pertpy) $ 
      (pertpy) $ # for Cori Haswell
      (pertpy) $ salloc -N 1 -C haswell -q interactive -t 00:20:00

#. Setup the PERTURBO_RUN variable

   .. code-block:: console

      (pertpy) $ # for Cori KNL
      (pertpy) $ source ./test_scripts/env_setup_examples.sh KNL
      PERTURBO_RUN COMMAND:
      srun -n 4 -c 68 --cpu_bind=cores perturbo.x -npools 4

      (pertpy) $ # for Cori Haswell
      (pertpy) $ source ./test_scripts/env_setup_examples.sh HSW
      PERTURBO_RUN COMMAND:
      srun -n 8 -c 8 --cpu_bind=cores perturbo.x -npools 8

#. Run the testsuite:

   .. code-block:: console

      (pertpy) $ pytest -s

Adding new tests
----------------

* epwan_info
* test folder names
* what is inside folder

Each test must have the pert_input.yml file, that has the following structure:

.. code-block:: python

	test info:
	   executable: perturbo.x

	   epwan: epwan1

	   tags:
	      - tag1
	      - tag2

	   desc:
	      "Test description"

	   test files:
	      pert_output.yml:

	         #only applies to top dict
	         test keywords:
	            - bands

	         #applies to dict at all levels
	         ignore keywords:
	            - input parameters
	            - start date and time
	            - timings

The following keys **must be present** in the ``test info`` section of `pert_input.yml` file:

* ``executable``
* ``epwan``
* ``desc``
* ``test files``
* ``test keywords``

The following keys **are optional** in the ``test info`` section of `pert_input.yml` file:

* ``tags``
* ``ignore keywords``

Also a *tolerance* for the comparison can be optionally specified for each output file in the following way:

.. code-block :: python

      output_file.yml:
         tolerance:
            default:
               1e-10
            key:
               1e-8

where ``output_file.yml`` is the name of an output file (not only a YAML one) and ``key`` referes a keyword of a value of matrix to compare.

