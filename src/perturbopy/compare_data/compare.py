"""
   This module is wrapper to functions that compare yaml or h5 files
"""
import perturbopy.compare_data.yaml as cyaml
import perturbopy.compare_data.h5 as ch5


def equal_values(file1, file2, kw_n_tol):
   """
      1) determines file types
      2) determins if files containe the same values
         -for both yaml/h5 the objects of the highest level
          are checked then checks are performed on common
          objects

      Parameters
      -----
         file1       first  file
         file2       second file
         kw_n_tol    dictionary of keywords and tolerances
                     needed to make comparison on files

      Returns
      -----
         equal_vlaues boolean specifying if both files 
                      contain the same group/datasets/keys/values
      
      Warns
      -----
         None
   """
   
   
   # get file extension 
   file1_type = file1.split(".")[-1]
   file2_type = file2.split(".")[-1]
   
   errmsg = ("file1 and file2 extension do not match"
             "file1_type = {file1_type}\n"
             "file2_type = {file2_type}\n")
   assert file1_type == file2_type, errmsg

   file_type = file1_type

   # use appropriate compare function for file type
   if file_type == "yaml" or file_type == "yml":
      equal_values = cyaml.equal_values(file1, file2, kw_n_tol)

   elif file_type == "h5" or file_type == "hdf5":
      equal_values = ch5.equal_values(file1, file2)

   else:
      errmsg = ("Can only compare files with extensions "
                "yaml, yml, hdf5, or h5")
      raise ValueError(errmsg)

   return equal_values 
