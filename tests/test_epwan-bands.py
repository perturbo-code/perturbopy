import os
import subprocess
from perturbopy.compare_data.compare import equal_values 
from perturbopy.compare_data.yaml import open_yaml


def test_epwan1_bands():
   """
      driver to run tests_perturbo/epwan1-setup/ test

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
   # test name (also test dir name)
   test_name               = 'epwan1-bands'
   # suffixes of paths needed to find driver/utils/references
   driver_path_suffix      = 'tests_perturbo/'+test_name
   test_utils_path_suffix  = 'test_utils'
   ref_data_path_suffix    = 'refs_perturbo/'+test_name
   
   cwd = os.getcwd()
 
   # determine needed paths
   interactive_job_script   = [x[0] for x in os.walk(cwd) if x[0].endswith(test_utils_path_suffix)][0]
   perturbo_driver_dir_path = [x[0] for x in os.walk(cwd) if x[0].endswith(driver_path_suffix)][0]
   out_path                 = perturbo_driver_dir_path
   ref_path                 = [x[0] for x in os.walk(cwd) if x[0].endswith(ref_data_path_suffix)][0]
 
   os.chdir(perturbo_driver_dir_path)
   print(f'{os.getcwd()}')
   print(f'{interactive_job_script}/run_interactive.sh')
   subprocess.call(f"{interactive_job_script}/run_interactive.sh")
   os.chdir(cwd)

   # input yaml for perturbo job 
   pert_input = open_yaml(f'{perturbo_driver_dir_path}/pert_input.yml')
   # dictionary containing information about files to check
   test_files = pert_input['test info']['test files'] 
   # names of files to check
   out_files  = test_files.keys()
   
   # full path to reference output
   ref_outs    = [ref_path+'/'+out_file for out_file in out_files]
   # full path to new output
   new_outs    = [out_path+'/'+out_file for out_file in out_files]
   # keywords and tolerances (information about how to compare outputs)
   kw_n_tols   = [test_files[out_file] for out_file in out_files]

   for ref_file, new_file, kw_n_tol in zip(ref_outs,new_outs,kw_n_tols):
      print(f'comparing files {ref_file} and {new_file}')
      errmsg = (f'files {ref_file} and {new_file} do not match')
      assert equal_values(ref_file, new_file, kw_n_tol), errmsg

