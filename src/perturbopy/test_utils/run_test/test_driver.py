"""
   Run an executable for the testsuite.
"""
import os
import sys
import shlex
import shutil
import subprocess
from perturbopy.io_utils.io import open_yaml
from perturbopy.test_utils.run_test.env_utils import perturbo_run_from_env
from perturbopy.test_utils.run_test.env_utils import perturbo_scratch_dir_from_env
from perturbopy.test_utils.run_test.run_utils import print_test_info
from perturbopy.test_utils.run_test.run_utils import setup_default_tol


def run_perturbo(cwd, perturbo_driver_dir_path,
                 input_name='pert.in', output_name='pert.out'):
    """
    Function to run Perturbo and produce output files

    .. note ::
       The Perturbo run command must be specified in the PERTURBO_RUN environment
       variable. Check the perturbopy/tests/test_scripts/env_setup_examples.sh script
       for examples.


    Parameters
    ----------
    cwd : str
       path of current working directory
    perturbo_driver_dir_path : str
       path to dir with pert.in file
    input_name : str, optional
       name of the input file, default: 'pert.in'
    output_name : str, optional
       name of the output file, default: 'pert.out'

    Returns
    -------
    None

    """

    perturbo_run = perturbo_run_from_env()

    perturbo_run = f'{perturbo_run} -i {input_name} | tee {output_name}'

    os.chdir(perturbo_driver_dir_path)

    print(f'\n ====== Path ======= :\n {os.getcwd()}\n')

    print(f' === Running Perturbo === :\n {perturbo_run}')
    sys.stdout.flush()

    subprocess.run(shlex.split(perturbo_run))

    os.chdir(cwd)


def get_test_materials(test_name):
    """
    Run one test:
       #. run perturbo.x to produce output files
       #. determine paths to files for comparison
       #. associated settings for file comparison with file paths

    Parameters
    ----------
    test_name : str
       name of test

    Returns
    -----
    ref_outs : list
       list of paths to reference files
    new_outs : list
       list of paths to outputted files
    igns_n_tols : list
       list of dictionaries containing the ignore keywords and tolerances needed to performance comparison of ref_outs and new_outs

    """
    # suffixes of paths needed to find driver/utils/references
    inputs_path_suffix = 'tests_perturbo/' + test_name
    ref_data_path_suffix = 'refs_perturbo/' + test_name

    cwd = os.getcwd()

    # determine needed paths
    perturbo_inputs_dir_path = [x[0] for x in os.walk(cwd) if x[0].endswith(inputs_path_suffix)][0]
    work_path                = perturbo_scratch_dir_from_env(cwd, perturbo_inputs_dir_path, test_name)
    ref_path                 = [x[0] for x in os.walk(cwd) if x[0].endswith(ref_data_path_suffix)][0]

    # input yaml for perturbo job
    pert_input = open_yaml(f'{work_path}/pert_input.yml')
    # dictionary containing information about files to check
    test_files = pert_input['test info']['test files']
    # names of files to check
    out_files  = test_files.keys()
    # list of full paths to reference outputs
    ref_outs    = [ref_path + '/' + out_file for out_file in out_files]
    # list of full paths to new outputs
    new_outs    = [work_path + '/' + out_file for out_file in out_files]

    # remove outputs if they already exist
    # WARNING: the output files can sometimes serve as inputs
    # for out_file in new_outs:
    #    if os.path.exists(out_file):
    #       os.remove(out_file)

    # print the test information before the run
    print_test_info(test_name, pert_input)

    # run Perturbo to produce outputs
    run_perturbo(cwd, work_path)

    # list of dict. Each dict contains ignore keywords and
    # tolerances (information about how to compare outputs)
    igns_n_tols = [test_files[out_file] for out_file in out_files]

    igns_n_tols = setup_default_tol(igns_n_tols)

    return (ref_outs,
            new_outs,
            igns_n_tols)


def clean_test_materials(test_name, new_outs):
    """
    clean one test:
       #. removes new files and dirs produced by test

    Parameters
    ----------
    test_name : str
       name of test
    new_outs : list
       list of paths to produced outputs

    Returns
    -----
    None

    """
    # suffixes of paths needed to find driver/utils/references
    inputs_path_suffix = 'tests_perturbo/' + test_name

    cwd = os.getcwd()

    # determine paths
    perturbo_inputs_dir_path = [x[0] for x in os.walk(cwd) if x[0].endswith(inputs_path_suffix)][0]
    work_path                = perturbo_scratch_dir_from_env(cwd, perturbo_inputs_dir_path, test_name, rm_preexist_dir=False)

    if os.path.isdir(work_path):
        print(f'\n === Test {test_name} passed ===\n\n Removing {work_path} ...')
        shutil.rmtree(work_path)

    return None
