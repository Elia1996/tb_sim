#!/bin/bash
# $1 nome dello script.do da eseguire

#CDIR=~/script/modelsim_script
CDIR=~/git/lab_lowpower/lab6/456/simulator


if test $# -ne 1; then
	echo "Errore, definire lo script.do da eseguire"	
	exit
fi
if ! test -f $1; then
	echo "Errore, lo script $1 non esiste"
	exit
fi

cat "$CDIR/auto_vsim.py" | sed "s/compile.do/$1/" > auto_vsim_custom.py
chmod 777 auto_vsim_custom.py
./auto_vsim_custom.py
rm auto_vsim_custom.py
