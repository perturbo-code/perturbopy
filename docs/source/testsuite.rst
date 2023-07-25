Testing Perturbo
================

.. contents::
   :depth: 3

Perturbo package provides two executables: 

1. ``qe2pert.x`` to postprocess the preliminary DFT, DFPT, and Wannier90 calculations and to compute the electron-phonon elements in the Wannier basis stored in the ``prefix_epr.h5`` file.

2. ``perturbo.x`` - the core executable of Perturbo package performing transport calculations, ultrafast dynamics, etc. 

For more details, please read this `Perturbo page <https://perturbo-code.github.io/mydoc_features.html>`_.

To test Perturbo (``qe2pert.x`` and ``perturbo.x`` executables), we provide a testsuite within the `Perturbopy` package. We recommend to run the testsuite:

* to verify that the code runs correctly after download and installation;
* if some modifications to the source code have been made;
* if you would like to contribute to the Perturbo public version

For the Perturbo code download and installation, please refer to `this page <https://perturbo-code.github.io/mydoc_installation.html>`_. Also, you can use and test Perturbo from the `Docker image <https://perturbo-code.github.io/mydoc_docker.html>`_.

Running testsuite
-----------------

Basic run
~~~~~~~~~

We assume that the Python environment is :ref:`activated <Conda activate>` and `Perturbopy` package is :ref:`installed <Installation>`.

Testing ``perturbo.x`` only
+++++++++++++++++++++++++++
If you plan to use (or you did modifications only to) the ``perturbo.x`` executable, the testsuite will automatically run ``perturbo.x`` for several materials and calculation modes and check that the results obtained with the new executable are the same as the reference.

To test the ``perturbo.x`` executable:

1. Modify the *config_machine/config_machine.yml* file:

.. code-block:: python

    PERT_SCRATCH: tmp
    prel_coms:
        - module load perturbo
    comp_info:
        perturbo:
            exec: srun -n 8 perturbo.x -npools 8

Below the meaning of each of the blocks:

* ``PERT_SCRATCH`` is the address of the folder where the auxiliary files in the tests will be located. This is an optional parameter, in case of its absence the ``PERT_SCRATCH`` folder name will be used.
* ``prel_coms`` is a set of commands to be executed *before* the ``perturbo.x`` run. This could be loading packages, specifying any environment variables, etc.
* ``comp_info`` - this block stores information about ``perturbo.x`` computation. It contains the exec field that specifies the execution command taking into account the parallelizaion and other commands specific to a machine.

Once, the ``config_machine.yml`` is set up, navigate to the `perturbopy/tests_f90` folder and run:

.. code-block:: console

   (perturbopy) $ pytest

In the case of successful run of all tests, one will see **<n> passed** as the final line of the output, where <n> is the number of tests. You will also see that some tests have been skipped. This is fine, because the tests for ``qe2pert.x`` are skipped if it's not specified.

By default, the tests wil be run in the *perturbopy/tests_f90/PERT_SCRATCH* directory. If all tests are passed, this directory will be empty after the pytest run. In the case of a failure of one or more tests, the corresponding test folder(s) will be not removed from the *tests_f90/PERT_SCRATCH* directory.

On clusters and supercomputers, the testsuite can be launched both in the interactive mode and as a job. 

Complete test of ``qe2pert.x`` and ``perturbo.x``
+++++++++++++++++++++++++++++++++++++++++++++++++

If you would like to test both ``qe2pert.x`` and ``perturbo.x`` executables, which is recommended after a compilation of the code from scratch or if you have done modifications to ``qe2pert.x``, 
the testuite will consist of three parts:

1. Run ``perturbo.x`` for several materials and calculation modes and check that the results obtained with the new executable are the same as the reference.
2. Perform preliminary *ab initio* calculations from scratch (DFT, DFPT, Wannier90, more on that `here <https://perturbo-code.github.io/mydoc_qe2pert.html>`_), and use ``qe2pert.x`` to get new ``prefix_epr.h5`` files.
3. Run the same calculations as in step 1 again, and compare the outputs of ``perturbo.x`` produced with the new ``prefix_epr.h5`` files with the reference ones.

