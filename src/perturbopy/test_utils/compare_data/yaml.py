"""
   This module contains functions to compare YAML files
"""
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from numbers import Number
import numpy as np
import perturbopy.test_utils.compare_data.h5 as ch5


def open_yaml(file_name):
   """
   Load YAML file as dictionary

   Parameters
   ----------
   file_name : str
      name of YAML file to be loaded

   Returns
   -------
   yaml_dict : dict
      YAML file loaded as dict

   """
   with open(file_name, 'r') as file:
      yaml_dict = load(file, Loader=Loader)
   return yaml_dict


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
   errmsg = ('scalar1/2 are not Numbers')
   assert isinstance(scalar1, Number) and isinstance(scalar2, Number), errmsg

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


def equal_list(list1, list2, key, ig_n_tol):
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

   Returns
   -------
   equal_vlaues : bool
      boolean specifying if both lists are equivalent
   
   """
   # check that list1 and list2 are lists
   errmsg = ('list1/2 are not lists')
   assert isinstance(list1, list) and isinstance(list2, list), errmsg
   
   errmsg = ('list1/2 are not the same length')
   assert len(list1) == len(list2), errmsg

   # check if lists can be converted to ndarray
   if (all(isinstance(x, Number) for x in list1) and all(isinstance(x, Number) for x in list2)):
      # compare lists as nparrays for speed up
      return ch5.equal_ndarray(np.array(list1),
                               np.array(list2),
                               key,
                               ig_n_tol)
   
   # a list of bool values
   equal_per_item = []

   for item1, item2 in zip(list1, list2):
      errmsg = ('list1/2 values'
                'are not of the same type')
      assert type(item1) == type(item2), errmsg
      
      if isinstance(item1, dict):
         equal_per_item.append(equal_dict(item1, item2, ig_n_tol))
      
      elif isinstance(item1, list):
         equal_per_item.append(equal_list(item1, item2, key, ig_n_tol))
      
      elif isinstance(item1, Number):
         equal_per_item.append(equal_scalar(item1, item2, key, ig_n_tol))
      
      elif isinstance(item1, str):
         equal_per_item.append(item1 == item2)
      
      elif isinstance(item1, type(None)):
         equal_per_item.append(item1 == item2)
      
      else:
         errmsg = ('list must only contain values of type dict, list, scalar, None, or str')
         known_types_present = False
         assert known_types_present, errmsg

   # equal dicts produce list of only bool=True
   equal_values  = (len(equal_per_item) == sum(equal_per_item))
   return equal_values


def equal_dict(dict1, dict2, ig_n_tol):
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
   
   Returns
   -------
   equal_vlaues : bool
      boolean specifying if both dicts contain the same keys and values
   
   """
   # check that dict1 and dict2 are dictionaries
   errmsg = ('dic1/2 are not dictionaries')
   assert isinstance(dict1, dict) and isinstance(dict2, dict), errmsg

   # check that dictionaries have the same keys
   errmsg = ('dict1/2  do not have the same keys')
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
      
      if isinstance(dict1[key], dict):
         equal_per_key.append(equal_dict(dict1[key], dict2[key], ig_n_tol))
      
      elif isinstance(dict1[key], list):
         equal_per_key.append(equal_list(dict1[key], dict2[key], key, ig_n_tol))
      
      elif isinstance(dict1[key], Number):
         equal_per_key.append(equal_scalar(dict1[key], dict2[key], key, ig_n_tol))
      
      elif isinstance(dict1[key], str):
         equal_per_key.append(dict1[key] == dict2[key])
      
      elif isinstance(dict1[key], type(None)):
         equal_per_key.append(dict1[key] == dict2[key])
      
      else:
         errmsg = (f'dict must only contain values of type dict, list, scalar, None, or str '
                   f'but found type {type(dict1[key])}')
         known_types_present = False
         assert known_types_present, errmsg

   # equal dicts produce list of only bool=True
   equal_values  = (len(equal_per_key) == sum(equal_per_key))
   return equal_values


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

   return equal_dict(yaml1_dict, yaml2_dict, ig_n_tol)
