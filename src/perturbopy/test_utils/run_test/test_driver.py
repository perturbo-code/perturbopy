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
from perturbopy.test_utils.run_test.env_utils import perturbo_scratch_dir_config
from perturbopy.test_utils.run_test.run_utils import print_test_info
from perturbopy.test_utils.run_test.run_utils import setup_default_tol


def run_perturbo(cwd, perturbo_driver_dir_path, config_machine,
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

    subprocess.run(preliminary_commands(config_machine, 'scf') + run, shell=True)

    os.chdir(cwd)
    

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
    

def run_scf(cwd, work_path, config_machine, input_name='scf.in', output_name='scf.out'):
    """
    Function for scf calculation

    Parameters
    ----------
    cwd : str
        path of current working directory
    work_path : str
        path to dir with input file, where we'll run the calculations
    config_machine : dict
        dictionary, which include the commands for scf calculation
    input_name : str, optional
        name of the input file, default: 'scf.in'
    output_name : str, optional
        name of the output file, default: 'scf.out'

    Returns
    -------
    None

    """

    command = run_from_config_machine(config_machine, 'scf')
    run = f'{command} -i {input_name} | tee {output_name}'

    os.chdir(f'{work_path}/pw-ph-wann/scf/')

    print(f'\n ====== Path ======= :\n {os.getcwd()}\n')

    print(f' === Running scf === :\n {run}')
    sys.stdout.flush()

    subprocess.run(preliminary_commands(config_machine, 'scf') + run, shell=True)

    os.chdir(cwd)
    

def run_phonon(cwd, work_path, config_machine, input_name='ph.in', output_name='ph.out'):
    """
    Function for nscf calculation

    Parameters
    ----------
    cwd : str
        path of current working directory
    work_path : str
        path to dir with input file, where we'll run the calculations
    config_machine : dict
        dictionary, which include the commands for phonon calculation
    input_name : str, optional
        name of the input file, default: 'ph.in'
    output_name : str, optional
        name of the output file, default: 'ph.out'

    Returns
    -------
    None

    """

    command = run_from_config_machine(config_machine, 'phonon')
    run = f'{command} -i {input_name} | tee {output_name}'

    os.chdir(f'{work_path}/pw-ph-wann/phonon/')
    softlink = '../scf/tmp'
    print(f'\n ====== Path ======= :\n {os.getcwd()}\n')
    print(f'\n =Link tmp from scf= :\n {softlink}')
    sys.stdout.flush()
    os.symlink(softlink, 'tmp')

    print(f' == Running Phonon = :\n {run}')
    sys.stdout.flush()

    subprocess.run(preliminary_commands(config_machine, 'phonon') + run, shell=True)
    
    collect = 'bash ./ph-collect.sh'
    print(f' == Collect files == :\n {collect}')
    sys.stdout.flush()
    
    subprocess.run(shlex.split(collect))
    
    os.chdir(cwd)

    
def run_nscf(cwd, work_path, config_machine, input_name='nscf.in', output_name='nscf.out'):
    """
    Function for nscf calculation

    Parameters
    ----------
    cwd : str
        path of current working directory
    work_path : str
        path to dir with input file, where we'll run the calculations
    config_machine : dict
        dictionary, which include the commands for nscf calculation
    input_name : str, optional
        name of the input file, default: 'nscf.in'
    output_name : str, optional
        name of the output file, default: 'nscf.out'

    Returns
    -------
    None

    """

    command = run_from_config_machine(config_machine, 'nscf')
    run = f'{command} -i {input_name} | tee {output_name}'

    os.chdir(f'{work_path}/pw-ph-wann/nscf/')
    softlink = '../scf/tmp'
    print(f'\n ====== Path ======= :\n {os.getcwd()}\n')
    print(f'\n =Link tmp from scf= :\n {softlink}')
    sys.stdout.flush()
    os.symlink(softlink, 'tmp')

    print(f' === Running nscf === :\n {run}')
    sys.stdout.flush()

    subprocess.run(preliminary_commands(config_machine, 'nscf') + run, shell=True)

    os.chdir(cwd)
    

def run_wannier(cwd, work_path, config_machine, prefix, input_name='pw2wan.in', output_name='pw2wan.out'):
    """
    Function for wannier90 calculation

    Parameters
    ----------
    cwd : str
        path of current working directory
    work_path : str
        path to dir with input file, where we'll run the calculations
    config_machine : dict
        dictionary, which include the commands for wannier calculation
    prefix : str
        prefix which we use for the filenames
    input_name : str, optional
        name of the input file, default: 'pw2wan.in'
    output_name : str, optional
        name of the output file, default: 'pw2wan.out'

    Returns
    -------
    None

    """

    command = run_from_config_machine(config_machine, 'wannier90')
    run = f'{command} -pp {prefix}'
    
    # link the save-file from scf calculation
    os.chdir(f'{work_path}/pw-ph-wann/wann/')
    os.mkdir('tmp')
    softlink = f'../../scf/tmp/{prefix}.save'
    print(f'\n ====== Path ======= :\n {os.getcwd()}\n')
    print(f'\n =Link tmp from scf= :\n {softlink}')
    sys.stdout.flush()
    os.symlink(softlink, f'tmp/{prefix}.save')

    # first run of wannier90
    print(f' === Running pp === :\n {run}')
    sys.stdout.flush()
    subprocess.run(preliminary_commands(config_machine, 'wannier90') + run, shell=True)
    
    # run of pw2wan
    command = run_from_config_machine(config_machine, 'pw2wannier90')
    run = f'{command} -i {input_name} | tee {output_name}'
    print(f' = Running pw2wan = :\n {run}')
    sys.stdout.flush()
    subprocess.run(preliminary_commands(config_machine, 'pw2wannier90') + run, shell=True)
    
    # second run of wannier90
    command = run_from_config_machine(config_machine, 'wannier90')
    run = f'{command} {prefix}'
    print(f' = Running Wannier= :\n {run}')
    sys.stdout.flush()
    subprocess.run(preliminary_commands(config_machine, 'wannier90') + run, shell=True)
    
    os.chdir(cwd)
    

def run_qe2pert(cwd, work_path, config_machine, prefix, input_name='qe2pert.in', output_name='qe2pert.out'):
    """
    Function for qe2pert calculation

    Parameters
    ----------
    cwd : str
       path of current working directory
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
    softlink = f'../pw-ph-wann/wann/{prefix}_u.mat'
    print(f'\n = Link rest files = :\n {softlink};')
    sys.stdout.flush()
    os.symlink(softlink, f'{prefix}_u.mat')
    softlink = f'../pw-ph-wann/wann/{prefix}_u_dis.mat'
    print(f'\n {softlink};')
    sys.stdout.flush()
    os.symlink(softlink, f'{prefix}_u_dis.mat')
    softlink = f'../pw-ph-wann/wann/{prefix}_centres.xyz'
    print(f'\n {softlink};')
    sys.stdout.flush()
    os.symlink(softlink, f'{prefix}_centres.xyz')

    # run qe2pert
    print(f' = Running qe2pert = :\n {run}')
    sys.stdout.flush()
    
    subprocess.run(preliminary_commands(config_machine, 'qe2pert') + run, shell=True)

    os.chdir(cwd)


def get_test_materials(test_name, test_case, config_machine):
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
        Should be in folder tests_f90/config_machine

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
    config_machine = open_yaml(f'{cwd}/config_machine/{config_machine}')

    # determine needed paths
    perturbo_inputs_dir_path = [x[0] for x in os.walk(cwd) if x[0].endswith(inputs_path_suffix)][0]
    work_path                = perturbo_scratch_dir_config(cwd, perturbo_inputs_dir_path, test_name, config_machine, test_case)
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

    # print the test information before the run
    print_test_info(test_name, pert_input, test_type='perturbo')

    # run Perturbo to produce outputs
    run_perturbo(cwd, work_path, config_machine)

    # list of dict. Each dict contains ignore keywords and
    # tolerances (information about how to compare outputs)
    igns_n_tols = [test_files[out_file] for out_file in out_files]

    igns_n_tols = setup_default_tol(igns_n_tols, test_case)

    return (ref_outs,
            new_outs,
            igns_n_tols)


def run_ephr_calculation(ephr_name, config_machine):
    """
    Run one test:
        #. Run scf calculation
        #. Run phonon calculation
        #. Run nscf calculation
        #. Run wannier90 calculation
        #. Run qe2pert calculation

    Parameters
    ----------
    ephr_name : str
        name of computed ephr_name file
    config_machine : str
        name of file with computational information, which we'll use in this set of computations.
        Should be in folder tests_f90/config_machine.

    Returns
    -----
    None
    """
    # suffixes of paths needed to find driver/utils/references
    cwd = os.getcwd()
    inputs_path_suffix = f'ephr_computation/{ephr_name}'
    config_machine = open_yaml(f'{cwd}/config_machine/{config_machine}')

    # determine needed paths
    inputs_dir_path = f'{cwd}/{inputs_path_suffix}/'
    work_path = perturbo_scratch_dir_config(cwd, inputs_dir_path, ephr_name, config_machine, test_case='ephr_calculation')
    
    # open input yaml-files with supplementary info
    # and computational commands
    input_yaml = open_yaml(f'{cwd}/epwan_info.yml')

    # print the test information before the run
    print_test_info(ephr_name, input_yaml, test_type='qe2pert')
    
    # define the prefix - we'll need to have it in the later computations
    prefix = input_yaml[ephr_name]['prefix']

    # run scf
    run_scf(cwd, work_path, config_machine)
    
    # run phonon
    run_phonon(cwd, work_path, config_machine)

    # run nscf
    run_nscf(cwd, work_path, config_machine)
    
    # run wannier90
    run_wannier(cwd, work_path, config_machine, prefix)
    
    # run qe2pert
    run_qe2pert(cwd, work_path, config_machine, prefix)

    return


def clean_test_materials(test_name, new_outs, config_machine):
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

    Returns
    -----
    None

    """
    # suffixes of paths needed to find driver/utils/references
    inputs_path_suffix = 'tests_perturbo/' + test_name

    cwd = os.getcwd()
    config_machine = open_yaml(f'{cwd}/config_machine/{config_machine}')

    # determine paths
    perturbo_inputs_dir_path = [x[0] for x in os.walk(cwd) if x[0].endswith(inputs_path_suffix)][0]
    work_path                = perturbo_scratch_dir_config(cwd, perturbo_inputs_dir_path, test_name, config_machine, rm_preexist_dir=False)

    if os.path.isdir(work_path):
        print(f'\n === Test {test_name} passed ===\n\n Removing {work_path} ...')
        shutil.rmtree(work_path)

    return None
    

def clean_ephr_folders(ephr_failed, config_machine, keep_ephr, keep_preliminary):
    """
    Delete all temporary ephr folders for the tests which were passed

    Parameters
    ----------
    ephr_failed : list
        names of ephr calculations, for which we obtained errors. The
        corresponding folders will be saved
    
    config_machine : dict
        dictionary with computational information, which we'll use in this set of computations.
    
    keep_ephr : bool
        save all ephr-files from the qe2pert testing
    
    keep_preliminary : bool
        save all preliminary files for ephr calculation

    Returns
    -----
    None

    """
    cwd = os.getcwd()
    config_machine = open_yaml(f'{cwd}/config_machine/{config_machine}')

    work_path   = cwd + "/PSCRATCH"
    try:
        work_path    = config_machine['PSCRATCH']
    except KeyError:
        print(f'PSCRATCH not set in the config_machine. using default location of {work_path}')
    ephr_dict_path = 'epwan_info.yml'
    ephr_full_list = [ephr for ephr in open_yaml(ephr_dict_path)]
    deleting_ephr = list(set(ephr_full_list) - set(ephr_failed))
    print('\n == Tests finished ==\n\n')
    if not keep_preliminary:
        # if keep_preliminary, simply pass this function
        if keep_ephr:
            # if keep only ephr, collect them in a separate new folder:
            dst = os.path.join(work_path, 'collected_ephr')
            os.mkdir(dst)
            for ephr in ephr_full_list:
                src = os.path.join(work_path, 'ephr_calculation', ephr, 'qe2pert')
                if os.path.isdir(src):
                    file_list = os.listdir(src)
                    for file_name in file_list:
                        if file_name.endswith('epwan.h5'):
                            full_src = os.path.join(src, file_name)
                            full_dst = os.path.join(dst, file_name)
                            shutil.copy2(full_src, dst)
        # last steps in both cases - delete all computational folders
        for ephr in deleting_ephr:
            del_dir = os.path.join(work_path, 'ephr_calculation', ephr)
            if os.path.isdir(del_dir):
                print(f'Removing {del_dir} ... \n')
                shutil.rmtree(del_dir)
