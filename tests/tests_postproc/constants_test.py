import os
from subprocess import call

repo_dir = 'C:/Users/shael/github/perturbopy'
conda_path = 'C:/Users/shael/Anaconda3/Scripts/conda.exe'

os.chdir(repo_dir)
call(['pip','install','.'])

from perturbopy.postproc.utils.constants import *

print(convert_energy_units(0.5,'ha','J'))
print(convert_energy_units(0.5,'ha','electronvolt'))
