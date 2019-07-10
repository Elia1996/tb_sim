#!/usr/bin/python3
import data_extract as de
import sys

obj = de.extract_param(sys.argv[1],"ciao","ciao2",0)
obj.extract_all()
if sys.argv[1]=="in_file":
    print(obj.param['file']['input'])
elif sys_argv[1]=="out_dir":
    print(obj.param['dir']['out'])
elif sys.argv[1]=="correct_file":
    out_file=obj.param['file']['output']['dut']
    if out_file=="0":
        out_file="correct_out"
    print(out_file)
elif sys.argv[1]=="n_in":

elif sys.argv[1]=="n_out":

elif sys.argv[1]=="p_in":

elif sys.argv[1]=="p_out":

elif sys.argv[1]=="n_step:


