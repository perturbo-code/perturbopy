Testing Perturbo
================

.. contents::
   :depth: 3

General information
-------------------

Perturbo package provides two executables: 

1. ``qe2pert.x`` to postprocess the preliminary DFT, DFPT, and Wannier90 calculations and to compute the electron-phonon matrix elements in the Wannier basis stored in the ``prefix_epr.h5`` file.

2. ``perturbo.x`` - the core executable of Perturbo package performing transport calculations, ultrafast dynamics, etc. 

For more details, please read this `Perturbo page <https://perturbo-code.github.io/mydoc_features.html>`_.

To test this executables, we provide a testsuite within the `Perturbopy` package. We recommend to run the testsuite:

* to verify that the code runs correctly after download and installation;
* if some modifications to the source code have been made;
* if you would like to contribute to the Perturbo public version (in this situation, new test cases are also required).

For the Perturbo code download and installation, please refer to `this page <https://perturbo-code.github.io/mydoc_installation.html>`_. Also, you can use and test Perturbo from the `Docker image <https://perturbo-code.github.io/mydoc_docker.html>`_.

Running testsuite
-----------------

Basic run
~~~~~~~~~

We assume that the Python environment is :ref:`activated <Conda activate>` and `Perturbopy` package is :ref:`installed <Installation>`.

To run testsuite you need a folder with input files, reference files, configuration files, etc. You can find an example of such a `tests` folder in the `perturbo repository <https://github.com/perturbo-code/perturbo/tree/master/tests>`_..  We advise you to use this set of files for initial testing. Below we assume that you have downloaded this folder and work with it.

Testing ``perturbo.x`` only
+++++++++++++++++++++++++++
If you plan to use (or you did modifications only to) the ``perturbo.x`` executable, the testsuite will automatically run ``perturbo.x`` for several materials and calculation modes and check that the results obtained with the new executable are the same as the reference.

To test the ``perturbo.x`` executable you need to make the configuration file. As an example, in the *tests/config_machine* folder, you can take the *config_machine_perturbo.yml* file. This file contains basic information about running tesuite for ``perturbo.x``. 

1. Copy the template YAML file inside the *tests/config_machine* folder:

.. code-block:: python

    cd config_machine
    cp config_machine_perturbo.yml config_machine.yml
	
By default, the file named *config_machine.yml* is the one called by the program. If you want to use a file with a different name, you can use one of the `command-line options`_.

2. Make changes to the configuration file. By default, the *config_machine_perturbo.yml* file is as follows:

.. code-block:: python

    PERT_SCRATCH: tmp
    prel_coms:
        - module load perturbo
        - export OMP_NUM_THREADS=8
    comp_info:
        perturbo:
            exec: srun -n 8 perturbo.x -npools 8

Below the meaning of each of the blocks:

* ``PERT_SCRATCH`` is the address of the folder where the auxiliary files in the tests will be located. 
* ``prel_coms`` is a set of commands to be executed *before* the ``perturbo.x`` run. This could be loading packages, specifying any environment variables, etc. Enter every command as a separate line preceded by a hyphen, respecting the file indentation.
* ``comp_info`` - this block contains information about the ``perturbo.x`` computation. It has the ``exec`` field that specifies the run command taking into account the parallelization and other machine specifics. In this example, ``perturbo.x`` will be ran with the SLURM srun command using 8 MPI tasks.


Once, the ``config_machine.yml`` is set up, navigate to the `tests` folder and run:

.. code-block:: console

   (perturbopy) $ ./run_tests.py
   
This script will automatically load and run all the tests from the `perturbopy` package.

By default, in the case of successful run of all tests one will see **<n> passed** as the final line of the output, where <n> is the number of tests. You will also see that some tests have been skipped. This is fine, because the tests for ``qe2pert.x`` are skipped if it's not specified.

If all tests are passed, the `PERT_SCRATCH/perturbo` directory will be empty after the ``./run_tests.py`` execution. In the case of a failure of one or more tests, the corresponding test folder(s) kept in the ``PERT_SCRATH/perturbo`` directory.

.. _test-complete:

Complete test of ``qe2pert.x`` and ``perturbo.x``
+++++++++++++++++++++++++++++++++++++++++++++++++

If you would like to test both ``qe2pert.x`` and ``perturbo.x`` executables, which is recommended after a compilation of the code from scratch or if you have done modifications to ``qe2pert.x``, 
the testsuite will consist of three parts:

1. Test ``perturbo.x`` (similar to the section above).
2. Download results of preliminary *ab initio* calculations (DFT, DFPT, Wannier90, more on that `here <https://perturbo-code.github.io/mydoc_qe2pert.html>`_) from the cloud, and use ``qe2pert.x`` to generate new ``prefix_epr.h5`` files.
3. Run part of the calculations from step 1 again, and compare the outputs of ``perturbo.x`` produced with the new ``prefix_epr.h5`` files. 

