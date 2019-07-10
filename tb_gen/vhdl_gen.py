# -*- coding: utf-8 -*-
#!/usr/bin/python3
import os
from random import *
import sys
# aggiungo il path dove sono presenti gli altri file
# del programma, così posso importare i moduli
# da me scritti
install_path="/home/lp19.10/Desktop/lab6/456/simulator/tb_gen"
sys.path.append(install_path)


# fn sta per filename

class vhdl_gen:
    def __init__(sf, fn_dut, dir_out):
        # Questa funzione prende in ingresso:
        # 	fn_dut -> nome della dut.vhd che dev'essere simulata
        #	dir_out -> directory in cui salvare le uscite
        #       
        # Con questi due nomi vengono generati i seguenti file con nomi
        # automatici:
        #	fn_dut_out -> file in cui verranno scritte le uscite della
        #					dut da testare, il file ha lo stesso nome della dut
        #					ma viene aggiunto "_out" alla finie
        #	fn_aref_out -> file in cui verranno scritte le uscite della
        #						dut corretta, il file ha lo stesso nome della
        #						dut corretta ma viene aggiunto "_out" alla fine
        #	fn_tb -> nome del testbench, ha lo stesso nome della dut ma viene
        #				aggiunto "tb_" all'inizio
        
        # nome del file vhdl della testbench
        sf.fn_dut= fn_dut
        if dir_out[-1]=="/":
            dir_out=dir_out[:-1]

        # nome del file d'uscita della dut
        sf.fn_dut_out = dir_out +"/" + os.path.basename(sf.fn_dut)[:-4]+ "_out.txt"
       
        sf.fn_tb = dir_out+"/tb_" + os.path.basename(sf.fn_dut)
        print("sf.fn_dut "+sf.fn_dut)
        print("sf.fn_dut_out "+sf.fn_dut_out)
        print("sf.fn_tb "+sf.fn_tb)
        
            # variabile di profondità: poichè si vuole indentare il codice del
        # testbench si tiene conto con questa variabile quando si entra in
        # un'entity etc. incrementandola
        sf.indent_deep=0
        # spazio base di indentazione
        sf.indent_space="		"
        # apro il file di testbench da generare, eliminando versioni precedenti
        CommandToEliminateTest = "rm " + sf.fn_tb
        os.system(CommandToEliminateTest)
        sf.f_tb = open(sf.fn_tb, "w")
        # posso decidere di stampare su file o su una variabile
        sf.buffer=""
        sf.buffer_on=False
        sf.gen_and_port_en=False

        sf.signed_std={}


    ###########################################################################
    #######  funzioni per scrivere i segnali base uno per uno     #############

    def clear_buf(sf):
            sf.buffer=""

    def buf_on(sf):
            sf.buffer_on=True
    def buf_off(sf):
            sf.buffer_on=False
            sf.clear_buf()
    def set_indent(sf, n_indent):
            sf.previous_indent_deep = sf.indent_deep
            sf.indent_deep = n_indent

    def set_previous_indent(sf):
            sf.indent_deep = sf.previous_indent_deep  

    def call_func_indent(sf, func_name, indent, *args):
            sf.set_indent(indent)
            func_name(*args)
            sf.set_previous_indent()
    
    def file_print (sf, stringa, newline="\n"):
            # inserisce la formattazione corretta
            stringaa=str(stringa)
            for i in stringaa.split("\n"):
                    if not sf.buffer_on:
                            sf.f_tb.write(sf.indent_space*sf.indent_deep + str(i) + newline)
                    else:
                            sf.buffer+=sf.indent_space*sf.indent_deep + str(i) + newline
    
    def skip(sf, skip):
            for i in range(0,skip):
                    sf.file_print("")

    def signal (sf, name, type, default_value="#"): 
            # genero un signal
            # name -> nome del segnale
            # type -> tipo del segnale
            # defalut_value -> valore di defalut, se non viene dato il segnale non
            #					viene inizializzato
            if default_value=="#":
                    sf.file_print("SIGNAL " + str(name) + " : " + str(type) + " ;")
            else:
                    sf.file_print("SIGNAL " + str(name) + " : " + str(type) + " := " + str(default_value) + " ;")

    def constant_def (sf, name, type, value): 
            # genero un signal
            # name -> nome del segnale
            # type -> tipo del segnale
            # value -> valore della costante
            sf.file_print("CONSTANT " + str(name) + " : " + str(type) + " := " + str(value) + " ;")

    def signal_io (sf, name, type, io, end=0):
            # genero un signal da mettere nel port o port_map
            # name -> nome dell'io
            # io -> IN o OUT 
            # type -> tipo del segnale: std_logic, std_logic_vector(0 to 4) ...
            sf.file_print(name + " : " + str(io) + " " + str(type) + " ;"*(not end))

    def signal_generic (sf, name, type, default_value, end=0):
            # genero un segnale generic
            # name -> nome del segnale
            # type -> tipo del segnale generico
            # default -> default del segnale generico
            sf.file_print(name + " : " + str(type) + " := " + str(default_value) + " ;"*(not end))	

    def variable (sf, name, type, default_value="#"):
            # genero una variable dentro ad un processo
            # name -> nome della variabile
            # type -> tipo della variabile
            # default_value ->  valore di default della variabile
            if default_value=="#":
                    sf.file_print("VARIABLE " + name + " : " + str(type) + " ;")
            else:
                    sf.file_print("VARIABLE " + name + " : " + str(type) + " := " + str(default_value) + " ;")

    def mapping (sf, name_io, name_signal,end=0):
            # setto il mapping
            # name_io -> nome del segnale della porta a cui collegare il signal
            # 			interno al testbench
            # name_signal -> nome del segnale da collegare all'io
            sf.file_print(name_io + " => " + str(name_signal) + " ,"*(not end))

    def signal_connection_or_assign (sf, name_from_or_value, name_to, end=0):
            # name_from_or_value -> nome del segnale o del valore da assegnare al
            # 						segnale naame_to
            # name_to -> nome del segnale che dev'essere collegato o assegnato
            sf.file_print(name_to + " <= " + str(name_from_or_value) + " ;"*(not end))

    def variable_connection_or_assign (sf, name_from_or_value, name_to, end=0):
            # name_from_or_value -> nome del segnale o del valore da assegnare alla
            # 						variabile name_to
            # name_to -> nome della variabile che dev'essere collegata o assegnata
            sf.file_print(name_to + " := " + str(name_from_or_value) + " ;"*(not end))

    def file_open(sf, file_name, file_variable, mode):
            sf.file_print('file_open( '+file_variable+", "+"\""+file_name+"\""+', '+mode+'); ')

    def file_close(sf, file_variable):
            sf.file_print('file_close( '+file_variable+' );')

    def file_def(sf, file_variable):
            sf.file_print('FILE ' + file_variable + ': text;')

    def file_loop_begin(sf, file_variable):
            sf.file_print('WHILE NOT endfile(' + file_variable + ') LOOP')

    def while_condition(sf, condition):
            sf.file_print("WHILE " + condition + " LOOP")

    def loop_number(sf, variable, fromm, to):
            sf.file_print('FOR '+ variabile+' IN '+fromm+' TO '+to+' LOOP')

    def loop_end(sf):
            sf.file_print('END LOOP;')

    def read_line(sf, file_variable, line_var):
            sf.file_print('readline(' + file_variable  + ', ' + line_var+ ' );')

    def read_col(sf, file_variable, col_var):
            sf.file_print('read(' + file_variable  + ', ' + col_var+ ' );')

    def writeline(sf, file_variable, riga_variable):
            sf.file_print("writeline("+file_variable+", "+riga_variable+");")

    def write(sf, riga_variable, value):
            sf.file_print("write("+riga_variable+", "+value+");")

    def f_assert(sf, condition, report_str, warninig_type):
            sf.file_print("ASSERT ("+condition+") REPORT "+report_str+" "+warninig_type)

    # sincronizzazione
    def wait(sf, for_until, time):
            sf.file_print('WAIT ' + for_until + ' ' + time + ';')

    def library(sf, library):
        sf.file_print("LIBRARY " + library + " ;")

    def use(sf, library):
        sf.file_print("USE " + library + " ;")

    def sync_wave(sf, signal_name, l_value, l_time):
        for value,time in zip(l_value, l_time):
            sf.signal_connection_or_assign(value, signal_name,0)
            if time=="end":
                sf.wait("","")
            else:
                sf.wait("FOR", time)

    def assign_delay_loop(sf, l_signal, l_variable, l_time, indent=1):
        for signal,variable,time in zip(l_signal, l_variable, l_time):
            sf.signal_connection_or_assign(variable, signal,indent)
            if time=="end":
                sf.wait("","")
            else:
                sf.wait("FOR", time)

    def double_assign_delay_loop(sf, l_signal, l_variable, l_signal2, l_variable2, l_time, indent=1):
        if len(l_time)<len(l_signal):
            l_time.append("nop")

        for signal,variable,signal2,variable2,time in zip(l_signal, l_variable, l_signal2, l_variable2, l_time):
            sf.signal_connection_or_assign(variable, signal,indent)
            sf.signal_connection_or_assign(variable2, signal2,indent)
            if time=="end":
                sf.wait("","")
            elif time=="nop":
                pass
            else:
                sf.wait("FOR", time)

    ###########################################################################
    #######  funzioni per scrivere le varie sezioni     #############


    def section (sf, section_begin, section_end, func, l_name, l_type_or_name2, end_enable, l_default_value="#"):
            # creo una sezione generic da inserire nell'entity
            # section_begin -> stringa iniziale di inizio sezione, tipo "port (" 
            # section_end -> stringa finale della sezione, tipo ");" o ")"
            # func -> nome della funzione da usare per scrivere con la sintassi
            #		 giusta i segnali all'interno della sezione
            # l_name -> lista di nomi dei segnali generic
            # l_type -> lista di tipi dei generic
            # l_default_value -> lista di valori di default dei generici

            sf.file_print(section_begin)
            # se non ci sono i default non ciclo su essi
            if end_enable:
                if l_default_value=="#":
                        lunghezza=len(l_name)
                        i=1
                        for name,type in  zip(l_name, l_type_or_name2):
                                func(name, type, i==lunghezza)
                                i+=1
                else:                        
                        lunghezza=len(l_name)
                        i=1
                        for name,type,def_value in  zip(l_name, l_type_or_name2, l_default_value):
                                func(name, type, def_value, i==lunghezza)
                                i+=1
            else:
                if l_default_value=="#":
                        for name,type in  zip(l_name, l_type_or_name2):
                                func(name, type)
                else:
                        for name,type,def_value in  zip(l_name, l_type_or_name2, l_default_value):
                                func(name, type, def_value)
            sf.file_print(section_end)

    def section_free(sf, func_name, *args):
            ll=len(args[0])
            l=len(args)
            for i in range(0,ll):
                    to_pass=[]
                    for j in range(0,l):
                            to_pass.append(args[j][i])
                    func_name(*to_pass)

    def section_signal_connection_or_assign (sf, begin_comment, end_comment, l_name_to, l_name_from_or_value, end=1):
            # creo una connessione di un segnale(l_name_from_or_value) con un altro segnale(l_name_to) oppure
            # l'assegnazione di un segnale(l_name_from_or_value) ad un valore(l_name_to)
            sf.section (begin_comment, 
                                    end_comment,
                                    sf.signal_connection_or_assign, 
                                    l_name_from_or_value, 
                                    l_name_to, end)
            
    def section_variable_connection_or_assign (sf, begin_comment, end_comment, 	l_name_to, l_name_from_or_value, end=1):
            # creo una connessione di una variabile(l_name_from_or_value) con un
            # segnale(l_name_to) oppure l'assegnazione di una variabile(l_name_from_or_value) 
            # ad un valore(l_name_to)
            sf.section (begin_comment, 
                                    end_comment,
                                    sf.variable_connection_or_assign, 
                                    l_name_from_or_value, 
                                    l_name_to, end)
            

    def section_generic (sf, l_name, l_type, l_default_value):
            # creo una sezione generic da inserire nell'entity
            # l_name -> lista di nomi dei segnali generic
            # l_type -> lista di tipi dei generic
            # l_default_value -> lista di valori di default dei generici
            sf.section("GENERIC (", ");", sf.signal_generic, l_name, l_type,1,  l_default_value)

    def section_port (sf, l_name, l_type, l_default_value):
            # creo una sezione generic da inserire nell'entity
            # l_name -> lista di nomi dei segnali generic
            # l_type -> lista di tipi dei generic
            # l_default_value -> lista di valori di default dei generici
            sf.section("PORT (", ");", sf.signal_io, l_name, l_type,1,  l_default_value)

    def section_generic_map(sf, l_name_io, l_name_signal):
            # creo una sezione generic map da inserire nel portmap
            # l_name_io -> lista di nomi dei segnali di io da collegare
            # l_name_signal -> lista dei nomi dei segnali
            sf.section("GENERIC MAP (", ")"+";"*(not sf.gen_and_port_en ), sf.mapping, l_name_io, l_name_signal,1)

    def section_port_map(sf, l_name_io, l_name_signal):
            # creo una sezione port map da inserire nel portmap
            # l_name_io -> lista di nomi dei segnali di io da collegare
            # l_name_signal -> lista dei nomi dei segnali
            sf.section("PORT MAP (", ");", sf.mapping, l_name_io, l_name_signal, 1)

    def section_signal_definition(sf, l_name, l_type, l_value="#"):
            # creo una sezione in cui vado a inserire i segnali che userò nel
            # testbench per andare a passare i valori ai componenti
            # l_name -> lista di nomi dei segnali
            # l_type -> lista di tipi dei segnali
            # l_value -> lista dei default dei segnali, se c'è un "#"
            # 					considero che il default non c'è e non lo metto
            comment="-- lista dei segnali utili per passare i valori ai componenti"
            sf.section(comment, "---- fine segnali\n\n", sf.signal, l_name, l_type,0, l_value)

    def section_constant_definition(sf, l_name, l_type, l_value):
            # creo una sezione in cui vado a inserire i segnali che userò nel
            # testbench per andare a passare i valori ai componenti
            # l_name -> lista di nomi delle costanti
            # l_type -> lista di tipi delle costanti
            # l_default_value -> lista dei valori delle costanti
            comment="-- lista delle costanti utilizzate"
            sf.section(comment, "---- fine costanti\n\n", sf.constant_def, l_name, l_type,0, l_value)

    def section_variable(sf, l_name, l_type, l_value):
            # creo una sezione in cui vado a inserire le variabili
            # l_name -> lista di nomi delle variabili
            # l_type -> lista di tipi delle variabili
            # l_default_value -> lista dei valori di default delle variabili
            comment="-- lista di variabili utilizzate del processo"
            sf.section(comment, "---- fine variabili\n\n", sf.variable, l_name, l_type,0, l_value)

    def section_read_col(sf, file_variable, l_variable):
            for i in range(0,len(l_variable)):
                    sf.read_col(file_variable, l_variable[i])


    ####################################################################################
    #######  funzioni per scrivere le varie sezioni a livello più alto     #############

    def generic_and_port_map (sf,  l_p_io="#", l_p_name="#", l_g_io="#", l_g_name="#" ):
            # l_p_name -> lista dei segnali della porta
            # l_p_io -> lista dell'io, IN/OUT etc
            # l_g_name -> lista dei nomi dei generici
            # l_p_io -> lista delloutput da collegare
        if l_g_name=="#":
            sf.section_port_map(l_p_io, l_p_name)
        elif l_p_name=="#":
            print("-----------------------------------------")
            sf.section_generic_map(l_g_io, l_g_name)
        else:
            sf.gen_and_port_en=True
            sf.section_generic_map(l_g_io, l_g_name)
            sf.section_port_map(l_p_io, l_p_name)
            sf.gen_and_port_en=False

    def generic_and_port (sf, l_p_name="#", l_p_type="#", l_p_io="#", l_g_name="#", l_g_type="#", l_g_value="#" ):
            # l_p_name -> lista dei segnali della porta
            # l_p_type -> lista dei tipi dei segnali
            # l_p_io -> lista dell'io, IN/OUT etc
            # l_g_name -> lista dei nomi dei generici
            # l_g_type -> lista del tipo di generico
            # l_g_value -> valore di default generico
        if l_g_name=="#":
            sf.section_port(l_p_name, l_p_type, l_p_io)
        elif l_p_name=="#":
            print("-----------------------------------------")
            sf.section_generic(l_g_name, l_g_type, l_g_value)
        else:
            sf.gen_and_port_en=True
            sf.section_generic(l_g_name, l_g_type, l_g_value)
            sf.section_port(l_p_name, l_p_type, l_p_io)
            sf.gen_and_port_en=False

    def section2 (sf, begin, end, func, *args):
            # begin -> stringa di intestazione
            # end -> stringa finale 
            # guardare generic_and_port per spiegazioni su args
            # l_p_name, l_p_type, l_p_io, l_g_name=0, l_g_type=0, l_g_value=0 
            sf.file_print(begin)
            sf.indent_deep+=1
            func(*args)
            sf.indent_deep-=1
            sf.file_print(str(end))
            

    def print_entity (sf, entity_name, *args):
            # guardare generic_and_port per spiegazioni
            # l_ap_name, l_p_type, l_p_io, l_g_name=0, l_g_type=0, l_g_value=0 
            sf.section2("ENTITY "+entity_name+" IS", "END "+entity_name+" ;", sf.generic_and_port, *args)

    def print_component (sf, component_name, *args):
            # guardare generic_and_port per spiegazioni
            # l_p_name, l_p_type, l_p_io, l_g_name=0, l_g_type=0, l_g_value=0 
            sf.section2("COMPONENT " + component_name, "END COMPONENT;", sf.generic_and_port, *args)

    def print_port_map (sf, inst_name, component_name, *args):
            # inst_name -> nome dell'istanza (istanz: componente)
            # component_name -> nome del componente
            # guardare generic_and_port per spiegazioni
            # l_p_name, l_p_type, l_p_io, l_g_name=0, l_g_type=0, l_g_value=0 
            sf.section2(inst_name+": "+component_name, "", sf.generic_and_port, *args)

    def print_process (sf, process_name, str_before_begin, str_after_begin):
            # process_name -> nome del processo
            # str_in_process -> che ci deve stare nel processo
            sf.file_print(process_name+':')
            sf.indent_deep+=1
            sf.section2("PROCESS IS\n"+
                                    str_before_begin+"BEGIN",  
                                    "END PROCESS;",
                                    sf.file_print, 
                                    str_after_begin)
            sf.indent_deep-=1

    ####################################################################################
    #######  classi per semplificare la gestione del codice   #############

    def kargs_args1(sf, **kargs):
        l_port_name="#"
        l_port_type="#"
        l_port_io="#"
        l_gen_name="#"
        l_gen_type="#"
        l_gen_value="#"
        try:
            l_port_name=kargs['l_port_name']
            l_port_type=kargs['l_port_type']
            l_port_io=kargs['l_port_io']
            l_gen_name=kargs['l_gen_name']
            l_gen_type=kargs['l_gen_type']
            l_gen_value=kargs['l_gen_value']
        except KeyError:
            try:
                l_gen_name=kargs['l_gen_name']
                l_gen_type=kargs['l_gen_type']
                l_gen_value=kargs['l_gen_value']
            except:
                pass
            pass
        return [l_port_name, l_port_type, l_port_io, l_gen_name, l_gen_type, l_gen_value]

    def kargs_args2(sf, **kargs):
        l_name="#"
        l_type="#"
        l_value="#"
        try:
            l_name=kargs['l_name']
            l_type=kargs['l_type']
            l_value=kargs['l_value']
        except KeyError:
            pass
        return [l_name, l_type, l_value]
    
    def kargs_args_var(sf, **kargs):
        l_name="#"
        l_type="#"
        l_value="#"
        try:
            l_name=kargs['l_name']
            l_type=kargs['l_type']
            l_value=kargs['l_value']
        except KeyError:
            pass
        l_new_type=[]
        for j,i in zip(l_name,l_type):
            if i[0:6]=="signed":
                l_new_type.append("std_logic_vector"+i[6:])
                sf.signed_std[sf.real_sig(j)]=True
            else:
                l_new_type.append(i)
        return [l_name, l_new_type, l_value]

    def kargs_args3(sf, **kargs):
        l_p_io="#"
        l_p_name="#"
        l_g_io="#"
        l_g_name= "#"
        try:
            l_p_io=kargs['l_p_io']
            l_p_name=kargs['l_p_name']
            l_g_io= kargs['l_g_io']
            l_g_name= kargs['l_g_name']
        except KeyError:
            pass
        print([l_p_io, l_p_name, l_g_io, l_g_name])
        return [l_p_io, l_p_name, l_g_io, l_g_name]

    def real_sig(sf, stringa):
        return stringa.split("_")[-1]
    
    def correct_sig(sf, sig):
        try:
            correct_sig=sf.current_prefix*sf.signed_std[sf.real_sig(sig)]+"("+sig+")"
        except:
            correct_sig=sig
        return correct_sig
    def correct_sig_list(sf,l_sig, current_prefix):
        sf.current_prefix=current_prefix
        out=[]
        for i in l_sig:
            out.append(sf.correct_sig(i))
        return out


    class cl_entity:
            def __init__(sf, tb,  entity_name, indent_deep, **kargs):
                    # i seguenti sono i valori passabili con kargs
                    # l_port_name, l_port_type, l_port_io, l_gen_name, l_gen_type, l_gen_value
                    sf.entity_name=entity_name
                    sf.args=tb.kargs_args1(**kargs)
                    sf.tb=tb
                    sf.indent_deep=indent_deep
            def printer(sf):
                    sf.tb.indent_deep = sf.indent_deep
                    sf.tb.print_entity(sf.entity_name, *sf.args)
                    sf.tb.skip(2)
            def print_str(sf):
                    sf.tb.indent_deep = sf.indent_deep
                    sf.tb.buf_on()
                    sf.tb.print_entity(sf.entity_name, *sf.args)
                    sf.buffer=sf.tb.buffer
                    sf.tb.buf_off()

    class cl_component:
            def __init__(sf, tb, component_name, indent_deep, **kargs):
                    # i seguenti sono i valori passabili con kargs
                    # l_port_name, l_port_type, l_port_io, l_gen_name, l_gen_type, l_gen_value
                    sf.component_name = component_name
                    sf.args = tb.kargs_args1(**kargs)
                    sf.tb = tb
                    sf.indent_deep=indent_deep
            def printer(sf):
                    sf.tb.indent_deep = sf.indent_deep
                    sf.tb.print_component(sf.component_name, *sf.args)
                    sf.tb.skip(2)
            def print_str(sf):
                    sf.tb.indent_deep = sf.indent_deep
                    sf.tb.buf_on()
                    sf.tb.print_component(sf.component_name, *sf.args)
                    sf.buffer=sf.tb.buffer
                    sf.tb.buf_off()

    class cl_map:
            def __init__(sf, tb, instance_name, component_name,indent_deep, **kargs):
                    # i seguenti sono i valori passabili con kargs
                    # l_p_io, l_p_name, l_g_io, l_g_name
                    sf.instance_name= instance_name
                    sf.component_name= component_name
                    sf.args = tb.kargs_args3(**kargs)
                    sf.tb = tb
                    sf.indent_deep=indent_deep

            def printer(sf):
                    sf.tb.indent_deep = sf.indent_deep
                    sf.tb.file_print(sf.instance_name+" : "+sf.component_name)
                    sf.tb.indent_deep = sf.indent_deep+1
                    sf.tb.generic_and_port_map(*sf.args)
                    sf.tb.indent_deep = sf.indent_deep
                    sf.tb.skip(2)
            def print_str(sf):
                    sf.tb.indent_deep = sf.indent_deep
                    sf.tb.buf_on()
                    sf.tb.file_print(sf.instance_name+" : "+sf.component_name)
                    sf.tb.indent_deep = sf.indent_deep+1
                    sf.tb.generic_and_port_map( *sf.args)
                    sf.tb.indent_deep = sf.indent_deep
                    sf.buffer=sf.tb.buffer
                    sf.tb.buf_off()

    class cl_signal:
            def __init__(sf, tb, signal_name, indent_deep, *kargs):
                    # i seguenti sono i valori passabili con kargs
                    # l__name, l_type, l_value
                    sf.signal_name = signal_name
                    sf.args = tb.kargs_args2(**kargs)
                    sf.tb = tb
                    sf.indent_deep=indent_deep
            def printer(sf):
                    sf.tb.indent_deep = sf.indent_deep
                    sf.tb.section_signal_definition(*sf.args)
                    sf.tb.skip(2)
            def print_str(sf):
                    sf.tb.indent_deep = sf.indent_deep
                    sf.tb.buf_on()
                    sf.tb.section_signal_definition(*sf.args)
                    sf.buffer=sf.tb.buffer
                    sf.tb.buf_off()

    class cl_constant:
            def __init__(sf, tb, constant_name, indent_deep, **kargs):
                    # i seguenti sono i valori passabili con kargs
                    # l_name, l_type, l_value
                    sf.constant_name = constant_name
                    sf.args = tb.kargs_args2(**kargs)
                    sf.tb = tb
                    sf.indent_deep=indent_deep
            def printer(sf):
                    sf.tb.indent_deep = sf.indent_deep
                    sf.tb.section_constant_definition(*sf.args)
                    sf.tb.skip(2)
            def print_str(sf):
                    sf.tb.indent_deep = sf.indent_deep
                    sf.tb.buf_on()
                    sf.tb.section_constant_definition(*sf.args)
                    sf.buffer=sf.tb.buffer
                    sf.tb.buf_off()


    class cl_process:
            def __init__(sf, tb, process_name, indent_deep):
                    sf.tb = tb
                    sf.indent_deep=indent_deep
                    sf.process_name = process_name
                    # queste due variabili verranno scritte 
                    # man mano che si chiamano le funzioni della classe, quando verrà
                    # chiamata la funzione print verranno mandate alla funzione che
                    # stampa i process
                    # sono entrambe a livello 3 di indentazione
                    sf.before_begin=""
                    sf.after_begin=""
                    # dentro un process posso avere varie sezioni, naturalmente questa
                    # classe al momento ne permette solo alcune, in ogni caso si vuole
                    # permettere una interconnessione fra le varie sezioni, se per
                    # esempio si settano le costanti voglio poterle usare in una
                    # sezione di acquisizione, per questo motivo vado a salvare in
                    # liste i vari dati acquisiti
                    sf.file=[]

            def clock(sf, clk_signal, clk_period):
                    sf.after_append(sf.tb.file_print, 0, clk_signal+" <= '1', '0' AFTER "+clk_period+"/2;\nWAIT FOR "+clk_period+" ;")

            def rst(sf, rst_name, l_value, l_time):
                    sf.after_append(sf.tb.sync_wave, 0, rst_name, l_value, l_time)

            def before_append(sf, func_name, indent, *args):
                    # imposto la scrittura sul buffer e non sul file
                    sf.tb.buf_on()
                    # scrivo sul buffer il vhdl della variabile
                    sf.tb.call_func_indent(func_name, indent, *args)
                    # scrivo il vhdl nella parte prima del begin
                    sf.before_begin += sf.tb.buffer
                    # disabilito la scrittura nel buffer cancellandone il contenuto
                    sf.tb.buf_off()

            def after_append(sf, func_name, indent, *args):
                    # imposto la scrittura sul buffer e non sul file
                    sf.tb.buf_on()
                    # scrivo sul buffer il vhdl della variabile
                    sf.tb.call_func_indent(func_name, indent, *args)
                    # scrivo il vhdl nella parte prima del begin
                    sf.after_begin += sf.tb.buffer
                    # disabilito la scrittura nel buffer cancellandone il contenuto
                    sf.tb.buf_off()
                    

            #####  Livello 2 di indentazione  ###########
            def def_variable(sf, **kargs):
                    # i seguenti sono i valori passabili con kargs
                    # l_name, l_type, l_value
                    # l_value è opzionale, se non c'è non viene messo
                    # scrivo sul buffer il vhdl della variabile
                    sf.before_append(sf.tb.section_variable, 1, *sf.tb.kargs_args_var(**kargs))

            def file_open(sf, file_name, file_variable, mode):
                    # file_name -> nome del file 
                    # mode -> modo di apertura del file
                    sf.after_append(sf.tb.file_open, 0, file_name, file_variable, mode)
            
            def file_close(sf, file_variable):
                    sf.after_append(sf.tb.file_close, 0, file_variable)

            def set_signal(sf, begin_comment, end_comment, l_name1, l_name2,indent =0,end=0):
                    # l_name1 <= l_name2
                    l_name2=sf.tb.correct_sig_list(l_name2,"signed")  
                    sf.after_append(sf.tb.section_signal_connection_or_assign, indent,
                                                    begin_comment, end_comment, l_name1, l_name2, end)

            def assign_delay_loop(sf, l_signal, l_variable, l_time, indent =0):
                    # l_name1 <= l_name2
                    sf.after_append(sf.tb.assign_delay_loop, indent, l_signal, l_variable, l_time)

            def double_assign_delay_loop(sf, l_signal, l_variable, l_signal2, l_variable2, l_time, indent =0):
                    # l_name1 <= l_name2
                    sf.after_append(sf.tb.double_assign_delay_loop, indent, l_signal, l_variable, l_signal2, l_variable2, l_time)

            def set_variable(sf, begin_comment, end_comment, l_name1, l_name2, indent=0, end=0):
                    # l_name1 := l_name2
                    l_name2=sf.tb.correct_sig_list(l_name2,"std_logic_vector")  
                    sf.after_append(sf.tb.section_variable_connection_or_assign, indent, 
                                                    begin_comment, end_comment, l_name1, l_name2, end)
            def def_file(sf, file_variable):	
                    sf.before_append(sf.tb.file_def, 1, file_variable)
            
            def file_loop_begin(sf, file_variable):
                    sf.after_append(sf.tb.file_loop_begin, 0,  file_variable)

            def while_condition(sf, condition):
                    sf.after_append(sf.tb.while_condition, 0, condition)

            def loop_number(sf, variable, fromm, to):
                    sf.after_append(sf.tb.loop_number,0, variable, fromm, to)

            def loop_end(sf):
                    sf.after_append(sf.tb.loop_end,0 )
            
            def f_assert(sf, condition, report_str, warning_type, indent=0):
                    # ASSERT "condition" REPORT "report_str" "warning_type"
                    sf.after_append(sf.tb.f_assert,indent,condition, report_str, warning_type)

            #####  Livello in loop o no, percui posso avere livello 3 o 4 #####
            def read_line(sf, file_variable, line_var, indent_level=1):
                    sf.after_append(sf.tb.read_line, indent_level, file_variable, line_var)

            def read_col(sf, file_variable, l_col_var, indent_level=1):
                    sf.after_append(sf.tb.section_read_col, indent_level, file_variable, l_col_var)

            def writeline(sf, file_variable, riga_variable, indent_level=1):
                    sf.after_append(sf.tb.writeline, indent_level, file_variable, riga_variable)

            def write(sf, riga_variable, value, indent_level=1):
                    if type(value)==list:
                        for i in value:
                              sf.after_append(sf.tb.write, indent_level, riga_variable, i)
                              sf.after_append(sf.tb.write, indent_level, riga_variable, "\' \'")
                    else:
                        sf.after_append(sf.tb.write, indent_level, riga_variable, value)

            def save_variable_in_signal(sf, l_name1, l_name2, indent_level=1):
                    sf.after_append(sf.tb.section_signal_connection_or_assign, indent_level, 
                                                    "", "", l_name1, l_name2)

            def printer(sf):
                    sf.tb.indent_deep = sf.indent_deep
                    sf.tb.print_process(sf.process_name, sf.before_begin, sf.after_begin)	
                    sf.tb.skip(2)
            
            def print_str(sf):
                    sf.tb.indent_deep = sf.indent_deep
                    sf.tb.buf_on()
                    sf.tb.print_process(sf.process_name, sf.before_begin, sf.after_begin)
                    sf.buffer = sf.tb.buffer
                    sf.tb.buf_off()
                    

            #### Livello specifico #####################à
            def wait(sf, for_until, time, indent=1):
                    sf.after_append(sf.tb.wait, indent, for_until, time)

    def arch_start(sf, type,  arch_name):
            sf.file_print('ARCHITECTURE ' + type + ' OF ' + arch_name + ' IS' )
            sf.skip(2)

    def arch_begin(sf):
            sf.file_print('BEGIN')
            sf.skip(2)
    def arch_end(sf):
            sf.file_print('END ARCHITECTURE;')
            sf.skip(2)

    def test_function(sf):
        name=["IN1", "IN2", "IN3", "SEL1", "OUT1", "OUT2"]
        name2=[v+"_s" for v in name ]
        io=["IN","IN", "IN", "OUT", "OUT", "OUT"]
        type=["std_logic_vector", "std_logic_vector", "std_logic_vector", "std_logic", "std_logic_vector", "std_logic"]
        value=[1,2,3,4,5,6]
        entity1=sf.entity(sf, "pippo",
            l_port_name=name,l_port_type=type,l_port_io=io,l_gen_name=name2,l_gen_type=type,
            l_gen_value=value)
        entity1.printer()
        #sf.section_port_map(name, name2)
        #sf.section_generic_map(name, name2)
        #sf.section_port(name, type, value)
        #sf.section_generic(name, type, value)
        #sf.print_entity("pippo",name, type, io, name2, type, value)
        #sf.print_component("pippo",name, type, io, name2, type, value)
        #sf.print_port_map("DUT","pippo",name, type, io, name2, type, value)
        #sf.print_process("Clock","variable a: std_logic;","CLK_s <= '1', '0' AFTER CLK_PERIOD/2;\nWAIT FOR CLK_PERIOD;")
        #process1=sf.process(sf,"READ_PROCESS")
        #process1.def_variable ( l_name=['INPUT_BIN'], 
        #						l_type=['text'])
        #process1.def_file ("INPUT_BIN")
        #IN_name=['WR','WI','AR','AI','BR','BI']
        #IN_name=['WR','WI','AR','AI','BR','BI']
        #IN_type=["STD_LOGIC_VECTOR(15 DOWNTO 0)","STD_LOGIC_VECTOR(15 DOWNTO 0)",
        #"STD_LOGIC_VECTOR(15 DOWNTO 0)","STD_LOGIC_VECTOR(15 DOWNTO 0)",
        #"STD_LOGIC_VECTOR(15 DOWNTO 0)","STD_LOGIC_VECTOR(15 DOWNTO 0)"]
        #process1.def_variable( l_name=IN_name+['read_line'],
        #					   l_type=IN_type+['LINE'])
        #
        #process1.file_open("INPUT_BIN.txt","INPUT_BIN","read_mode")
        #process1.set_signal("--- valori di default","---- end valori di default",
        #					['WI_s','WR_s','A_IN_s','B_IN_s'],
        #					['"0000000000000000"','"0000000000000000"','"0000000000000000"','"0000000000000000"'])
        #process1.file_loop_begin("INPUT_BIN")
        #process1.wait("UNTIL", "START_s = '1'",3)
        #process1.wait("FOR", "CLK_PERIOD",3)
        #process1.read_line("INPUT_BIN","riga_line")
        #process1.read_col("riga_line",IN_name)
        #process1.loop_end()
        #process1.file_close("INPUT_BIN")


#obj = vhdl_gen("dut.vhd")
#obj.test_function()
#obj.entity()
