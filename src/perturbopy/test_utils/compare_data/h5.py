"""
This module contains functions to compare hdf5 files

"""
import h5py
import numpy as np
from perturbopy.test_utils.run_test.run_utils import get_tol


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
    errmsg = ('scalar1/2 are not float64 or int32')
    assert (
           (scalar1.dtype == 'int32' and scalar2.dtype == 'int32')
           or (scalar1.dtype == 'float64' and scalar2.dtype == 'float64')
           ), errmsg

    atol, rtol = get_tol(ig_n_tol, key)

    equal_value = np.allclose(np.array(scalar1),
                              np.array(scalar2),
                              atol=atol,
                              rtol=rtol,
                              equal_nan=True)

    diff = np.abs(scalar1 - scalar2)

    if np.abs(scalar1) > 1e-10:
        rdiff = np.abs((scalar2 - scalar1) / scalar1)
        diff_str = f'{diff:.1e}, {rdiff*100:.1e}%, {scalar1 = }, {scalar2 = }'

    else:
        diff_str = f'{diff:.1e}'
        
    output_res_val = diff_str

    return equal_value, diff_str, output_res_val
    
    
def format_string(val1, val2):
    """
    Supplementary function for the equal_ndarray function.
    Return the string in the desired format.

    """
    if abs(val2)<1e-20:
        rel_diff = float('inf')
    else:
        rel_diff = abs(val2 - val1) / val2

    return f"value here: {val1:.2e}, reference:({val2:.2e}), abs_diff={abs(val2-val1):.2e}, rel_diff={rel_diff:.2e}"


def equal_ndarray(ndarray1, ndarray2, key, ig_n_tol):
    """
    Determines if two ndarrays contain the same values

    Parameters
    ----------
    ndarray1 : numpy.ndarray
       first numpy ndarray
    ndarray2 : numpy.ndarray
       second numpy ndarray
    key: str
       A key for the tolerance. If this key is not specified in the tolerance dict,
       a default tolerance will be applied
    ig_n_tol : dict
       dictionary of ignore keywords and tolerances needed to make comparison on values

    Returns
    -------
    equal_vlaues : bool
       boolean specifying if both ndarrays are equivalent
    diff : str
        string which contains the information about biggest
        difference between produced file and reference
    output_arr : ndarray
        numpy array with the original data from the produced files.
        Where the error was found, value is changed by the line:
        value here: {val1}, reference:({val2}), abs_diff={abs(val2-val1)}, rel_diff={abs(val2-val1)/val2}

    """
    errmsg = ('ndarray1/2 are not ndarrays')
    assert isinstance(ndarray1, np.ndarray) and isinstance(ndarray2, np.ndarray), \
           errmsg

    errmsg = ('ndarray1/2 have different shapes')
    assert ndarray1.shape == ndarray2.shape, errmsg

    atol, rtol = get_tol(ig_n_tol, key)

    equal_value = np.allclose(ndarray1,
                              ndarray2,
                              atol=atol,
                              rtol=rtol,
                              equal_nan=True)

    diff = np.max(np.abs(ndarray1 - ndarray2))

    # find max percentage diff only if comparison fails
    if not equal_value:

        tmp_array = ndarray1
        tmp_array[np.abs(tmp_array) < 1e-10] = 1e-10

        idxmax_flat = np.argmax(np.abs((ndarray2 - ndarray1) / tmp_array))
        idxmax = np.unravel_index(idxmax_flat, ndarray1.shape)

        v1 = ndarray1[idxmax]
        v2 = ndarray2[idxmax]

        rdiff = np.abs((v2 - v1) / v1)
        diff_str = (f'{diff:.1e}, {rdiff*100:.1e}%, v1={v1:.1e}, v2={v2:.1e},'
                    f'atol={atol:.1e}, rtol={rtol:.1e},')
        where_error = np.isclose(ndarray1,
                                      ndarray2,
                                      atol=atol,
                                      rtol=rtol,
                                      equal_nan=True)

    else:
        diff_str = f'{diff:.1e}'
        
    where_error = ~np.isclose(ndarray1,
                              ndarray2,
                              atol=atol,
                              rtol=rtol,
                              equal_nan=True)
                              
    vectorized_format = np.vectorize(format_string)
    output_arr = np.where(where_error, vectorized_format(ndarray2, ndarray1), ndarray2.astype(str))

    return equal_value, diff_str, output_arr


