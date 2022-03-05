"""
   This module contains functions to compare hdf5 files
"""
import hdfdict
import numpy as np


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

   """
   # check that scalar1 and scalar2 are Numbers
   errmsg = ('scalar1/2 are not float64 or int32')
   assert (
          (scalar1.dtype == 'int32' and scalar2.dtype == 'int32')
          or (scalar1.dtype == 'float64' and scalar2.dtype == 'float64')
          ), errmsg

   # dict of tolerances for comparisons
   tol = ig_n_tol['tolerance']
   # check if key for scalar has set tolerance
   if key in tol:
      delta = tol[key]
   else:
      delta = tol['default']

   equal_value = np.allclose(np.array(scalar1),
                             np.array(scalar2),
                             atol=float(delta),
                             rtol=0.0,
                             equal_nan=True)
   return equal_value


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

   """
   errmsg = ('ndarray1/2 are not ndarrays')
   assert isinstance(ndarray1, np.ndarray) and isinstance(ndarray2, np.ndarray), \
          errmsg

   # dict of tolerances for comparisons
   tol = ig_n_tol['tolerance']
   # check if key for scalar has set tolerance
   if key in tol:
      delta = tol[key]
   else:
      delta = tol['default']

   equal_value = np.allclose(ndarray1,
                             ndarray2,
                             atol=float(delta),
                             rtol=0.0,
                             equal_nan=True)
   return equal_value


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

   for key in keys:
      errmsg = (f'dict1/2 values associated with key:{key} '
                f'are not of the same type')
      assert type(dict1[key]) == type(dict2[key]), errmsg

      # pseudo path to current item being compared
      key_path = (f'{path}.{key}')
      if isinstance(dict1[key], dict):
         equal_value = equal_dict(dict1[key], dict2[key], ig_n_tol, key_path)

      elif isinstance(dict1[key], np.ndarray):
         equal_value = equal_ndarray(dict1[key], dict2[key], key, ig_n_tol)

      elif (dict1[key].dtype == 'int32' or dict1[key].dtype == 'float64'):
         equal_value = equal_scalar(dict1[key], dict2[key], key, ig_n_tol)

      else:
         errmsg = (f'dict must only contain values of type dict, np.ndarray, np.int32,or np.float64 '
                   f'but found type {type(dict1[key])}')
         known_types_present = False
         assert known_types_present, errmsg

      equal_per_key.append(equal_value)

      if not equal_value:
         print(f'!!! discrepancy found at {key_path}')
         print(f' tolerance not respected: {ig_n_tol["tolerance"]}')

   # equal dicts produce list of only bool=True
   equal_values  = (len(equal_per_key) == sum(equal_per_key))
   return equal_values


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

   """
   h51_dict = dict(hdfdict.load(file1))
   h52_dict = dict(hdfdict.load(file2))

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

   return equal_dict(h51_dict, h52_dict, ig_n_tol, 'top of h5')
