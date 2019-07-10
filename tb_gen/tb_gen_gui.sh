#!/bin/bash

# $1 è la directory di installazione
# vi devono essere presenti tutti i moduli utilizzati
install_path="/home/lp19.10/Desktop/lab6/456/simulator/tb_gen"

entity_signal=$install_path/entity_signal.py

function pr(){
	   echo "$1 "${!1}
}

function signal_in_entity_select() {
	# $1 filename completo della dut o do aref
	# $2 nome del file in cui sono stati presi i segnali
	# $3 nome del segnale da indicare
	lista_sig=$($entity_signal $1)
	scelta=$(zenity --list --checklist --title "" --text "Selezionare il segnale di $3, fra i segnali presi da: $2." --column "scelta" --column "sig" $lista_sig)
	echo $scelta
}

function entry() {
	# ritorna il testo inserito
	# $1 messaggio dato all'utente
	if test $2 = "sequence"; then
		var=$(zenity --entry --text="$1")
		var="$(echo $var | tr -s " " | sed s/ /\\n/g)" 
	else
		echo $(zenity --entry --text="$1")
	fi
}

function error() {
	zenity --error --text="opzione non supportata ancora dal programma"
}

function dir_select() {
	echo $(zenity --file-selection --title="$1" --directory)  
}

function file_select() {
	echo $(zenity --file-selection --title="$1")  
}
function file_vhdl_select() {

	echo $(zenity --file-selection --title="$1" --file-filter=""*.vhd" "*.vhdl"")  
}

function yes_no() {
	# $1 title
	# $2 testo della domanda
	# $3 valore ritornato se la risposta è si
	# $4 valore ritornato se la risposta è no
	zenity --question --title="$1" --text="$2"
	case $? in
		0)
			echo $3;;
		1)
			echo $4;;
	esac
}
###### 	PROGRAMMA  	##################################################################
# directory di lavoro
dir_param=$(dir_select "Scegliere la directory di lavoro dove salvare la configurazione")
echo "$dir_param" > $install_path/.dir_param

# il circuito è combinatorio??
flag_seq_comb=$(yes_no "flag_seq_comb" "Il circuito è sequenziale?" "seq" "comb")

# directory in cui è presente la dut
filename_dut=$(file_vhdl_select "Selezionare il file della dut")
dir_dut=$(dirname $filename_dut)
dut_filename=$(basename $filename_dut)

# Directory e nome del file di ingresso 
filename_in=$(file_select "Selezionare il file di dati di ingresso")
dir_in=$(dirname $filename_in)
input_filename=$(basename $filename_in)
# Directory in cui salvare i file di uscita dei dati
dir_out="$(dir_select "Directory in cui salvare i file di uscita dei dati")"

# Sequenza di ingresso
input_sequence="$(entry "Gli ingressi verranno presi dal file indicato\n e dovranno essere tutti sulla stessa riga.\n\
	Viene qua richiesto di indicare l'ordine degli ingressi (in1 in2 in3 ... .)" "seq")"
output_sequence="$(entry "Le uscite verranno salvate nel file secondo l'ordine di seguito dato:( out1 out2 ...)" "seq")"

# Chiedo se si vuole confrontare la dut con un'architettura di riferimento
flag_aref=$(yes_no "flag_aref" "Si vuole confrontare la DUT con un'architettura di riferimento?" "1" "0")

# se ho l'architettura di riferimento posso decidere di
# salvare o meno le uscite su un file
if test $flag_aref = "1"; then
	flag_save_output=$(yes_no "flag_save_output" "Si vogliono salvare le uscite della DUT e di AREF?" "1" "0")
	# prendo il path completo e lo spezzo poi in due
	filename_aref=$(file_vhdl_select "Selezionare AREF")
	dir_aref=$(dirname $filename_aref)
	aref_filename=$(basename $filename_aref)
	correct_out_filename="nome_non_esistente.txt"
else
	flag_save_output="0"
	dir_aref=$dir_dut
	aref_filename="AREF_non_esiste.vhd"
	# Nel caso in cui non Ho aref chiedo se devo avere un'uscita di 
	# riferimento, salvo qua il nome del file con le uscite
	# corrette se ci sono
	flag_correct_out=$(yes_no "flag_correct_out" "Si vogliono confrontare le uscite della dut con un file di uscite corrette?" "1" "0")
	if test $flag_correct_out = "1"; then
		correct_out_filename=$(entry "Indicare il nome del file di uscita corretto (la directory è quella di uscita)")
	fi
fi

