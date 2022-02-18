"""
   This module contains functions to compare hdf5 files
"""
import hdfdict
import numpy as np

def equal_scalar(scalar1, scalar2, key, ig_n_tol):
   """
      Determines if two scalars contain the same value

      Parameters
      -----
         scalar1     first  scalar (numpy.dtype) 
         scalar2     second scalar (numpy.dtype)
         key         key associated with this scalar
         ig_n_tol    dict of ignore keywords and tolerances
                     needed to make comparison on values
      
      Returns
      -----
         equal_value boolean specifying if both scalars 
                     contain the same values
      
      Warns
      -----
         None
   """
   # check that scalar1 and scalar2 are Numbers 
   errmsg = ('scalar1/2 are not float64 or int32')
   assert (  (scalar1.dtype == 'int32'   and scalar2.dtype == 'int32')  
           or
             (scalar1.dtype == 'float64' and scalar2.dtype == 'float64')  
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
      -----
         ndarray1     first numpy ndarray  
         ndarray2     second numpy ndarray 
         ig_n_tol     dict of ignore keywords and tolerances
                      needed to make comparison on values
      
      Returns
      -----
         equal_vlaues boolean specifying if both ndarrays 
                      are equivalent 
      
      Warns
      -----
         None
   """
   errmsg = ('ndarray1/2 are not ndarrays')
   assert isinstance(ndarray1, np.ndarray) and isinstance(ndarray2, np.ndarray)
   
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
   



def equal_dict(dict1, dict2, ig_n_tol):
   """
      Determines if two dicts contain the same value
      for the same key 
   
      NOTE: Dict structure is assumed to be composed of 
      other dictionaries, numpy.ndarray, numpy.int32 and
      numpy.float64

      Parameters
      -----
         dict1        first  dict
         dict2        second dict
         ig_n_tol     dict of ignore keywords and tolerances
                      needed to make comparison on values
      
      Returns
      -----
         equal_vlaues boolean specifying if both dicts 
                      contain the same keys and values
      
      Warns
      -----
         None
   """
   # check that dict1 and dict2 are dictionaries
   errmsg = ('dic1/2 are not dictionaries')
   assert isinstance(dict1,dict) and isinstance(dict2,dict), errmsg

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
         equal_per_key.append(equal_dict(dict1[key], dict2[key],ig_n_tol))
      
      elif isinstance(dict1[key], np.ndarray):
         equal_per_key.append(equal_ndarray(dict1[key], dict2[key], key, ig_n_tol))
      
      elif (dict1[key].dtype == 'int32' or dict1[key].dtype == 'float64'):
         equal_per_key.append(equal_scalar(dict1[key], dict2[key], key, ig_n_tol))
      
      else:
         errmsg = (f'dict must only contain values of type dict, np.ndarray, np.int32,or np.float64 '
                   f'but found type {type(dict1[key])}')
         known_types_present = False
         assert known_types_present, errmsg 

   # equal dicts produce list of only bool=True
   equal_values  = (len(equal_per_key) == sum(equal_per_key))
   return equal_values 

def equal_values(file1, file2, ig_n_tol):
   """
      Checks if two h5 files contain the same 
      hierarchy/groups/datasets


      Parameters
      -----
         file1       first  h5 file
         file2       second h5 file
         ig_n_tol    dictionary of keywords and tolerances
                     needed to make comparison on files
      
      Returns
      -----
         equal_vlaues boolean specifying if both h5 files 
                      contain the same information 
      
      Warns
      -----
         None
   """
   h51_dict = dict(hdfdict.load(file1))
   h52_dict = dict(hdfdict.load(file2))

   if 'test keywords' in ig_n_tol:
      h51_del_keys = [ key for key in h51_dict.keys() if key not in ig_n_tol['test keywords'] ]
      h52_del_keys = [ key for key in h52_dict.keys() if key not in ig_n_tol['test keywords'] ]

      for key in h51_del_keys:
         del h51_dict[key]
      for key in h52_del_keys:
         del h52_dict[key]

      errmsg = ('no entries left in dict after applying \'test keywords\'')
      assert len(h51_dict) > 0, errmsg
      assert len(h52_dict) > 0, errmsg


   return equal_dict(h51_dict, h52_dict, ig_n_tol)
