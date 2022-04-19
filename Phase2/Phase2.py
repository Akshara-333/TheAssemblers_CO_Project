from Phase1 import Memory
import math
import time
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication,  QWidget, QTableWidget, QTableWidgetItem, QVBoxLayout
import sys
from PyQt5.QtCore import Qt
mem = Memory()
mem.Memo()

myfile = open('output.txt','w')

def printregs(f,cycle):
    if f==1:
        print("\n","------ The regs after ",cycle," cycle(s) are ------","\n")
        for i in [0,1,2,3,4,5,6,7,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31]:
            print("\t\tx{}\t".format(i),'0x'+(hex(int(regs[i],2)).replace('0x','').zfill(8)))
        print("\n")

def printregsRUN():
    print('\n-------The regs after 5 cycles or next Instruction are-------')
    for i in [0,1,2,3,4,5,6,7,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31]:
        print("\t\tx{}\t".format(i),'0x'+(hex(int(regs[i],2)).replace('0x','').zfill(8)))
    print("\n")

def extract(stringin, n):
    if(len(stringin) == n):
        if(stringin[0] == '0'):
            return int(stringin, 2)
        else:
            return int(stringin, 2)-2**(n)
    else:
        return int(stringin, 2)

def convert(number,n): #number - decimal number and n - decimal unit
    pop = -1
    if(n==12):
        pop = 0xfff
    elif(n==4):
        pop=0xf
    elif(n==20):
        pop = 0xfffff
    elif( n ==32):
        pop = 0xffffffff
    ans = bin( number & pop).replace("0b",'').zfill(n)
    if(number<(-1)*(2**(n-1)) or number>2**(n-1) - 1):
        print("error: overflow=",number)

    return ans

'''0:rs1 1:rs2 2:imm 3:rd 4:f3 5:f7 6:opcode 7:ir 8:pc 9:current_function '''
#list=['00000000000000000000000000000000', '00000000000000000000000000000000', '00000000000000000000000000000000', '00000000000000000000000000000000',
# '00000000000000000000000000000000', '00000000000000000000000000000000', '00000000000000000000000000000000', '00000000000000000000000000000000', '00000000000000000000000000000000',
# '00000000000000000000000000000000'] #list of strings

# Initialised values of all the 32 regs in binary
regs=['00000000000000000000000000000000','00000000000000000000000000000000','01111111111111111111111111110000','00010000000000000000000000000000','00000000000000000000000000000000',
'00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000',
'00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000',
'00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000',
'00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000',
'00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000',
'00000000000000000000000000000000','00000000000000000000000000000000']

stack = {}

def com_8(str):
    x = len(str)
    if x==8:
        return str
    else:
        m = str[::-1]
        # i=0
        for y in range(0,8-x):
            m = m + '0'
        m = m[::-1]
        return m

def com_32(str1):
    x = len(str1)
    if x==32:
        return str1
    else:
        m = str1[::-1]
        # i=0
        for y in range(0,32-x):
            m = m + '0'
        m = m[::-1]
        return m

def get_inst(inst):
    rfile=open("outfile.mc","r+")
    bc=rfile.readlines()
    inst="0x"+(hex(int(inst,2)).replace("0x","")).zfill(8)
    # print(inst)
    #exit()
    for i in bc:
        i=i.split(' ',2)
        if i[1]==inst:
            return i[2].replace('\n','')

def getIR(file_name,pc):
    f = open(file_name,'r')
    i = 0
    for x in f:
        if i==pc:
            ins_a = x.split()
            ins_a[1]=ins_a[1].replace("0x","")
            res = "{0:32b}".format(int(ins_a[1], 16))
            res=res.replace(" ","0")
            return res
        i=i+4
    return -1

i_file = "outfile.mc" 
ab = {} # (KEY)PC -> (VALUE)TARGET-ADDRESS
ch = {} # (KEY)PC -> (VALUE)prediction-bit

def fetch(list,stallflag):
    # print("inside FETCH",list,' stallflag=',stallflag)
    if(stallflag==0):
        list[7] = getIR(i_file,int(list[8],2))
        if list[8] in ab.keys():
            if ch[list[8]]==1:
                predict = ab[list[8]]
            else:
                predict = bin(int(list[8],2)+4).replace("0b","")
            list[8] = bin(int(list[8],2)+4).replace("0b","")
            if(list[7]==-1):
                return "over",predict
            return "continue",predict

    # if(stallflag==0):
        list[8]=bin(int(list[8],2)+4).replace("0b","")
    else:
        return 'continue',list[8]
    if(list[7]==-1):
        return "over",-1;
    return "continue",-1;

