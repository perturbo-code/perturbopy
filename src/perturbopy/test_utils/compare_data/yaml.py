"""
This module contains functions to compare YAML files

"""
from numbers import Number
import numpy as np
import yaml
import perturbopy.test_utils.compare_data.h5 as ch5
from perturbopy.test_utils.run_test.run_utils import get_tol
from perturbopy.io_utils.io import open_yaml


def equal_scalar(scalar1, scalar2, key, ig_n_tol):
    """
    Determines if two scalars contain the same value

    Parameters
    ----------
    scalar1 : numpy.dtype
        first  scalar
    scalar2 : numpy.dtype
        second scalar
    key : str
        key associated with this scalar
    ig_n_tol : dict
        dictionary of ignore keywords and tolerances needed to make comparison on values

    Returns
    -------
    equal_value : bool
        boolean specifying if both scalars contain the same values
    diff_str : str
        string which contains the information about the calculation error
    output_res_val : str
        here for consistency, just a copy of the diff_str

    """
    # check that scalar1 and scalar2 are Numbers
    errmsg = ('scalar1/2 are not Numbers')
    assert isinstance(scalar1, Number) and isinstance(scalar2, Number), errmsg

    atol, rtol = get_tol(ig_n_tol, key)

    equal_value = np.allclose(np.array(scalar1),
                              np.array(scalar2),
                              atol=atol,
                              rtol=rtol,
                              equal_nan=True)

    diff = np.abs(scalar1 - scalar2)

    if np.abs(scalar1) > 1e-10:
        rdiff = np.abs((scalar2 - scalar1) / scalar1)
        diff_str = f'{diff:.1e}, {rdiff*100:.1e}%, computed={scalar1}, reference={scalar2}'

    else:
        diff_str = f'{diff:.1e}'

    output_res_val = f'{diff_str}'

    return equal_value, diff_str, output_res_val


def equal_list(list1, list2, key, ig_n_tol, path):
    """
    Determines if two lists contain the same values

    Parameters
    ----------
    list1 : list
        first  list
    list2 : list
        second list
    key: str
        A key for the tolerance. If this key is not specified in the tolerance dict,
        a default tolerance will be applied
    ig_n_tol : dict
        dictionary of ignore keywords and tolerances needed to make comparison on values
    path : str
        pseudo path to this item being compared

    Returns
    -------
    equal_vlaues : bool
        boolean specifying if both lists are equivalent
    diff : str
        string which contains the information about the number of
        failed tests
    output_res_list : list
        list with testing results. Either the item from the
        produced yaml-file will be saved, or it will be saved
        with the additional string FAIL

    """
    # check that list1 and list2 are lists
    errmsg = ('list1/2 are not lists')
    assert isinstance(list1, list) and isinstance(list2, list), errmsg

    errmsg = ('list1/2 are not the same length')
    assert len(list1) == len(list2), errmsg
    indices = range(len(list1))

    # a list of bool values
    equal_per_item = []

    output_res_list = []
    for item1, item2, index in zip(list1, list2, indices):
        errmsg = ('list1/2 values'
                  'are not of the same type')
        assert type(item1) == type(item2), errmsg

        # pseudo path to current item being compared
        item_path = (f'{path}.list[{index}]')
        if isinstance(item1, dict):
            equal_value, diff, output_res = equal_dict(item1, item2, ig_n_tol, item_path)

        elif isinstance(item1, list):
            equal_value, diff, output_res = equal_list(item1, item2, key, ig_n_tol, item_path)

        elif isinstance(item1, Number):
            equal_value, diff, output_res = equal_scalar(item1, item2, key, ig_n_tol)

        elif isinstance(item1, str):
            equal_value = item1 == item2
            diff = f'{item1} {item2}'

        elif isinstance(item1, type(None)):
            equal_value = item1 == item2
            diff = None

        else:
            errmsg = ('list must only contain values of type dict, list, scalar, None, or str')
            known_types_present = False
            assert known_types_present, errmsg

        equal_per_item.append(equal_value)
        if not equal_value:
            print(f'\n !!! discrepancy found at {item_path}')
            print(f' difference: {diff}')
            output_res_list.append(['!!!!FAIL!!!!', output_res])
        else:
            output_res_list.append(f'{item2}')

    # equal dicts produce list of only bool=True
    nitems = len(equal_per_item)
    ncompared = sum(equal_per_item)

    equal_values  = (nitems == ncompared)

    if equal_values:
        diff = None
    else:
        diff = f'among {nitems} elements, {nitems - ncompared} failed comparison'

    return equal_values, diff, output_res_list
    