The step 3 is necessary to test the ``qe2pert.x`` executable because one cannot compare the ``prefix_epr.h5`` files to the reference ones directly due to gauge freedom. Therefore, we need to use ``perturbo.x``, whose correctness we confirmed in step 1, to use it to determine whether ``qe2pert.x`` worked correctly. Since there is no need to check all the ``perturbo.x`` tests to verify the work of ``qe2pert.x``, at the third stage we run only three claculation modes of Perturbo for each ``prefix_epr.h5`` file: ``phdisp``, ``ephmat`` and ``bands``. If these three tests pass, it means that ``qe2pert.x`` works correctly.

By default, the ``qe2pert.x`` testing is disabled, because the programs associated with this executable are rarely modified, and also these tests require additional files to be downloaded from the cloud.

To enable the tests of ``qe2pert.x``, activate the ``--run_qe2pert`` option:

.. code-block:: console

   (perturbopy) $ ./run_tests.py --run_qe2pert

Similarly to ``perturbo.x``-only tests, the user needs to make a new the *config_machine/config_machine.yml* file, but this time the file should include more information. As a reference, you can take file  *config_machine_qe2pert.yaml*.

1. Make your copy of the template YAML file:

.. code-block:: bash
 
    cd config_machine
    cp config_machine_qe2pert.yml config_machine.yml

2. Update the *config_machine.yml*  file for your specific case. By default,  the file has the following structure:

.. code-block:: python

    PERT_SCRATCH: tmp
	source_link: https://caltech.box.com/shared/static/3xj9sknmt75aho66eyad1wwa6dat4s0d.zip
    prel_coms:
        - module load perturbo
    comp_info:
        qe2pert:
            prel_coms:
                - export OMP_NUM_THREADS=8
            exec: srun -n 8 qe2pert -npools 8
        perturbo:
            prel_coms:
                - export OMP_NUM_THREADS=8
            exec: srun -n 8 perturbo.x -npools 8

			
where ``PERT_SCRATCH`` and ``prel_coms`` are similar to the ``perturbo.x``-only testing. Please note that the ``prel_coms`` (the top one) will be executed before each of the stages. An additional parameter here is ``source_link``, which defines where all auxiliary files for testing ``qe2pert.x`` should be downloaded from. The archive with the files is small (~400 MB), but comparable to the size of the main perturbo code and is not used regularly, so it was decided to keep it apart. ``comp_info`` now includes the run commands for ``perturbo.x`` and ``qe2pert.x`` stages. If there are preliminary commands to be run *only* before a specific stage, this can be specified by the ``prel_coms`` field within the stage (see examples for the ``qe2pert`` and ``perturbo`` runs in the YAML file).

On clusters and supercomputers, the testsuite can be launched both in the interactive mode and as a job. 

Parameterization of testsuite
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using the command-line options and environmental variables, one can parametrize running the testsuite:
   
.. option:: -s

   Print output of the testing functions.
   
.. option:: --durations

   Show times for tests and setup and teardown. If `--durations=0`, show all times, if `--durations=1` - for the slowest one, `--durations=2` - for the two slowest, etc.
   
.. option:: --source_folder

   Address of the folder with all reference files for the test performance. By default equal to ``./``.
   
.. option:: --tags

   List of tests tags to include in this testsuite run.
   
.. option:: --exclude-tags

   List of tests tags to exclude from this testsuite run.
   
.. option:: --epr_tags

   List of tags of the epr files to include in this testsuite run.
  
.. option:: --exclude-epr_tags

   List of tags of the epr files to exclude from this testsuite run.
   
.. option:: --epr

   List of epr files to test. If the option is not specified, all the available epr files will be included in testing.


.. option:: --test-names

   List of test names to include in this testsuite run, e.g., epr1_bands, etc.
   
.. option:: --run_qe2pert

   Include the ``qe2pert.x`` tests. See :ref:`test-complete`.
   
   .. _command-line options:
.. option:: --config_machine
	
   Name of file containing the run commands for Perturbo and, in case of ``qe2pert.x`` test, for Quantum Espresso, Wannier90. Should be in the folder `tests/config_machine`. By default equal to `config_machine.yml`.

.. option:: --keep_perturbo

   Save all the materials related to ``perturbo.x`` tests.

.. option:: --keep_epr

   Save all epr-files from the ``qe2pert.x`` testing.


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
~~~~~~~~~~~~~~

#. Navigate to the tests folder:

   .. code-block:: console

      $ cd perturbopy/tests

#. Modify the submission and environment setup :ref:`scripts <Job scripts>`.

#. Submit the job: 

   .. code-block:: console

      $ sbatch test_scripts/nersc_perlmutter_job_example.slurm

#. The testsuite output will be written into the `pytest_output` file.

   .. note::
	  The job must be submitted from the `tests` folder and the `perturbopy` environment is not activated manually (it is       activated from the submission script).

Interactive mode
~~~~~~~~~~~~~~~~

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

      Don't forget to create configurational file with the set of running commands for your case.
	  
	  

Making new tests
----------------

Modifications of code and new tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you make changes to the ``perturbo`` source code, you **must** not only check the performance of existing tests, but also write new ones. The required tests depend on the specific case:

