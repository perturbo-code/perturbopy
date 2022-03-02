import sys
import argparse
from perturbopy.test_utils.run_test.run_utils import read_test_tags

test_folder_list = [
                    'epwan1-bands',
                    'epwan1-setup',
                   ]

command_line_args = sys.argv[1:]

print(command_line_args)

print('\nThese test folders will used:')
print('\n'.join(test_folder_list))
print('')
sys.stdout.flush()


print('TAGS:')
print(read_test_tags(test_folder_list[0]), '\n')
print(read_test_tags(test_folder_list[1]), '\n')