def equal_dict(dict1, dict2, ig_n_tol, path):
    """
    Determines if two dicts contain the same value
    for the same key

    Parameters
    ----------
    dict1 : dict
        first  dictionary
    dict2 : dict
        second dictionary
    ig_n_tol : dict
        dictionary of ignore keywords and tolerances needed to make comparison on values
    path : str
        pseudo path to this item being compared

    Returns
    -------
    equal_vlaues : bool
        boolean specifying if both dicts contain the same keys and values
    diff : str
        string which contains the information about the number of
        failed tests
    output_res_dict : dict
        list with testing results. Either the item from the
        produced yaml-file will be saved, or it will be saved
        with the additional string FAIL

    """
    # check that dict1 and dict2 are dictionaries
    errmsg = (f'dict1/2 at {path} are not dictionaries')
    assert isinstance(dict1, dict) and isinstance(dict2, dict), errmsg

    # check that dictionaries have the same keys
    errmsg = (f'dict1/2 found at {path} do not have the same keys')
    assert dict1.keys() == dict2.keys(), errmsg

    # total set of keys
    keys = set(dict1.keys())

    for key in dict1.keys():
        # remove 'ignore keys'
        if 'ignore keywords' in ig_n_tol:
            if key in ig_n_tol['ignore keywords']:
                keys.remove(key)

    # a list of bool values
    equal_per_key = []
    output_res_dict = {}
    for key in keys:
        errmsg = (f'dict1/2 values associated with key:{key} '
                  f'are not of the same type')
        assert type(dict1[key]) == type(dict2[key]), errmsg

        # pseudo path to current item being compared
        key_path = (f'{path}.{key}')
        if isinstance(dict1[key], dict):
            equal_value, diff, output_res = equal_dict(dict1[key], dict2[key], ig_n_tol, key_path)

        elif isinstance(dict1[key], list):
            equal_value, diff, output_res = equal_list(dict1[key], dict2[key], key, ig_n_tol, key_path)

        elif isinstance(dict1[key], Number):
            equal_value, diff, output_res = equal_scalar(dict1[key], dict2[key], key, ig_n_tol)

        elif isinstance(dict1[key], str):
            equal_value = dict1[key] == dict2[key]
            diff = f'{dict1[key]} {dict2[key]}'

        elif isinstance(dict1[key], type(None)):
            equal_value = dict1[key] == dict2[key]
            diff = None

        else:
            errmsg = (f'dict must only contain values of type dict, list, scalar, None, or str '
                      f'but found type {type(dict1[key])}')
            known_types_present = False
            assert known_types_present, errmsg

        equal_per_key.append(equal_value)
        if not equal_value:
            print(f'\n !!! discrepancy found at {key_path}')
            print(f' difference: {diff}')
            output_res_dict[key] = ["# !!!!FAIL!!!!", output_res]
        else:
            output_res_dict[key] = [dict2[key]]

    # equal dicts produce list of only bool=True
    nitems = len(equal_per_key)
    ncompared = sum(equal_per_key)

    equal_values  = (nitems == ncompared)

    if equal_values:
        diff = None
    else:
        diff = f'among {nitems} elements, {nitems - ncompared} failed comparison'

    return equal_values, diff, output_res_dict


def equal_values(file1, file2, ig_n_tol):
    """
    Determines if two YAML files contain the same value
    for the same keys. keys must be in 'test keywords'

    Parameters
    ----------
    file1 : str
        first  YAML file name
    file2 : str
        second YAML file name
    ig_n_tol : dict
        dictionary of keywords and tolerances needed to make comparison on files

    Returns
    -------
    equal_vlaues : bool
        boolean specifying if both YAML files contain the same keys and values
    diff : str
        string which contains the information about the number of
        failed tests
    
    .. note::
        Also, the file {name_of_file}_errors_file.yml will be generated in case of the fail
        of some comparisons.

    """
    yaml1_dict = open_yaml(file1)
    yaml2_dict = open_yaml(file2)

    if 'test keywords' in ig_n_tol:
        yaml1_del_keys = [key for key in yaml1_dict.keys() if key not in ig_n_tol['test keywords']]
        yaml2_del_keys = [key for key in yaml2_dict.keys() if key not in ig_n_tol['test keywords']]

        for key in yaml1_del_keys:
            del yaml1_dict[key]
        for key in yaml2_del_keys:
            del yaml2_dict[key]

        errmsg = ('no entries left in dict after applying \'test keywords\'')
        assert len(yaml1_dict) > 0, errmsg
        assert len(yaml2_dict) > 0, errmsg

    equal_values, diff, output_res_dict = equal_dict(yaml1_dict, yaml2_dict, ig_n_tol, 'top of yaml')

    if not equal_values:
        file_name = f"{file2[:file2.find('.yml')]}_errors_file.yml"

        with open(file_name, 'w', encoding='utf-8') as yaml_file:
            yaml.dump(output_res_dict, yaml_file, allow_unicode=True)

    return equal_values, diff
