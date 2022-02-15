import os
import subprocess
from perturbopy.compare_data.compare import equal_values 


def test_epwan1_setup():
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
   # test name (also test dir name
   test_name               = 'epwan1-setup'
   # suffixes of paths needed to find driver/utils/references
   driver_path_suffix      = 'tests_perturbo/'+test_name
   test_utils_path_suffix  = 'test_utils'
   ref_data_path_suffix    = 'refs_perturbo/'+test_name
   
   # output files to check against reference data
   out_files = ['/pert_output.yml',
                'gaas_tet.h5',
               ]

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
   
   ref_outs = [ref_path+out_file for out_file in out_files]
   new_outs = [out_path+out_file for out_file in out_files]

   for ref_file, new_file in zip(ref_outs,new_outs):
      print(f'comparing files {ref_file} and {new_file}')
      errmsg = (f'files {ref_file} and {new_file} do not match')
      assert equal_values(ref_file,new_file), errmsg

