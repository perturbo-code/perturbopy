"""
How this works.

In the tests fodler, the test_perturbo.py script runs Perturbo for
a given 'test_name'. The idea is to use the same function (test_perturbo())
to run all of the calc. modes, ephr files, etc. All of this should be
happening under the pytest environment (ran by `pytest`).

In this file (conftest.py), we parametrize pytest to make this work.
"""

from perturbopy.test_utils.run_test.run_utils import get_all_tests
from perturbopy.test_utils.run_test.run_utils import filter_tests
from perturbopy.test_utils.run_test.test_driver import clean_ephr_folders
import pytest

# define all supplementary arguments for the test running. This function declared in the PyTest itself


def pytest_addoption(parser):

    parser.addoption('--tags',
                     help = 'List of tags to include in this testsuite run.',
                     nargs='*', default = None)

    parser.addoption('--exclude-tags',
                     help = 'List of tags to exclude from this testsuite run.',
                     nargs='*', default = None)
                     
    parser.addoption('--ephr_tags',
                     help = 'List of ephr_tags to include in this testsuite run.',
                     nargs='*', default = None)

    parser.addoption('--exclude-ephr_tags',
                     help = 'List of ephr_tags to exclude from this testsuite run.',
                     nargs='*', default = None)

    parser.addoption('--epwan',
                     help = 'List of epwan files to test.',
                     nargs='*', default = None)

    parser.addoption('--test-names',
                     help = 'List of test folder names to include in this testsuite run.',
                     nargs='*', default = None)

    parser.addoption('--devel',
                     help = 'Include the development-stage tests.',
                     action='store_true', default = False)

    parser.addoption('--run_qe2pert',
                     help = 'Include the qe2pert tests',
                     action='store_true')
                     
    parser.addoption('--config_machine',
                     help = 'Name of file with computational information for qe2pert computation. Should be in the folder tests_f90/comp_qe2pert',
                     nargs="?", default='config_machine.yml')
                     
    parser.addoption('--keep_perturbo',
                     help = 'Save all the materials related to perturbo tests',
                     action='store_true')
                     
    parser.addoption('--keep_ephr',
                     help = 'Save all ephr-files from the qe2pert testing',
                     action='store_true')
                     
    parser.addoption('--keep_preliminary',
                     help = 'Save all preliminary files for ephr calculation',
                     action='store_true')

# generation of test for each type of test function. This function automatically called,
# when we run tests from the subfolders of folder, where this function is saved.


def pytest_generate_tests(metafunc):
    """
    The purpose of this function is to feed multiple test names to the
    tests/test_perturbo.py test_perturbo(test_name) function. 
    Here, this function is referred as 'metafunc'.

    First, we get the list of all of the test folders using the tests/epwan_info.yml file.
    We retrieve the test folder as <epwan name>-<test name>. This is done by the get_all_tests()
    function.

    Next, we remove some of the tests based on the command line options and obtain the target
    test_list using the filer_tests() function.

    Finally, we feed the elements of the test_list to the test_perturbo() (metafunction)
    as the test_name input argument of the function.
    """
    if 'test_name' in metafunc.fixturenames:

        # Get the list of all test folders
        all_test_list, all_dev_test_list = get_all_tests(metafunc.function.__name__)

        # Add the devel tests if --devel was specified
        if  metafunc.config.getoption('devel'):
            all_test_list += all_dev_test_list

        if (metafunc.function.__name__ == 'test_perturbo') or (metafunc.function.__name__ == 'test_perturbo_for_qe2pert'):
        # sort out test folders based on command-line options (if present)
            test_list = filter_tests(
                                     all_test_list,
                                     metafunc.config.getoption('tags'),
                                     metafunc.config.getoption('exclude_tags'),
                                     metafunc.config.getoption('epwan'),
                                     metafunc.config.getoption('test_names'),
                                     metafunc.function.__name__
                                    )
        elif (metafunc.function.__name__ == 'test_qe2pert'):
            test_list = filter_tests(
                                     all_test_list,
                                     metafunc.config.getoption('ephr_tags'),
                                     metafunc.config.getoption('exclude_ephr_tags'),
                                     metafunc.config.getoption('epwan'),
                                     None,
                                     metafunc.function.__name__
                                    )
        
        if metafunc.function.__name__ == 'test_perturbo_for_qe2pert' or metafunc.function.__name__ == 'test_qe2pert':
            metafunc.parametrize('test_name', test_list, indirect=True)
            metafunc.parametrize('run_qe2pert', [metafunc.config.getoption('run_qe2pert')], indirect=True)
            metafunc.parametrize('config_machine', [metafunc.config.getoption('config_machine')], indirect=True)
        elif metafunc.function.__name__ == 'test_perturbo':
            metafunc.parametrize('test_name', test_list, indirect=True)
            metafunc.parametrize('config_machine', [metafunc.config.getoption('config_machine')], indirect=True)
        
# in order to properly run pytest functions, we need to declare fixtures,
# which allow us to use parametrization of test functions


@pytest.fixture
def test_name(request):
    return request.param
    

@pytest.fixture
def run_qe2pert(request):
    return request.param


@pytest.fixture
def config_machine(request):
    return request.param
    

@pytest.fixture
def clean_tests(request):
    return request.param
    
# # this is predefined function of PyTest, which is runned after the end of all tests
# def pytest_unconfigure(config):
#     # Run your auxiliary function here
#     if config.getoption('clean_tests'):
#         clean_test_folder()
        

# this is predefined function of PyTest, which is runned after the end of all tests.
# here we delete all ephr-folders, for which all tests were passed
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if config.getoption('run_qe2pert'):
        if exitstatus == 0:
            # delete all ephr files
            ephr_failed=[]
        else:
            failed_reports = terminalreporter.getreports('failed')
            # Process the list of failed test reports as needed
            ephr_failed = set()
            for report in failed_reports:
                # obtain ephr-name of failed test
                ephr_failed.add(report.nodeid.split("[")[1].rstrip("]").split('-')[0])
                ephr_failed = list(ephr_failed)
    
        clean_ephr_folders(ephr_failed, config.getoption('config_machine'), config.getoption('keep_ephr'), config.getoption('keep_preliminary'))