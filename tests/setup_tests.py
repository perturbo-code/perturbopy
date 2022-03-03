import sys
import argparse
from perturbopy.test_utils.run_test.run_utils import read_test_tags, parse_args

tests_folder_list = [
                    'epwan1-bands',
                    'epwan1-setup',
                   ]

args = parse_args(sys.argv[1:])

tests_folder_run_list = []



print(args.tags)
print(args.exclude_tags)

print('\nThese test folders will used:')
print('\n'.join(test_folder_list))
print('')

print('TAGS:')
print(read_test_tags(test_folder_list[0]), '\n')
print(read_test_tags(test_folder_list[1]), '\n')
sys.stdout.flush()


