import pytest
import os
import sys
from perturbopy import testing_code


def do_tests(testing_args):
    dir_path = os.path.dirname(testing_code.__file__)
    testing_args.insert(0, dir_path)
    result = pytest.main(testing_args)
    return result


def main():
    result = do_tests(sys.argv[1:])
    sys.exit(result)
