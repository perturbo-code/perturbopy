"""
   Run an executable for the testsuite.
"""
import numpy as np
import os
import sys
import shlex
import shutil
import subprocess
from perturbopy.io_utils.io import open_yaml
from perturbopy.test_utils.run_test.env_utils import run_from_config_machine
from perturbopy.test_utils.run_test.env_utils import perturbo_scratch_dir_config, move_qe2pert_files
from perturbopy.test_utils.run_test.run_utils import print_test_info, setup_default_tol
from perturbopy.test_utils.run_test.run_utils import ph_collection, define_nq_num


def run_perturbo(source_folder, perturbo_driver_dir_path, config_machine,
                 input_name='pert.in', output_name='pert.out'):
    """
    Function to run Perturbo and produce output files


    Parameters
    ----------
    source_folder : str
        path of source directory
    perturbo_driver_dir_path : str
        path to dir with pert.in file
    config_machine : dict
        dictionary with computational information, which we'll use in this set of computations.
    input_name : str, optional
        name of the input file, default: 'pert.in'
    output_name : str, optional
        name of the output file, default: 'pert.out'

    Returns
    -------
    None

    """

    command = run_from_config_machine(config_machine, 'perturbo')

    run = f'{command} -i {input_name} | tee {output_name}'

    os.chdir(perturbo_driver_dir_path)

    print(f'\n ====== Path ======= :\n {os.getcwd()}\n')

    print(f' === Running Perturbo === :\n {run}')
    sys.stdout.flush()

    subprocess.run(preliminary_commands(config_machine, 'perturbo') + run, shell=True)

    os.chdir(source_folder)


def preliminary_commands(config_machine, step):
    """
    Function which define all comands which you want to run before the qe2pert computations and
    each separate computation
    
    Parameters
    ----------
    config_machine : str
        dictionary, which include the list of running commands
    step : str
        name of the computational step which is computed ('scf', 'nscf', etc.)
    """

    print(' == Prel commands == :')
    list_of_coms = ''
    if 'prel_coms' in config_machine:
        for com in config_machine['prel_coms']:
            print(f' ======= Run ======= :\n {com}')
            sys.stdout.flush()
            list_of_coms += f'{com}\n'
    if 'prel_coms' in config_machine['comp_info'][step]:
        for com in config_machine['comp_info'][step]['prel_coms']:
            print(f' ======= Run ======= :\n {com}')
            sys.stdout.flush()
            list_of_coms += f'{com}\n'
    return list_of_coms


def run_qe2pert(source_folder, work_path, config_machine, prefix, input_name='qe2pert.in', output_name='qe2pert.out'):
    """
    Function for qe2pert calculation

    Parameters
    ----------
    source_folder : str
        path of source directory
    work_path : str
        path to dir with input file, where we'll run the calculations
    config_machine : dict
        dictionary, which include the commands for qe2pert calculation
    prefix : str
        prefix which we use for the filenames
    input_name : str, optional
       name of the input file, default: 'qe2pert.in'
    output_name : str, optional
       name of the output file, default: 'qe2pert.out'

    Returns
    -------
    None

    """

    command = run_from_config_machine(config_machine, 'qe2pert')
    run = f'{command} -i {input_name} | tee {output_name}'

    # link the save-file from scf calculation
    os.chdir(f'{work_path}/qe2pert/')
    os.mkdir('tmp')
    softlink = f'../../pw-ph-wann/nscf/tmp/{prefix}.save'
    print(f'\n ====== Path ======= :\n {os.getcwd()}\n')
    print(f'\n =Link tmp from nscf :\n {softlink}')
    sys.stdout.flush()
    os.symlink(softlink, f'tmp/{prefix}.save')
    
    # link rest files
    wann_files = os.listdir('../pw-ph-wann/wann/')
    print('\n = Link rest files = :\n')
    for wf in wann_files:
        softlink = f'../pw-ph-wann/wann/{wf}'
        print(f'{softlink}; \n')
        sys.stdout.flush()
        os.symlink(softlink, f'{wf}')

    # run qe2pert
    print(f' = Running qe2pert = :\n {run}')
    sys.stdout.flush()
    
    subprocess.run(preliminary_commands(config_machine, 'qe2pert') + run, shell=True)

    os.chdir(source_folder)


