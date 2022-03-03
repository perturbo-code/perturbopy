test_folder_list = [
                    'epwan1-bands',
                    'epwan1-setup',
                   ]

def pytest_addoption(parser):

   parser.addoption('--tags',
                    help = 'List of tags to include in this testsuite run.',
                    nargs='*', default = None)

   parser.addoption('--names',
                    help = 'List of folder names to include in this testsuite run.',
                    nargs='*', default = None)

   parser.addoption('--exclude-tags',
                    help = 'List of tags to exclude from this testsuite run.',
                    nargs='*', default = None)

def pytest_generate_tests(metafunc):
   if 'test_name' in metafunc.fixturenames:
      print('*'*30+'HERE')
      print(metafunc.config.getoption('tags'))
      metafunc.parametrize('test_name', test_folder_list)
