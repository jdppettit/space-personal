import subprocess
import data

def get_memory_stats():
    command = "virsh nodememstats"

    p = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = p.communicate()[0]

    output = output.replace(" ", "")
    output = output.split("\n")
   
    total_memory = output[0].split(":")[1][:-3]      
    free_memory = output[1].split(":")[1][:-3]

    data.set_host_memory(total_memory, free_memory)

def get_cpu_stats():
    command = "virsh nodecpustats --percent"

    p = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = p.communicate()[0]
    
    output = output.replace(" ", "")
    output = output.split("\n")

    cpu_system = output[0].split(":")[1]
    io_wait = output[4].split(":")[1]

    data.set_host_cpu(cpu_system, io_wait)
      
