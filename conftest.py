from perturbopy.test_utils.run_test.run_utils import get_all_tests
from perturbopy.test_utils.run_test.run_utils import filter_tests

def pytest_addoption(parser):

   parser.addoption('--tags',
                    help = 'List of tags to include in this testsuite run.',
                    nargs='*', default = None)

   parser.addoption('--exclude-tags',
                    help = 'List of tags to exclude from this testsuite run.',
                    nargs='*', default = None)

   parser.addoption('--test-names',
                    help = 'List of test folder names to include in this testsuite run.',
                    nargs='*', default = None)


def pytest_generate_tests(metafunc):
   if 'test_name' in metafunc.fixturenames:

      # Get the list of all test folders
      all_test_list = get_all_tests()

      # sort out folders based on command-line options (if present)
      test_list = filter_tests(
                               all_test_list,
                               metafunc.config.getoption('tags'),
                               metafunc.config.getoption('exclude_tags'),
                               metafunc.config.getoption('test_names'),
                              )

      metafunc.parametrize('test_name', test_list)
