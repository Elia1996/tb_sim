# -*- coding: utf-8 -*-
import re
import os
import sys

# aggiungo il path dove sono presenti gli altri file
# del programma, così posso importare i moduli
# da me scritti
install_path="/home/lp19.10/Desktop/lab6/456/simulator/tb_gen"
sys.path.append(install_path)


def dir(stringa):
    if stringa[-1]=="/":    
        stringa=stringa[0:-1]
    if stringa[0]!="/":
        stringa="/"+stringa
    return stringa


class extract_entity:
    def __init__(sf, vhdl_file, end_str, debug=0):
        # per rendere unici i nomi dei segnali viene passata
        # anche una stringa che viene aggiunta alla fine di 
        # ciascun segnale
        sf.end_str = end_str 
        # si ipotizza di avere la cartella main_dir in cui ci
        # sta il file vhdl da estrarre
        # questo è il file vhdl da cui estrarre l'entity
        sf.vhdl_file = vhdl_file
        # se a 1 stampa variabili per debuggare
        sf.debug=debug
        sf.param={}
        sf.param['name']=""
        sf.param['port']={}
        sf.param['port']['port']={}
        sf.param['port']['sig']={}
        sf.param['port']['var']={}
        # nomi presi dal file
        sf.param['port']['port']['name']=[]
        sf.param['port']['port']['type']=[]
        sf.param['port']['port']['io']=[]
        # nomi di segnali creati utilizzando quelli della porta	
        sf.param['port']['sig']['name']=[]
        sf.param['port']['sig']['type']=[]
        # nomi di variabili creati usabdo quelli della porta
        sf.param['port']['var']['name']=[]
        sf.param['port']['var']['type']=[]
        # nomi di variabili per salvare i dati di ingresso corretti
        sf.param['port']['var']['correct_out_name']=[]
        sf.param['port']['var']['correct_out_type']=[]
        
        sf.param['generic']={}
        # generico
        sf.param['generic']['name']=[]
        sf.param['generic']['type']=[]
        sf.param['generic']['value']=[]
        # generico da inserire nell'entity della testbench
        sf.param['generic']['glob_name']=[]
        sf.param['generic']['glob_type']=[]
        sf.param['generic']['glob_value']=[]
        # costanti
        sf.param['constant']={}
        sf.param['constant']['default_in_value']={}
        sf.param['constant']['default_in_value']['name']=[]
        sf.param['constant']['default_in_value']['sig']=[]
        sf.param['constant']['default_in_value']['value']=[]
        sf.param['constant']['in_out_delay']=""
        # definisco gli ingressi  e le uscite
        sf.param['port']['in']={}
        sf.param['port']['out']={}
        sf.param['port']['in']['name']=[]
        sf.param['port']['in']['type']=[]
        sf.param['port']['out']['name']=[]
        sf.param['port']['out']['type']=[]


        # librerie 
        sf.param['library']=""
    
        sf.supp=""
    
    def save_library (sf):
        # estraggo l'entity
        with open(sf.vhdl_file,'r') as f:
            # estaggo tutto il testo, tolgo gli spazi e 
            # rendo tuttto minuscolo
            file=' '.join(f.readlines()).lower()
            file2=re.sub(r'--[^\n]*',' ',file)
            # estraggo la parte sopra all'entity
            file=file.split("entity")[0]
            ##### ESTRAGGO LE LIBRERIE ############
            sf.param['library'] = file 
        
            
    def save_entity(sf):
        sf.save_library()
        # estraggo l'entity
        with open(sf.vhdl_file,'r') as f:
            # estaggo tutto il testo, tolgo gli spazi e 
            # rendo tuttto minuscolo
            file=' '.join(f.readlines()).lower()
            file2=re.sub(r'--[^\n]*',' ',file)
            # estraggo la parte dell'entiry
            file=file.split("architecture")[0]
            #####   NOME DELL'ENTITY   #######################
            file2=re.sub(r'\s\s+|\t+',' ',re.sub(r'\n',' ',re.sub(r'\s\s+',' ',file)))
            p=re.compile(r'entity (?P<entityname>\w+) *is')
            sf.print_db("file2: ",file2)
            # trovo il nome dell'entity
            try:
                entity=p.search(file2).group('entityname')
                sf.print_db("nome entity:",entity)
                sf.param['name']=str(entity)
            except:
                print("error!!! entity name not found, verify filename:"+sf.vhdl_file)
                return 

            file=file.split("entity")[1]
            sf.print_db(file)
            # ora in file ho la parte dell'entity, tolgo tutte le
            # indentazioni e gli spazi doppi
            file=re.sub(r'\s\s+|\t+',' ',re.sub(r'\n',' ',re.sub(r'\s\s+',' ',file)))
            sf.print_db(file)
            #####   GENERIC   ################################
            # estraggo la parte dentro le parentesi del generic
            p=re.compile(r'generic\s*\(\s*(?P<generic>.*)\)\s*;\s*port')
            # la salvo in generic 
            try:
                generic=p.search(file).group('generic')
                sf.print_db(generic)
                # espressione regolare per trovare il nome tipo e
                # valore del gei generic nella stringa generic prima
                # trovata
                p=re.compile(r'(?P<name>\w+)\s*:\s*(?P<io>\w+)\s*:=\s*(?P<type>\w+)\s*;*')
                # trovo i generic
                generic=p.findall(generic)
                sf.print_db("generic data: ", generic)  # stampo i generic
                # ciclo per salvare i valori dentro data
                for gen in generic: 
                    sf.param['generic']['name'].append(gen[0])
                    sf.param['generic']['type'].append(gen[1])
                    sf.param['generic']['value'].append(gen[2])
                    sf.param['generic']['glob_name'].append(gen[0])
                    sf.param['generic']['glob_type'].append(gen[1])
                    sf.param['generic']['glob_value'].append(gen[2])
            except:
                sf.print_db("!!!!!!!  No generic in entity !!!!!!!!!")
            #####   PORT      ################################
            try:
                # estraggo la parte dentro le partentesi del port
                p=re.compile(r'port\s*\(\s*(?P<port>.*)\)\s*;\s*end')
                # la salvo in port
                port=p.search(file).group('port')
                # espressione regolare per trovare il nome tipo e
                # valore del gei generic nella stringa generic prima
                # trovata
                p=re.compile(r'(?P<name>\w+)\s*:\s*(?P<io>\w+) (?P<type>[^;]+)\s*;*')
                port=p.findall(port)
                # ciclo sulle porte salvando i dati in data come
                # vettori
                
                for p in port:
                    sf.param['port']['port']['name'].append(p[0])
                    sf.param['port']['port']['type'].append(p[2])
                    sf.param['port']['port']['io'].append(p[1])
                    # nomi di segnali creati utilizzando quelli della porta	
                    sf.param['port']['sig']['name'].append("s_"+sf.end_str+"_"+p[0])
                    sf.param['port']['sig']['type'].append(p[2])
                    # nomi di variabili creati usabdo quelli della porta
                    sf.param['port']['var']['name'].append("v_"+sf.end_str+"_"+p[0])
                    sf.param['port']['var']['type'].append(p[2])
                sf.print_db("dati completi salvati: ", sf.param)
                for inout,tipo,name in zip(sf.param['port']['port']['io'], sf.param['port']['port']['type'], sf.param['port']['port']['name']):
                    if inout=="in":
                        sf.param['port']['in']['name'].append(name)
                        sf.param['port']['in']['type'].append(tipo)
                    else:
                        sf.param['port']['out']['name'].append(name)
                        sf.param['port']['out']['type'].append(tipo)

            except:
                sf.print_db("!!!!!!! No port in entity !!!!!!!!")
    
    #####################################################################
    #############    FUNZIONI DI SUPPORTO  #############################
    def print_db(sf, stringa, param='#'):
        if sf.debug:
            print(stringa)
            if not param=='#':
                if type(param) is list:
                    for i in param:
                        print(" "*len(stringa)+str(i))
                    print("\n")
                elif type(param) is dict:
                    sf.print_db("   generic name:", param['generic']['name'])    
                    sf.print_db("   generic type", param['generic']['type'])
                    sf.print_db("   generic value", param['generic']['value'])
                    sf.print_db("   generic glob name:", param['generic']['glob_name'])    
                    sf.print_db("   generic glob type", param['generic']['glob_type'])
                    sf.print_db("   generic glob value", param['generic']['glob_value'])
                    sf.print_db("   port name", param['port']['port']['name'])
                    sf.print_db("   port type", param['port']['port']['type'])
                    sf.print_db("   port io", param['port']['port']['io'])
                    sf.print_db("   sig name", param['port']['sig']['name'])
                    sf.print_db("   sig type", param['port']['sig']['type'])
                    sf.print_db("   variable name", param['port']['var']['name'])
                    sf.print_db("   variable type", param['port']['var']['type'])
                    
                else:
                    print(" "*len(stringa)+param)
            else:
                print("\n")





