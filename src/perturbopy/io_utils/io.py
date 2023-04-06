"""
Open/close binary and ASCII files (HDF5, YAML, text inputs/outputs)

"""
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


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
