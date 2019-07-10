#!/usr/bin/python3
import data_extract as de
import sys

obj = de.extract_param(sys.argv[1],"ciao","ciao2",0)
obj.extract_all()
print(obj.param['file']['output']['dut'])

