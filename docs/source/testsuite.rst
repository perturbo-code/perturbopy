Testing Perturbo
================

To test Perturbo (``perturbo.x`` executable), we provide a testsuite within the `perturbopy` package. We recommend to run the testsuite:

* to verify that the code runs correctly after download and installation
* if some modifications to the source code have been made.

For the Perturbo code download and installation, please refer to `this page <https://perturbo-code.github.io/mydoc_installation.html>`_.

Running testsuite
-----------------

We assume that the `pertpy` Python environment is :ref:`activated <Conda activate>` and `perturbopy` is :ref:`installed <Installation>`.

The testsuite automatically launches the Perturbo executable and verifies that the produced output is the same as the reference output produced beforehand. Therefore, the testsuite must have access to the Perturbo executable. This is done through the PERTURBO_RUN environmental variable.

.. note::

   The PERTURBO_RUN environmental variable must be set before running the testsuite.

Here are the examples to set the PERTURBO_RUN environmental variable:

.. code-block:: console

   (pertpy) $ # for sequential runs:
   (pertpy) $ export PERTURBO_RUN='<path>/perturbo.x'

   (pertpy) $ # for MPI (+OpenMP)
   (pertpy) $ export PERTURBO_RUN='mpirun -np 4 <path>/perturbo.x -npools 4'

Once, the PERTURBO_RUN variable is set up, navigate to the `perturbopy/tests` folder and run:

.. code-block:: console

   (pertpy) $ pytest

To see a verbose output, run:

.. code-block:: console

   (pertpy) $ pytest -s

On clusters and supercomputers, the testsuite can be launched both in the interactive mode and as a job. 

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

The following keys **must be present** in the ``test info`` section of `pert_input.yml` file:

* ``executable``
* ``epwan``
* ``desc``
* ``test files``

The following keys **are optional** in the ``test info`` section of `pert_input.yml` file:

* ``tags``

Also a *tolerance* for the comparison can be optionally specified in the following way:

.. code-block :: python

      output_file.yml:
         tolerance:
            default:
               1e-10
            key:
               1e-8

where ``key`` referes a keyword of a value of matrix to compare.

