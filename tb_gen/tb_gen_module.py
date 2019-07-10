# -*- coding: utf-8 -*-
#!/usr/bin/python3
# Questa classe è stata sviluppata da ER per automatizzare la
# generazione di testbench utilizzando file di configurazione
# di seguito vengono illustati particolari dell'implementazione;
# al fine di semplificare l'utilizzo della classe:
#
#### note generali sul vhdl generato #############
#
# 1) Le LIBRERIE INCLUSE sono prelevate dal file della dut
#   , inoltre sono aggiunte le librerie necessarie per il
#   testbench. NON è stato fatto il controllo se le librerie
#   aggiunte da testbench siano già presenti, percui controllare
#   il vhdl per evitare doppi "USE ...".
#
# 2) Vengono generati dei segnali GENERIC globali collegati
#   a quelli dei component, in questo modo è possibili modificare
#   il valore dei generic della dut direttamente dall'entity della
#   testbench.
#   L'altro motivo per cui si fa ciò e che tutti i segnali generati
#   all'interno del tb per collegare il component hanno lo stesso 
#   tipo di quelli dell'entity, percui supponendo di avere uno
#   STD_LOGIC(n_bit-1 dowto 0) è necessario definire anche nel tb
#   il generic "n_bit" utilizzato, per questo motivo viene definito
#   anche globale.
#   Viene inoltre supposto che dut e aref abbiano stessi generic, 
#   percui si usano solo quelli della dut
#
# 3)

import vhdl_gen
import sys
# aggiungo il path dove sono presenti gli altri file
# del programma, così posso importare i moduli
# da me scritti
install_path="/home/lp19.10/Desktop/lab6/4/tb_generator"
sys.path.append(install_path)


import data_extract


