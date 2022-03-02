"""
   Utils to select which tests to run based on the command line arguments and
   test tags.
"""
import os
import sys
from perturbopy.test_utils.compare_data.yaml import open_yaml

def read_test_tags(test_name):
   """
   Get a list of tags for a given test. List of tags is combined from the tags from
   pert_input.yml and epwan_info.yml for a given epwan file.

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

   epwan_name = pert_input['epwan']

   epwan_dict_path = os.path.join('refs_perturbo','epwan_files','epwan_info.yml')

   epwan_info = open_yaml(epwan_dict_path)

   epwan_tags = []
   if 'tags' in epwan_info:
      epwan_tags = epwan_info['tags']

   tag_list = input_tags + epwan_tags
   tag_list = list(set(tag_list))

   return tag_list