The step 3 is necessary to test the ``qe2pert.x`` executable because one cannot compare the ``prefix_epr.h5`` files to the reference once directly due to gauge freedom. Therefore, we need to use ``perturbo.x``, whose correctness we confirmed in step 1, to use it to determine whether ``qe2pert.x`` worked correctly. Since there is no need to check all the ``perturbo.x`` tests to verify the work of ``qe2pert.x``, at the third stage we run only three tests for each of the presented ``prefix_epr.h5`` files - ``phdisp``, ``ephmat`` and ``bands``. If these three tests pass, it means that ``qe2pert.x`` works correctly.

By default, the ``qe2pert.x`` testing is disabled as it is more time consuming (!!! indicate time estimation !!!) and requires a user to specify the Quantum Espresso and Wannier90 executables.
To enable the tests of ``qe2pert.x``, activate the ??? option.

Similarly to a simple ``perturbo.x`` tests, the user needs to modify the *config_machine/config_machine.yml* file, but this time the file should include more information.

Copy the template YAML file (check this !!!):

.. code-block:: bash
 
    cd config_machine
    cp config_machine_qe2pert.yml config_machine.yml

The file has the following structure:

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

			
where ``PERT_SCRATCH`` amd ``prel_coms`` are similar to the ``perturbo.x``-only testing. Please note that the ``prel_coms`` will be executed before each of the stages. ``comp_info`` now includes the run commands for each of the stages. If there are preliminary commands to be run *only* before a specific stage, this can be specified by the ``prel_coms`` field within the stage (see example for the ``qe2pert`` run).

.. note::

   The ``config_machine.yml`` must contain information about the execution of each step, which you make during the testing


Parametrization of testsuite
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using the command-line options and environmental variables, one can parametrize running the testsuite:
   
.. option:: -s

   Print output of the testing functions.
   
.. option:: --durations

   Show times for tests and setup and teardown. If `--durations=0`, show all times, if `--durations=1` - for the slowest one, `--durations=2` - for the two slowest, etc.
   
.. option:: --devel

   Additionally run the tests which are in the development stage.
   
.. option:: --tags

   List of tests tags to include in this testsuite run.
   
.. option:: --exclude-tags

   List of tests tags to exclude from this testsuite run.
   
.. option:: --ephr_tags

   List of ephr_tags to include in this testsuite run.
  
.. option:: --exclude-ephr_tags

   List of ephr_tags to exclude from this testsuite run.
   
.. option:: --epwan

   List of epwan files to test.


.. option:: --test-names

   List of test names to include in this testsuite run.
   
.. option:: --run_qe2pert

   Include the ``qe2pert.x`` tests.
   
.. option:: --config_machine

   Name of file with computational information for qe2pert computation. Should be in the folder tests_f90/comp_qe2pert. By default called `config_machine.yml`

.. option:: --keep_perturbo

   Save all the materials related to ``perturbo.x`` tests.

.. option:: --keep_ephr

   Save all ephr-files from the ``qe2pert.x`` testing.
   
.. option:: --keep_preliminary

   Save all preliminary files for ephr files calculations.



Running testsuite on NERSC
--------------------------

In this section, we provide examples to run the testsuite on `NERSC <https://www.nersc.gov>`_. However, for other supercomputers, the commands are similar. 

.. _Job scripts:

The example scripts and job submission files are in the `test_scripts` folder:

* `env_setup_examples.sh`
* `nersc_perlmutter_job_example.slurm`

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

      $ sbatch test_scripts/nersc_perlmutter_job_example.slurm

#. The testsuite output will be written into the `pytest_output` file.

   .. note::
	  The job must be submitted from the `tests_f90` folder and the `perturbopy` environment is not activated manually (it is       activated from the submission script).

Interactive mode
................

Here are the commands to run the Perturbo testsuite on Perlmutter in the `interactive mode <https://docs.nersc.gov/jobs/interactive/>`_.

#. Navigate to the tests folder:

   .. code-block:: console

      $ cd perturbopy/tests

#. Load the ``python`` module:

   .. code-block:: console

      $ module load python

#. Activate the `perturbopy` environment (to create the environment, see :ref:`this page <Conda activate>`)

   .. code-block:: console

      $ conda activate perturbopy

#. Launch the `interactive mode <https://docs.nersc.gov/jobs/interactive/>`_:

   .. code-block:: console

      (perturbopy) $ salloc --nodes 1 --qos interactive --time 01:00:00

#. Run the testsuite:

   .. code-block:: console

      (perturbopy) $ pytest -s

   .. note::

      Don't forget to create configurational file with the set of running commands for your case
	  
	  

