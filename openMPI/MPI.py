from mpi4py import MPI
from mpi4py.MPI import ANY_SOURCE
import pylab as p
from time import time, sleep

import saving
import myplots

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

debug_mode = False
loader = saving.Loader(debug_on = debug_mode)
plotter = myplots.Plotter(debug_on = debug_mode)

def gen_file_list():
    load_path = "/home/dwh1g08/sabre-data/laser1.9/"
    #load_path = "/data/magnetic_heating/laser1.85/"
    files = loader.filelist(folder=load_path)[0]
    return sorted(files)

def chunks(l, n):
    n = max(1, n)
    return [l[i::n] for i in range(0,n)]

def cal_PSD(files):
    for i in files:
        t_xpsd, t_ypsd = plotter.psddata(filename=i)
        try:
            ypsd += t_ypsd
        except NameError:
            ypsd = t_ypsd
    return t_xpsd, ypsd

files = gen_file_list()
file_chucks = chunks(files, size)
xpsd, ypsd = cal_PSD(file_chucks[rank])
recv_buffer = p.zeros(len(ypsd))

if rank == 0:
    for i in range(1, size):
        comm.Recv(recv_buffer, ANY_SOURCE)
        ypsd += recv_buffer
    ypsd = ypsd / len(files)
    loader.savedata([xpsd, ypsd], filename="/home/dwh1g08/sabre-data/laser1.9/run.txt")
else:
    comm.Send(ypsd)
