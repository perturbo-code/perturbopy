"""
   Run an executable for the testsuite.
"""
import os
import subprocess
from perturbopy.test_utils.compare_data.yaml import open_yaml


def run_perturbo(cwd, perturbo_driver_dir_path, interactive_job_script):
   """
   Function to run Perturbo and produce output files


   Parameters
   ----------
   cwd : str
      path of current working directory
   perturbo_driver_dir_path : str
      path to dir with pert.in file
   interactive_job_script : str
      path to dir with run_interactive.sh script

   Returns
   -------
   None

   """

   os.chdir(perturbo_driver_dir_path)
   print(f'{os.getcwd()}')
   print(f'{interactive_job_script}/run_interactive.sh')
   subprocess.call(f"{interactive_job_script}/run_interactive.sh")
   os.chdir(cwd)


def get_test_materials(test_name):
   """
   Run one test:
      #. run perturbo.x to produce output files
      #. determine paths to files for comparison
      #. associated settings for file comparison with file paths

   Parameters
   ----------
   test_name : str
      name of test

   Returns
   -----
   ref_outs :
      list of paths to reference files
   new_outs :
      list of paths to outputted files
   igns_n_tols :
      dictionary containing the ignore keywords and tolerances needed to performance comparison of ref_outs and new_outs

   """
   # suffixes of paths needed to find driver/utils/references
   driver_path_suffix = 'tests_perturbo/' + test_name
   test_scripts_path_suffix = 'test_scripts'
   ref_data_path_suffix = 'refs_perturbo/' + test_name

   cwd = os.getcwd()

   # determine needed paths
   interactive_job_script   = [x[0] for x in os.walk(cwd) if x[0].endswith(test_scripts_path_suffix)][0]
   perturbo_driver_dir_path = [x[0] for x in os.walk(cwd) if x[0].endswith(driver_path_suffix)][0]
   out_path                 = perturbo_driver_dir_path
   ref_path                 = [x[0] for x in os.walk(cwd) if x[0].endswith(ref_data_path_suffix)][0]

   # run perturbo.exe to produce outputs
   run_perturbo(cwd, perturbo_driver_dir_path, interactive_job_script)

   # input yaml for perturbo job
   pert_input = open_yaml(f'{perturbo_driver_dir_path}/pert_input.yml')
   # dictionary containing information about files to check
   test_files = pert_input['test info']['test files']
   # names of files to check
   out_files  = test_files.keys()

   # list of full paths to reference outputs
   ref_outs    = [ref_path + '/' + out_file for out_file in out_files]
   # list of full paths to new outputs
   new_outs    = [out_path + '/' + out_file for out_file in out_files]
   # list of dict. Each dict contains ignore keywords and
   # tolerances (information about how to compare outputs)
   igns_n_tols = [test_files[out_file] for out_file in out_files]

   return (ref_outs,
           new_outs,
           igns_n_tols)
