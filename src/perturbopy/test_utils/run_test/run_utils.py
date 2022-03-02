"""
   Utils to select which tests to run based on the command line arguments and
   test tags.
"""
import os
import sys
from perturbopy.test_utils.compare_data.yaml import open_yaml

def read_test_tags(test_name):
   """
   Get a list of tags for a given test.

   Parameters
   ----------
      test_name : str
         name of the folder inside the tests/ folder

   Returns
   -------
      tag_list : list
         list of tags for a given test
   """

   cwd = os.getcwd()

   driver_path_suffix = 'tests_perturbo/' + test_name 
   perturbo_driver_dir_path = [x[0] for x in os.walk(cwd) if x[0].endswith(driver_path_suffix)][0]

   pert_input = open_yaml(f'{perturbo_driver_dir_path}/pert_input.yml')

   input_tags = []
   if 'tags' in pert_input:
      input_tags = pert_input['tags']

   print(pert_input)
   sys.stdout.flush()
