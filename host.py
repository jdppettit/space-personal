import subprocess
import data
import datetime

from domfunctions import connect

def get_host_stats():
    con = connect()
    memory_stats = con.getMemoryStats(0,0)
    
    total_memory = memory_stats['total'] / 1024
    free_memory = memory_stats['free'] / 1024 

    command = "virsh nodecpustats --percent"

    p = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = p.communicate()[0]
    
    output = output.replace(" ", "")
    output = output.split("\n")

    cpu_system = output[0].split(":")[1]
    io_wait = output[4].split(":")[1]

    data.make_host_statistic(float(cpu_system.replace("%","")), int(free_memory), int(total_memory), float(io_wait.replace("%","")), datetime.datetime.now()) 
