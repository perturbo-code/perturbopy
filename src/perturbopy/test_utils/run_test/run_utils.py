"""
   Utils to select which tests to run based on the command line arguments and
   test tags.
"""
import os
import copy
import shutil
import sys
from perturbopy.io_utils.io import open_yaml


def read_test_tags(test_name, func_name, source_folder):
    """
    Get a list of tags for a given test. List of tags is combined from the tags from
    pert_input.yml and test_listing.yml for a given epr file.

    Parameters
    ----------
    test_name : str
        name of the folder inside the tests/ folder

    func_name : str
        name of the test programm, which we run
        (do we test perturbo or qe2pert)
    source_folder : str
        name of the folder, where should be all the testing supplementary files (reference, input files, etc.)
    Returns
    -------
    tag_list : list
        list of tags for a given test
    epr_name : str
        name of the epr file associated with this test
    """
    
    epr_dict_path = os.path.join(source_folder, 'test_listing.yml')
    epr_info = open_yaml(epr_dict_path)

    if (func_name == 'test_perturbo') or (func_name == 'test_perturbo_for_qe2pert'):
        driver_path_suffix = 'inputs/' + test_name
        perturbo_driver_dir_path = [x[0] for x in os.walk(source_folder) if x[0].endswith(driver_path_suffix)][0]
        pert_input = open_yaml(f'{perturbo_driver_dir_path}/pert_input.yml')

        # Read the tags from pert_input.yml
        input_tags = []
        if 'tags' in pert_input['test info'].keys():
            input_tags = pert_input['test info']['tags']

        # Read the tags from test_listing.yml
        epr_name = pert_input['test info']['epr']

        epr_tags = []
        if 'tags' in epr_info[epr_name].keys():
            epr_tags = epr_info[epr_name]['tags']

        tag_list = input_tags + epr_tags
        tag_list = sorted(list(set(tag_list)))
    
    elif func_name == 'test_qe2pert':
        if 'tags' in epr_info[test_name]:
            tag_list = epr_info[test_name]['tags']
        epr_name = test_name

    return tag_list, epr_name


def get_all_tests(func_name, source_folder):
    """
    Get the names of all test folders based on the test_listing.yml file.

    Parameters
    ----------
    func_name : str
       name of the metafunction, which we parametrize

    Returns
    -------
    test_folder_list : list
       list of all test names
    source_folder : str
        name of the folder, where should be all the testing supplementary files (reference, input files, etc.)
    """
    test_folder_list = []
    dev_test_folder_list = []

    epr_dict_path = os.path.join(source_folder, 'test_listing.yml')
    epr_info = open_yaml(epr_dict_path)

    if (func_name == 'test_perturbo') or (func_name == 'test_perturbo_for_qe2pert'):

        test_list = ['bands', 'phdisp', 'ephmat']
        for epr in epr_info:
            if 'tests' in epr_info[epr].keys():
                if (func_name == 'test_perturbo'):
                    test_list = epr_info[epr]['tests']

                test_folder_list += [f'{epr}-{t}' for t in test_list]

            if 'devel tests' in epr_info[epr].keys():
                dev_test_list = epr_info[epr]['devel tests']

                dev_test_folder_list += [f'{epr}-{t}' for t in dev_test_list]

    elif func_name == 'test_qe2pert':
        test_folder_list = [epr for epr in epr_info]

    return test_folder_list, dev_test_folder_list


def print_test_info(test_name, input_dict, test_type):
    """
    Print information about a test.

    Parameters
    ----------
    test_name : str
        name of the test folder
    input_dict : dict
        dictionary contatining the test info
    test_type : str
        define that type of testing we make - either 'qe2pert' or 'perturbo'
    """

    if test_type == 'perturbo':
        if 'desc' in input_dict['test info']:
            desc = input_dict['test info']['desc']
        else:
            desc = None
    elif test_type == 'qe2pert':
        if 'description' in input_dict[test_name]:
            desc = input_dict[test_name]['description']
        else:
            desc = None
        
    print(f'\n === Test folder === :\n {test_name}')

    if desc is not None:
        print(f'\n === Description === :\n {desc}')

    sys.stdout.flush()


