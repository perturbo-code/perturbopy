from perturbopy.test_utils.run_test.test_driver import get_test_materials
from perturbopy.test_utils.run_test.test_driver import clean_test_materials
from perturbopy.test_utils.compare_data.compare import equal_values

import os
import sys
import pytest
import subprocess

@pytest.mark.order(before="test_qe2pert")
@pytest.mark.order(after="test_qe2pert")
def test_perturbo(test_name):
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

    # run test, get files paths, get comparisons settings
    (ref_outs,
     new_outs,
     igns_n_tols) = get_test_materials(test_name)

    # compare all files
    for ref_file, new_file, ign_n_tol in zip(ref_outs,new_outs,igns_n_tols):

        ref_file_short = '/'.join(os.path.normpath(ref_file).split(os.sep)[-3:])
        new_file_short = '/'.join(os.path.normpath(new_file).split(os.sep)[-3:])

        #print(f'\ncomparing files {ref_file_short} and {new_file_short}')
        print(f'\n comparing files: \n {ref_file}  {new_file}')

        errmsg = (f'files {ref_file} and {new_file} do not match')
        assert equal_values(ref_file, new_file, ign_n_tol), errmsg

    #clean up test materials
    clean_test_materials(test_name, new_outs)
    print('')
    
    
def test_qe2pert():
    assert True
