# Legacy code, it may be possible to use it again in the future, so don't delete it yet.
# from test_driver.py

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


def run_scf(source_folder, work_path, config_machine, input_name='scf.in', output_name='scf.out'):
    """
    Function for scf calculation

    Parameters
    ----------
    source_folder : str
        path of source directory
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

    os.chdir(source_folder)


def run_phonon(source_folder, work_path, config_machine, prefix, input_name='ph.in', output_name='ph.out'):
    """
    Function for nscf calculation

    Parameters
    ----------
    source_folder : str
        path of source directory
    work_path : str
        path to dir with input file, where we'll run the calculations
    config_machine : dict
        dictionary, which include the commands for phonon calculation
    prefix : str
        prefix which we use for the filenames
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

    nq_num = define_nq_num(output_name)
    print(f' == Collect files == :\n ph_collection({prefix},{nq_num})')
    sys.stdout.flush()
    ph_collection(prefix, nq_num)

    os.chdir(source_folder)


def run_nscf(source_folder, work_path, config_machine, input_name='nscf.in', output_name='nscf.out'):
    """
    Function for nscf calculation

    Parameters
    ----------
    source_folder : str
        path of source directory
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

    os.chdir(source_folder)


def run_wannier(source_folder, work_path, config_machine, prefix, input_name='pw2wan.in', output_name='pw2wan.out'):
    """
    Function for wannier90 calculation

    Parameters
    ----------
    source_folder : str
        path of source directory
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

    os.chdir(source_folder)


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

    os.chdir(source_folder)


def run_epr_calculation(epr_name, config_machine, source_folder):
    """
    Run one test:
        #. Run scf calculation
        #. Run phonon calculation
        #. Run nscf calculation
        #. Run wannier90 calculation
        #. Run qe2pert calculation

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

    # run scf
    run_scf(source_folder, work_path, config_machine)

    # run phonon
    run_phonon(source_folder, work_path, config_machine, prefix)

    # run nscf
    run_nscf(source_folder, work_path, config_machine)

    # run wannier90
    run_wannier(source_folder, work_path, config_machine, prefix)

    # run qe2pert
    run_qe2pert(source_folder, work_path, config_machine, prefix)

    return
