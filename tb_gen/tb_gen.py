# -*- coding: utf-8 -*-
#!/usr/bin/python
# Dev'essere passata da linea di comando la directory in cui è presente
# la configurazione 
import sys 
dir_param=sys.argv[1]

# aggiungo il path dove sono presenti gli altri file
# del programma, così posso importare i moduli
# da me scritti
install_path="/home/tesla/git/lab_lowpower/lab6/4/tb_generator"
sys.path.append(install_path)

import tb_gen_module as tb

obj=tb.tb_gen(dir_param, "testbench", "behavioural",1,1)
obj.extract_data()
obj.generate_testbench()