def equal_dict(dict1, dict2, ig_n_tol, path):
    r"""
    Determines if two dicts contain the same value
    for the same key

    .. note::

        Dict structure is assumed to be composed of
        other dictionaries, numpy.ndarray, numpy.int32 and
        numpy.float64

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
    equal_values : bool
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
    errmsg = ('dic1/2 are not dictionaries')
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

        elif isinstance(dict1[key], np.ndarray):
            equal_value, diff, output_res = equal_ndarray(dict1[key], dict2[key], key, ig_n_tol)

        elif (dict1[key].dtype == 'int32' or dict1[key].dtype == 'float64'):
            equal_value, diff, output_res = equal_scalar(dict1[key], dict2[key], key, ig_n_tol)

        else:
            errmsg = (f'dict must only contain values of type dict, np.ndarray, np.int32,or np.float64 '
                      f'but found type {type(dict1[key])}')
            known_types_present = False
            assert known_types_present, errmsg

        equal_per_key.append(equal_value)

        if not equal_value:
            print(f'\n !!! discrepancy found at {key_path}')
            print(f' difference: {diff}')
            output_res_dict[key] = [output_res, "# !!!!FAIL!!!!"]
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


def hdf5_to_dict(file_path):
    r"""
    Read the hdf5 file and return it in the form of dictionary

    Parameters
    ----------
    file_path : str
        path to the hdf5 file

    Returns
    -------
    hdf5_dict : dict
       data from the hdf5 file in the form of dictionary

    """
    hdf5_dict = {}
    with h5py.File(file_path, 'r') as file:
        # Recursively traverse all groups and datasets within the file
        def traverse_datasets(name, node):
            if isinstance(node, h5py.Dataset):
                hdf5_dict[name] = node[()]
            elif isinstance(node, h5py.Group):
                for key in node.keys():
                    traverse_datasets(f"{name}/{key}", node[key])
        
        # Start traversing the file, starting with the root group
        for key in file.keys():
            traverse_datasets(key, file[key])
    
    return hdf5_dict


def save_dict_to_hdf5(group, dictionary):
    """
    Saved the dictionary into HDF5 file recursively.
    Parameters
    ----------
    group : HDF5 file
        file, where the dictionary will be saved
    
    dictionary: dict
        dictionary with the information which will be saved

    Returns
    -------
    None
    .. note::
        The initial passed group will be changed itself in-place
    """
    for key, value in dictionary.items():
        if isinstance(value, dict):
            # Если значение является словарем, создаем подгруппу и рекурсивно сохраняем туда данные
            subgroup = group.create_group(key)
            save_dict_to_hdf5(subgroup, value)
        else:
            if len(value) == 1:
                group.create_dataset(key, data=value[0])
            elif len(value) == 2:
                dset = group.create_dataset(key, data=value[0].astype('S'), dtype=h5py.string_dtype(encoding='ascii'))
                dset.attrs['attribute'] = value[1]


def equal_values(file1, file2, ig_n_tol):
    """
    Checks if two h5 files contain the same hierarchy/groups/datasets


    Parameters
    ----------
    file1 : str
       first  HDF5 file name
    file2 : str
       second  HDF5 file name
    ig_n_tol : dict
       dictionary of keywords and tolerances needed to make comparison on files

    Returns
    -------
    equal_values : bool
       boolean specifying if both h5 files contain the same information
    diff : str
        string which contains the information about the number of
        failed tests

    .. note::
        Also, the file {name_of_file}_errors_file.h5 will be generated in case of the fail
        of some comparisons.
    """

    h51_dict = hdf5_to_dict(file1)
    h52_dict = hdf5_to_dict(file2)

    if 'test keywords' in ig_n_tol:
        h51_del_keys = [key for key in h51_dict.keys() if key not in ig_n_tol['test keywords']]
        h52_del_keys = [key for key in h52_dict.keys() if key not in ig_n_tol['test keywords']]

        for key in h51_del_keys:
            del h51_dict[key]
        for key in h52_del_keys:
            del h52_dict[key]

        errmsg = ('no entries left in dict after applying \'test keywords\'')
        assert len(h51_dict) > 0, errmsg
        assert len(h52_dict) > 0, errmsg
        
    equal_values, diff, output_res_dict = equal_dict(h51_dict, h52_dict, ig_n_tol, 'top of h5')
    
#    if not equal_values:
    errors_file_name = f"{file2[:file2.find('.h5')]}_errors_file.h5"
    with h5py.File(errors_file_name, 'w') as f:
        print(errors_file_name)
        save_dict_to_hdf5(f, output_res_dict)

    return equal_values, diff
