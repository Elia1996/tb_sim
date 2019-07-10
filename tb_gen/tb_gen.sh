#!/bin/bash

install_path="/home/lp19.10/Desktop/lab6/456/simulator/tb_gen"

help="
 \$1 può essere\n
	-new -> chiama l'iterfaccia grafica per generare una nuova configurazionei\n
	-exe -> genera il testbench\n
"

case $1 in 
	-new)
		$install_path/tb_gen_gui.sh
		;;
	-exe)
		dir_param=$(cat $install_path/.dir_param)
		python $install_path/tb_gen.py $dir_param
		;;
	*)
		echo -e "$help"
		;;
esac
