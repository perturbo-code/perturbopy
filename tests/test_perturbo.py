from perturbopy.test_utils.run_test.test_driver import get_test_materials
from perturbopy.test_utils.compare_data.compare import equal_values 

import os
import sys
import pytest
import subprocess
import setup_tests

@pytest.mark.parametrize('test_name', setup_tests.test_folder_list)
def test_epwan1_bands(test_name):
   """
   Driver to run the tests for the perturbo.x executable.

   Parameters
   -----
      test_name : str
         name of the folder inside the tests/ folder
   
   Returns
   -----
      None
   """

   print(f'\n === Test folder === : {test_name}\n')
   sys.stdout.flush()

   # run test, get files paths, get comparisons settings
   (ref_outs,
    new_outs,
    igns_n_tols) = get_test_materials(test_name)

   # compare all files
   for ref_file, new_file, ign_n_tol in zip(ref_outs,new_outs,igns_n_tols):
      ref_file_short = '/'.join(os.path.normpath(ref_file).split(os.sep)[-3:])
      new_file_short = '/'.join(os.path.normpath(new_file).split(os.sep)[-3:])
      print(f'\ncomparing files {ref_file_short} and {new_file_short}')
      errmsg = (f'files {ref_file} and {new_file} do not match')
      assert equal_values(ref_file, new_file, ign_n_tol), errmsg

   print('')
