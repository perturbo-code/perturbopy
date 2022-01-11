"""
   This module contains functions to compare hdf5 files
"""
import h5py

def equal_hierarchy():
   """
      Determines if two hdf5 files contain the same hierarchy of 
      groups and datasets

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
   return False

def equal_shape():
   """
      Determines if two datasets have equivalent shapes

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
   return False

def equal_values():
   """
      Determines if two datasets have equivalent values. Equivalent values
      is defined as having the sum of the square differences of all elements
      within a defined tolerance.

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
   return False
