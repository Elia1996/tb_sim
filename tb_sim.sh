#!/bin/bash

shopt -s expand_aliases
source ~/.bash_aliases


case $1 in 
	-new)
		tb_gen -new
		;;
	-exe)
		tb_gen -exe
		# trovo il file di uscita
		tb_out_file > sup
		out_file=$(cat sup)
		rm sup
		dir_out=$(dirname $out_file)
		in_gen $dir_out/input.txt 3 200 4 4 1 
		correct_out $dir_out/input.txt $dir_out/correct_out.txt	
		auto_vsim "compile.do"
		ck_file $out_file $dir_out/correct_out.txt $dir_out/input.txt > $dir_out/report.txt
		echo "##########################################################"
		echo "out_dut_file = "$out_file
		echo "correct_out_file = "$dir_out"/correct_out.txt"
esac



