"""
   Set up the environment for Perturbo runs.
"""
import os
import shutil


def run_from_config_machine(config_machine, step):
    """
    Check if the executional command defined for the step of computation

    Returns
    -------
    run : str
       string containing a command to run this step

    """

    # Read the perturbo_run variable from the environment
    try:
        run = config_machine['comp_info'][step]['exec']
    except KeyError:
        errmsg = (f'To run {step} as a part of the testsuite,\n'
                  'the exec element must be set in the configurational file.\n'
                  'Example:\n'
                  'exec: srun -n 64 pw.x -npools 8"'
                 )
        raise AttributeError(errmsg)

    return run
    

def create_soft_links(src, dst):
    """
    Create a new folder dst with the same structure as src and files-softlinks
    from src

    Parameters
    ----------
    src : str
        source folder, which will be copied and softlinked
    dst : str
        destination folder, which will be created and where the softlinks wiil be placed
    Returns
    -------
    perturbo_run : str
       string containing a command to run Perturbo

    """
    os.makedirs(dst, exist_ok=True)

    for root, dirs, files in os.walk(src):
        for file in files:
            src_file = os.path.abspath(os.path.join(root, file))
            dst_file = os.path.abspath(os.path.join(dst, os.path.relpath(src_file, src)))
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            os.link(src_file, dst_file)


def perturbo_scratch_dir_config(cwd, perturbo_inputs_dir_path, test_name, config_machine, test_case='perturbo', rm_preexist_dir=True):
    """
    Check if the PERT_SCRATCH variable is written in the config_machine file.
    If not - use default location "/PERT_SCRATCH"

    Parameters
    ----------
    cwd : str
        path to cwd which should be .../perturbopy/tests_f90
    perturbo_inputs_dir_path : str
        folder with all input files for the test
    test_name : str
        name of test
    config_machine : dict
        dictionary with computational information, which we'll use in this set of computations.
    test_case : str
        define what type of the test we run - for perturbo testing or for the
        qe2pert testing.
    rm_preexist_dir : bool
        whether to remove dir if it preexists

    Returns
    -------
    perturbo_scratch_dir : str
        string containing the path to generate dir named tmp_test_name in which
        outputs for test_name will be generated

    """
    # Read the perturbo_run variable from the environment
    perturbo_scratch_dir_prefix   = cwd + "/PERT_SCRATCH"
    try:
        perturbo_scratch_dir_prefix = config_machine['PERT_SCRATCH']
    except KeyError:
        print(f'PSCRATCH not set in the config_machine. using default location -  {perturbo_scratch_dir_prefix}')

    perturbo_scratch_dir = os.path.join(perturbo_scratch_dir_prefix, test_case, test_name)
    if not rm_preexist_dir:
        return perturbo_scratch_dir

    # copy over input files to scratch dir
    src = perturbo_inputs_dir_path
    dst = perturbo_scratch_dir
    if os.path.isdir(dst):
        print(f'\n directory {dst} exists. Removing this directory ...\n')
        shutil.rmtree(dst)
        # create_soft_links(src, dst) - can't use due to restarts, which rewrite the sourse file
        shutil.copytree(src, dst)
    else:
        # create_soft_links(src, dst)
        shutil.copytree(src, dst)
    if test_case == 'qe2pert':
        ephr_name = test_name[:test_name.find('-')]
        ephr_address = os.path.join(perturbo_scratch_dir_prefix, 'ephr_calculation', ephr_name, 'qe2pert')
        file_list = os.listdir(dst)
        for file_name in file_list:
            # Delete previously copied ephr-file
            if file_name.endswith('epwan.h5'):
                os.remove(os.path.join(dst, file_name))
        
        file_list = os.listdir(ephr_address)
        succesfull_copy = False
        for file_name in file_list:
            # Check if the file has the desired format (.h5)
            if file_name.endswith('epwan.h5'):
                # copy from our previous computation to the current computation folder
                source = os.path.abspath(os.path.join(ephr_address, file_name))
                destination = os.path.abspath(os.path.join(dst, file_name))
                os.symlink(source, destination)
                succesfull_copy = True
        if not succesfull_copy:
            raise ValueError(f"Ephr-file for {test_name} wasn't calculated")
                
    return perturbo_scratch_dir