def update_bht(pc,taken,target):
    ch[pc]=taken
    # print(ch,ab)

'''0:rs1 1:rs2 2:imm 3:rd 4:f3 5:f7 6:opcode 7:ir 8:pc 9:current_function '''
def decode(list,bhtflag):
    #print(list)
    ins=list[7]
    opcode = ins[25:32]
    list[6]=opcode
    if(opcode=="0110011"):#r-format
        list[5]=ins[0:7]
        list[1]=ins[7:12]
        list[0]=ins[12:17]
        list[4]=ins[17:20]
        list[3]=ins[20:25]

        if list[5]== "0000000": #f7 = 0000000
            if list[4]=="000":
                list[9]="add"


            elif list[4]=="111":
                list[9]="and"

            elif list[4]=="110":
                list[9]="or"

            elif list[4]=="001":
                list[9]="sll"

            elif list[4]=="010":
                list[9]="slt"

            elif list[4]=="101":
                list[9]="srl"

            elif list[4]=="100":
                list[9]="xor"

        elif list[5]== "0100000":
            if list[4]=="101":
                list[9]="sra"

            elif list[4]=="000":
                list[9]="sub"

        elif list[5]== "0000001":
            if list[4]=="000":
                list[9]="mul"

            elif list[4]=="100":
                list[9]="div"

            elif list[4]=="110":
                list[9]="rem"
        return 1,list[8],"R";

    elif(opcode=="0100011"):# s-format
        list[2]=ins[0:7]   #immediate value should take only starting 12 bits of this string
        list[1]=ins[7:12]
        list[0]=ins[12:17]
        list[4]=ins[17:20]
        list[2]+=ins[20:25]
        # list[2]+ins[20:25]
        if list[4]=="000":
            list[9]="sb"

        elif list[4]=="010":
            list[9]="sw"

        elif list[4]=="011":
            list[9]="sd"

        elif list[4]=="001":
            list[9]="sh"

        return 1,list[8],"S";


            #'''0:rs1 1:rs2 2:imm 3:rd 4:f3 5:f7 6:opcode 7:ir 8:pc 9:current_function '''

    elif(opcode=="1100011"):#sb
        list[1]=ins[7:12]
        list[0]=ins[12:17]
        list[4]=ins[17:20]
        list[2]=(ins[0]+ins[24]+ins[1:7]+ins[20:24])
        offset=extract(list[2],12)*2
        target = bin(int(list[8],2)+ offset - 4).replace("0b","")
        # print('inside decode-- instruction is BRANCH')
        if(knob1==1):
            if bin(int(list[8],2) - 4).replace("0b","") not in ab.keys():
                ab[bin(int(list[8],2) - 4).replace("0b","")]=target
                ch[bin(int(list[8],2) - 4).replace("0b","")]=0

        if list[4]=="000":
            list[9]="beq"
            m=int(list[0],2)
            n=int(list[1],2)
            o=extract(list[2],12)*2
            # print(list[8],"inside beq function",extract(regs[m],32),extract(regs[n],32))
            if(knob1==1):
                if extract(regs[m],32)==extract(regs[n],32):
                    if bin(int(list[8],2) - 4).replace("0b","") in ch.keys():
                        if ch[bin(int(list[8],2) - 4).replace("0b","")]==1:
                            return 1, target,["SB",1] # 1 indicates that the branch is taken and prediction is correct
                        else:
                            # ch[bin(int(list[8],2) - 4).replace("0b","")] = 1
                            return 0,target ,["SB",1]#prediction is wrong,  target address is returned
                else:
                    if bin(int(list[8],2) - 4).replace("0b","") in ch.keys():
                        if ch[bin(int(list[8],2) - 4).replace("0b","")]==0:
                            return 1,bin(int(list[8],2)).replace("0b","") ,["SB",0] # 1 indicates that the prediction is correct and the branch is not taken
                        else:
                            # ch[bin(int(list[8],2) - 4).replace("0b","")] = 0
                            return 0,bin(int(list[8],2)).replace("0b","") ,["SB",0]#prediction is wrong. target address is returned
            elif(knob1==0):
                if extract(regs[m],32)==extract(regs[n],32):
                    return 1,target ,["SB",1]#prediction is wrong,  target address is returned
                else:
                    return 1,bin(int(list[8],2)).replace("0b","") ,["SB",0] 

        elif list[4]=="001":
            list[9]="bne"
            m=int(list[0],2)
            n=int(list[1],2)
            o=extract(list[2],12)*2
            # print(list[8],"inside beq function",extract(regs[m],32),extract(regs[n],32))
            if(knob1==1):
                if extract(regs[m],32)!=extract(regs[n],32):
                    if bin(int(list[8],2) - 4).replace("0b","") in ch.keys():
                        if ch[bin(int(list[8],2) - 4).replace("0b","")]==1:
                            return 1, target,["SB",1]# 1 indicates that the branch is taken and prediction is correct
                        else:
                            # ch[bin(int(list[8],2) - 4).replace("0b","")] = 1
                            return 0,target ,["SB",1]#prediction is wrong,  target address is returned
                else:
                    if bin(int(list[8],2) - 4).replace("0b","") in ch.keys():
                        if ch[bin(int(list[8],2) - 4).replace("0b","")]==0:
                            return 1,bin(int(list[8],2)).replace("0b","") ,["SB",0]  # 1 indicates that the prediction is correct and the branch is not taken
                        else:
                            # ch[bin(int(list[8],2) - 4).replace("0b","")] = 0
                            return 0,bin(int(list[8],2)).replace("0b","") ,["SB",0]#prediction is wrong, target address is returned
                        # ch[bin(int(list[8],2) - 4).replace("0b","")]=0
            elif(knob1==0):
                if extract(regs[m],32)!=extract(regs[n],32):
                    return 1, target,["SB",1] # 1 indicates that the branch is taken and prediction is correct
                else:
                    return 1,bin(int(list[8],2)).replace("0b","") ,["SB",0] # 1 indicates that the prediction is correct and the branch is not taken
                                
        elif list[4]=="101":
            list[9]="bge"
            m=int(list[0],2)
            n=int(list[1],2)
            o=extract(list[2],12)*2
            # print('value of regs comparing',regs[m],regs[n])
            # print("DECODE bge function",extract(regs[m],32),extract(regs[n],32))
            if(knob1==1):
                if extract(regs[m],32)>=extract(regs[n],32):
                    if bin(int(list[8],2) - 4).replace("0b","") in ch.keys():
                        if ch[bin(int(list[8],2) - 4).replace("0b","")]==1:
                            return 1, target,["SB",1] # 1 indicates that the branch is taken and prediction is correct
                        else:
                            # ch[bin(int(list[8],2) - 4).replace("0b","")] = 1
                            return 0,target ,["SB",1]#prediction is wrong,  target address is returned
                else:
                    if bin(int(list[8],2) - 4).replace("0b","") in ch.keys():
                        if ch[bin(int(list[8],2) - 4).replace("0b","")]==0:
                            return 1,bin(int(list[8],2)).replace("0b","") ,["SB",0] # 1 indicates that the prediction is correct and the branch is not taken
                        else:
                            # ch[bin(int(list[8],2) - 4).replace("0b","")] = 0
                            return 0,bin(int(list[8],2)).replace("0b","") ,["SB",0]#prediction is wrong, target address is returned
                        # ch[bin(int(list[8],2) - 4).replace("0b","")]=0
            elif(knob1==0):
                if extract(regs[m],32)>=extract(regs[n],32):
                    return 1, target,["SB",1] # 1 indicates that the branch is taken and prediction is correct
                else:
                    return 1,bin(int(list[8],2)).replace("0b","") ,["SB",0] # 1 indicates that the prediction is correct and the branch is not taken
                
        elif list[4]=="100":
            list[9]="blt"
            m=int(list[0],2)
            n=int(list[1],2)
            o=extract(list[2],12)*2
            # print(list[8],"inside blt function",extract(regs[m],32),extract(regs[n],32))
            # print(ch,"\t",ab)
            if(knob1==1):
                if extract(regs[m],32)<extract(regs[n],32):
                    if bin(int(list[8],2) - 4).replace("0b","") in ch.keys():
                        # print("found in ab and should be TAKEN ")
                        if ch[bin(int(list[8],2) - 4).replace("0b","")]==1:
                            return 1,target,["SB",1] # 1 indicates that the branch is taken and prediction is correct
                        else:
                            # ch[bin(int(list[8],2) - 4).replace("0b","")] = 1
                            return 0,target,["SB",1]
                else:
                    if bin(int(list[8],2) - 4).replace("0b","") in ch.keys():
                        # print('found in ab and Should be NOT TAKEN')
                        if ch[bin(int(list[8],2) - 4).replace("0b","")]==0:
                            return 1,bin(int(list[8],2)).replace("0b","") ,["SB",0] # 1 indicates that the prediction is correct and the branch is not taken
                        else:
                            # ch[bin(int(list[8],2) - 4).replace("0b","")] = 0
                            return 0,bin(int(list[8],2)).replace("0b","") ,["SB",0]    #prediction is wrong, target address is returned
            elif(knob1==0):
                if extract(regs[m],32)<extract(regs[n],32):
                    return 1,target,["SB",1] # 1 indicates that the branch is taken and prediction is correct
                else:
                    return 1,bin(int(list[8],2)).replace("0b","") ,["SB",0]

    elif(opcode=="0000011"):#lb,lw,ld
        list[2]=ins[0:12]
        list[0]=ins[12:17]
        list[3]=ins[20:25]
        list[4]=ins[17:20]

        if list[4]=="000":
            list[9]="lb"

        elif list[4]=="010":
            list[9]="lw"

        elif list[4]=="011":
            list[9]="ld"

        return 1,list[8],"LOAD";

    elif opcode=="0110111": #U-lui
        list[2]=ins[0:20]
        list[3]=ins[20:25]
        list[9]="lui"
        return 1,list[8],"U";

    elif opcode=="0010011": #andi ori addi
        list[2]=ins[0:12]
        list[0]=ins[12:17]
        list[3]=ins[20:25]
        list[4]=ins[17:20]

        if list[4]=="110":
            list[9]="ori"

        elif list[4]=="111":
            list[9]="andi"

        elif list[4]=="000":
            list[9]="addi"

        return 1,list[8],"I";

    elif opcode=="1100111": #jalr
        list[2]=ins[0:12]
        list[0]=ins[12:17]
        list[3]=ins[20:25]
        list[4]=ins[17:20]
        list[9]="jalr"
        m=extract(list[2],12) #imm
        k=int(list[0],2) #rs1
        n=m+int(regs[k],2) #relative address to load from memory
        o=int(list[3],2)

        if(knob1==1):
            if bin(int(list[8],2) - 4).replace("0b","") not in ab.keys():
                ab[bin(int(list[8],2) - 4).replace("0b","")]=bin(int(convert(n,32),2)).replace('0b','')
                # ab[bin(int(list[8],2) - 4).replace("0b","")] = convert(n,32)
                ch[bin(int(list[8],2) - 4).replace("0b","")]=0
            else:
                ab[bin(int(list[8],2) - 4).replace("0b","")]=bin(int(convert(n,32),2)).replace('0b','')
            # ab[bin(int(list[8],2) - 4).replace("0b","")] = convert(n,32)
            if ch[bin(int(list[8],2) - 4).replace("0b","")]==0:
                ch[bin(int(list[8],2) - 4).replace("0b","")]=1
                return 0,convert(n,32),["JALR",1]
            else:
                ch[bin(int(list[8],2) - 4).replace("0b","")]=1
                return 1,convert(n,32),["JALR",1]
        elif(knob1==0):
            return 1,convert(n,32),['JALR',1]
        # ab[bin(int(list[8],2) - 4).replace("0b","")]=convert(n,32)

        # list[8]=bin(n).replace("0b","").zfill(32)
        # list[8] = convert(n,32)

    elif opcode=="1101111": #jal
        list[2]=ins[0]+ins[12:20]+ins[11]+ins[1:11]
        list[3]=ins[20:25]
        list[9]="jal"
        m=extract(list[2],20)*2 #imm
        n=int(list[3],2) #rd
        # print("jump from jal=",m,"pc before=",int(list[8],2))
       
        if(knob1==1):
            if bin(int(list[8],2) - 4).replace("0b","") not in ab.keys():
                ab[bin(int(list[8],2) - 4).replace("0b","")]=bin(int(list[8],2)+m - 4).replace("0b","")
                ch[bin(int(list[8],2) - 4).replace("0b","")]=0

            if ch[bin(int(list[8],2) - 4).replace("0b","")]==0:
                ch[bin(int(list[8],2) - 4).replace("0b","")]=1
                return 0,bin(int(list[8],2)+m - 4).replace("0b",""),["JAL",1]
            else:
                ch[bin(int(list[8],2) - 4).replace("0b","")]=1
                return 1,bin(int(list[8],2)+m - 4).replace("0b",""),["JAL",1]
        elif(knob1==0):
            return 1,bin(int(list[8],2)+m - 4).replace("0b",""),["JAL",1]
