from perturbopy.test_utils.run_test.test_driver import get_test_materials, run_epr_calculation
from perturbopy.test_utils.run_test.test_driver import clean_test_materials
from perturbopy.test_utils.compare_data.compare import equal_values

import os
import sys
import pytest
import subprocess


@pytest.mark.order(before="test_qe2pert")
def test_perturbo(test_name, config_machine, keep_perturbo, source_folder, test_case='perturbo'):
    """
    Driver to run the tests for the perturbo.x executable.

    Parameters
    -----
    test_name : str
        name of the folder inside the tests/ folder
    test_case : str
        define what type of the test we run - for perturbo testing or for the
        qe2pert testing.
    config_machine : str
        name of file with computational information, which we'll use in this set of computations.
        Should be in folder source_folder/config_machine
    source_folder : str
        name of the folder, where should be all the testing supplementary files (reference, input files, etc.)

    Returns
    -----
    None
    """

    # run test, get files paths, get comparisons settings
    (ref_outs,
     new_outs,
     igns_n_tols) = get_test_materials(test_name, test_case, config_machine, source_folder)

    # compare all files
    for ref_file, new_file, ign_n_tol in zip(ref_outs, new_outs, igns_n_tols):

        # print(f'\ncomparing files {ref_file_short} and {new_file_short}')
        print(f'\n comparing files: \n {ref_file}  {new_file}')

        errmsg = (f'files {ref_file} and {new_file} do not match')
        assert equal_values(ref_file, new_file, ign_n_tol), errmsg

    # clean up test materials
    if not keep_perturbo:
        clean_test_materials(test_name, new_outs, config_machine, source_folder)
    print('')
    
    
def test_qe2pert(test_name, run_qe2pert, config_machine, source_folder):
    """
    Driver to run the the qe2pert set of computations.

    Parameters
    -----
    test_name : str
        name of the computing epr-file
    run_qe2pert : bool
        do we run qe2pert testing or not
    config_machine : str
        name of file with computational information, which we'll use in this set of computations.
        Should be in folder source_folder/config_machine
    source_folder : str
        name of the folder, where should be all the testing supplementary files (reference, input files, etc.)

    Returns
    -----
    None
    """
    if not run_qe2pert:
        pytest.skip("Skipping by default, pass the --run_qe2pert arg in the command line for this test")
    run_epr_calculation(test_name, config_machine, source_folder)
    assert True
    

# @pytest.mark.order(after="test_qe2pert")
# def test_perturbo_for_qe2pert(test_name, run_qe2pert, config_machine, keep_perturbo, source_folder):
#     """
#     Second driver to run the tests for the perturbo.x executable.
#     We call it only in the case if we call test_qe2pert as well
#
#     Parameters
#     -----
#     test_name : str
#         name of the folder inside the tests/ folder
#     run_qe2pert : str
#         do we run qe2pert testing or not
#     source_folder : str
#         name of the folder, where should be all the testing supplementary files (reference, input files, etc.)
#     Returns
#     -----
#     None
#     """
#     if not run_qe2pert:
#         pytest.skip("Skipping by default, pass the --run_qe2pert arg in the command line for this test")
#     test_perturbo(test_name, config_machine, keep_perturbo, source_folder, test_case='perturbo_for_qe2pert')
