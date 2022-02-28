#!/bin/bash
#SBATCH -N 2
#SBATCH -C knl
#SBATCH -q debug
#SBATCH --output=pytest_output
#SBATCH -J pytest_pert
#SBATCH -t 00:30:00

echo `date`

module load python

# Here we assume that py310pert conda environment is created
conda activate py310pert

source test_scripts/env_setup_examples.sh KNL

pytest -s
