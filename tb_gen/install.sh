#!/bin/bash

function f_install_path() { 
	cat $1 | sed 's/=/ = /g' | awk -v d="$2" '{if ($1 == "install_path") { print $1" = \""d"\""} else { print $0 }}' | sed 's/ = /=/g' > sup.txt
	cat sup.txt > $1
	rm sup.txt
}

dir=$(pwd)
# installation path
echo $dir

# vado a salvare la directory corrente nei file  in modo da aggiungerla al path 
# in cui python va a cercare i moduli
f_install_path data_extract.py $dir
f_install_path entity_signal.py $dir
f_install_path tb_gen_gui.sh $dir
f_install_path vhdl_gen.py $dir
f_install_path tb_gen.sh $dir
f_install_path tb_gen_module.py $dir
f_install_path out_file.sh $dir

# installazione nel terminale
echo "alias tb_gen=\"$dir/tb_gen.sh\"" >> ~/.bash_aliases
echo "alias tb_out_file=\"$dir/out_file.sh\"" >> ~/.bash_aliases
echo "########
	Riavviare il terminale per completare l'installazione,
	il programma potrà essere chiamato da qualsiasi directory
	col comando:
		tb_gen 
########"
