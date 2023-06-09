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