class tb_gen:
    def __init__(sf, dir_param, tb_name, arch_type, debug=0, lldb=0):
        # dir_param -> directory coi parametri
        sf.debug = debug
        # debug a livello più basso
        sf.lldb = lldb
        sf.dir_param = dir_param
        # creo l'oggetto per estrarre i dati dai file
        # inserisco come stringa "dut" perchè alcuni segnali come 
        # il clock, il reset e lo start sono inizializzati in 
        # processi: nella variabile param['sync']['clk']['sig_name']
        # param['sync']['start']['sig_name'] e param['sync']['rst']['sig_name']
        # sono salvati i segnali uguali a quelli utilizzati per il portmap della 
        # dut
        sf.dut_sig_pfx = "dut"
        sf.aref_sig_pfx = "aref"
        sf.obj_param = data_extract.extract_param(dir_param,
                                                    sf.dut_sig_pfx,
                                                    sf.aref_sig_pfx, 
                                                    sf.lldb)
        # parametri che verranno acquisiti con l'oggetto precedente
        sf.param = {}
        # nome della testbench
        sf.tb_name = tb_name
        # tipo di architettura
        sf.arch_type = arch_type

        ###### gestione dei prefissi e dei nomi
        # le instanze di dut e aref
        sf.dut_process_pfx = "inst_dut_"
        sf.aref_process_pfx = "inst_aref_"
        # nome del processo di clock
        sf.clk_process_name = "clk_process"
        # nome del processo di reset
        sf.rst_process_name = "rst_process"
        # nome del processo di start
        sf.start_process_name = "start_process"
        
        ###### gestione delle variabili create nel testbench ex novo
        sf.clk_constant = "CLK_PERIOD"
        sf.read_process_name = "READ_PROCESS"
        sf.write_process_name = "WRITE_PROCESS"
        sf.read_input_file_variable = "INPUT_BIN"
        sf.write_output_file_variable = "OUTPUT_BIN"
        sf.write_output_file_aref_variable = "OUTPUT_BIN_AREF"
        sf.write_output_file_correct_variable = "CORRECT_OUTPUT_BIN"
        sf.read_riga = "read_riga"
        sf.write_riga = "write_riga"
        sf.write_riga_aref = "write_riga_aref"
        sf.read_riga_correct = "correct_write_riga"
        sf.end_loop_sig = "end_loop"



    ###############################
    # funzioni di estrazione dati
    def extract_data(sf):
        # I parametri estratti si dividono in:
        #   sf.param -> sono i parametri estratti da tutti i file,
        #               il primo elemento del dizionario fa riferimento
        #               al file relativo; per esempio i parametri che sono
        #               presenti nel file sync.gen sono salvati come
        #               sf.param['sync']
        #   sf.dut   -> sono salvati tutti i parametri riferiti alla dut
        #               percui si troveranno le porte e i segnali e le 
        #               librerie utilizzate.
        #   sf.aref  -> sono i parametri riferiti all'arch di riferimento
        #               i parametri salvati sono gli stessi della dut
        #               
        #
        # estraggo i parametri
        sf.obj_param.extract_all()
        sf.param = sf.obj_param.param 
        # estraggo i parametri dall'entity della dut e li salvo
        # in sf.dut
        sf.obj_dut = data_extract.extract_entity(sf.param['file']['dut'],
               sf.dut_sig_pfx,
               sf.lldb) 
        sf.obj_dut.save_entity()
        sf.dut = sf.obj_dut.param

        #print("--------------------"+sf.param['flag']['aref'])
        if sf.is_aref():
            # estraggo i parametri dall'entity  della dut e li salvo
            # in sf.dut
            sf.obj_aref = data_extract.extract_entity(sf.param['file']['aref'],
                sf.aref_sig_pfx,
                sf.lldb) 
            sf.obj_aref.save_entity()
            sf.aref = sf.obj_aref.param
            



    ###############################
    def generate_testbench(sf):
        sf.obj_vhd = vhdl_gen.vhdl_gen(sf.param['file']['dut'], sf.param['dir']['out'])
        ## oggetto per il processo di READ
        sf.read_pr = sf.obj_vhd.cl_process(sf.obj_vhd, sf.read_process_name, 1)
        ## oggetto per il processo di WRITE
        sf.write_pr = sf.obj_vhd.cl_process(sf.obj_vhd, sf.write_process_name, 1)
        ## oggetto per leggere e scrivere
        sf.read_write_pr = sf.obj_vhd.cl_process(sf.obj_vhd, sf.write_process_name, 1)

        # La modalità 1 viene implementata se si ha la
        # seguente configurazione:
        #   flag_seq_comb = seq
        #   flag_FSM = 0
        #   flag_aref = 1
        # Di conseguenza serve per le macchine sequenziali che 
        # non hanno fsm ma hanno un'architettura di riferimento
        # con cui confrontarsi, il confronto con questa architettura
        # verrà quindi fatto clock per clock
       
        # dall'inizio fino ai procecss
        sf.tb_LEASP()
        # clock, reset
        sf.tb_CR()
        # processo di lettura
        if sf.is_seq():
            sf.current_process=sf.read_pr
            sf.tb_read()
            sf.current_process=sf.write_pr
            sf.tb_write()
        else:
            # per i circuiti combinatori
            if sf.is_aref():
                # con aref
                sf.mod8()
            else:
                if sf.is_correct_out():
                    # senza aref, ma col file delle uscite corrette
                    sf.mod9()
                else:
                    # senza aref ne il file delle uscite corrette,
                    # semplicemente salvo le uscite su file
                    sf.mod7()    
    	sf.tb_arch_end(0)


    ##############################################################
    ## MODALITÀ
    ##############################################################
    def mod7(sf):
        print("----------------- mod7 -------------------------")
        # la modalità 7 è fatta per un circuito combinatorio
        # da i valori in ingresso e salva quelli in uscita
        sf.current_process = sf.obj_vhd.cl_process(sf.obj_vhd, sf.write_process_name, 1)
        
        # definizione della variabile per il file
        sf.tb_read_def_file_variable()
        # variabile per salvare ad ogni ciclo la linea del file
        sf.tb_read_def_line_variable()
        # tutte le restanti variabili
        sf.tb_read_def_input_varaible()
        ######## BEGIN
        # apro il file degli ingressi
        sf.tb_read_file_open()
        
        # definizione di
        #  FILE OUTPUT_BIN: text;
        #  VARIABLE riga_write: LINE;
        #  # definisco le variabili per scrivere su file
        #  VARIABLE AR_OUT : SIGNED(15 DOWNTO 0);
        #  # apro il file
        #  file_open(OUTPUT_BIN, "param['output_dut_filename']" , write_mode);
        sf.tb_file_line_write_open("dut")
        
        # Inizio il loop per prelevare i dati dal file
        sf.tb_read_while_begin()
        ####### lettura dati di ingresso  #################
        sf.tb_read_readline()
        #salvo i dati nelle variabili
        sf.tb_read_line_in_variable()
        # salvo le variabili nei segnali
        sf.tb_read_variable_in_signal()
        # aspetto che vengano processati
        sf.tb_read_wait_in_out_delay()
        
        ####### scrittura dati in uscita ##################
        # connetto le variabili ai segnali per poterli stampare in uscita
        sf.tb_variable_connect("dut")
        # se devo salvare le uscite le salvo
        sf.tb_write_write_variable("dut")

        # fine loop
        sf.current_process.loop_end()

        # chiudo i file
        sf.tb_read_file_close()
        sf.tb_file_close_dut()

        # WAIT;
        sf.current_process.wait("","",0)
     
        sf.current_process.printer()

        
    def mod8(sf):
        print("------------- mod8  ----------------------")
        # la modalità 8 è fatta per un circuito combinatorio
        # da i valori in ingresso e confronta quelli in uscita
        # grazie all'architettura di riferimento

        sf.current_process = sf.read_write_pr
        
        # definizione della variabile per il file
        sf.tb_read_def_file_variable()
        # variabile per salvare ad ogni ciclo la linea del file
        sf.tb_read_def_line_variable()
        # tutte le restanti variabili
        sf.tb_read_def_input_varaible()
        ######## BEGIN
        # apro il file degli ingressi
        sf.tb_read_file_open()
        
        
        # Inizio il loop per prelevare i dati dal file
        sf.tb_read_while_begin()
        ####### lettura dati di ingresso  #################
        sf.tb_read_readline()
        #salvo i dati nelle variabili
        sf.tb_read_line_in_variable()
        # salvo le variabili nei segnali
        sf.tb_read_variable_in_signal()
        # aspetto che vengano processati
        sf.tb_read_wait_in_out_delay()
        
        ####### scrittura dati in uscita ##################
        # connetto le variabili ai segnali per poterli confrontare
        sf.tb_variable_connect("dut")
        sf.tb_variable_connect("aref")
        # confronto le uscite
        sf.tb_write_assert_aref()

        # fine loop
        sf.current_process.loop_end()

        # chiudo i file
        sf.tb_read_file_close()

        # WAIT;
        sf.current_process.wait("","",0)
     
        sf.current_process.printer()

    def mod9(sf):
        print("------------- mod9  ----------------------")
        # la modalità 9 è fatta per un circuito combinatorio
        # da i valori in ingresso e confronta quelli in uscita
        # con un file di uscite corrette

        sf.current_process = sf.read_write_pr
        
        # definizione della variabile per il file
        sf.tb_read_def_file_variable()
        # variabile per salvare ad ogni ciclo la linea del file
        sf.tb_read_def_line_variable()
        # tutte le restanti variabili
        sf.tb_read_def_input_varaible()
        ######## BEGIN
        # apro il file degli ingressi
        sf.tb_read_file_open()
        
        # definizione di
        #  FILE OUTPUT_BIN: text;
        #  VARIABLE riga_write: LINE;
        #  # definisco le variabili per scrivere su file
        #  VARIABLE AR_OUT : SIGNED(15 DOWNTO 0);
        #  # apro il file
        #  file_open(OUTPUT_BIN, "param['output_dut_filename']" , write_mode);
        sf.tb_file_line_write_open("dut")
        sf.tb_file_line_write_open("correct")
        
        # Inizio il loop per prelevare i dati dal file
        sf.tb_read_while_begin()
        ####### lettura dati di ingresso  #################
        sf.tb_read_readline()
        #salvo i dati nelle variabili
        sf.tb_read_line_in_variable()
        # salvo le variabili nei segnali
        sf.tb_read_variable_in_signal()
        # aspetto che vengano processati
        sf.tb_read_wait_in_out_delay()

        ####### prelevo i dati corretti ###################
        sf.tb_read_readline_correct_out()
        sf.tb_read_line_in_variable_correct_out()
        
        ####### scrittura dati in uscita ##################
        # connetto le variabili ai segnali per poterli confrontare
        sf.tb_variable_connect("dut")
        # confronto le uscite
        sf.tb_write_assert_correct_out()
        # salvo le uscite
        sf.tb_write_write_variable("dut")

        # fine loop
        sf.current_process.loop_end()

        # chiudo i file
        sf.tb_read_file_close()
        sf.tb_file_close_dut()
        sf.tb_file_close_correct_out()

        # WAIT;
        sf.current_process.wait("","",0)
     
        sf.current_process.printer()

    ##############################################################
    # funzioni che utilizzano quelle più a basso livello implementando
    # pezzi di testbench più ampi
    
    def tb_LEASP(sf):
        # Crea le parti comuni a quasi tutte le modalità
        # La sigla sta per le parti del vhdl aggiunte
        # Library Entity Aarchitecture Signal Portmap
        ######### LIBRERIE  ####################
        # istanziazione delle librerie
        sf.tb_library(0)
        ######### ENTITY #######################
        # generazione entity
        sf.tb_entity(0)
        # inizia l'architettura
        ######### ARCHITETTURA #################
        sf.tb_arch_start(0)
        #### COMPONENT
        # definisco la dut
        sf.tb_dut_component(1)
        # se devo definisco aref
        sf.tb_aref_component(1)
        #### SIGNAL
        # definisco i segnali della dut
        sf.tb_dut_signal(1)
        # se c'è aref definisco i segnali per aref
        sf.tb_aref_signal(1)
        # se è sequenziale definisco il clock
        if sf.is_seq():
            sf.obj_vhd.set_indent(1)
            sf.obj_vhd.constant_def(sf.clk_constant, "TIME", sf.param['sync']['clk']['period'])
        ########## BEGIN ########################
        # inizio
        sf.tb_arch_begin(0)
        # instanziazione dut
        sf.tb_dut_map(1)
        # instanziazione aref eventuale
        sf.tb_aref_map(1)
        
    def tb_CR(sf):
        # inizializza i processi di:
        #   clock se flag_seq_comb=1
        #   rst se flag_seq_comb=1
        if sf.is_seq():
            sf.tb_clock(1)
            sf.tb_rst(1)


    ##############################################################
    # funzioni che implementano pezzi di testbench per semplificare
    # la creazione dei vari mod
    def tb_read(sf):

        # definizione della variabile per il file
        sf.tb_read_def_file_variable()
        # variabile per salvare ad ogni ciclo la linea del file
        sf.tb_read_def_line_variable()
        # tutte le restanti variabili
        sf.tb_read_def_input_varaible()
       
        ######## BEGIN
        # apro il file degli ingressi
        sf.tb_read_file_open()

        # Inizio il loop per prelevare i dati dal file
        sf.tb_read_while_begin()
        ####### lettura dati
        sf.tb_read_readline()
        #salvo i dati nelle variabili
        sf.tb_read_line_in_variable()
        # salvo le variabili nei segnali
        sf.tb_read_variable_in_signal()
        # se il circuito è comnbinatorio
        sf.tb_read_wait_in_out_delay()
        # fine loop
        sf.current_process.loop_end()
        
        # chiudo il file
        sf.tb_read_file_close()
        # WAIT;
        sf.current_process.wait("","",0)
     
        sf.current_process.printer()

    def tb_write(sf):
        sf.tb_file_line_write_open("dut")
        if sf.is_aref(): 
            sf.tb_file_line_write_open("aref")
        elif not sf.is_aref():
            sf.tb_file_line_write_open("correct")
        
        sf.tb_while_aref()
        
        sf.current_process.printer()
    

    def tb_file_line_write_open(sf, tipo):
        # definisco la variabile del file d'ingresso
        # FILE OUTPUT_BIN: text;
        sf.tb_write_def_file_variable(tipo)
        # definisco la variabile della riga
        # VARIABLE riga_write: LINE;
        sf.tb_write_def_line_variable(tipo)
        # definisco le variabili per scrivere su file
        # VARIABLE AR_OUT : SIGNED(15 DOWNTO 0);
        sf.tb_write_def_write_variable(tipo)
        # file_open(OUTPUT_BIN, "param['output_dut_filename']" , write_mode);
        sf.tb_write_open_file(tipo) 

    def tb_while_aref(sf):
        if not sf.is_aref():
            sf.print_bug(" ERRORE IN tb_while_aref, non può essere chiamata se non c'è aref")
        else:
            # questa funzione serve nel caso in cui io abbia aref 
            # , in questo caso ciclo semplicemente sulle due uscite
            # e le controllo istante per istante che siano uguali
            if sf.is_fsm():
                # aspetto lo start
                sf.tb_read_wait_start(1)
            # aspetto clk quinti
            sf.tb_wait_clk_quinti(0)
            # inizia il ciclo che continua finchè non arriva l'end loop
            sf.tb_while_condition(sf.end_loop_sig+"=0")
            # se sono nella modalità 1 aspetto qua un colpo di clock
            if not sf.is_fsm() and sf.is_seq():
                sf.tb_wait_n_clk(1, 1)

            # connetto le variabili ai segnali per poterli confrontare
            sf.tb_variable_connect("dut")
            sf.tb_variable_connect("aref")
            # confronto le uscite
            sf.tb_write_assert_aref()
            # se devo salvare le uscite le salvo
            if sf.is_save_output():
                sf.tb_write_write_variable("dut")
                sf.tb_write_write_variable("aref")
            sf.current_process.loop_end()
            sf.tb_file_close_dut()
            sf.tb_file_close_aref()

            
            
    ####### WRITE FUNCTION #######################################
    def tb_file_close_dut(sf):
        sf.current_process.file_close(sf.write_output_file_variable)
    def tb_file_close_aref(sf):
        sf.current_process.file_close(sf.write_output_file_aref_variable)
    def tb_file_close_correct_out(sf):
        sf.current_process.file_close(sf.write_output_file_correct_variable)

    def tb_write_write_variable(sf, tipo):
        # questa funzione serve per creare il seguente codice:
        #
        # ---- # Ciclo per creare la riga da salvare in OUTPUT_BIN
        # write(riga_write, dut['port']['var']['name']);
        # ---- # Ciclo per creare la riga da salvare in OUTPUT_BIN_AREF
        # write(riga_write_aref, aref['port']['var']['name']);
        # ---- END cycle
        # writeline(OUTPUT_BIN, riga_write);
        # writeline(OUTPUT_BIN_AREF,  riga_write_aref);
        # 
        # serve per stampare su file le variabili lette dalla dut o 
        # da aref
        if tipo == "dut":
            sf.current_process.write(sf.write_riga, sf.to_var( sf.dut['port']['out']['name'], "dut_out"))
            sf.current_process.writeline(sf.write_output_file_variable, sf.write_riga)
        elif tipo == "aref":
            sf.current_process.write(sf.write_riga_aref, sf.to_var( sf.aref['port']['out']['name'], "aref_out"))
            sf.current_process.writeline(sf.write_output_file_aref_variable, sf.write_riga_aref)


    def tb_write_assert_aref(sf):
        for d,a,a_sig in zip(sf.to_var( sf.dut['port']['out']['name'], "dut"), sf.to_var( sf.aref['port']['out']['name'], "aref"), sf.aref['port']['out']['name']):
            sf.current_process.f_assert(d+" = "+a, "\"Errore, il segnale "+a_sig+"  è diverso per dut e aref\"","severity warning",1)

    def tb_write_assert_correct_out(sf):
        print(sf.to_var( sf.dut['port']['out']['name'], "dut"))
        print(sf.to_var(sf.param['sync']['correct_out_name']['sig'],"correct"))
        print(sf.param['sync']['correct_out_name'])
        for d,a,a_sig in zip(sf.to_var( sf.dut['port']['out']['name'], "dut"), 
                sf.to_var(sf.param['sync']['correct_out_name']['sig'],"correct"), 
                sf.param['sync']['correct_out_name']['sig']):
            print(d+"|"+a+"|"+a_sig)
            sf.current_process.f_assert(d+" = "+a, "\"Errore, il segnale "+a_sig+" è diverso per dut e file d'uscita\"","severity warning",1)

    def tb_variable_connect(sf, tipo):
        # connette i segnali di dut o aref nelle corrispettive variabili
        # definite dalla funzione tb_write_def_write_variable
        if tipo == "dut":
            sf.current_process.set_variable("-- salvo i segnali della dut nelle variabili",
                    "-- end", sf.to_var( sf.dut['port']['out']['name'], "dut_out"),
                    sf.to_signal(sf.dut['port']['out']['name'], "dut"),1)
        elif tipo == "aref":
            sf.current_process.set_variable("-- salvo i segnali di aref nelle variabili",
                    "-- end", sf.to_var( sf.aref['port']['out']['name'], "aref_out"),
                    sf.to_signal(sf.aref['port']['out']['name'], "aref"),1)
        else:
            sf.print_bug("error in tb_gen, tb_variable_connect")


    def tb_write_open_file(sf, tipo):
        if tipo == 'dut':
            sf.current_process.file_open(sf.param['file']['output']['dut'], sf.write_output_file_variable, "write_mode")
        elif tipo == "aref":
            sf.current_process.file_open(sf.param['file']['output']['aref'], sf.write_output_file_aref_variable, "write_mode")
        elif tipo == "correct":
            sf.current_process.file_open(sf.param['file']['output']['correct'], sf.write_output_file_correct_variable, "read_mode")
        else:
            sf.print_bug("error")

    def tb_write_def_write_variable(sf, tipo):
        if tipo == "dut":
            # definizione delle variabili utilizzate per scrivere su file
            #   VARIABILE var: std_logic;
            sf.current_process.def_variable(l_name=sf.to_var( sf.dut['port']['out']['name'], "dut_out"),
                    l_type = sf.dut['port']['out']['type'])
        elif tipo == "aref":
            # definizione delle variabili utilizzate per scrivere su file
            #   VARIABILE var: std_logic;
            sf.current_process.def_variable(l_name=sf.to_var( sf.aref['port']['out']['name'], "aref_out"),
                    l_type = sf.aref['port']['out']['type'])
        elif tipo == "correct":
            # definizione delle variabili utilizzate per scrivere su file
            #   VARIABILE var: std_logic;
            sf.print_bug("tb_write_def_write_variable")
            sf.print_bug(sf.param['sync']['correct_out_name']['sig'])
            sf.print_bug(sf.dut['port']['port']['name'])
            sf.print_bug(sf.dut['port']['port']['type'])
            l_type = sf.type_of( sf.param['sync']['correct_out_name']['sig'],
                                sf.dut['port']['port']['name'],
                                sf.dut['port']['port']['type'])
            sf.print_bug("---lllll----")
            sf.print_bug(str(l_type))
            sf.print_bug("---llllll----")
            sf.current_process.def_variable(l_name= sf.to_var(sf.param['sync']['correct_out_name']['sig'], "correct"),
                    l_type = l_type)

    def tb_write_def_file_variable(sf,tipo):
        if tipo == "dut":
            # definizione della variabile per il file, esempio: 
            #   FILE CORRECT_OUTPUT_BIN: text;
            sf.current_process.def_file( sf.write_output_file_variable )
        elif tipo == "correct":
            # definizione della variabile per il file, esempio: 
            #   FILE CORRECT_OUTPUT_BIN: text;
            sf.current_process.def_file( sf.write_output_file_correct_variable)
        elif tipo == "aref":
            # definizione della variabile per il file, esempio: 
            #   FILE OUTPUT_BIN_AREF: text;
            sf.current_process.def_file( sf.write_output_file_aref_variable )
        else:
            sf.print_bug("error in  tb_write_def_file_variable")
    
    def tb_write_def_line_variable(sf, tipo):
        if tipo == "dut":
            # variabile per salvare ad ogni ciclo la linea del file
            #   VARIABLE riga_write: LINE;
            sf.current_process.def_variable(l_name=[sf.write_riga], l_type=['LINE'])
        elif tipo == "aref":
            # variabile per salvare ad ogni ciclo la linea del file
            # riferite ad aref
            #   VARIABLE riga_write_aref: LINE;
            sf.current_process.def_variable(l_name=[sf.write_riga_aref], l_type=['LINE'])
        elif tipo == "correct":
            # variabile per salvare ad ogni ciclo la linea del file
            # riferite al file di uscite corrette
            #   VARIABLE red_riga_correct: LINE;
            sf.current_process.def_variable(l_name=[sf.read_riga_correct], l_type=['LINE'])
    
    
    ####### READ FUNCTIOafter_append ########################################
    def tb_read_set_end_loop(sf):
        sf.current_process.set_signal("-- viene settato il segnale che dice al ciclo di write di\n -- smettere di confrontare le uscite",
                "-- end", [sf.end_loop_sig], ["1"],0);
    
    def tb_read_file_close(sf):
        # chiudo il file
        sf.current_process.file_close(sf.read_input_file_variable)

    def tb_read_wait_in_out_delay(sf):
        # aspetto che lo start sia 1
        sf.current_process.wait("FOR", sf.param['constant']['in_out_delay'],1)
    
    def tb_read_wait_clk_between_input(sf):
        # aspetto che lo start sia 1
        sf.current_process.wait("FOR", sf.number_to_clknum(sf.param['constant']['clk_between_input']),1)
    
    def tb_read_variable_in_signal_custom_time(sf):
        if not sf.is_aref():
            sf.current_process.assign_delay_loop(sf.obj_param.to_signal(sf.param['sync']['custom_in']['name']),
                    sf.obj_param.to_variable(sf.param['sync']['custom_in']['name']),
                    sf.number_to_clknum(sf.param['sync']['custom_in']['shift']),1)
        else:
            sf.current_process.double_assign_delay_loop(sf.obj_param.to_signal(sf.param['sync']['custom_in']['name']),
                    sf.obj_param.to_variable(sf.param['sync']['custom_in']['name']),
                    sf.obj_param.to_signal2(sf.param['sync']['custom_in']['name']),
                    sf.obj_param.to_variable2(sf.param['sync']['custom_in']['name']),
                    sf.number_to_clknum(sf.param['sync']['custom_in']['shift']),1)


    def tb_read_variable_in_signal(sf):
        sf.current_process.set_signal("-- scrivo i valori delle variabili nei segnali", "-- fine",
                sf.param['sync']['input_sequence_sig'],
                sf.param['sync']['input_sequence_var'],1)
        if sf.is_aref():
            sf.current_process.set_signal("-- scrivo i valori delle variabili nei segnali", "-- fine",
                    sf.param['sync']['input_sequence_sig2'],
                    sf.param['sync']['input_sequence_var'],1)
            
    def tb_read_line_in_variable(sf):
        # salvo nelle variabili della dut i valori
        sf.current_process.read_col(sf.read_riga, sf.param['sync']['input_sequence_var'])
    
    def tb_read_line_in_variable_correct_out(sf):
        # salvo nelle variabili delle uscite corrette i valori
        sf.current_process.read_col(sf.read_riga_correct, sf.to_var(sf.param['sync']['correct_out_name']['sig'],"correct"))

    def tb_read_readline_correct_out(sf):
        # vado a leggere il file di uscite corrette 
        # e ne salvo una riga
        sf.current_process.read_line(sf.write_output_file_correct_variable, sf.read_riga_correct)

    def tb_read_readline(sf):
        # leggo una riga di file
        sf.current_process.read_line(sf.read_input_file_variable, sf.read_riga)

    def tb_read_wait_start(sf, indent=2):
        # aspetto che lo start sia 1
        sf.current_process.wait("UNTIL", "START  = '1'",indent)

    def tb_read_while_begin(sf):
        # Inizia il while
        sf.current_process.file_loop_begin(sf.read_input_file_variable)

    def tb_read_set_default_aref_signal(sf):
        # sezione in cui vengono settati i valori di defaault
        # d'ingresso di prf
        sf.current_process.set_signal("-- Definizione dei default AREF", 
                "-- Fine definizione default",
                sf.param['constant']['default_in_value']['name'],
                sf.param['constant']['default_in_value']['value'])

    def tb_read_set_default_dut_signal(sf):
        # sezione in cui vengono settati i valori di default
        # d'ingresso della dut
        sf.current_process.set_signal("-- Definizione dei default DUT", 
                "-- Fine definizione default",
                sf.param['constant']['default_in_value']['name'],
                sf.param['constant']['default_in_value']['value'])

    def tb_read_file_open(sf): 
        # Apertura del file dei dati di ingresso
        sf.current_process.file_open(sf.param['file']['input'], sf.read_input_file_variable, "read_mode")
    
    def tb_read_def_input_varaible(sf):
        # tutte le restanti variabili
        sf.current_process.def_variable(l_name= sf.dut['port']['var']['name'],
                l_type = sf.dut['port']['var']['type'])

    def tb_read_def_line_variable(sf):
        # variabile per salvare ad ogni ciclo la linea del file
        #   VARIABLE riga_read: LINE;
        sf.current_process.def_variable(l_name=[sf.read_riga], l_type=['LINE'])

    def tb_read_def_file_variable(sf):
        # definizione della variabile per il file, esempio: 
        #   FILE INPUT_BIN: text;
        sf.current_process.def_file( sf.read_input_file_variable )
    #############################i################################

    def tb_while_condition(sf, condition):
        # obj dev'essere del tipo vhdl_gen.cl_process
        sf.current_process.while_condition(condition)

    def tb_wait_clk_quinti(sf, indent):
        # obj dev'essere un oggetto process dell'oggetto
        # vhdl_gen
        # aspetto clock quinti per non dare o prendere i dati sul fronte
        sf.current_process.wait("FOR", sf.clk_constant+"/5",indent)

    def tb_wait_n_clk(sf, n, indent=0):
        # obj_in_which_write è un oggetto process dell'oggetto vhdl_gen
        # aspetto n clk
        if n == 1:
            sf.current_process.wait("FOR", sf.clk_constant, indent) 
        else:
            sf.current_process.wait("FOR", sf.clk_constant+"*"+str(n), indent) 
   
    def tb_clock(sf, indent):
        # in processo di clock si utilizza la costante clk_constant come periodo
        # di clock
        clk_process = sf.obj_vhd.cl_process(sf.obj_vhd, sf.clk_process_name, indent)
        clk_process.clock(sf.param['sync']['clk']['sig_name'], sf.clk_constant)
        clk_process.printer()
        # se c'è aref devo collegare anche il segnale di clock di aref
        sf.obj_vhd.signal_connection_or_assign(sf.param['sync']['clk']['sig_name'], sf.param['sync']['clk']['sig_name2'], 0)
        sf.obj_vhd.skip(1)

    
    def tb_rst(sf, indent):
        # Questa funzione inizializza il reset utilizzando una lista di valori del reset
        # e un'altra lista che gli dice quanto tempo 
        clk_process = sf.obj_vhd.cl_process(sf.obj_vhd, sf.rst_process_name, indent)
        l_time = [ sf.clk_constant+'*'+str(i) for i in sf.param['sync']['rst']['wave']['time'] ]
        l_time[-1]="end"
        clk_process.rst(sf.param['sync']['rst']['sig_name'],sf.param['sync']['rst']['wave']['value'],  l_time)
        clk_process.printer()
        # se c'è aref devo collegare anche il segnale di clock di aref
        sf.obj_vhd.signal_connection_or_assign(sf.param['sync']['rst']['sig_name'], sf.param['sync']['rst']['sig_name2'], 0)
        sf.obj_vhd.skip(1)


    def tb_library(sf, indent, lib = ["ieee.std_logic_textio.all","std.textio.all"]):
        sf.obj_vhd.set_indent(indent)
        print("--- libb "+sf.dut['library'])
        sf.obj_vhd.file_print(sf.dut['library'])
        for i in lib:
            sf.obj_vhd.use(i)
        sf.obj_vhd.skip(2)


    def tb_entity (sf, indent):
        # stampa l'entity della testbench con i generic 
        entity1 = sf.obj_vhd.cl_entity(sf.obj_vhd, sf.tb_name, indent, l_gen_name=sf.dut['generic']['glob_name'],
                                                l_gen_type=sf.dut['generic']['glob_type'],  
                                                l_gen_value=sf.dut['generic']['glob_value'])

        entity1.printer()

    def tb_dut_component(sf, indent):
        # crea l'instanziazione della dut come componente e la stampa su file
        dut_component = sf.obj_vhd.cl_component(sf.obj_vhd, sf.dut['name'],indent, l_port_name=sf.dut['port']['port']['name'],
                                        l_port_type=sf.dut['port']['port']['type'],
                                        l_port_io=sf.dut['port']['port']['io'],
                                        l_gen_name=sf.dut['generic']['name'],
                                        l_gen_type=sf.dut['generic']['type'],
                                        l_gen_value=sf.dut['generic']['value'])
        dut_component.printer()

    def tb_aref_component(sf, indent):
        # crea l'instanziazione di aref come componente e la stampa su file
        if sf.is_aref():
            aref_component = sf.obj_vhd.cl_component(sf.obj_vhd, sf.aref['name'],indent, 
                                        l_port_name=sf.aref['port']['port']['name'],
                                        l_port_type=sf.aref['port']['port']['type'],
                                        l_port_io=sf.aref['port']['port']['io'],
                                        l_gen_name=sf.aref['generic']['name'],
                                        l_gen_type=sf.aref['generic']['type'],
                                        l_gen_value=sf.aref['generic']['value'])
            aref_component.printer()


    def tb_arch_start(sf, indent):
        sf.obj_vhd.set_indent(indent)
        sf.obj_vhd.arch_start(sf.arch_type, sf.tb_name)

    def tb_arch_begin(sf, indent):
        sf.obj_vhd.set_indent(indent)
        sf.obj_vhd.arch_begin()

    def tb_arch_end(sf, indent):
        sf.obj_vhd.set_indent(indent)
        sf.obj_vhd.arch_end()
   
    def tb_dut_signal(sf, indent):
        sf.obj_vhd.set_indent(indent)
        sf.obj_vhd.section_signal_definition(sf.dut['port']['sig']['name'], sf.dut['port']['sig']['type'])
        # segnale per sapere quando ho finito di dare gli input, non serve
        # in tutte le modalità
        sf.obj_vhd.section_signal_definition([sf.end_loop_sig],['INTEGER'])

    def tb_aref_signal(sf, indent):
        sf.obj_vhd.set_indent(indent)
        if sf.is_aref():
            sf.obj_vhd.section_signal_definition(sf.aref['port']['sig']['name'], sf.aref['port']['sig']['type'])
        
    def tb_dut_map(sf, indent):
        dut_map = sf.obj_vhd.cl_map( sf.obj_vhd, sf.dut_process_pfx+sf.dut['name'], sf.dut['name'], indent, 
                                l_p_io=sf.dut['port']['port']['name'], 
                                l_p_name=sf.dut['port']['sig']['name'], 
                                l_g_io=sf.dut['generic']['name'], 
                                l_g_name=sf.dut['generic']['glob_name'])
        sf.print_bug("...................")
        sf.print_bug(sf.dut['port']['port']['name'])
        sf.print_bug(sf.dut['port']['sig']['name'])
        sf.print_bug(sf.dut['generic']['name'])
        sf.print_bug(sf.dut['generic']['glob_type'])
        sf.print_bug("...................")
        dut_map.printer()

    def tb_aref_map(sf, indent):
        if sf.is_aref(): 
            dut_map = sf.obj_vhd.cl_map(sf.obj_vhd, sf.aref_process_pfx+sf.aref['name'], sf.aref['name'], indent, 
                                l_p_io=sf.aref['port']['port']['name'], 
                                l_p_name=sf.aref['port']['sig']['name'], 
                                l_g_io=sf.aref['generic']['name'], 
                                l_g_name=sf.aref['generic']['glob_name'])
            dut_map.printer()

    

    ###############################
    # funzioni di supporto
    def type_of(sf, l_name_to_find, l_name, l_type):
        c=l_name_to_find
        d= l_name
        e=l_type
        sf.print_bug("c: "+str(c)+"  d:"+str(d)+" e:"+str(e))
        try:
            lista=[e[int(str([n-1 for i,n in zip(d,range(1,len(d)+1)) if i==l])[1:2])] for l in c ]
        except ValueError:
            print("---------\nErrore ingressi o uscite selezionate non esistenti\n-----------")
            return 0
        return lista
    
    def to_var(sf, stringa, tipo):
        if tipo=="":
            return [ "v_"+ i for i in stringa]  
        return [ "v_"+tipo +"_"+ i for i in stringa]
    
    def to_signal(sf, stringa, tipo):
        if tipo=="":
            return [ "s_"+ i for i in stringa]  
        return [ "s_"+tipo +"_"+ i for i in stringa]

    def is_aref(sf):
        return sf.param['flag']['aref'] == "1"
    def is_seq(sf):
        return sf.param['flag']['seq_comb'] =="seq"
    def is_fsm(sf):
        return sf.param['flag']['fsm'] =="1"
    def is_parallel_custom_in(sf):
        return sf.param['flag']['parallel_custom_in'] =="1"
    def is_save_output(sf):
        return sf.param['flag']['save_output']=="1"
    def is_correct_out(sf):
        return sf.param['flag']['correct_out']=="1"

    def number_to_clknum(sf, l_number):
        if type(l_number)==str:
            return sf.clk_constant+"*"+l_number
        l_num =  l_number[1:]
        return [ sf.clk_constant+"*"+i for i in l_num ]
    def print_bug(sf,stringa):
        if sf.debug:
            print(stringa)

#dirconf="/media/tesla/Storage/Linux/Scrivania/Progetti_work/git/lab_lowpower/lab6/4/tb_generator/config"
#dirconf="/home/tesla/git/lab_lowpower/lab6/4/tb_generator/conf2"
#dire="/media/tesla/Storage/Linux/Scrivania/Progetti_work/git/lab_lowpower/lab6/4/tb_generator"
#obj=tb_gen(dirconf, "testbench", "behavioural",1,0)
#obj.extract_data()
#obj.generate_testbench()
