import os
from subprocess import call

repo_dir = 'C:/Users/shael/github/perturbopy'
conda_path = 'C:/Users/shael/Anaconda3/Scripts/conda.exe'

os.chdir(repo_dir)
call(['pip','install','.'])

from perturbopy.postproc.utils.constants import *

print(energy_conversion_factor('ha','J'))
print(energy_conversion_factor('ha','eLectronvolt'))
print(energy_conversion_factor('ha','mJ'))
print(energy_conversion_factor('ha','miLliJoule'))
print(energy_conversion_factor('ha','milli-Joule'))
print(energy_conversion_factor('ha','MJ'))
print(energy_conversion_factor('ha','millielectronvolt'))