def filter_tests(all_test_list, tags, exclude_tags, epr, test_names, func_name, run_qe2pert, source_folder):
    """
    Return the list of test folders based on command line options

    Parameters
    ----------
    all_test_list : list
       list of all the test folders

    tags : list or None
       list of tags to include

    exclude_tags : list or None
       list of tags to exclude

    epr : list or None
       list of the epr files

    test_names : list or None
       list of test folders to include
    
    func_name : str
        name of the test programm, which we run
        (do we test perturbo or qe2pert)
    
    run_qe2pert : bool
        whether perturbo_for_qe2pert tests are conducted or not

    source_folder : str
        name of the folder, where should be all the testing supplementary files (reference, input files, etc.)

    Returns
    -------
    test_list : list
       list of test for a given pytest run

    Raises
    ------
    RuntimeError
       if --test-names and (--tags or --exclude_tags) are specified at the same time
       or
       if no test folders are selected

    ValueError
       if --test-names contains a name of a test that is not present
    """

    test_list = copy.deepcopy(all_test_list)

    # sort based on tags
    if tags is not None or exclude_tags is not None or epr is not None:
        for test_name in all_test_list:

            # tags for a given test
            test_tag_list, epr_name = read_test_tags(test_name, func_name, source_folder)

            # tags from command line
            if tags is not None:

                keep_test = False

                for tag in tags:
                    if tag in test_tag_list:
                        keep_test = True
                        break

                if not keep_test:
                    test_list.remove(test_name)

            # exclude tags from command line
            if exclude_tags is not None:

                keep_test = True

                for tag in exclude_tags:
                    if tag in test_tag_list:
                        keep_test = False
                        break

                if not keep_test and test_name in test_list:
                    test_list.remove(test_name)

            # epr file name
            if epr is not None:

                if epr_name not in epr and test_name in test_list:
                    test_list.remove(test_name)

    # test name from command line
    if test_names is not None:

        if tags is not None or exclude_tags is not None:
            errmsg = ('If the --test-names option is specified, \n'
                      '--tags and --exclude_tags must NOT be specified.'
                     )

            raise RuntimeError(errmsg)

        for test_name_cmd in test_names:
            if test_name_cmd not in all_test_list:
                if (func_name == 'test_perturbo') or (func_name == 'test_qe2pert'):
                    errmsg = (f'Test {test_name_cmd} is not listed in test_listing.yml, \n'
                              f'but specified in --test-names option. Full test_list: {test_list}'
                             )
                    raise ValueError(errmsg)
                elif (func_name == 'test_perturbo_for_qe2pert') and run_qe2pert:
                    errmsg = (f'Test {test_name_cmd} is not listed for running on the perturbo run for \n'
                              'qe2pert check but specified in --test-names option. On this run, only \n'
                              f'this tests supposed to run: {test_list}'
                             )
                    raise ValueError(errmsg)

        test_list = test_names

    if not test_list and not ((func_name == 'test_perturbo_for_qe2pert') and not (run_qe2pert)):
        raise RuntimeError('No test folders selected')
    
    if (func_name == 'test_perturbo'):
        print('\n\n === Test folders == :')
    print(' \n'.join(test_list))
    print('')
    sys.stdout.flush()

    return test_list


def setup_default_tol(igns_n_tols, test_case):
    """
    Setup the default tolerances for each file to compare if the tolerances are
    not specified in the pert_input.yml file.

    This function ensures that every output file to compare has the following
    dictionary structure:

    .. code-block :: python

        output_file.yml:
            abs tol:
                default:
                    1e-8

            # relative error
            rel tol:
                default:
                    0.01

    The elements are considerent different if the following equation does not apply:

    >>> absolute(a - b) <= (abs_tol + rel_tol * absolute(b))

    Parameters
    ----------
    igns_n_tols : list
        list of dictionaries, which contain containing the tolerances needed
        to performance comparison of ref_outs and new_outs
    test_case : str
        define what type of the test we run - for perturbo testing or for the
        qe2pert testing.

    Returns
    -------
    igns_n_tols_updated : list
        **updated** list containing the dictionary with tolerances

    """

    if test_case == 'perturbo':
        default_abs_tol = 1e-8
        default_rel_tol = 0.01
    elif test_case == 'perturbo_for_qe2pert':
        # in case of the testing qe2pert relative error could be bigger
        # due to the error that accumulates from scf calculations
        default_abs_tol = 1e-8
        default_rel_tol = 0.01

    igns_n_tols_updated = []

    # run thru all files (their list is the keys set)
    for outfile in igns_n_tols:

        if not isinstance(outfile, dict):
            # if we don't have any information about the errors
            # for this file - define default one
            outfile = {'abs tol':
                       {'default': default_abs_tol},
                       'rel tol':
                       {'default': default_rel_tol}
                      }

        else:
            if test_case == 'perturbo_for_qe2pert':
                # if we test perturbo for qe2pert,
                # we move error for qe2pert testing into the cells
                # `abs_tol` and `rel_tol`
                if 'qe2pert abs tol' in outfile.keys():
                    outfile['abs tol'] = outfile['qe2pert abs tol']
                if 'qe2pert rel tol' in outfile.keys():
                    outfile['rel tol'] = outfile['qe2pert rel tol']

            # if we have some dict but without `abs_tol` key - take default
            if 'abs tol' not in outfile.keys():
                outfile['abs tol'] = {'default': default_abs_tol}

            # if we have some `abs_tol` key, but only for specific cases,
            # add default values
            elif 'default' not in outfile['abs tol'].keys():
                outfile['abs tol']['default'] = default_abs_tol

            # if we have some dict but without `rel_tol` key - take default
            if 'rel tol' not in outfile.keys():
                outfile['rel tol'] = {'default': default_rel_tol}

            # if we have some `rel_tol` key, but only for specific cases,
            # add default values
            elif 'default' not in outfile['rel tol'].keys():
                outfile['rel tol']['default'] = default_rel_tol

        igns_n_tols_updated.append(outfile)

    return igns_n_tols_updated