if test $flag_seq_comb = "comb"; then
	in_out_delay="$(entry "Indicare il ritardo ingresso uscita ( ex: \"10 ns\").")"
	flag_parallel_in="p"
	flag_fsm="0"
else
	# verifico se il circuito ha una fsm
	flag_fsm=$(yes_no "flag_fsm" "Il circuito ha una FSM?" "1" "0")
	
	# se ho una fsm potrei volere gli ingressi non paralleli
	if test $flag_fsm = "1"; then
		flag_parallel_in=$(yes_no "flag_parallel_in" "Vuole dare alla macchina gli ingressi sfalsati temporalmente? ( se si verrà poi chiesta la tempistica )"\
						"c" "p")
	else
		flag_parallel_in="p"
	fi


	# Se è un circuito sequenziale avrà un periodo di clk
	# e il clk avrà un nome
	clk_name="$(signal_in_entity_select $filename_dut "DUT file" "CLOCK")"
	clk_period="$(entry "Indicare il periodo di clock ( ex: \"10 ns\").")"	
	rst_name=$(signal_in_entity_select $filename_dut "DUT file" "RESET")
	rst_wave="$(entry "Indicare l'onda del reset, per farlo seguire la seguente sintassi:\n\
		| valore  =  n° di clk |\n\
		0 = 3, 1 = 10, 0 = end\n\
		In questo modo rst sarà a 0 per 3 clk, poi a 1 per 10 clk e poi a 0 fino alla fine.")"
	rst_wave="$(echo $rst_wave  | sed s/,/\\n/g)"
	if [[ $flag_aref = "0" ]] && [[ $flag_fsm = "1" ]]; then
		done_name=$(signal_in_entity_select $filename_dut "DUT_file" " DONE")
		start_name=$(signal_in_entity_select $filename_dut "DUT_file" " START")
	fi

	# Ingresso custom
	if [[ $flag_parallel_in = "1" ]] && [[ $flag_fsm = "1" ]]; then
		timing_custom_in="$(entry "Indicare la sequenza dei dati in ingresso:\n per far ciò indicare per ogni\n\
			segnale lo shift rispetto al done.\n\
			Di seguito un esempio di sintassi:\n\
			0 = a, 3 = b\n\
			In questo modo a verrà data sul done mentre b verrà data dopo 3 clk.")"
		timing_custom_in="$(echo $timing_custom_in  | sed s/,/\\n/g)"
	fi

	
	in_out_delay="0"
	clk_between_input=$(entry "Settare il numero di clk fra un ingresso e l'altro.")
	default_in_value="$(entry "Indicarei valori di default dei segnali di ingresso.\n\
             Di seguito un esempio di sintassi:\n\
			 a = 0, b = 1")"
	default_in_value="$(echo $default_in_value  | sed s/,/\\n/g)"

fi

pr default_in_value
pr in_out_delay
pr output_sequence
pr input_sequence
pr timing_custom_in

pr start_name
pr done_name
pr rst_name
pr clk_name

pr clk_between_input
pr clk_period
pr rst_wave

pr correct_out_filename
pr input_filename
pr aref_filename
pr dut_filename

pr filename_in
pr filename_aref
pr filename_dut

pr flag_save_output
pr flag_parallel_in
pr flag_fsm
pr flag_seq_comb
pr flag_aref

pr dir_param
pr dir_dut 
pr dir_aref
pr dir_aref
pr dir_out
pr dir_in


########  FLAG   ######################################
echo "\
# invece MOD è riferito alle modalità di testbench
# finora sono state implementate solo 7 modalità
######################################################


# flag per sapere se il circuito è combinatorio o meno
# seq/comb
### param['flag']['seq_comb'] (stringa) 
### MOD 1-7
flag_seq_comb = $flag_seq_comb;

# flag per sapere se c'è l'fsm
# 1/0
# implica:
#   flag_seq_comb = seq
### param['flag']['fsm'] (1/0)
### MOD 1,2,3,4,5,6
flag_fsm = $flag_fsm;

# flag per sapere se c'è l'aref di riferimento
# 1/0
### param['flag']['aref'] (1/0)
### MOD 1-7
flag_aref = $flag_aref;

# flag per sapere se confrontare i dati con le uscite corrette
# salvate in un file
# 1/0
### param['flag']['correct_out']
### MOD 9
flag_correct_out = $flag_correct_out;

# flag per sapere se ho l'ingresso parallelo o custom
# p/c
# implica:
#   flag_seq_comb = seq && flag_fsm = 1
### param['flag']['parallel_custom_in'] (p/c)
### MOD 3,4,5,6
flag_parallel_custom_in = $flag_parallel_in;