1. You modified `pert-src`, which affected ``perturbo.x`` behavior and this can be tested used the `existing` epr file. Than you need to `add new test`_.

2. Same modification type as in 1 (You modified `pert-src`, which affected ``perturbo.x``), but you need `another` epr file to test this. Than you need to `add new epr`_ with the set of tests for it.

3. You modified `qe2pert-src`, which affected ``qe2pert.x``. In this case, you also need to `add new epr`_ with the set of tests for it.

.. _add new test:

Add new test
~~~~~~~~~~~~

If you want to add new tests for existing epr files, you need to provide the following information:

1. Test folder in format `eprN-test-name`, where `N` - number of corresponding epr file. This folder should be saved in the directory `tests/tests_perturbo` and contain:

* Link to the corresponding epr file (all files are saved in the folder `/tests/refs_perturbo/epr_files`);
* Input file `pert.in`;
* All necessary computational files for this input;
* File `pert_input.yml`, that has the following structure:
.. code-block:: python

    test info:

        epr: eprN

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
                    - ignore_key1
                    - ignore_key2
                
                abs tol:
                    - default: value_1

                qe2pert abs tol:
                    - default: value_2

                rel tol:
                    - default: value_3

                qe2pert rel tol:
                    - default: value_4
                    - keyword1: value_5

The following keys **must be present** in the ``test info`` section of `pert_input.yml` file:

* ``epr`` - name of corresponding epr file;
* ``desc`` - description of this test;
* ``test files`` - names of the output files, for which we make a comparison, file type must be YAML or HDF5;
* ``test keywords`` - which sections of the corresponding file would be checked.

The following keys **are optional** in the ``test info`` section of `pert_input.yml` file:

* ``tags`` - tags of this test;
* ``ignore keywords`` - blocks of the YAML-file with this keys would be ignored during the comparison;
* ``abs tol``, ``rel tol``, ``qe2pert abs tol``, ``qe2pert rel tol`` - values of the tolerance, with which the result can be accepted as correct. The elements are considered different if the following equation does not apply:
.. math::

   |a - b| \leq (abs\_tol + rel\_tol \times |b|)

Same is true for the tolerances with the `qe2pert` label, but these tolerances are applied on the the second run of ``perturbo.x`` tests. If you want to use a special tolerance for some block, specify it in the corresponding tolerances with a corresponding key (``keyword1`` from the example above).

2. Reference folder in format `eprN-test-name`, where `N` - number of corresponding epr file. This folder should be saved in the directory `tests/refs_perturbo` and contain all output files, for which comparison should be done.

3. List the name of the test in the ``epr_info.yml`` file stored in the ``tests/`` folder. The list of tests is specified in the ``tests`` block of each of the epr files. If you do not specify your test name there, that test will not be runned.

.. note::

    The output file extensions for the testsuite must be YAML or HDF5.

.. _add new epr:

Add new epr-files
~~~~~~~~~~~~~~~~~

If you want to create a new test with a new epr file, you will need to perform the following steps:

1. In the `tests/epr_computation/` folder, you will need to add a folder with the name of your epr file. We enumerate these folders, so for consistency, we suggest calling it `eprN`. This folder will contain all the files needed for your epr file's calculations. This folder should have the following hierarchy:

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



Here each subfolder corresponds to one of the calculation steps, plus additionally there is a folder with pseudopotentials. ``prefix`` in the file ``prefix.win`` should be the same as specified in the ``scf.in`` file. Pseudopotentials also should be the same as enlisted in the ``scf.in`` file. We need all this information to be able to generate all the auxiliary files for ``qe2pert.x``.

2. Add information about the epr file in the ``epr_info.yml``. Block for each epr file looks in the following way:

.. code-block:: python

	eprN:
	   prefix: prefix
	   filename: prefix_epr.h5
	   SOC: False
	   polar: False
	   description: "Description of this epr file"
	   pseudopotential: Description of the used pseudopotentials
	   tags:
	      - tag1
	      - tag2
	   tests:
	      - bands
	      - phdisp
	      - ephmat
	      - test4

In general, the name of each block speaks for itself. Note that the list of tests includes ``bands``, ``phdisp`` and ``ephmat``.  These ``perturbo.x`` calculation mode tests **must** be created for the new epr file. These particular tests are run to verify the operation of ``qe2pert.x``. More tests for a given epr file can be optionally added.

3. Save your epr file in the folder `/tests/refs_perturbo/epr_files`.

4. Provide the supplementary files, which are used for the ``qe2pert.x`` calculations, to the code developers. We need to add them to the current cloud storage in order to be able to download all of them at once from the one place. 

5. Add each of the specified tests using the procedure described in the previous subsection.

.. note::

    The new ``perturbo.x`` or ``qe2pert.x`` tests must cover all of the new functionality that you added to the code. At the same time, new test cases should not significantly increase the runtime. We advise using very small grids, etc., which could result in physically incorrect outcome, however, this will still serve the purpose of testing the new functionality of the code.
