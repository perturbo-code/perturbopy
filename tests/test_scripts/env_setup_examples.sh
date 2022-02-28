#!/bin/bash

#machine="HSW"

machine="KNL"

if [[ "$machine" == "HSW" ]]; then

   # Modify the path to the Perturbo executable
   PERTURBO=perturbo.x

   mpi_per_node=8
   omp_threads=8
   threads_total=8

elif [[ "$machine" == "KNL" ]]; then

   # Modify the path to the Perturbo executable
   PERTURBO=perturbo.x

   mpi_per_node=4
   omp_threads=64
   threads_total=68

else
   echo "WRONG machine value" $machine
   exit
fi

export OMP_NUM_THREADS=$omp_threads
export OMP_PLACES=threads
export OMP_PROC_BIND=spread

nodes="$SLURM_NNODES"
mpi_tasks=`echo $mpi_tasks $nodes | awk '{print $1*$2}'`

export PERTURBO_RUN="srun -n $mpi_per_node -c $threads_total --cpu_bind=cores $PERTURBO -npools $mpi_per_node"

echo "PERTURBO_RUN COMMAND:"
echo $PERTURBO_RUN
