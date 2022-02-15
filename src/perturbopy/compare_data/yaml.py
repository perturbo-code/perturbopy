"""
   This module contains functions to compare yaml files
"""
import yaml

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
   with open(file1) as f1, open(file2) as f2:
      yaml1  = yaml.load(f1, Loader=yaml.FullLoader)
      yaml2  = yaml.load(f2, Loader=yaml.FullLoader)
      
      yaml1_keys = set(yaml1.keys())
      yaml2_keys = set(yaml2.keys())
  
   equal_keys = (yaml1_keys == yaml2_keys)
   
   return equal_keys

def equal_values(file1, file2):
   """
      Determines if two yaml files contain the same value
      for the same key 

      Parameters
      -----
         file1    first  yaml file
         file2    second yaml file
      
      Returns
      -----
         equal_vlaues boolean spcifying if both yaml files 
                      contain the same keys and values
      
      Warns
      -----
         None
   """
   errmsg = ('yaml files must contain the same keys in '
             'order to be able to compare values')
   assert equal_keys(file1, file2), errmsg
   
   with open(file1) as f1, open(file2) as f2:
      yaml1  = yaml.load(f1, Loader=yaml.FullLoader)
      yaml2  = yaml.load(f2, Loader=yaml.FullLoader)
      
      keys = set(yaml1.keys())

   # a list of bool values
   equal_per_key = [yaml1[key] == yaml2[key] for key in keys]
   # equal dicts produce list of only bool=True
   equal_values  = (len(equal_per_key) == sum(equal_per_key))

   return equal_values 


