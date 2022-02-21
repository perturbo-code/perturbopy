#!/bin/bash

#
# Parallelization
#

# On Tempo, omp * mpi MUST be 20
mpi=5
omp=4

export PBS_NUM_PPN=$mpi

export OMP_NUM_THREADS=$omp
export OMP_STACKSIZE=64M

#
# Libraries
#

module load compilers/intel/19.4
source /usr/local/Intel/19.4/impi/2019.4.243/intel64/bin/mpivars.sh


#
# Go to the work folder
#
#cd $PBS_O_WORKDIR

#
# Run command
#
PT=/home/timescale/testsuite/new_executable_and_script/perturbo.x
RUN="mpirun -np $mpi $PT -npools $mpi -i pert.in"

echo `date`
echo "Running "$RUN" ..."

$RUN | tee pert.out

echo "====="
echo "Done."
echo `date`