def get_tol(ig_n_tol, key, exact_match=False):
    """
    Extract the absolute and relative tolerances for ``key`` from ``ig_n_tol`` dict.

    Parameters
    ----------
    ig_n_tol : dict
       dictionary of ignore keywords and tolerances needed to make comparison on values
    key : str
       A key for the tolerance. If this key is not specified in the tolerance dict,
       a default tolerance will be applied.

    exact_match : bool, optional
       if True, the non-default tolerance if applied to a key only if this key
       matches exactly with the one from the ig_n_tol;
       if False, ``str1 in str2`` condition is enough. For example ``phys`` would
       be considered as a key for ``physics`` if exact_match is False.
       Default is False.

    .. note ::
       The ``rel tol`` from the dictionary is assumed to be in **percents**.

    Returns
    -------
    atol : float
       absolute tolerance for key
    rtol : float
       relative tolerance for key
    """

    atol_dict = ig_n_tol['abs tol']

    kname, cond = key_in_dict(key, atol_dict, exact_match=exact_match)

    if cond:
        atol = atol_dict[kname]
    else:
        atol = atol_dict['default']

    rtol_dict = ig_n_tol['rel tol']

    kname, cond = key_in_dict(key, rtol_dict, exact_match=exact_match)

    if cond:
        rtol = rtol_dict[kname]
    else:
        rtol = rtol_dict['default']

    return float(atol), float(rtol) / 100


def key_in_dict(k, d, exact_match=False):
    """
    Check is a key is in dictionary.

    Parameters
    ----------
    k : str
       A dictionary key.
    d : dict
       A dictionary.

    exact_match : bool
       Whether apply or not the exact match condition for the key

    Returns
    -------
    key : str
       A key from dictionary d that contains k

    condition : bool
       True is the key k is in dict d
    """

    if exact_match:
        return k, k in d

    else:

        for kk in d:
            if str(k) in str(kk) or str(kk) in str(k):
                return kk, True
                break

        return k, False
        

def define_nq_num(output_name):
    """
    Define the number of the q-points,
    obtained during the phonon
    calculation

    Parameters:
    output_name : str
        name to the ph output file from which we obtain
        number of q-points

    Returns
    -------
    nq_num : int
       number of q-points
    """
    with open(output_name, "r") as f:
        for i, line in enumerate(f):
            if line.find('q-points)') != -1:
                nq_num = int(line.split()[1])
    return nq_num


def ph_collection(prefix, nq_num):
    """
    Collect the phonon data into a directory called save.
    The save directory contains all the information needed
    for PERTURBO to interface with QE

    Parameters:
    prefix : str
        prefix of this calculation
    nq_num : int
        number of q points in this calculation
    """
    print(os.getcwd())
    
    os.makedirs('save', exist_ok=True)
    
    # remove wfc files in tmp
    if os.path.exists('tmp'):
        for file in os.listdir('tmp'):
            if 'wfc' in file:
                os.remove(f'tmp/{file}')

    dir = 'tmp/_ph0'
    
    shutil.copytree(f'{dir}/{prefix}.phsave', f'save/{prefix}.phsave')
    
    # copy dyn files
    for file in os.listdir('.'):
        if file.startswith(f'{prefix}.dyn'):
            shutil.copy(file, 'save')

    for nq in range(1, nq_num + 1):
        
        # copy dvscf files
        if nq > 1:

            # parallel version
            if os.path.exists(f'{dir}/{prefix}.q_{nq}/{prefix}.dvscf1'):
                shutil.copy(f'{dir}/{prefix}.q_{nq}/{prefix}.dvscf1', f'save/{prefix}.dvscf_q{nq}')
            # serial version
            elif os.path.exists(f'{dir}/{prefix}.q_{nq}/{prefix}.dvscf'):
                shutil.copy(f'{dir}/{prefix}.q_{nq}/{prefix}.dvscf', f'save/{prefix}.dvscf_q{nq}')
            else:
                raise FileNotFoundError(f"{dir}/{prefix}.q_{nq}/{prefix}.dvscf and {dir}/{prefix}.q_{nq}/{prefix}.dvscf1 don't exist")

            for file in os.listdir(f'{dir}/{prefix}.q_{nq}'):
                if file.endswith('wfc'):
                    os.remove(f'{dir}/{prefix}.q_{nq}/{file}')

        else:

            # parallel version
            if os.path.exists(f'{dir}/{prefix}.dvscf1'):
                shutil.copy(f'{dir}/{prefix}.dvscf1', f'save/{prefix}.dvscf_q{nq}')
            # serial version
            elif os.path.exists(f'{dir}/{prefix}.dvscf'):
                shutil.copy(f'{dir}/{prefix}.dvscf', f'save/{prefix}.dvscf_q{nq}')
            else:
                raise FileNotFoundError(f"{dir}/{prefix}.dvscf and {dir}/{prefix}.dvscf1 don't exist")

            for file in os.listdir(dir):
                if 'wfc' in file:
                    os.remove(f'{dir}/{file}')
             
    shutil.copy(f'save/{prefix}.dyn0', f'save/{prefix}.dyn0.xml')
