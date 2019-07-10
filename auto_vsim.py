#!/usr/bin/env python
import os
import subprocess

# Clean folder. Deleting working directories and outputs
#os.system("rm -rf work")
#os.system("rm output_results.txt")
#os.system("rm transcript")
#os.system("rm vsim.wlf")

# Setting up environement variables
os.environ["PATH"] += os.pathsep + "/software/mentor/modelsim_6.5c/modeltech/linux_x86_64/"
os.environ["LM_LICENSE_FILE"] = "1717@led-x3850-1.polito.it"

# Print out environement variables
os.system("echo $PATH")
os.system("echo $LM_LICENSE_FILE")

# Launch Modelsim simulation
print ("Starting simulation...")
process = subprocess.call(["vsim", "-c", "-do", "compile.do"])
print ("Simulation completed")



