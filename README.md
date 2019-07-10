# tb_sim
tool di generazione automatica di testbench e di simulazione in modelsim

Per installare il pacchetto eseguire
./install.sh
tb_gen/.install.sh
in_out_gen/.install.sh

sarà disponibile il programma:
tb_sim -new/-exe
	-new -> Crea una nuova configurazione chiamando la GUI bash;
	-exe -> Genera il vhdl con tb_gen, tramite tb_out_file preleva il nome del file di uscita della dut, attraverso in_gen crea i dati di ingresso della dut, genera le uscite corrette con correct_out, lancia modelsim con lo script automatico auto_vsim e infine confronta le uscite con ck_file creando il file report.txt in cui sono presenti gli eventuali errori.

