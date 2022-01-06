#!/usr/bin/env python3
"""
A simple script the 'mimics' an executable
"""

import os
import sys
import numpy as np

# Load YAML loader and dumper
from yaml        import load,dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def func_linear(x_grid, alpha, beta):
   """
   A linear function

   Parameters
   ----------
   x_grid: a grid of x-values
   alpha: first parameter
   beta: second parameter
   """

   matrix = alpha * x_grid + beta

   number = np.sum(matrix)

   return number, matrix

def func_square(x_grid, alpha, beta):
   """
   A linear function

   Parameters
   ----------
   x_grid: a grid of x-values
   alpha: first parameter
   beta: second parameter
   """

   matrix = alpha * x_grid**2 + beta

   number = np.sum(matrix)

   return number, matrix

def write_output(number, matrix, input_param, output_filename = 'pert_output.yml'):
   """
   Write a simple YAML output file that would mimic an actual output file.

   Parameters
   ----------
   number: a float number
   matrix: a numpy array
   input_param: a dictionary of input parameters
   """

   output_dict = {}

   output_dict['comment'] = "This is an exmample of a YAML output file"
   
   output_dict['input_parameters'] = input_param

   output_dict['output_number'] = {}
   output_dict['output_number']['comment'] = "A description of the value, units, etc."
   output_dict['output_number']['values'] = float(number)

   output_dict['matrix'] = {}
   output_dict['matrix']['comment'] = "A description of the matrix."
   output_dict['matrix']['values'] = matrix.tolist()

   with open(output_filename, 'w') as outfile:
      #dump(output_dict, outfile, default_flow_style=True)
      dump(output_dict, outfile)

def main():

   input_filename = 'pert.yml'

   req_filename = 'empty_epwan.h5'

   # Check if req_filename is in the folder
   errmsg = f"I must have the {req_filename} file for no reason!"
   assert os.path.exists(req_filename), errmsg

   #
   # Read the input parameters
   #
   with open(input_filename,'r') as stream:
      input_dict = load(stream, Loader = Loader)
   
   input_param = input_dict['perturbo']

   errmsg = f"The input file {input_filename} must contain a calc_mode parameter."
   assert 'calc_mode' in input_param, errmsg

   alpha = input_param.get('alpha', 1.0)
   beta = input_param.get('beta', 1.0)

   # Setup a grid of x-values
   xmin = input_param.get('xmin', 0)
   xmax = input_param.get('xmax', 1)
   dx = input_param.get('dx', 0.1)

   x_grid = np.arange(xmin, xmax + dx, dx)

   if input_param['calc_mode'] == 'linear':
      output_number, matrix = func_linear(x_grid, alpha, beta)

   elif input_param['calc_mode'] == 'square':
      output_number, matrix = func_square(x_grid, alpha, beta)

   write_output(output_number, matrix, input_param)

if __name__ == '__main__':
   main()
