"""
   Utils to select which tests to run based on the command line arguments and
   test tags.
"""
import os
import sys
import copy
import argparse
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

   # Read the tags from pert_input.yml
   input_tags = []
   if 'tags' in pert_input['test info'].keys():
      input_tags = pert_input['test info']['tags']

   # Read the tags from epwan_info.yml
   epwan_name = pert_input['test info']['epwan']

   epwan_dict_path = 'epwan_info.yml'

   epwan_info = open_yaml(epwan_dict_path)

   epwan_tags = []
   if 'tags' in epwan_info[epwan_name].keys():
      epwan_tags = epwan_info[epwan_name]['tags']

   tag_list = input_tags + epwan_tags
   tag_list = sorted(list(set(tag_list)))

   return tag_list


def get_all_tests():
   """
   Get the names of all test folders based on the epwan_info.yml file.

   Returns
   -------
   test_folder_list : list
      list of all test names
   """

   epwan_dict_path = 'epwan_info.yml'

   epwan_info = open_yaml(epwan_dict_path)

   test_folder_list = []

   for epwan in epwan_info:
      if 'tests' in epwan_info[epwan].keys():
         test_list = epwan_info[epwan]['tests']

         test_folder_list += [ f'{epwan}-{t}' for t in test_list ]

   return test_folder_list


def print_test_info(test_name, pert_input):
   """
   Print information about a test.

   Parameters
   ----------
   test_name : str
      name of the test folder
   pert_input : dict
      dictionary contatining the test info
   """

   if 'desc' in pert_input['test info']:
      desc = pert_input['test info']['desc']
   else:
      desc = None

   print(f'\n === Test folder === :\n {test_name}')

   if desc is not None:
      print(f'\n === Description === :\n {desc}')

   sys.stdout.flush()


def filter_tests(all_test_list, tags, exclude_tags, test_names):
   """
   Return the list of test folders based on command line options

   Parameters
   ----------
   all_test_list : list
      list of all the test folders
   tags : list or None
      list of tags to include
   exclude_tags : list or None
      list of tags to exclude
   test_names : list or None
      list of test folders to include

   Returns
   -------
   test_list : list
      list of test for a given pytest run

   Raises
   ------
   RuntimeError
      if --test-names and (--tags or --exclude_tags) are specified at the same time
      or
      if no test folders are selected

   ValueError
      if --test-names contains a name of a test that is not present
   """

   test_list = copy.deepcopy(all_test_list)

   # sort based on tags
   if tags is not None or exclude_tags is not None:
      for test_name in all_test_list:

         # tags for a given test
         test_tag_list = read_test_tags(test_name)
         
         # tags from command line
         if tags is not None:

            keep_test = False

            for tag in tags:
               if tag in test_tag_list:
                  keep_test = True
                  break

            if not keep_test:
               test_list.remove(test_name)

         # exclude tags from command line
         if exclude_tags is not None:
            
            keep_test = True

            for tag in exclude_tags:
               if tag in test_tag_list:
                  keep_test = False
                  break

            if not keep_test and test_name in test_list:
               test_list.remove(test_name)
            
   # test name from command line
   if test_names is not None:

      if tags is not None or exclude_tags is not None:
         errmsg = (
                   'If the --test-names option is specified, \n'
                   '--tags and --exclude_tags must NOT be specified.'
                  )

         raise RuntimeError(errmsg)
      
      for test_name_cmd in test_names:
         if test_name_cmd not in all_test_list:
            errmsg = (
                      f'Test {test_name_cmd} does not exist, \n'
                      'but specified in --test-names option.'
                     )
            raise ValueError(errmsg)

      test_list = test_names

   if not test_list:
      raise RuntimeError('No test folders selected')

   print('\n\n === Test folders == :')
   print(' \n'.join(test_list))
   print('')
   sys.stdout.flush()

   return test_list
