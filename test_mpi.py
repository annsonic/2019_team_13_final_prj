# mpirun -np 3 /home/sea/workspace/gesture_prj/HandPose/env_4_HandPose/bin/python -m mpi4py test_mpi.py

# from mpi4py import MPI
#
# comm = MPI.COMM_WORLD
# rank = comm.Get_rank()
# node_name = MPI.Get_processor_name()
# print('Hello world from process %d at %s.' % (rank, node_name))


import datetime
import os
import sys
from mpi4py import MPI

base_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(base_dir, 'HandPose'))
sys.path.append(os.path.join(base_dir, 'ZenboJunior'))
from HandPose import HandPose
from ZenboJunior import robot


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
node_name = MPI.Get_processor_name()
print('Hello world from process {} at {} at {}'.format(rank, node_name, datetime.datetime.now()))

if rank == 0:
    HandPose.main(comm, rank)
elif rank == 1:
    robot.main(comm, rank)