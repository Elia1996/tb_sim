# -*- coding: utf-8 -*-
#!/usr/bin/python
import os
import sys
from random import *

if len(sys.argv)<2:
	print("1) nome del file di uscita binario \n2) nome del file di uscita corretto generato")
	sys.exit()


######################################################################################################################################
############################################## Insert here all the input parameters ##################################################

# Name of the file
Filename = sys.argv[1];
Output = sys.argv[2];
######################################################################################################################################


######################################################################################################################################
############################################## Read values ###########################################################################

# Open file and acquire data 
with open(Filename, "r") as f:
	InputsBinary = [x.strip().split() for x in f]

# Creation of a matrix to store values converted in decimal
InputsDecimal = InputsBinary

# Calculation of matrix size
width = len(InputsBinary[0])
height = len(InputsBinary)

def somma(n1, n2,c_in, n_bit):
	s=int(int(n1)+int(n2)+int(c_in))
	out="{0:b}".format(s)
	if len(out)<n_bit:
		out="0"*(n_bit-len(out))+str(out)
		cout=0
	elif len(out)==n_bit:
		cout=0
	else:
		cout=1
		out=out[-n_bit:]
	return  [out,cout]

def somma_bin(n1, n2,c_in, n_bit):
	out=bin_add(n1,n2,c_in)
	if len(out)<n_bit:
		out="0"*(n_bit-len(out))+str(out)
		cout=0
	elif len(out)==n_bit:
		cout=0
	else:
		cout=1
		out=out[-n_bit:]
	return  [out,cout]

def bin_add(*args): 
	sum=bin(sum(int(x, 2) for x in args))[2:]


# Conversion of values from binary to decimal
with open(Output, "w") as f:
	for i in range(0, height):
		n=int(len(InputsBinary[i][0]))
		for j in range(0, width):
			InputsDecimal[i][j] = [int(InputsBinary[i][j], 2)]
			print InputsDecimal[i][j],
		out=somma(InputsBinary[i][0][0],InputsBinary[i][1][0],InputsBinary[i][2][0],\
					n)
		f.write(str(out[0])+" "+str(out[1])+"\n")
		print("")
	f.close()
