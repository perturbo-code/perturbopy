import pytest
from perturbopy import testing_code


def do_tests(testing_args):
    testing_args.insert(0, testing_code.__file__)
    pytest.main(testing_args)
