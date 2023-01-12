import os
from subprocess import call
import numpy as np
repo_dir = 'C:/Users/shael/github/perturbopy'
conda_path = 'C:/Users/shael/Anaconda3/Scripts/conda.exe'

os.chdir(repo_dir)
call(['pip','install','.'])

from perturbopy.postproc.utils.constants import *

# Test prefix_exp
assert(prefix_exp('m') == -3)
assert(prefix_exp('M') == 6)
assert(prefix_exp('mu') == -6)
assert(prefix_exp('Y') == 24)
assert(prefix_exp('') == 0)

# Test prefix_conversion_exp
assert(prefix_conversion_exp('m') == 3)
assert(prefix_conversion_exp('M') == -6)
assert(prefix_conversion_exp('mu') == 6)
assert(prefix_conversion_exp('Y') == -24)
assert(prefix_conversion_exp('') == 0)

# Test find_prefix_and_root_units

test_dict = {'bohr':['bohr', 'a.u', 'atomic units', 'au'], 'angstrom':['angstrom, a'], 'm':['m', 'meter'] }

assert(find_prefix_and_root_units('a.u', test_dict) == ('', 'bohr'))
assert(find_prefix_and_root_units('A.U', test_dict) == ('', 'bohr'))
assert(find_prefix_and_root_units('bohr', test_dict) == ('', 'bohr'))
assert(find_prefix_and_root_units('Bohr', test_dict) == ('', 'bohr'))
assert(find_prefix_and_root_units('nm', test_dict) == ('n', 'm'))


# Test standardize_units_name
assert(standardize_units_name('a.u', test_dict) == 'bohr')
assert(standardize_units_name('A.U', test_dict) == 'bohr')
assert(standardize_units_name('bohr', test_dict) == 'bohr')
assert(standardize_units_name('Bohr', test_dict) == 'bohr')
assert(standardize_units_name('nm', test_dict) == 'nm')

# Test conversion_factor
test_vals = {'bohr': (1, 0), 'angstrom': (0.529177249, 0), 'm': (5.29177249, -11)}
assert(conversion_factor('a.u', 'bohr', test_dict, test_vals) == (1, 0))
assert(conversion_factor('a.u', 'nm', test_dict, test_vals) == (5.29177249, -2))
assert(conversion_factor('cm', 'fm', test_dict, test_vals) == (1, 13))
assert(conversion_factor('fm', 'cm', test_dict, test_vals) == (1, -13))

# Test energy_conversion_factor

# Test length_conversion_factor

# Test hbar
