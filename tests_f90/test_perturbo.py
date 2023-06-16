from perturbopy.test_utils.run_test.test_driver import get_test_materials, run_ephr_calculation
from perturbopy.test_utils.run_test.test_driver import clean_test_materials
from perturbopy.test_utils.compare_data.compare import equal_values

import os
import sys
import pytest
import subprocess


@pytest.mark.order(before="test_qe2pert")
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
    
    # DELETE !!!!!!!!!!!!!!
    # if "RUN_QE2PERT_2" not in os.environ or os.environ["RUN_QE2PERT_2"]!='1':
    #     pytest.skip("Skipping by default, set the 'RUN_QE2PERT=1' environment variable to run this test")

    # run test, get files paths, get comparisons settings
    (ref_outs,
     new_outs,
     igns_n_tols) = get_test_materials(test_name)

    # compare all files
    for ref_file, new_file, ign_n_tol in zip(ref_outs,new_outs,igns_n_tols):

        ref_file_short = '/'.join(os.path.normpath(ref_file).split(os.sep)[-3:])
        new_file_short = '/'.join(os.path.normpath(new_file).split(os.sep)[-3:])

        # print(f'\ncomparing files {ref_file_short} and {new_file_short}')
        print(f'\n comparing files: \n {ref_file}  {new_file}')

        errmsg = (f'files {ref_file} and {new_file} do not match')
        assert equal_values(ref_file, new_file, ign_n_tol), errmsg

    # clean up test materials
    clean_test_materials(test_name, new_outs)
    print('')
    
    
def test_qe2pert(test_name, run):
    """
    Driver to run the the qe2pert.x executable in the test format.

    Parameters
    -----
       test_name : str
          name of the folder inside the tests/ folder

    Returns
    -----
       None
    """
    if not run:
        pytest.skip("Skipping by default, pass the --run_qe2pert arg in the command line for this test")
    run_ephr_calculation(test_name)
    

@pytest.mark.order(after="test_qe2pert")
def test_perturbo_for_qe2pert(test_name, run):
    # CHANGE ON RUN_QE2PERT !!!!!!!!!!!!!!
    # if "RUN_QE2PERT_2" not in os.environ or os.environ["RUN_QE2PERT_2"]!='1':
    #     pytest.skip("Skipping by default, set the 'RUN_QE2PERT=1' environment variable to run this test")
    if not run:
        pytest.skip("Skipping by default, pass the --run_qe2pert arg in the command line for this test")
    test_perturbo(test_name)
    
