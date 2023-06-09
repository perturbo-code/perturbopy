#!/bin/bash

# Check if the machine value is specified as as the command line argument
if [[ "$1" == "" ]]; then
   machine="KNL"
else
   machine=$1
fi

# Check if the $SLURM_NNODES variable is defined
if [[ "$SLURM_NNODES" == "" ]]; then
   nodes=1
else
   nodes=$SLURM_NNODES
fi

if [[ "$machine" == "HSW" ]]; then

   # Modify the path to the Perturbo executable
   PERTURBO=perturbo.x

   mpi_per_node=8
   omp_threads=8
   cpus_per_task=8

elif [[ "$machine" == "KNL" ]]; then

   # Modify the path to the Perturbo executable
   PERTURBO=perturbo.x

   mpi_per_node=4
   omp_threads=64
   cpus_per_task=68

else
   echo "WRONG machine value" $machine
   exit
fi

# Setup the OpenMP environment
export OMP_NUM_THREADS=$omp_threads
export OMP_PLACES=threads
export OMP_PROC_BIND=spread

mpi_tasks=`echo $mpi_per_node $nodes | awk '{print $1*$2}'`

export PERTURBO_RUN="srun -n $mpi_tasks -c $cpus_per_task --cpu_bind=cores $PERTURBO -npools $mpi_tasks"

echo "PERTURBO_RUN COMMAND:"
echo $PERTURBO_RUN

# setup the run directory
export PERTURBO_SCRATCH=$SCRATCH"/tmp_tests_perturbo"

echo ""
echo "PERTURBO_SCRATCH DIRECTORY:"
echo $PERTURBO_SCRATCH

# HDF5 locking
export HDF5_USE_FILE_LOCKING=FALSE
