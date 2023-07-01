"""
   Set up the environment for Perturbo runs.
"""
import os
import shutil


def run_from_config_machine(config_machine, step):
    """
    Check if the executional command defined for the step of computation
    
    Parameters
    ----------
    config_machine : dict
        dictionary with executional commands for the test steps
    step : str
        name of running step ('scf', 'nscf', etc.)
    Returns

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
    

def copy_folder_with_softlinks(src, dst, perturbo_scratch_dir_prefix=None, test_name=None, second_run=False):
    """
    Copy the src directory to the dst directory, except the ephr file - for it softlink is created.

    Parameters
    ----------
    src : str
        folder with computational info, which is copied
    
    dst : str
        folder, where the files will be copied

    perturbo_scratch_dir_prefix : str or None
        path to the scratch folder with computational files and results, None by default

    test_name : str or None
        name of test, None by default
    second_run : bool
        check that this is second run of perturbo (for qe2pert testing)

    Returns
    -------
    None
    """
    os.makedirs(dst)

    # Get the list of files in the source folder
    for root, dirs, files in os.walk(src):
        
        # Determine the relative path of the current directory
        relative_path = os.path.relpath(root, src)
        
        # Create the corresponding subdirectory in the destination folder
        dst_subfolder = os.path.join(dst, relative_path)
        if not os.path.exists(dst_subfolder):
            os.makedirs(dst_subfolder)

        for file_name in files:
            src_file_path = os.path.join(root, file_name)
            dst_file_path = os.path.join(dst_subfolder, file_name)

            if file_name.endswith("epwan.h5"):
                # Create a softlink for files ending with "epwan.h5"
                if not second_run:
                    # if it's first run of perturbo - simply make softlink of file
                    os.symlink(src_file_path, dst_file_path)
                else:
                    # if it's second run - softlink the file from our previous calculations
                    softlink_ephr_files(perturbo_scratch_dir_prefix, test_name, dst_file_path, file_name)
            else:
                # Copy other files
                shutil.copy2(src_file_path, dst_file_path)
                


def perturbo_scratch_dir_config(cwd, perturbo_inputs_dir_path, test_name, config_machine, test_case='perturbo', rm_preexist_dir=True):
    """
    Check if the PERT_SCRATCH variable is written in the config_machine file.
    If not - use default location "/PERT_SCRATCH".
    After it, this programm make the copy from folder with tests from either ephr_computation or tests_perturbo folder.
    

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

    # if folder already exist and we don't want to change it - simply pass rest of the function
    perturbo_scratch_dir = os.path.join(perturbo_scratch_dir_prefix, test_case, test_name)
    if not rm_preexist_dir:
        return perturbo_scratch_dir

    # else - copy over input files to scratch dir
    src = perturbo_inputs_dir_path
    dst = perturbo_scratch_dir
    if os.path.isdir(dst):
        print(f'\n directory {dst} exists. Removing this directory ...\n')
        shutil.rmtree(dst)
        if test_case == 'perturbo' or test_case == 'ephr_calculation':
            copy_folder_with_softlinks(src, dst)
        elif test_case == 'perturbo_for_qe2pert':
            copy_folder_with_softlinks(src, dst, perturbo_scratch_dir_prefix, test_name, second_run=True)
        # shutil.copytree(src, dst)
    else:
        if test_case == 'perturbo' or test_case == 'ephr_calculation':
            copy_folder_with_softlinks(src, dst)
        elif test_case == 'perturbo_for_qe2pert':
            copy_folder_with_softlinks(src, dst, perturbo_scratch_dir_prefix, test_name, second_run=True)
        # shutil.copytree(src, dst) 

    return perturbo_scratch_dir
        
   
def softlink_ephr_files(perturbo_scratch_dir_prefix, test_name, dst, file_name): 
    """
    Make a softlink from scratch folder to the computed ephr file

    Parameters
    ----------
    perturbo_scratch_dir_prefix : str
        path to the scratch folder with computational files and results

    test_name : str
        name of test

    dst : str
        folder where the softlink will be placed
    
    file_name : str
        name of the linked ephr-file

    Raises
    ------
    ValueError
       if corresponding ephr-file wasn't found or calculated. 

    Returns
    -------
    None

    """
    ephr_name = test_name[:test_name.find('-')]
    ephr_address = os.path.join(perturbo_scratch_dir_prefix, 'ephr_calculation', ephr_name, 'qe2pert')
    # copy from our previous computation to the current computation folder
    try:
        src = os.path.abspath(os.path.join(ephr_address, file_name))
        os.symlink(src, dst)
    except:
        raise ValueError(f"Ephr-file for {test_name} wasn't found or calculated")
