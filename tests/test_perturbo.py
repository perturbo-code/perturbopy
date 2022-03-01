from perturbopy.test_utils.run_test.test_driver import get_test_materials
from perturbopy.test_utils.compare_data.compare import equal_values 

import os
import pytest
import subprocess


@pytest.mark.parametrize('test_name', [
                                       'epwan1-bands',
                                       'epwan1-setup',
                                      ]
                        )
def test_epwan1_bands(test_name):
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

   # run test, get files paths, get comparisons settings
   (ref_outs,
    new_outs,
    igns_n_tols) = get_test_materials(test_name)

   # compare all files
   for ref_file, new_file, ign_n_tol in zip(ref_outs,new_outs,igns_n_tols):
      ref_file_short = os.path.basename(ref_file)
      new_file_short = os.path.basename(new_file)
      print(f'\ncomparing files {ref_file_short} and {new_file_short}')
      errmsg = (f'files {ref_file} and {new_file} do not match')
      assert equal_values(ref_file, new_file, ign_n_tol), errmsg
