#!/bin/bash

#cori_architecture="KNL"
#cori_architecture="HSW"

if [[ "$cori_architecture" == "HSW" ]]; then
   PERTURBO=/global/homes/i/imaliyov/software/qe-6.5_hsw/perturbo-dev_FORK/bin/perturbo.x
   QE2PERT=/global/homes/i/imaliyov/software/qe-6.5_hsw/perturbo-dev_FORK/bin/qe2pert.x

   mpi_tasks=8
   omp_threads=8
   threads_total=8

elif [[ "$cori_architecture" == "KNL" ]]; then
   PERTURBO=/global/homes/i/imaliyov/software/qe-6.5_knl/perturbo-dev_FORK/bin/perturbo.x
   QE2PERT=/global/homes/i/imaliyov/software/qe-6.5_knl/perturbo-dev_FORK/bin/qe2pert.x

   mpi_tasks=4
   omp_threads=64
   threads_total=68

else
   echo "WRONG cori_architecture value" $cori_architecture
   exit
fi

nodes="$SLURM_NNODES"
mpi_tasks_total=`echo $mpi_tasks $nodes | awk '{print $1*$2}'`

export OMP_NUM_THREADS=$omp_threads
export OMP_PLACES=threads
export OMP_PROC_BIND=spread

RUN="srun -n $mpi_tasks_total -c $threads_total --cpu_bind=cores $PERTURBO -npools $mpi_tasks_total"

echo "RUN COMMAND:"
echo $RUN
echo
echo "Running..."
echo `date`

$RUN -i pert.in | tee pert.out