class extract_param:
    def __init__(sf, dir_param, end_str,end_str2, debug=0):
        # dir_param -> directory coi parametri
        # end_str -> stringa per differenziare i segnali e le variabili
        #           nel testbench
        # end_str2 -> stringa uguale all'altra ma per creare altri segnali con
        #           end_str2 nel nome
        sf.dir_param = dir(dir_param)
        # per rendere unici i nomi dei segnali viene passata
        # anche una stringa che viene aggiunta alla fine di 
        # ciascun segnale
        sf.end_str = end_str 
        sf.end_str2 = end_str2 

        # debug
        sf.debug=debug

        # costanti
        sf.param={}
        sf.param['constant']={}
        sf.param['constant']['default_in_value']={}
        sf.param['constant']['default_in_value']['name']=[]
        sf.param['constant']['default_in_value']['sig']=[]
        sf.param['constant']['default_in_value']['value']=[]
        sf.param['constant']['in_out_delay']=""
        sf.param['constant']['clk_between_input']=""
        # dir
        sf.param['dir']={}
        sf.param['dir']['dut']=""
        sf.param['dir']['aref']=""
        sf.param['dir']['in']=""
        sf.param['dir']['out']=""
        sf.param['dir']['param']=""
        # file
        sf.param['file']={}
        sf.param['file']['dut']=""
        sf.param['file']['aref']=""
        sf.param['file']['input']=""
        sf.param['file']['output']={}
        sf.param['file']['output']['dut']=""
        sf.param['file']['output']['aref']=""
        sf.param['file']['output']['correct']=""
        # flag
        sf.param['flag']={}
        sf.param['flag']['seq_comb']=""
        sf.param['flag']['fsm']=""
        sf.param['flag']['aref']=""
        sf.param['flag']['parallel_custom_in']=""
        sf.param['flag']['flag_correct_out']=""
        # viene considerata solo se c'è aref
        sf.param['flag']['save_output']=""
        # sync
        sf.param['sync']={}
        sf.param['sync']['clk']={}
        sf.param['sync']['clk']['period']=""
        sf.param['sync']['clk']['name']=""
        sf.param['sync']['clk']['sig_name']=""
        sf.param['sync']['rst']={}
        sf.param['sync']['rst']['name']=""
        sf.param['sync']['rst']['sig_name']="" # per la dut
        sf.param['sync']['rst']['sig_name2']="" # per aref
        sf.param['sync']['rst']['wave']={}
        sf.param['sync']['rst']['wave']['value']=[]
        sf.param['sync']['rst']['wave']['time']=[]
        sf.param['sync']['done']={}
        sf.param['sync']['done']['name']=""
        sf.param['sync']['done']['sig_name']="" # per la dut
        sf.param['sync']['done']['sig_name2']="" # per aref
        sf.param['sync']['start']={} 
        sf.param['sync']['start']['name']=""
        sf.param['sync']['start']['sig_name']="" # per la dut
        sf.param['sync']['start']['sig_name2']="" # per aref
        sf.param['sync']['custom_in']={} 
        sf.param['sync']['custom_in']['name']=[]
        sf.param['sync']['custom_in']['shift']=[]
        sf.param['sync']['input_sequence']=[]
        sf.param['sync']['input_sequence_sig']=[]
        sf.param['sync']['input_sequence_sig2']=[]
        sf.param['sync']['input_sequence_var']=[]
        sf.param['sync']['input_sequence_var2']=[]
        sf.param['sync']['correct_out_name']={}
        sf.param['sync']['correct_out_name']['sig'] = []
    
        sf.param['error'] =""
        sf.supp=""

    
    def extract_all(sf):
        sf.extract_constant()
        sf.extract_file()
        sf.extract_flag()
        sf.extract_sync()

            
    def extract_constant (sf):
        ##################################################################
        # CONSTANT.GEN
        with open(sf.dir_param+"/constant.gen",'r') as f:
            file=sf.get_string(f)
         
            # in_out_delay = 10 ns ;
            sf.param['constant']['in_out_delay'] = sf.extract_param("in_out_delay", file)
            # clk_between_input = 1 ;
            sf.param['constant']['clk_between_input'] = sf.extract_param("clk_between_input", file)
       
            # default_in_value(
            # in1 = 01010
            # in2 = 00120
            # );
            sf.extract_seq(sf.param['constant']['default_in_value']['name'],
                        sf.param['constant']['default_in_value']['value'],"default_in_value", file)
    
            for i in sf.param['constant']['default_in_value']['name']:
                sf.param['constant']['default_in_value']['sig']="s_"+sf.end_str+"_"+i
    
    def extract_file(sf):
        ##################################################################
        # FILE.GEN
        with open(sf.dir_param+"/file.gen",'r') as f: 
            file=sf.get_string(f)
            
            # dir_vhdl 
            sf.param['dir']['dut'] = sf.extract_param("dir_dut",file)
            # dir_vhdl 
            sf.param['dir']['aref'] = sf.extract_param("dir_aref",file)
            # dir_in
            sf.param['dir']['in'] = sf.extract_param("dir_in",file)
            # dir_out
            sf.param['dir']['out'] = sf.extract_param("dir_out",file)
            # dir_param
            sf.param['dir']['param'] = sf.extract_param("dir_param",file)
    
            # dut_filename = dut.vhd;
            sf.supp = sf.extract_param("dut_filename", file)
            sf.print_db("sf.supp "+sf.supp)
            sf.param['file']['dut'] = sf.abs_file(sf.supp,sf.param['dir']['dut'])
            sf.param['file']['output']['dut'] = sf.abs_file_ext(sf.supp,"_out",sf.param['dir']['out'])
            # input_filename = input_data.txt;
            sf.supp = sf.extract_param("input_filename", file)
            sf.param['file']['input'] = sf.abs_file(sf.supp,sf.param['dir']['in'])
            # correct_out_filename;
            sf.supp = sf.extract_param("correct_out_filename", file)
            sf.param['file']['output']['correct'] = sf.abs_file(sf.supp,sf.param['dir']['out'])
            # aref_filename;
            sf.supp = sf.extract_param("aref_filename", file)
            sf.print_db("sf.supp "+sf.supp)
            sf.param['file']['aref'] = sf.abs_file(sf.supp,sf.param['dir']['aref'])
            sf.param['file']['output']['aref'] = sf.abs_file_ext(sf.supp,"_out",sf.param['dir']['out'])
        
    def extract_flag(sf):
        ##################################################################
        # FLAG.GEN
        with open(sf.dir_param+"/flag.gen",'r') as f: 
            file=sf.get_string(f)
            
            # seq_comb
            sf.param['flag']['seq_comb'] = sf.extract_param("flag_seq_comb", file)
            # flag_fsm 
            sf.param['flag']['fsm'] = sf.extract_param("flag_fsm", file)
            # flag_aref
            sf.param['flag']['aref'] = sf.extract_param("flag_aref", file)
            # flag_parallel_custom_in
            sf.param['flag']['parallel_custom_in'] = sf.extract_param("flag_parallel_custom_in", file)
            # flag_save_output
            sf.param['flag']['save_output'] = sf.extract_param("flag_save_output", file)
            # flag_correct_out
            sf.param['flag']['correct_out'] = sf.extract_param("flag_correct_out", file)
        
    def extract_sync(sf):
        ##################################################################
        # SYNC.GEN
        with open(sf.dir_param+"/sync.gen",'r') as f: 
            file=sf.get_string(f)
        
            # clk_period
            sf.param['sync']['clk']['period'] = sf.extract_param("clk_period", file)
            # clk_name
            sf.param['sync']['clk']['name'] = sf.extract_param("clk_name", file)
            sf.param['sync']['clk']['sig_name'] = sf.to_signal( sf.param['sync']['clk']['name'])
            sf.param['sync']['clk']['sig_name2'] = sf.to_signal2( sf.param['sync']['clk']['name'])
            # rst_name
            sf.param['sync']['rst']['name'] = sf.extract_param("rst_name", file)
            sf.param['sync']['rst']['sig_name'] = sf.to_signal( sf.param['sync']['rst']['name'] )
            sf.param['sync']['rst']['sig_name2'] = sf.to_signal2( sf.param['sync']['rst']['name'] )
            # done_name
            sf.param['sync']['done']['name'] = sf.extract_param("done_name", file)
            sf.param['sync']['done']['sig_name'] = sf.to_signal( sf.param['sync']['done']['name'])
            sf.param['sync']['done']['sig_name2'] = sf.to_signal2( sf.param['sync']['done']['name'])
            # start_name
            sf.param['sync']['start']['name'] = sf.extract_param("start_name", file)
            sf.param['sync']['start']['sig_name'] = sf.to_signal( sf.param['sync']['start']['name'] )
            sf.param['sync']['start']['sig_name2'] = sf.to_signal2( sf.param['sync']['start']['name'] )
            # rst_wave
            sf.extract_seq(sf.param['sync']['rst']['wave']['value'], sf.param['sync']['rst']['wave']['time'], "rst_wave", file)  
            # timing_custom_in
            sf.extract_seq(sf.param['sync']['custom_in']['shift'], sf.param['sync']['custom_in']['name'], "timing_custom_in",file)

            # estrazione della sequenza degli input
            sf.extract_list(sf.param['sync']['input_sequence'], "input_sequence",file)
            sf.param['sync']['input_sequence_sig'] = sf.to_signal(sf.param['sync']['input_sequence'])
            sf.param['sync']['input_sequence_sig2'] = sf.to_signal2( sf.param['sync']['input_sequence'])
            sf.param['sync']['input_sequence_var'] = sf.to_variable(sf.param['sync']['input_sequence'])
            sf.param['sync']['input_sequence_var2'] = sf.to_variable2( sf.param['sync']['input_sequence'])


            sf.extract_list(sf.param['sync']['correct_out_name']['sig'], "output_sequence",file)
            # nomi di variabili creati per salvare i dati di ini

        sf.print_db("param: ",sf.param)



    #####################################################################
    #############    FUNZIONI DI SUPPORTO  #############################
    def is_in(to_control, in_what):
        try:
            [ i in in_what for i in to_control].index(False)       
            iss=1
        except ValueError:
            iss=0
        # ritorno 1 se to_control è il in_what
        return iss 

    def error(stringa):
        sf.param['error'] = sf.param['error']+"\n" + stringa
    def type_of(l_name_to_find, l_name, l_type):
        c=l_name_to_find
        d= l_name
        e=l_type
        [e[int(str([n-1 for i,n in zip(d,range(1,len(d)+1)) if i==l])[1:2])] for l in c ]
    def to_signal(sf, stringa):
        if type(stringa)==list:
            lista=[]
            for i in stringa:
                lista.append(sf.to_signal(i))
            return lista
        return "s_"+sf.end_str+"_"+stringa

    def to_signal2(sf, stringa):
        if type(stringa)==list:
            lista=[]
            for i in stringa:
                lista.append(sf.to_signal2(i))
            return lista
        return "s_"+sf.end_str2+"_"+stringa

    def to_variable(sf, stringa):
        if type(stringa)==list:
            lista=[]
            for i in stringa:
                lista.append(sf.to_variable(i))
            return lista
        return "v_"+sf.end_str+"_"+stringa
    
    def to_variable2(sf, stringa):
        if type(stringa)==list:
            lista=[]
            for i in stringa:
                lista.append(sf.to_variable2(i))
            return lista
        return "v_"+sf.end_str2+"_"+stringa


    def abs_file(sf, file, directory=0):
        if file=="0" or file=="":
            return "0"
        if directory==0:
                directory=sf.dir_param_file
        return  directory+"/"+file

    def abs_file_ext(sf, file, end_before_extention, directory=0):
        # file -> nome del file tipo ciao.vhd
        # end_before_extention -> stringa da aggiungere prima
        #       dell'estensione
        if file=="0" or file=="":
            return "0"
        if directory==0:
                directory=sf.dir_param_file
        sf.print_db(file)
        return directory+"/"+file.split('.')[0]+end_before_extention+"."+file.split('.')[1] 

    def extract_param(sf, nome_parametro, stringa):
        # questa funzione estrae un parametro del tipo
        # parametro
        stringa=re.sub(r'\s*#+.*\n',' ', stringa)
        #sf.print_db(nome_parametro+" :", stringa)
        ####################################################
        # in_out_delay = 10 ns ;
        ####################################################
        stringa=re.sub(r'\s\s+|\t+',' ',re.sub(r'\n',' ',re.sub(r'\s\s+',' ',stringa)))
        p=re.compile(r''+nome_parametro+'\s*=\s*(?P<valore>[^;]*)\s*;')
        try:
            value=p.search(stringa).group('valore')
        except AttributeError:
            value="0"
        #sf.print_db(nome_parametro+": ", value)
        return value
           
    def extract_seq(sf, l_par1, l_par2, nome_parametro, stringa):
        stringa=re.sub(r'\s*#+.*\n',' ', stringa)
        stringa=re.sub(r'\s\s+|\t+',' ',re.sub(r'\n',' ',re.sub(r'\s\s+',' ',stringa)))
        # trovo la stringa interna alle parentesi
        p=re.compile(r''+nome_parametro+'\s*\(\s*(?P<stringa_interna>[^\)]+)\s*\)\s*;')
        stringa_interna=p.search(stringa).group('stringa_interna')
        #sf.print_db(nome_parametro+": ", stringa_interna)
        # trovo tutti i valori interni 
        p=re.compile(r'\s*(?P<in>\w+)\s*=\s*(?P<val>[^ ]*)\s*')
        try:
            stringa_interna=p.findall(stringa_interna)
            #sf.print_db("valori: ", stringa_interna)
                
            for v in stringa_interna:
                l_par1.append(v[0])
                l_par2.append(v[1])
        except AttributeError:
            l_par1.append("0")
            l_par2.append("0")
    
        #sf.print_db("param: ",sf.param)

    def extract_list(sf, l_par1, nome_parametro, stringa):
        stringa=re.sub(r'\s*#+.*\n',' ', stringa)
        stringa=re.sub(r'\s\s+|\t+',' ',re.sub(r'\n',' ',re.sub(r'\s\s+',' ',stringa)))
        # trovo la stringa interna alle parentesi
        p=re.compile(r''+nome_parametro+'\s*\(\s*(?P<stringa_interna>[^\)]+)\s*\)\s*;')
        try:
            stringa_interna=p.search(stringa).group('stringa_interna')
            #sf.print_db(nome_parametro+": ", stringa_interna)
            # trovo tutti i valori interni 
            #=re.compile(r'\s*(?P<in>\w+)\s*\n')
            #sf.print_db("valori: "+nome_parametro+"à###################", stringa_interna)
                
            for v in stringa_interna.split():
                l_par1.append(v)
        except AttributeError:
            l_par1.append("0")

    def get_string(sf, fp):
        # estaggo tutto, tolgo gli spazi e 
        # rendo tutto minuscolo
        return ' '.join(fp.readlines())

    def print_db(sf, stringa, param='#'):
        if sf.debug:
            print(stringa)
            if not param=='#':
                if type(param) is list:
                    for i in param:
                        print(" "*len(stringa)+str(i))
                    print("\n")
                elif type(param) is dict:
                    sf.print_db("   file dut", param['file']['dut'])
                    sf.print_db("   file aref", param['file']['aref'])
                    sf.print_db("   file input", param['file']['input'])
                    sf.print_db("   file output dut", param['file']['output']['dut'])
                    sf.print_db("   file output aref", param['file']['output']['aref'])
                    sf.print_db("   file output correct", param['file']['output']['correct'])
                    sf.print_db("   flag seq_comb", param['flag']['seq_comb'])
                    sf.print_db("   flag fsm", param['flag']['fsm'])
                    sf.print_db("   flag aref", param['flag']['aref'])
                    sf.print_db("   flag save_output", param['flag']['save_output'])
                    sf.print_db("   flag parallel_custom_in", param['flag']['parallel_custom_in'])
                    sf.print_db("   sync clk period",param['sync']['clk']['period'])
                    sf.print_db("   sync clk name",param['sync']['clk']['name'])
                    sf.print_db("   sync rst wave value",param['sync']['rst']['wave']['value'])
                    sf.print_db("   sync rst wave time",param['sync']['rst']['wave']['time'])
                    sf.print_db("   sync clk name",param['sync']['clk']['name'])
                    sf.print_db("   sync done nname",param['sync']['done']['name'])
                    sf.print_db("   sync start ncame",param['sync']['start']['name'])
                    sf.print_db("   sync custom_in name",param['sync']['custom_in']['name'])
                    sf.print_db("   sync custom_in shift",param['sync']['custom_in']['shift'])
                    sf.print_db("   dir dut", param['dir']['dut'])
                    sf.print_db("   dir aref", param['dir']['aref'])
                    sf.print_db("   dir in",param['dir']['in'])
                    sf.print_db("   dir out",param['dir']['out'])
                    sf.print_db("   dir param",param['dir']['param'])
                    sf.print_db("   constant def in name: ", 
                            param['constant']['default_in_value']['name'])
                    sf.print_db("   constant def in value: ",
                            param['constant']['default_in_value']['value'])
                    sf.print_db("   sync input_sequence: ", sf.param['sync']['input_sequence'])
                    sf.print_db("   sync input_sequence_sig: ", sf.param['sync']['input_sequence_sig'])
                    sf.print_db("   sync input_sequence_sig2: ", sf.param['sync']['input_sequence_sig2'])
                    sf.print_db("   sync output sequence sig: ", sf.param['sync']['correct_out_name']['sig'])
                    
                    
                else:
                    print(" "*len(stringa)+param)
            else:
                print("\n")










#obj.save_entity()
#obj=extract_entity("../rca.vhd","dut",1)
#obj.save_library()
#print(obj.param['library'])
#dire="/media/tesla/Storage/Linux/Scrivania/Progetti_work/git/lab_lowpower/lab6/4/tb_generator/config"
#obj2=extract_param(dire,dire,dire,dire, "dut",1)
#obj2.extract_allv)