Adding new tests
----------------

New tests for ``perturbo.x``
~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to add new tests for existing epwan files, you need to provide the following information:

1. Test folder in format `epwanN-test-name`, where `N` - number of corresponding epwan file. This folder should be saved in the directory `tests_f90/tests_perturbo` and contain:

	* Link to the corresponding epwan file (all files are saved in the folder `/perturbopy/tests_f90/refs_perturbo/epwan_files`);
	* Input file `pert.in`;
	* All necessary computational files for this input;
	* File `pert_input.yml`, that has the following structure:
	.. code-block:: python

	    test info:

	        epwan: epwanN

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
	                abs tol:
	                    - default: value_1

	                qe2pert abs tol:
	                    - default: value_2

	                rel tol:
	                    - default: value_3

	                qe2pert rel tol:
	                    - default: value_4
	                    - keyword: value_5

	The following keys **must be present** in the ``test info`` section of `pert_input.yml` file:

	* ``epwan`` - name of corresponding epwan file;
	* ``desc`` - description of this test;
	* ``test files`` - names of files, for which we make a comparison;
	* ``test keywords`` - which sections of the corresponding file would be checked.

	The following keys **are optional** in the ``test info`` section of `pert_input.yml` file:

	* ``tags`` - tags of this test;
	* ``ignore keywords`` - blocks of the YAML-file with this keys would be ignored during the comparison;
	* ``abs tol``, ``rel tol``, ``qe2pert abs tol``, ``qe2pert rel tol`` - values of the tolerance, with which the result can be accepted as correct. The elements are considerent different if the following equation does not apply:
	.. math::

	   |a - b| \leq (abs\_tol + rel\_tol \times |b|)

	Same is true for the tolerances with `qe2pert` label, but this tolerances are applied on the the second run of ``perturbo.x`` tests. If you want to use a special tolerance for some block, specify it in the corresponding tolerances block with a key corresponding to your block (``keyword`` from the example above)
2. Reference folder in format `epwanN-test-name`, where `N` - number of corresponding epwan file. This folder should be saved in the directory `tests_f90/refs_perturbo` and contain all output files, for which comparison should be done.
3. List the name of the test in the ``epwan_info.yml`` file stored in the ``tests_f90/`` folder. The list of tests is specified in the ``tests`` block of each of the epwan files. If you do not specify your test name there, that test will not be runned.

New tests for ``qe2pert.x``
~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to create a new test with a new epwan file, you will need to perform the following steps:

1. In the `tests_f90/ephr_computation/` folder, you will need to add a folder with the name of your epwan file. We number these folders, so for consistency, we suggest calling it `epwanN`. This folder will contain all the files needed for your epwan file's calculations. This folder should have the following hierarchy:

.. code-block:: python

    pw-ph-wann:
        nscf:
            - nscf.in
        phonon:
            - ph.in
        scf:
            - scf.in
        wann:
            - pw2wan.in
            - prefix.win
        pseudo:
            - Pseudo_1.upf
            - Pseudo_2.upf
    qe2pert:
        - qe2pert.in



Here each subfolder corresponds to one of the calculation steps, plus additionally there is a folder with pseudopotentials. ``Prefix`` in the file ``prefix.win`` should be the same as specified in the ``scf.in`` file. Pseudopotentials also should be the same that enlisted in the ``scf.in`` file.

2. Add information about the epwan file in the ``epwan_info.yml``. Block for each epwan file looks in the following way:

.. code-block:: python

	epwanN:
	   prefix: prefix
	   filename: prefix_epwan.h5
	   SOC: False
	   polar: False
	   description: "Desrciption of this epwan file"
	   pseudopotential: Description of the used pseudopotentials
	   tags:
	      - tag1
	      - tag2
	   tests:
	      - bands
	      - phdisp
	      - ephmat
		  - test4

In general, the name of each block speaks for itself. Note that the list of tests includes ``bands``, ``phdisp`` and ``ephmat``.  These tests **must** be for the new epwan file. These particular tests are run to verify the operation of ``qe2pert.x``. The rest of the tests can be added as you wish.

3. Save your epwan file in the folder `/perturbopy/tests_f90/refs_perturbo/epwan_files`.

3. Add each of the specified tests using the procedure described in the previous subsection.


