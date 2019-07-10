#-*- coding: utf-8 -*-
#!/usr/bin/python
import os
from random import *
import sys

help="\
1  Nome del file d'uscita\n\
2  Numero di segnali\n\
3  Numero di step\n\
4  parallelismo 1° segnale\n\
5  paralleismo 2° segnale\n\
... etc\n\
"

if len(sys.argv)<3:
	print(help)
	sys.exit()

######################################################################################################################################
############################################## Insert here all the input parameters ##################################################

# Number of signals
SignalsNumber = int(sys.argv[2])

# List containing the parallelism of each signal (the first one is referred to "IN1", the second one is referred to "IN2", ...)
GenericsAssignedValue = []
for i in sys.argv[-int(sys.argv[2]):]:
	GenericsAssignedValue.append(int(i))

# Number of steps
NumberOfSteps = int(sys.argv[3])

# Name of the file
Filename = sys.argv[1];
######################################################################################################################################






######################################################################################################################################
##################################################### File creation ##################################################################

# Clear previous version of the file
# Linux
CommandToEliminateTest = "rm ./" + Filename
os.system(CommandToEliminateTest)
# Windows
#CommandToEliminateTest = "del " + Filename
#os.system(CommandToEliminateTest) # Command used to execute external commands on the terminal

# Create and open file
Filepointer = open(Filename, "w")
######################################################################################################################################




######################################################################################################################################
##################################################### Generate numbers ###############################################################
# Loop for all steps
for i in range(0,NumberOfSteps):
	# Loop for all signals
	for i in range (0, SignalsNumber):
		# Generate integer number
		RandomInputInteger = randint(1,2**GenericsAssignedValue[i]-1)
		# Convert number to binary
		RandomInputBinary = ('{0:0{l}b}'.format((RandomInputInteger),l=GenericsAssignedValue[i]))
		# Write file
		Filepointer.write(RandomInputBinary + " ")
	# Write line termination
	Filepointer.write("\n")


# Closing testbench file
Filepointer.close()
