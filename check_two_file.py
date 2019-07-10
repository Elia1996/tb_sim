# -*- coding: utf-8 -*-

import sys
file1=sys.argv[1]
file2=sys.argv[2]
filein=sys.argv[3]

print("##########################################################")
print("Segnalazion errori ")
print("##########################################################")
all_ok=1
with open(file1,"r") as f1:
    with open(file2,"r") as f2:
    	with open(filein,"r") as fin:
			n=0
			for i,j,k in zip(f1,f2, fin):
				str1=i[:-1]
				str2=j[:-1]
				list1=str1.split(" ")
				list2=str2.split(" ")
				for l1,l2 in zip(list1,list2):
					#print("--"+str(l1)+" - "+str(l2))
					if not l1==l2:
						print("---------------------------------------------------")
						print(" Input line :"+str(k))
						print(" Error at line "+str(n)+": "+str(l1)+" != "+str(l2))
						print("")
						all_ok=0
				n=n+1

if all_ok:
    print("##########################################################")
    print("Tutte le uscite sono corrette")
    print("##########################################################")
