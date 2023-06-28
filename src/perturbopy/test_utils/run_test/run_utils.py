"""
   Utils to select which tests to run based on the command line arguments and
   test tags.
"""
import os
import sys
import copy
from perturbopy.io_utils.io import open_yaml


def read_test_tags(test_name, func_name):
    """
    Get a list of tags for a given test. List of tags is combined from the tags from
    pert_input.yml and epwan_info.yml for a given epwan file.

    Parameters
    ----------
    test_name : str
        name of the folder inside the tests/ folder

    func_name : str
        name of the test programm, which we run
        (do we test perturbo or qe2pert)

    Returns
    -------
    tag_list : list
        list of tags for a given test
    epwan_name : str
        name of the epwan file associated with this test
    """

    cwd = os.getcwd()
    
    epwan_dict_path = 'epwan_info.yml'
    epwan_info = open_yaml(epwan_dict_path)

    if (func_name == 'test_perturbo') or (func_name == 'test_perturbo_for_qe2pert'):
        driver_path_suffix = 'tests_perturbo/' + test_name
        perturbo_driver_dir_path = [x[0] for x in os.walk(cwd) if x[0].endswith(driver_path_suffix)][0]
        pert_input = open_yaml(f'{perturbo_driver_dir_path}/pert_input.yml')

        # Read the tags from pert_input.yml
        input_tags = []
        if 'tags' in pert_input['test info'].keys():
            input_tags = pert_input['test info']['tags']

        # Read the tags from epwan_info.yml
        epwan_name = pert_input['test info']['epwan']

        epwan_tags = []
        if 'tags' in epwan_info[epwan_name].keys():
            epwan_tags = epwan_info[epwan_name]['tags']

        tag_list = input_tags + epwan_tags
        tag_list = sorted(list(set(tag_list)))
    
    elif func_name == 'test_qe2pert':
        if 'tags' in epwan_info[test_name]:
            tag_list = epwan_info[test_name]['tags']
        epwan_name = test_name

    return tag_list, epwan_name


def get_all_tests(func_name):
    """
    Get the names of all test folders based on the epwan_info.yml file.

    Parameters
    ----------
    func_name : str
       name of the metafunction, which we parametrize

    Returns
    -------
    test_folder_list : list
       list of all test names
    """
    test_folder_list = []
    dev_test_folder_list = []

    epwan_dict_path = 'epwan_info.yml'
    epwan_info = open_yaml(epwan_dict_path)

    if (func_name == 'test_perturbo') or (func_name == 'test_perturbo_for_qe2pert'):
    
        for epwan in epwan_info:
            if 'tests' in epwan_info[epwan].keys():
                test_list = epwan_info[epwan]['tests']

                test_folder_list += [f'{epwan}-{t}' for t in test_list]

            if 'devel tests' in epwan_info[epwan].keys():
                dev_test_list = epwan_info[epwan]['devel tests']

                dev_test_folder_list += [f'{epwan}-{t}' for t in dev_test_list]

    elif func_name == 'test_qe2pert':
        test_folder_list = [ephr for ephr in epwan_info]

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


def filter_tests(all_test_list, tags, exclude_tags, epwan, test_names, func_name):
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

    epwan : list or None
       list of the epwan files

    test_names : list or None
       list of test folders to include
    
    func_name : str
        name of the test programm, which we run
        (do we test perturbo or qe2pert)

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
    if tags is not None or exclude_tags is not None or epwan is not None:
        for test_name in all_test_list:

            # tags for a given test
            test_tag_list, epwan_name = read_test_tags(test_name, func_name)

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

            # epwan file name
            if epwan is not None:

                if epwan_name not in epwan and test_name in test_list:
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
                errmsg = (f'Test {test_name_cmd} is not listed in epwan_info.yml, \n'
                          'but specified in --test-names option.'
                         )
                raise ValueError(errmsg)

        test_list = test_names

    if not test_list:
        raise RuntimeError('No test folders selected')

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

          # in percents
          rel tol:
             default:
                0.01

    The elements are considerent different if the following equation does not apply:

    >>> absolute(a - b) <= (abs_tol + rel_tol * absolute(b))

    Parameters
    ----------
    igns_n_tols : dict
        dictionary containing the ignore keywords and tolerances needed to performance comparison of ref_outs and new_outs
    test_case : str
        define what type of the test we run - for perturbo testing or for the
        qe2pert testing.

    Returns
    -------
    igns_n_tols_updated : dict
        **updated** dictionary containing the ignore keywords and tolerances

    """

    if test_case == 'perturbo':
        default_abs_tol = 1e-8
        default_rel_tol = 0.01
    elif test_case == 'qe2pert':
        default_abs_tol = 5e-7
        default_rel_tol = 0.5

    igns_n_tols_updated = []

    for outfile in igns_n_tols:

        if not isinstance(outfile, dict):
            outfile = {'abs tol':
                       {'default': default_abs_tol},
                       'rel tol':
                       {'default': default_rel_tol}
                      }

        else:
            if test_case == 'perturbo':
                if 'abs tol' not in outfile.keys():
                    outfile['abs tol'] = {'default': default_abs_tol}

                elif 'default' not in outfile['abs tol'].keys():
                    outfile['abs tol']['default'] = default_abs_tol

                if 'rel tol' not in outfile.keys():
                    outfile['rel tol'] = {'default': default_rel_tol}

                elif 'default' not in outfile['rel tol'].keys():
                    outfile['rel tol']['default'] = default_rel_tol
            elif test_case == 'qe2pert':
                if 'abs tol' not in outfile.keys():
                    outfile['abs tol'] = {'default': default_abs_tol}

                elif 'qe2pert' in outfile['abs tol'].keys():
                    outfile['abs tol']['default'] = outfile['abs tol']['qe2pert']

                elif 'default' not in outfile['abs tol'].keys():
                    outfile['abs tol']['default'] = default_abs_tol

                if 'rel tol' not in outfile.keys():
                    outfile['rel tol'] = {'default': default_rel_tol}
                    
                elif 'qe2pert' in outfile['rel tol'].keys():
                    outfile['rel tol']['default'] = outfile['rel tol']['qe2pert']

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