# flag per dire al programma di salvare le uscite
# per esempio nella modalità con aref le uscite
# potrebbero non interessare, tanto utilizza gli assert,
# in questo modo però è possibile forzare le uscite in ogni caso
### param['flag']['save_output']
### all
flag_save_output = $flag_save_output;" > $dir_param"/flag.gen"

######## CONSTANT ##############################
echo "\
#################################################
# File di configurazione per la generazione di 
# testbench, in questo file sono presenti le
# costanti usate
#################################################

# ritardo fra ingresso e uscita, da definire solo
# se il circuito è combinatorio.
# viene letta se:
# 	flag_seq_comb = comb
### param['constant']['in_out_delay'] (stringa)
in_out_delay = $in_out_delay;

# ritardo in clk fra due ingressi consecutivi 
# per i circuiti sequenziali
### param['constant']['clk_between_input']
clk_between_input = $clk_between_input;

# valori di default degli ingressi
# viene letta se:
#	flag_seq_comb = seq
### param['constant']['default_in_value']['name']
### param['constant']['default_in_value']['sig']
### param['constant']['default_in_value']['value']
default_in_value (
$default_in_value
);" > $dir_param"/constant.gen"

####### SYNC ###################################
echo "\
###################################################
# File per la configurazione del generatore di 
# testbench, in questo file sono salvate le
# variabili che servono per la sincronizzazione
###################################################


# clock
### param['sync']['clk']['period'] (stringa)
### param['sync']['clk']['name'] (stringa)
### MOD 1-7
# nome del clock nell'entiit
clk_name = $clk_name;
clk_period = $clk_period;

# reset
### param['sync']['rst']['wave']['value'] (lista di valori 1-0)
### param['sync']['rst']['wave']['time'] (lista del tempo che devono durare
###										  i valori)
### param['sync']['rst']['name'] (stringa)
### MOD 1-7
# nome del reset nell'entity
rst_name = rst;
rst_wave (
# valore = n di colpi di clock
$rst_wave
);

# done
# viene definito il nome del done nell'entity
### param['sync']['done']['name'] (stringa)
### MOD 3,6
done_name = $done_name;

# start
# viene definito il nome dello start nell'entity
### param['sync']['start']['name'] (stringa)
start_name = $start_name;

# timing per l'ingresso custom
# viene definito lo shift rispetto al done
### param['sync']['custom_in']['name'] (lista dei nomi di ingresso)
### param['sync']['custom_in']['shift'] (lsita dello shift rispetto allo start)
timing_custom_in (
# shift = nome_input
$timing_custom_in
);

# sequenza degli ingressi
### param['sync']['input_sequence']
input_sequence (
$input_sequence
);

output_sequence (
$output_sequence
);
" > $dir_param"/sync.gen"

####### FILE ###################################
echo "\
##############################################################
### file di parametri per il programma di generazione dei
### testbench
#############################################################


# nome della directory con  i vhdl
### param['dir']['vhdl']
dir_dut = $dir_dut;

# nome della directory con  i vhdl
### param['dir']['vhdl']
dir_aref = $dir_aref;

# nome della directory per i file di ingresso
### param['dir']['in']
dir_in = $dir_in;

# nome della directory con i file per le uscite
### param['dir']['out']
dir_out = $dir_out; 

# nome della directory dei parametri
### param['dir']['param']
#dir_param = /media/tesla/Storage/Linux/Scrivania/Progetti_work/git/lab_lowpower/lab6/4/tb_generator/config;
dir_param = $dir_param;

# nome del file della dut, verrà salvato in
# e verrà generato anche il file di uscita in cui verranno
# salvati i dati in uscita dalla dut in modo automatico
# il suo nome è lo stesso della dut col _out.txt finale
### param['file']['dut'] (stringa)
### param['file']['output']['dut'] (stringa) 
### MOD 1,2,3,4,5,6,7
dut_filename = $dut_filename;

# nome del file di input dei dati, verrà salvato in
### param['file']['input'] (stringa)
### MOD 1,2,3,4,5,6,7
input_filename = $input_filename;

# nome del file di output con le uscite corrette
### param['file']['output']['correct'] (stringa)
### MOD 2,3,6,7
correct_out_filename = $correct_out_filename;

# nome del file della AREF, ossia dell'architettura di 
# riferimento utilizzata, viene creato anche in automatico
# il nome del file d'uscita, aggiungendo _out.txt alla fine
### param['file']['aref'] (stringa)
### param['file']['output']['aref'] (stringa)
### MOD 1,4,5
aref_filename = $aref_filename;
" > $dir_param"/file.gen"


