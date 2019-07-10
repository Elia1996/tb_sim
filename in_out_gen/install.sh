#!/bin/bash

dir=$(pwd)

echo "alias in_gen=\"python $dir/generate_inputs.py\"" >> ~/.bash_aliases
echo "alias correct_out=\"python $dir/correct_out.py\"" >> ~/.bash_aliases

echo "
Sono disponibili i seguenti programmi dopo il riavvio del terminale:
	in_gen -> genera gli  ingressi random per il testbench
	correct_out -> genera le uscite corrette
"
