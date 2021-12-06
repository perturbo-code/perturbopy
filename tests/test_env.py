import os

def test_env_variables():
   """
      Check env variables for home directories of Perturbo and 
      other 3rd party software necessary to run Perturbo

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
   home_dirs = ['QE_HOME', 'WANNIER90_HOME', 'PERTURBO_HOME']

   for home_dir in home_dirs:
      errmsg = (f"The required environment variable {home_dir} is not set.\n"
                f"Please set the path to this home directory in your \n"
                f"environment. This env var is required to use \n"
                f"perturpy appropriately.\n") 
      
      assert os.environ.get(home_dir) != None, errmsg
