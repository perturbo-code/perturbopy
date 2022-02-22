from perturbopy.test_utils.run_test.test_driver import get_test_materials
from perturbopy.test_utils.compare_data.compare import equal_values 
from perturbopy.test_utils.compare_data.yaml import open_yaml

import os
import subprocess


def test_epwan1_bands():
   """
      driver to run tests_perturbo/epwan1-setup/ test

      Parameters
      -----
         None
      
      Returns
      -----
         None
      
      Warns
      -----
         None
   """
   # test name (also test dir name)
   test_name = 'epwan1-bands'

   # run test, get files paths, get comparisons settings
   (ref_outs,
    new_outs,
    igns_n_tols) = get_test_materials(test_name)

   # compare all files
   for ref_file, new_file, ign_n_tol in zip(ref_outs,new_outs,igns_n_tols):
      print(f'comparing files {ref_file} and {new_file}')
      errmsg = (f'files {ref_file} and {new_file} do not match')
      assert equal_values(ref_file, new_file, ign_n_tol), errmsg
