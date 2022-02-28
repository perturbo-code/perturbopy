"""
   Set up the environment for Perturbo runs.
"""
import os


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