def get_test_materials(test_name, test_case, config_machine, source_folder):
    """
    Run one test:
       #. run perturbo.x to produce output files
       #. determine paths to files for comparison
       #. associated settings for file comparison with file paths

    Parameters
    ----------
    test_name : str
        name of test
    test_case : str
        define what type of the test we run - for perturbo testing or for the
        qe2pert testing.
    config_machine : str
        name of file with computational information, which we'll use in this set of computations.
        Should be in folder {source_folder}/config_machine
    source_folder : str
        name of the folder, where should be all the testing supplementary files (reference, input files, etc.)

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
    inputs_path_suffix = 'inputs/' + test_name
    ref_data_path_suffix = 'refs/' + test_name

    config_machine = open_yaml(os.path.join(source_folder, f'config_machine/{config_machine}'))

    # determine needed paths
    perturbo_inputs_dir_path = [x[0] for x in os.walk(source_folder) if x[0].endswith(inputs_path_suffix)][0]
    work_path                = perturbo_scratch_dir_config(source_folder, perturbo_inputs_dir_path, test_name, config_machine, test_case)
    ref_path                 = [x[0] for x in os.walk(source_folder) if x[0].endswith(ref_data_path_suffix)][0]

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

    # print the test information before the run
    print_test_info(test_name, pert_input, test_type='perturbo')

    # run Perturbo to produce outputs
    run_perturbo(source_folder, work_path, config_machine)

    # list of dict. Each dict contains ignore keywords and
    # tolerances (information about how to compare outputs)
    igns_n_tols = [test_files[out_file] for out_file in out_files]

    igns_n_tols = setup_default_tol(igns_n_tols, test_case)

    return (ref_outs,
            new_outs,
            igns_n_tols)


def run_epr_calculation(epr_name, config_machine, source_folder):
    """
    Parameters
    ----------
    epr_name : str
        name of computed epr_name file
    config_machine : str
        name of file with computational information, which we'll use in this set of computations.
        Should be in folder {source_folder}/config_machine.
    source_folder : str
        name of the folder, where should be all the testing supplementary files (reference, input files, etc.)

    Returns
    -----
    None
    """
    # suffixes of paths needed to find driver/utils/references
    inputs_path_suffix = f'epr_computation/{epr_name}'
    config_machine = open_yaml(os.path.join(source_folder, f'config_machine/{config_machine}'))

    # determine needed paths
    inputs_dir_path = os.path.join(source_folder, inputs_path_suffix)
    work_path = perturbo_scratch_dir_config(source_folder, inputs_dir_path, epr_name, config_machine, test_case='epr_calculation')

    # open input yaml-files with supplementary info
    # and computational commands
    input_yaml = open_yaml(os.path.join(source_folder, 'test_listing.yml'))

    # print the test information before the run
    print_test_info(epr_name, input_yaml, test_type='qe2pert')

    # define the prefix - we'll need to have it in the later computations
    prefix = input_yaml[epr_name]['prefix']

    # move supplementary files for this calculation
    move_qe2pert_files(source_folder, work_path, epr_name, config_machine)

    # run qe2pert
    run_qe2pert(source_folder, work_path, config_machine, prefix)

    return


def clean_test_materials(test_name, new_outs, config_machine, source_folder):
    """
    clean one test:
       #. removes new files and dirs produced by test

    Parameters
    ----------
    test_name : str
       name of test
    new_outs : list
       list of paths to produced outputs
    config_machine : dict
        dictionary with computational information, which we'll use in this set of computations.
    source_folder : str
        path of source directory

    Returns
    -----
    None

    """
    # suffixes of paths needed to find driver/utils/references
    inputs_path_suffix = 'inputs/' + test_name

    config_machine = open_yaml(os.path.join(source_folder, f'config_machine/{config_machine}'))

    # determine paths
    perturbo_inputs_dir_path = [x[0] for x in os.walk(source_folder) if x[0].endswith(inputs_path_suffix)][0]
    work_path                = perturbo_scratch_dir_config(source_folder, perturbo_inputs_dir_path, test_name, config_machine, rm_preexist_dir=False)

    if os.path.isdir(work_path):
        print(f'\n === Test {test_name} passed ===\n\n Removing {work_path} ...')
        shutil.rmtree(work_path)

    return None
 

def clean_epr_folders(epr_failed, config_machine, keep_epr, keep_preliminary, source_folder):
    """
    Delete all temporary epr folders for the tests which were passed

    Parameters
    ----------
    epr_failed : list
        names of epr calculations, for which we obtained errors. The
        corresponding folders will be saved
    
    config_machine : dict
        dictionary with computational information, which we'll use in this set of computations.
    
    keep_epr : bool
        save all epr-files from the qe2pert testing
    
    keep_preliminary : bool
        save all preliminary files for epr calculation
    
    source_folder : str
        name of the folder, where should be all the testing supplementary files (reference, input files, etc.)

    Returns
    -----
    None

    """
    config_machine = open_yaml(os.path.join(source_folder, f'config_machine/{config_machine}'))

    # looking for the  location with the temporary files
    work_path   = os.path.join(source_folder, "PERT_SCRATCH")
    try:
        work_path    = os.path.join(source_folder, config_machine['PERT_SCRATCH'])
    except KeyError:
        print(f'PERT_SCRATCH not set in the config_machine. using default location -  {work_path}')
    epr_dict_path = os.path.join(source_folder, 'test_listing.yml')
    
    # set of all epr-files
    epr_full_list = [epr for epr in open_yaml(epr_dict_path)]
    
    # set of epr-files, for which tests have passed succescfully - we can delete them
    deleting_epr = list(set(epr_full_list) - set(epr_failed))
    print('\n == Tests finished ==\n\n')
    if not keep_preliminary:
        # if keep_preliminary, simply pass this function - we'll save all
        # files in this case

        if keep_epr:
            # if keep only epr, collect them in a separate new folder:
            dst = os.path.join(work_path, 'collected_epr')
            os.mkdir(dst)
            
            # collect all epr-files
            for epr in epr_full_list:
                src = os.path.join(work_path, 'epr_calculation', epr, 'qe2pert')
                
                # only if the directory with the epr-file exist:
                if os.path.isdir(src):
                    file_list = os.listdir(src)
                    
                    # looking for the epr-files in the files list
                    for file_name in file_list:
                        if file_name.endswith('epr.h5'):
                            full_src = os.path.join(src, file_name)
                            full_dst = os.path.join(dst, file_name)

                            # copy this file in the new folder
                            shutil.copy2(full_src, dst)

        # last steps in both cases - delete all computational folders
        for epr in deleting_epr:
            del_dir = os.path.join(work_path, 'epr_calculation', epr)
            if os.path.isdir(del_dir):
                print(f'Removing {del_dir} ... \n')
                shutil.rmtree(del_dir)
