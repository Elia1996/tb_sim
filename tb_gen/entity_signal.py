#!/usr/bin/python
##################################################
# questo script ritorna i segnali di un file vhdl
# nella forma
#   clk,co,a,b,s
#################################################
import sys
# aggiungo il path dove sono presenti gli altri file
# del programma, così posso importare i moduli
# da me scritti
install_path="/home/lp19.10/Desktop/lab6/456/simulator/tb_gen"
sys.path.append(install_path)

import data_extract

# in sys argv stanno gli argomenti da linea
# di comando, ma il primo è il nome dello
# script
file_name=sys.argv[1]


obj=data_extract.extract_entity(file_name,"dut",0)
obj.save_entity()
sig=obj.param['port']['port']['name']

print("False "+" False ".join(sig))
