"""
   This module contains functions to compare hdf5 files
"""
import h5py
import subprocess

def equal_values(file1, file2, delta=1.0):
   """
      Uses commandline tool h5diff to check if two h5 files
      contain the same hierarchy/groups/datasets


      Parameters
      -----
         file1    first  h5 file
         file2    second h5 file
         delta    parameter to determine if two data values are equal.
                  Two data values are considerd equal if the 
                  absolute value of the difference between the 
                  two is less than delta
      
      Returns
      -----
         equal_vlaues boolean specifying if both h5 files 
                      contain the same information 
      
      Warns
      -----
         None
   """

   #first check that the commandline tool h5diff exists
   status, errmsg = subprocess.getstatusoutput('which h5diff')

   assert status == 0, errmsg

   finished_process = subprocess.run(args=[
                                       "h5diff",f"--delta={delta}",file1, file2
                                          ],
                                     capture_output=True)

   errmsg = str(finished_process.stdout)
   equal_values = ("differences found" not in str(finished_process.stdout))
   assert equal_values, errmsg
   
   return equal_values 
