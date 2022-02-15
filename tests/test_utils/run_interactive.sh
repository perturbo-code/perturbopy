#!/bin/bash

#
# Libraries
#
source /usr/local/Intel/19.4/compilers_and_libraries/linux/bin/compilervars.sh intel64
export PATH=/home/timescale/Jinjian/libraries/hdf5-1.8.18-ifort/bin:$PATH
export LD_LIBRARY_PATH=/home/timescale/Jinjian/libraries/hdf5-1.8.18-ifort/lib:$LD_LIBRARY_PATH

#
# Go to the work folder
#
#cd $PBS_O_WORKDIR

#
# Parallelization
#

# On Tempo, omp * mpi MUST be 20
omp=4
mpi=5

export PBS_NUM_PPN=$mpi

export OMP_NUM_THREADS=$omp
export OMP_STACKSIZE=64M


#
# Run command
#
PT=/home/timescale/testsuite/perturbo.x
RUN="mpirun -np $mpi $PT -npools $mpi -i pert.in"

echo `date`
echo "Running "$RUN" ..."

$RUN | tee pert.out

echo "====="
echo "Done."
echo `date`

