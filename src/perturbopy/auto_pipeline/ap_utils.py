import os
import shutil


def make_computational_folder(perturbo_inputs_dir_path, config_machine, rm_preexist_dir=True):
    """
    Check if the COMP_FOLD variable is written in the config_machine file.
    If not - use default location "/COMP_FOLD".
    After it, this programm make the copy from folder with input files from inputs folder.
    

    Parameters
    ----------
    source_folder : str
        path of source directory

    perturbo_inputs_dir_path : str
        folder with all input files for the test

    config_machine : dict
        dictionary with computational information, which we'll use in this set of computations.

    rm_preexist_dir : bool
        whether to remove dir if it preexists

    Returns
    -------
    comp_folder : str
        string containing the path to generate directory in which
        outputs for computation will be generated

    """
    # Read the perturbo_run variable from the environment
    perturbo_folder_dir_prefix   = "COMP_FOLD"
    try:
        perturbo_folder_dir_prefix = config_machine['COMP_FOLD']
    except KeyError:
        print(f'COMP_FOLD not set in the config_machine. using default location -  {perturbo_folder_dir_prefix}')

    # if folder already exist and we don't want to change it - simply pass rest of the function
    perturbo_folder_dir = perturbo_folder_dir_prefix
    if not rm_preexist_dir:
        return perturbo_folder_dir

    # else - copy over input files to scratch dir
    src = perturbo_inputs_dir_path
    dst = perturbo_folder_dir
    if os.path.isdir(dst):
        print(f'\n directory {dst} exists. Removing this directory ...\n')
        shutil.rmtree(dst)
        copy_folder_with_softlinks(src, dst)
    else:
        copy_folder_with_softlinks(src, dst)

    return os.path.abspath(perturbo_folder_dir)


def copy_folder_with_softlinks(src, dst):
    """
    Copy the src directory to the dst directory.

    Parameters
    ----------
    src : str
        folder with computational info, which is copied
    
    dst : str
        folder, where the files will be copied

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
            shutil.copy2(src_file_path, dst_file_path)
