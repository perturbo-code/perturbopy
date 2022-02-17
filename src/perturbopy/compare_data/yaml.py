"""
   This module contains functions to compare yaml files
"""
from yaml import load,dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from numbers import Number
import numpy as np

def open_yaml(file_name):
   """ 
      load yaml file as dictionary
   """
   with open(file_name,'r') as file:
      yaml_dict = load(file, Loader=Loader)
   return yaml_dict


def equal_keys(file1, file2):
   """
      Determines if two yaml files contain the same keys 

      Parameters
      -----
         file1    first  yaml file
         file2    second yaml file
      
      Returns
      -----
         equal_keys     boolean specifying if both yaml files
                        contain the same keys
      
      Warns
      -----
         None
   """
   equal_keys = False
   
   yaml1 = open_yaml(file1)
   yaml2 = open_yaml(file2)

   yaml1_keys = set(yaml1.keys())
   yaml2_keys = set(yaml2.keys())
  
   equal_keys = (yaml1_keys == yaml2_keys)
   
   return equal_keys

def equivalent(obj1, obj2, key, tol):
   """
      function to determine in objects are equivalent.
      if the function is a number the delta arg determines
      the condition of equivalence
   """
   # check that both objs are the same type
   errmsg = ('obj1 and obj2 are not the same \'type\'')
   assert type(obj1) == type(obj2), errmsg

   # check if obj is not a number 
   if not isinstance(obj1, Number):
      return (obj1 == obj2)
   else:
      # determine delta from tolerance
      if key in tol:
         delta = tol[key]
      else:
         delta = tol['default']

      obj1 = np.array(obj1)
      obj2 = np.array(obj2)
      return np.allclose(obj1, obj2, atol=float(delta), rtol=0.0, equal_nan=True)

def equal_dict(yaml1, yaml2, ig_n_tol):
   """
   """
   # dict of tolerances for comparisons
   tol = ig_n_tol['tolerance']

   # total set of keys
   keys = set(yaml1.keys())

   # keys to nested dictionaries
   keys_to_dicts = set()

   for key in yaml1.keys():
      # remove 'ignore keys'
      if key in set(ig_n_tol['ignore keywords']):
         keys.remove(key)
      # set aside nested dictionaries
      elif isinstance(yaml1[key], dict):
         keys.remove(key)
         keys_to_dicts.add(key)
   
   # a list of bool values
   equal_per_key = [equivalent(yaml1[key], yaml2[key],key,tol) for key in keys]

   for key in keys_to_dicts:
      equal_per_key.append(equal_dict(yaml1[key], yaml2[key], ig_n_tol))
   
   # equal dicts produce list of only bool=True
   equal_values  = (len(equal_per_key) == sum(equal_per_key))

   return equal_values 

def equal_values(file1, file2, ig_n_tol):
   """
      Determines if two yaml files contain the same value
      for the same key 

      Parameters
      -----
         file1       first  yaml file
         file2       second yaml file
         ig_n_tol    dictionary of keywords and tolerances
                     needed to make comparison on files
      
      Returns
      -----
         equal_vlaues boolean specifying if both yaml files 
                      contain the same keys and values
      
      Warns
      -----
         None
   """
   errmsg = ('yaml files must contain the same keys in '
             'order to be able to compare values')
   assert equal_keys(file1, file2), errmsg
   
   yaml1 = open_yaml(file1)
   yaml2 = open_yaml(file2)

   return equal_dict(yaml1, yaml2, ig_n_tol)



