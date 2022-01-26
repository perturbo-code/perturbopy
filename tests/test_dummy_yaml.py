import os
import subprocess
from perturbopy.compare_data.yaml import *


def test_yaml_module():
   """
      Dummy teset (will be removed later)
      uses compare functions from compare_data.yaml module 

      Parameters
      -----
         None
      
      Returns
      -----
         None
      
      Warns
      -----
         None
   """
   # suffix of path to perturbo driver to produce output
   driver_path_suffix   = 'tests/tests_perturbo/test_template'
   ref_data_path_suffix = 'refs_perturbo/test_template'
   
   out_file = '/pert_output.yml'

   cwd = os.getcwd()
  
   perturbo_driver_dir_path = [x[0] for x in os.walk(cwd) if x[0].endswith(driver_path_suffix)][0]
   out_path                 = perturbo_driver_dir_path
   ref_path                 = [x[0] for x in os.walk(cwd) if x[0].endswith(ref_data_path_suffix)][0]
  
   os.chdir(perturbo_driver_dir_path)
   subprocess.call("./perturbo.py")
   os.chdir(cwd)
   
   ref_out = ref_path+out_file
   new_out = out_path+out_file

   errmsg = ('yaml files do not match')
   assert equal_values(ref_out,new_out), errmsg

