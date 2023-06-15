"""
How this works.

In the tests fodler, the test_perturbo.py script runs Perturbo for
a given 'test_name'. The idea is to use the same function (test_perturbo())
to run all of the calc. modes, epwan files, etc. All of this should be
happening under the pytest environment (ran by `pytest`).

In this file (conftest.py), we parametrize pytest to make this work.
"""

from perturbopy.test_utils.run_test.run_utils import get_all_tests
from perturbopy.test_utils.run_test.run_utils import filter_tests

def pytest_addoption(parser):

    parser.addoption('--tags',
                     help = 'List of tags to include in this testsuite run.',
                     nargs='*', default = None)

    parser.addoption('--exclude-tags',
                     help = 'List of tags to exclude from this testsuite run.',
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
        all_test_list, all_dev_test_list = get_all_tests()

        # Add the devel tests if --devel was specified
        if  metafunc.config.getoption('devel'):
            all_test_list += all_dev_test_list

        # sort out folders based on command-line options (if present)
        test_list = filter_tests(
                                 all_test_list,
                                 metafunc.config.getoption('tags'),
                                 metafunc.config.getoption('exclude_tags'),
                                 metafunc.config.getoption('epwan'),
                                 metafunc.config.getoption('test_names'),
                                )

        metafunc.parametrize('test_name', test_list)
