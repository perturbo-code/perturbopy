"""
   Set up the environment for Perturbo runs.
"""
import os
import shutil

def perturbo_run_from_env():
   """
   Check if the PERTURBO_RUN variable is present among the environment variables
   and read its value.

   Examples to set the PERTURBO_RUN variable:

   >>> export PERTURBO_RUN='mpirun -np 4 <path>/perturbo.x -npools 4'

   or

   >>> export PERTURBO_RUN='srun -n 4 <path>/perturbo.x -npools 4'

   Returns
   -------
   perturbo_run : str
      string containing a command to run Perturbo

   """

   # Read the perturbo_run variable from the environment
   try:
      perturbo_run = os.environ['PERTURBO_RUN']
   except KeyError:
      errmsg = ('To run Perturbo in the testsuite,\n'
                'the PERTURBO_RUN environmental variable must be set.\n'
                'Example:\n'
                'export PERTURBO_RUN="mpirun -np 4 <path>/perturbo.x -npools 4"'
               )
      raise EnvironmentError(errmsg)

   return perturbo_run

def perturbo_scratch_dir_from_env(perturbo_inputs_dir_path, test_name):
   """
   Check if the PERTURBO_SCRATCH variable is present among the environment variables
   and read its value. If not present use path to the test dir present in package

   Example to set the PERTURBO_SCRATCH variable:

   >>> export PERTURBO_SCRATCH='m/global/cscratch'

   Parameters
   ----------
   perturbo_inputs_dir_path : str
      path to dir containing perturbo input files
   test_name : str
      name of test

   Returns
   -------
   perturbo_scratch_dir : str
      string containing the path to generate dir named tmp_test_name in which
      outputs for test_name will be generated

   """
   # get test name

   # Read the perturbo_run variable from the environment
   try:
      perturbo_scratch_dir_preix = os.environ['PERTURBO_SCRATCH']
      perturbo_scratch_dir = perturbo_scratch_dir_preix + f'/{test_name}'
      # copy over input files to scratch dir
      src = perturbo_inputs_dir_path
      dst = perturbo_scratch_dir
      if os.path.isdir(dst):
         shutil.rmtree(dst)
         shutil.copytree(src,dst)
      else:
         shutil.copytree(src,dst)
   except KeyError:
      perturbo_scratch_dir = perturbo_inputs_dir_path

   return perturbo_scratch_dir
