import subprocess
import data
import datetime

def get_host_stats():
    command = "virsh nodememstats"

    p = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = p.communicate()[0]

    output = output.replace(" ", "")
    output = output.split("\n")
   
    total_memory = output[0].split(":")[1][:-3]      
    free_memory = output[1].split(":")[1][:-3]

    command = "virsh nodecpustats --percent"

    p = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = p.communicate()[0]
    
    output = output.replace(" ", "")
    output = output.split("\n")

    cpu_system = output[0].split(":")[1]
    io_wait = output[4].split(":")[1]

    data.make_host_statistic(float(cpu_system.replace("%","")), int(free_memory), int(total_memory), float(io_wait.replace("%","")), datetime.datetime.now()) 
