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
 def execute(list,regs):
    ins_name=list[9]
    if(ins_name=="add"):
        return add(list)
    elif(ins_name=="and"):
        return and1(list)
    elif(ins_name=="or"):
        return or1(list)
    elif(ins_name=="sll"):
        return sll(list)
    elif(ins_name=="slt"):
        return slt(list)
    elif(ins_name=="sra"):
        return sra(list)
    elif(ins_name=="srl"):
        return srl(list)
    elif(ins_name=="sub"):
        return sub(list)
    elif(ins_name=="xor"):
        return xor(list)
    elif(ins_name=="mul"):
        return mul(list)
    elif(ins_name=="div"):
        return div(list)
    elif(ins_name=="rem"):
        return rem(list)
    elif(ins_name=="addi"):
        return addi(list)
    elif(ins_name=="andi"):
        return andi(list)
    elif(ins_name=="ori"):
        return ori(list)
    elif(ins_name=="lb"):
        return lb(list)
    elif(ins_name=="lw"):
        return lw(list)
    elif(ins_name=="jalr"):
        return jalr(list)
    elif(ins_name=="sb"):
        return sb(list)
    elif(ins_name=="sw"):
        return sw(list)
    elif(ins_name=="sd"):
        return sd(list)
    elif(ins_name=="sh"):
        return sh(list)
    elif(ins_name=="beq"):
        return beq(list)
    elif(ins_name=="bne"):
        return bne(list)
    elif(ins_name=="bge"):
        return bge(list)
    elif(ins_name=="blt"):
        return blt(list)
    elif(ins_name=="lui"):
        return lui(list)
    elif(ins_name=="jal"):
        return jal(list)

#list_fun=[add, and1, or1, sll, slt, sra, srl, sub, xor, mul, div, rem,addi, andi, ori, lb, ld, lw, jalr,sb, sw, sd, sh,beq, bne, bge, blt, lui,jal]

def add(list):
    #print(list)
    m=int(list[0],2)#values in regs and list are in binary format
    n=int(list[1],2)
    x=extract(regs[m],32) + extract(regs[n],32)
    o=int(list[3],2)
    # regs[o]=convert(x,32)
    return convert(x,32),o,"R";

def and1(list):
    m = int(list[0],2)
    n = int(list[1],2)
    # print(int(regs[m],2),int(regs[n],2))
    x = extract(regs[m],32) & extract(regs[n],32)
    # print(x,"ans")
    o=int(list[3],2)
    return convert(x,32),o,"R";
    # print(o)
    # regs[o]=convert(x,32)
    # print(regs[o])

def or1(list):
    m = int(list[0],2)
    n = int(list[1],2)
    x = extract(regs[m],32) | extract(regs[n],32)
    o = int(list[3],2)
    return convert(x,32),o,"R";
    # regs[o]=convert(x,32)

def slt(list):
    m = int(list[0],2)
    n = int(list[1],2)
    o=int(list[3],2)
    if extract(regs[m],32) < extract(regs[n],32):
        return convert(1,32),o,"R";
        # regs[o]=convert(1,32)
    else:
        # regs[o]=convert(0,32)
        return convert(0,32),o,"R";

def sll(list):
    m = int(list[0],2) #rs1
    n = int(list[1],2) #rs2
    if(extract(regs[n],32)<0):
        print("error: negative shift not allowed")
        return "error: negative shift not allowed"
    if(extract(regs[n],32)>32):
        x=0
    else:
        x = extract(regs[m],32) << extract(regs[n],32)
    # print(int(regs[m],2),int(regs[n],2))
    o=int(list[3],2)
    # print(x)
    return convert(x,32),o,"R";

def sra(list):
    m = int(list[0],2)
    n = int(list[1],2)
    if(extract(regs[n],32)<0):
        print("error: negative shift not allowed")
        return "error: negative shift not allowed"
    elif(extract(regs[n],32)<=32):
        x = extract(regs[m],32)>>extract(regs[n],32)
    else:
        x= -1
    # x = int(regs[m],2) >> int(regs[n],2)
    o = int(list[3],2)
    # print(x)
    # regs[o]=convert(x,32)
    return convert(x,32),o,"R";

def srl(list):
    m = int(list[0],2) #rs1
    n = int(list[1],2) #rs2
    o = int(list[3],2)
    if(extract(regs[n],32)<0):
        print("error: negative shift not allowed")
        return "error: negative shift not allowed"
    elif(extract(regs[n],32)<=32):
        v = regs[m]
        for _ in range(int(regs[n],2)):
            v = ('0'+v)[:32]
        #regs[o]=com_32(v)
        return com_32(v),o,"R";
    else:
        v=0
        return convert(v,32),o,"R";
        # regs[o]=convert(v,32)

def sub(list):
    m=int(list[0],2)
    n=int(list[1],2)
    x=extract(regs[m],32) - extract(regs[n],32)
    o=int(list[3],2)
    return convert(x,32),o,"R";
    # regs[o]=convert(x,32)
    # print("yo1")

def xor(list):
    m = int(list[0],2)
    n = int(list[1],2)
    x = extract(regs[m],32) ^ extract(regs[n],32)
    o=int(list[3],2)
    return convert(x,32),o,"R";
    # regs[o]=convert(x,32)

def mul(list):
    m = int(list[0],2)
    n = int(list[1],2)
    x = extract(regs[m],32) * extract(regs[n],32)
    o=int(list[3],2)
    return convert(x,32),o,"R";
    # regs[o]=convert(x,32)

def div(list):
    m = int(list[0],2)
    n = int(list[1],2)
    if(extract(regs[n],32)==0):
        print("division by zero not allowed")
        return "error : division by zero not allowed"
    x = int(extract(regs[m],32) / extract(regs[n],32))
    o=int(list[3],2)
    return convert(x,32),o,"R";
    # regs[o]=convert(x,32)

def rem(list):
    m = int(list[0],2)
    n = int(list[1],2)
    x = extract(regs[m],32) % extract(regs[n],32)
    o=int(list[3],2)
    return convert(x,32),o,"R";
    # regs[o]=convert(x,32)

def addi(list):
    m = int(list[0],2)
    n = str(list[2])
    # print("immediate value =",n,extract(n,12))
    # print(regs[m],extract(regs[m],32))
    x = extract(regs[m],32) + extract(n,12)
    # print((x))
    # print(convert(x,32))
    o = int(list[3],2)
    return convert(x,32),o,"I";
    # regs[o]=convert(x,32)

def andi(list):
    m = int(list[0],2)
    n = str(list[2])
    # print("debug",m,n)
    x = extract(regs[m],32) & extract(n,12)
    o = int(list[3],2)
    return convert(x,32),o,"I";
    # regs[o]=convert(x,32)

def ori(list):
    m = int(list[0],2)
    n = str(list[2])
    x = extract(regs[m],32) | extract(n,12)
    o = int(list[3],2)
    return convert(x,32),o,"I";
    # regs[o]=convert(x,32)

def lb(list):
    m=extract(list[2],12) #immediate value
    k=int(list[0],2) #rs1
    n=m+extract(regs[k],32)
    y=int(list[3],2)
    return convert(n,32),y,"LOADBYTE";
    # regs[y]=convert(extract(bin(int('0x'+x,16))[2:],8),32)

def lw(list):
    # print("m=====",list[2])
    m=extract(list[2],12)
    # print(m)
    k=int(list[0],2)
    # print("address in register ",hex(int(regs[k],2)))
    n=m+int(regs[k],2)
    # print("n=====",(n-268435456))
    # print(hex(n),n)
    y=int(list[3],2)
    return convert(n,32),y,"LOADWORD";

def sb(list):
    m=extract(list[2],12)
    k=int(list[0],2)
    n=m+int(regs[k],2)
    y=int(list[1],2)
    it = regs[y]
    return convert(n,32),it,"S";
    #returning final address, register_to_access , "S"

def sw(list):
    m=extract(list[2],12)
    k=int(list[0],2)
    # print(k,m,regs[k])
    n=m+int(regs[k],2)
    y=int(list[1],2)
    it = regs[y]
    return convert(n,32),it,"S";
    #returning final address, register_to_access , "S"

def sh(list):
    m=extract(list[2],12)
    k=int(list[0],2)
    n=m+int(regs[k],2)
    y=int(list[1],2)
    it = regs[y]
    return convert(n,32),it,"S";
    #returning final address, register_to_access , "S"

def sd(list):
    m=extract(list[2],12)
    k=int(list[0],2)
    n=m+int(regs[k],2)
    y=int(list[1],2)
    it = regs[y]
    return convert(n,32),it,"S";
    #returning final address, register_to_access , "S"

def beq(list):
    return 1,1,"SB";

def bge(list):
    return 1,1,"SB";

def bne(list):
    return 1,1,"SB";

def blt(list):
    return 1,1,"SB";

def lui(list):
    m=int(list[2],2)
    n=int(list[3],2)
    # regs[n]=bin(m).replace("0b","")+"000000000000"
    # regs[n]=com_32(regs[n])
    return com_32(bin(m).replace("0b","")+"000000000000"),n,"U";

def auipc(list): 
    m=int(list[2],2) #current imm
    n=int(list[3],2)
    a = int(list[8],2) #current pc
    x=bin(m).replace("0b","")+"000000000000"
    x=bin(int(x,2)+int(list[8],2) - 4 ).replace("0b","")
    x = com_32(x)
    return x,n,"U";

def jal(list):
    m=extract(list[2],20)*2 #imm
    n=int(list[3],2) #rd
    if knob1==1 and knob2==0:
        list[8]=com_32(bin(int(list[8],2)+m-4).replace("0b",""))
        return com_32(bin(int(list[8],2)-m+4).replace("0b","")),n,"J1"
    elif knob1==1 and knob2==1:
        return com_32(list[8]),n,'J1'
    # print('executionJAL',list[8])
    #exit()
    return com_32(list[8]),n,'J1'

def jalr(list): 
    o=int(list[3],2)
    return com_32(list[8]),o,"J2"

def mem_access(list,v1,v2,v3):
    ins_type = v3 # index where ins_type is stored
    if(ins_type == "R"):
        return v1,v2,"R";
    elif(ins_type == "U"):
        return v1,v2,"U";
    elif(ins_type == "I"):
        return v1,v2,"I";
    elif(ins_type == "S"):
        ins_name = list[9]
        if  (ins_name=="sb"):
            n = int(v1,2) # index where final address is stored
            it = v2 
            if(n<500000000):
                mem.adddata(n,it[24:32])
            else:
                stack[hex(n)]=hex(int(it[24:32],2))[2::].zfill(2)
            return 1,1,"S";
        elif(ins_name=="sw"):
            n = int(v1,2) # index where final address is stored
            it = v2 # index where it is stored
            add3,add2,add1,add0=hex(n+3),hex(n+2),hex(n+1),hex(n)
            val3,val2,val1,val0=hex(int(it[0:8],2))[2::].zfill(2), hex(int(it[8:16],2))[2::].zfill(2),hex(int(it[16:24],2))[2::].zfill(2),hex(int(it[24:],2))[2::].zfill(2)
            # print('storing at',add0,add1,add2,add3)
            # print('value     ',val0,val1,val2,val3)
            if(n+3<500000000): #store in data segment 
                mem.adddata(n+3,it[0:8])
                mem.adddata(n+2,it[8:16])
                mem.adddata(n+1,it[16:24])
                mem.adddata(n,it[24:32])
            elif(int( add3 ,16)>0x7ffffff3):
                print("can't write in memory after 0x7ffffff3")
            else:
                stack[add3]=val3
                stack[add2]=val2
                stack[add1]=val1
                stack[add0]=val0
                # print(stack)
            return 1,1,"S";
        elif(ins_name=="sh"):
            n = int(v1,2) # index where final address is stored
            it = v2 # index where it is stored
            add1,add0=hex(n+1),hex(n)
            val1,val0=hex(int(it[16:24],2))[2::].zfill(2),hex(int(it[24:],2))[2::].zfill(2)
            if(n+1<500000000):
                mem.adddata(n+1,it[16:24])
                mem.adddata(n,it[24:32])

            else:
                stack[add1]=val1
                stack[add0]=val0
            return 1,1,"S";

    elif(ins_type == "SB"):
        return 1,1,"SB";

    elif(ins_type == "LOADBYTE"):
        n = int(v1,2)#index of address
        r_i = v2#index of register index
        if(n<500000000):
            # print("address",hex(n))
            x=mem.get_data_at(n) 
        else:
            try:
                x=stack[hex(n)]
            except:
                x='00'
        a = convert(extract(bin(int('0x'+x,16))[2:],8),32)
        return a,r_i,"LOADBYTE";
    elif(ins_type == "LOADWORD"):
        n = int(v1,2)#index of address
        r_i = v2#index of register index
        if(n+3<500000000):
            x1=mem.get_data_at(n)
            x2=mem.get_data_at(n+1)
            x3=mem.get_data_at(n+2)
            x4=mem.get_data_at(n+3)
            x=x4+x3+x2+x1
            # print("loaded value =",x)
        else:
            try:#x4 from n+3 address
                x4=stack[hex(n+3)]
            except:
                x4='00'
            try:
                x3=stack[hex(n+2)]
            except:
                x3='00'
            try:
                x2=stack[hex(n+1)]
            except:
                x2='00'
            try:
                x1=stack[hex(n)]
            except:
                x1='00'
            x = x4+x3+x2+x1
        a = convert(extract(bin(int('0x'+x,16))[2:],32),32)
        # print("return value from memaccess of LOADWORD,",a,r_i,"LOADWORD")
        return a,r_i,"LOADWORD";
    elif(ins_type == "J1"):
        # return com_32(bin(int(list[8],2)).replace("0b","")),v2,"J1";
        return v1,v2,"J1";
    elif(ins_type == "J2"):
        # return com_32(bin(int(regs[8],2)+4).replace("0b","")),v2,"J2";
        return v1,v2,"J2";

    def write(list,regs,v1,v2,v3,v4=1):
    ins_type = v3 # index where ins_type is stored
    index = v2 #index where index of destination register is stored
    result = v1
    if(v4=='skip'):
        return
    if(ins_type == "R"):
        if index!=0:
            regs[index] = result
    elif(ins_type == "I"):
        if index!=0:
            regs[index] = result
            # print(regs[index])
    elif(ins_type == "U"):
        if index!=0:
            regs[index] = result
    elif(ins_type == "S"):
        nothingness = "sad"
    elif(ins_type == "SB"):
        nothingness = "sad"
    elif(ins_type == "J1"):
        if index!=0:
            regs[index] = result
    elif(ins_type == "J2"):
        # nothingness = "sad"
        if index!=0:
            regs[index] = result
    elif(ins_type == "LOADBYTE"):
        if index!=0:
            regs[index] = result
    elif(ins_type == "LOADWORD"):
        # print('LOAD EXECUTION',index,result)
        if index!=0:
            regs[index] = result
            # print(' x',index,' = ',hex(int(regs[index],2))[2::].zfill(8) ,sep='')

def run(list):
    rfile=open("outfile.mc","r+")
    bc=rfile.readlines()
    start=time.time()
    elapsed=0
    count=0
    no_of_alu=0
    no_of_cont=0
    no_of_dt=0
    j,k=0,0
    while elapsed < 4:
        #print(list[7])
        t=int(list[8],2)
        string,lemme=fetch(list,0)
        #print(string)
        if string=="continue":
            count=count+1  #for GUI
            curr_pc = list[8]
            bs1,bs2,bs3=decode(list,0)
            list[8]=bs2
            # print(list)
            if(list[9]=='beq' or list[9]=='bne' or list[9]=='blt' or list[9]=='bge' or list[9]=='jal' or list[9]=='jalr'):
                no_of_cont+=1
                if(list[9]=='jal' or list[9]=='jalr'):
                    no_of_alu+=1
            else:
                no_of_alu+=1
            if(list[9]=='lb' or list[9]=='lw' or list[9]=='sb' or list[9]=='sw' or list[9]=='sh'):
                no_of_dt+=1
            
            v1,v2,v3 = execute(list,regs)
            v1,v2,v3 = mem_access(list,v1,v2,v3)
            if(list[9]=='jal'):
                v1 = com_32(curr_pc)
            write(list,regs,v1,v2,v3)

            elapsed=time.time()-start
            i=bc[int(t/4)]
            i=i.split(' ',2)
            i[2]=i[2].replace("\n","")
            item=QtWidgets.QTableWidgetItem(i[2])
            #item.setBackground(QtGui.QColor(255,0,0))
            #self.table.selectRow(j)
            window.tableWidget.setVerticalHeaderItem(j,item)
            window.tableWidget.setItem(j,k+0,QTableWidgetItem("Fetch"))
            window.tableWidget.setItem(j,k+1,QTableWidgetItem("Decode"))
            #self.table.item(j,k).setBackground(QtGui.QColor(125,125,125))
            window.tableWidget.setItem(j,k+2,QTableWidgetItem("Execute"))
            window.tableWidget.setItem(j,k+3,QTableWidgetItem("Mem_Access"))
            window.tableWidget.setItem(j,k+4,QTableWidgetItem("Write_back"))
            j=j+1
            k=k+5
            printregsRUN()
        else:
            print("Code successfully Executed")
            printregsRUN()
            break
    if(elapsed>4):
        print("Something is wrong, program took too long too execute, might be an infinite loop")
    print("----------------Non pipelined run-----------------")
    print("1.  Total Number of cycles taken\t\t: ",count*5)
    print('2.  Number of Instructions exeuted per cycle\t\t: ',count)
    print('3.  Cycles Per Instruction (CPI)\t\t: ',5)
    print('4.  Number of Stalls in pipeline\t\t: ', '0')
    
    myfile.write("\n----------------Non pipelined run-----------------")
    myfile.write("\n1.  Total Number of cycles taken\t\t: "+str(count*5))
    myfile.write('\n2.  Number of Instructions exeuted per cycle\t\t: '+str(count))
    myfile.write('\n3.  Cycles Per Instruction (CPI)\t\t: '+str(5))
    myfile.write('\n4.  Number of Stalls in pipeline\t\t: '+ '0')
  
    return count
    # print(regs)

def step(list):
    # print(list)

    string=fetch(list)
    if string=="continue":
        decode(list)
        print(">>> \t ENTER--->",list[9],"initial pc=",hex(int(list[8],2)))
        execute(list,regs)
        regs[0] = '00000000000000000000000000000000'
        #execute one step of code
    else:
        print("code successfully Executed")
    #print(list)
    x=int(list[8],2)
    print("step")
    return x-4

master_list=[['NIL','NIL','NIL','NIL','NIL','NIL','NIL',-2,'NIL','NIL'] for i in range(5)]       #list of lists(list)
master_list[0][8]='00000000000000000000000000000000'

def insert_carr():
    master_list.insert(0,['NIL','NIL','NIL','NIL','NIL','NIL','NIL',-2,'NIL','NIL'])
    master_list[0][8] = master_list[1][8]


def flush_dada(pc):
    master_list[0][7] = -1   # filling the next list with suitable pc
    master_list.insert(0,['NIL','NIL','NIL','NIL','NIL','NIL','NIL','NIL',pc,'NIL'])
    # print('flush done with new pc at 0 as',pc)

i=0

def flush(number_of_steps, pc):
    for i in range(number_of_steps):    # emptying the unnecessary instruction
        master_list[i][7] = -1
    master_list[0][8] = pc  # filling the next list with suitable pc

def stalling(i):               
    # master_list.pop(0)
    master_list.insert(i, ['NIL','NIL','NIL','NIL','NIL','NIL','NIL',-2,'NIL','NIL'])
    # master_list[i][7] = -2


def print_pipelined(pr_fd,pr_de,pr_em,pr_mw,f,cycle):
    if(f==1):
        '''printing pipeline regs'''
        print("------  The Pipeline regs after ",cycle," cycles  ------")
        print("\tBetween F & D : " + "IR = ",str((hex(int(pr_fd[0],2)).replace('0x','').zfill(8))),)
        print("\tBetween D & E : " + "Ra = ",str((hex(int(pr_de[0],2)).replace('0x','').zfill(8)))," , "+"Rb = ",str((hex(int(pr_de[1],2)).replace('0x','').zfill(8)))," , "+"Rd = ",str((hex(int(pr_de[2],2)).replace('0x','').zfill(8)))," , "+"Imm = ",str((hex(int(pr_de[3],2)).replace('0x','').zfill(8))))
        print("\tBetween E & M : " + "Rz = ",str((hex(int(pr_em[0],2)).replace('0x','').zfill(8)))," , "+"Rb = ",str((hex(int(pr_em[1],2)).replace('0x','').zfill(8)))," , "+"Rd = ",str((hex(int(pr_em[2],2)).replace('0x','').zfill(8)))," , "+"Imm = ",str((hex(int(pr_em[3],2)).replace('0x','').zfill(8))))
        print("\tBetween M & W : " + "Ry = ",str((hex(int(pr_mw[0],2)).replace('0x','').zfill(8)))," , "+"Rd = ",str((hex(int(pr_mw[1],2)).replace('0x','').zfill(8))),)
      

def printknob5(pr_printing,f):
    if(f!=-1):
        '''printing pipeline regs'''
        print("------  The Pipeline regs for ",f,"th instruction   ------")
        print("\tBetween F & D : " + "IR = ",str((hex(int(pr_printing[0],2)).replace('0x','').zfill(8))),)
        print("\tBetween D & E : " + "Ra = ",str((hex(int(pr_printing[1],2)).replace('0x','').zfill(8)))," , "+"Rb = ",str((hex(int(pr_printing[2],2)).replace('0x','').zfill(8)))," , "+"Rd = ",str((hex(int(pr_printing[3],2)).replace('0x','').zfill(8)))," , "+"Imm = ",str((hex(int(pr_printing[4],2)).replace('0x','').zfill(8))))
        print("\tBetween E & M : " + "Rz = ",str((hex(int(pr_printing[5],2)).replace('0x','').zfill(8)))," , "+"Rb = ",str((hex(int(pr_printing[6],2)).replace('0x','').zfill(8)))," , "+"Rd = ",str((hex(int(pr_printing[7],2)).replace('0x','').zfill(8)))," , "+"Imm = ",str((hex(int(pr_printing[8],2)).replace('0x','').zfill(8))))
        print("\tBetween M & W : " + "Ry = ",str((hex(int(pr_printing[9],2)).replace('0x','').zfill(8)))," , "+"Rd = ",str((hex(int(pr_printing[10],2)).replace('0x','').zfill(8))),)
        

def run_pipelined_data_for():
    flag = 0
    j=0
    rfile=open("outfile.mc","r+")
    bc=rfile.readlines()
    j,k=0,0
    start = time.time()
    elapsed = 0
    count = 0
    pr_mem = ['nil','nil','nil'] #pipeline register for decode stage
    pr_exe = ['nil','nil','nil']
    pr_printing = ['0','0','0','0','0','0','0','0','0','0','0'] 
    pr_fd = ['0']#IR
    pr_de = ['0','0','0','0'] 
    pr_em = ['0','0','0','0'] 
    pr_mw = ['0','0'] #Ry Rd
    nextflagMM=0
    nextflagMD=0
    nextflagED=0
    stallflag,flushflag=0,0
    no_of_stalls=0
    no_of_inst = 0
    lemme=[-1,-1]
    bs1,bs2,bs3=-1,-1,[-1,-1]
    curr_pc='00000'
    print("master_list")
    hj,hj_prev=-1,-1
    blank=[]
    blank2=[]
    blank3=[]
    app_flag=0
    while elapsed < 60:
        count=count+1
        t=0
        if(master_list[4][7]!=-1 and master_list[4][7]!=-2 and master_list[4][6]!='NIL'):
            no_of_inst+=1
            if(master_list[4][9]=='beq' or master_list[4][9]=='bge' or master_list[4][9]=='bne' or master_list[4][9]=='blt' or master_list[4][9]=='jal' or master_list[4][9]=='jalr'):
                no_of_control+=1
                if(master_list[4][9]=='jal' or master_list[4][9]=='jalr'):
                    no_of_alu+=1
            else:
                no_of_alu+=1
            if(master_list[4][9]=='sh' or master_list[4][9]=='sw' or master_list[4][9]=='sb' or master_list[4][9]=='lb' or master_list[4][9]=='lw'):
                no_of_dt+=1
        # if(master_list[1][8]!='NIL'):
        #     print("\n>>> (",count,") [",no_of_inst,"] \t ENTER--->",master_list[1][9], "initial pc=", hex(int(master_list[1][8], 2)))
        # else:
        #     print("\n>>> \t ENTER--->",master_list[1][9], "initial pc=", 'NIL')

        
        # lemme[2] = lemme[1]
        lemme[1] = lemme[0]                             

        string,lemme[0]=fetch(master_list[0],stallflag)            #lemme[0] is -1 if no branching found, else it represents next pc(target)
        # print("lemme[0] = ",lemme[0])
        if master_list[0][7]!='NIL' and master_list[0][7]!=-1:
            pr_fd[0] = master_list[0][7]
        if (int(master_list[0][8],2) == knob5*4):
            pr_printing[0] = master_list[0][7]
        if (string == "over" and master_list[4][7] == -1 and master_list[3][7]==-1 and master_list[2][7]==-1 and master_list[1][7]==-1):  # full code completed
            print("Code successfully executed")
            break
        else:
            if master_list[4][7] != -1 and master_list[4][7] != -2:
                write(master_list[4], regs, pr_mem[0],pr_mem[1],pr_mem[2],pr_mem[3])
                #z=int(master_list[4][8],2)
                #print(int(z/4))
                window.tableWidget.setItem(k+t,count-1,QTableWidgetItem("Write_back"))
                t=t+1
                app_flag=1
            
            if master_list[3][7] != -1 and master_list[3][7] != -2:
                pr_mem = mem_access(master_list[3], pr_exe[0],pr_exe[1],pr_exe[2])
                window.tableWidget.setItem(k+t,count-1,QTableWidgetItem("Mem_Access"))
                t=t+1
                pr_mem = list(pr_mem)
                pr_mem.append(pr_exe[3])
                if pr_mem[1]=='LOADBYTE' or  pr_mem[1]=='LOADWORD':
                    pr_mw[0] = pr_mem[0]
                # pr_mw[1] = pr_mem[1]
                if master_list[3][3] != 'NIL':
                    pr_mw[1]=master_list[3][3]
                if (int(master_list[3][8],2) == knob5*4):
                    if pr_mem[1]=='LOADBYTE' or  pr_mem[1]=='LOADWORD':
                        pr_printing[9] = pr_mem[0]
                    if master_list[3][3] != 'NIL':
                        pr_printing[10]=master_list[3][3]
            
            if master_list[2][7] != -1 and master_list[2][7] != -2:
                pr_exe = execute(master_list[2], regs)
                window.tableWidget.setItem(k+t,count-1,QTableWidgetItem("Execute"))
                t=t+1
                pr_exe = list(pr_exe)
                pr_exe.append(-1)
                # print('pr_exe ',pr_exe)
                if pr_exe[0]!='NIL':
                    pr_em[0] = com_32(str(pr_exe[0]))
                if master_list[2][3] != 'NIL':
                    pr_em[2]=master_list[2][3]
                if  master_list[2][1] != 'NIL':
                    pr_em[1]=regs[int(master_list[2][1],2)]
                if master_list[2][2] != 'NIL':
                    pr_de[3]=master_list[2][2]
                if (int(master_list[2][8],2) == knob5*4):
                    if pr_exe[0]!='NIL':
                        pr_printing[5] = com_32(str(pr_exe[0]))
                    if master_list[2][3] != 'NIL':
                        pr_printing[6]=master_list[2][3]
                    if  master_list[2][1] != 'NIL':
                        pr_printing[7]=regs[int(master_list[2][1],2)]
                    if master_list[2][2] != 'NIL':
                        pr_printing[8]=master_list[2][2]
                
            if master_list[1][7] != -1 and master_list[1][7] != -2:
                # print("decoding master_list[1]",master_list[1][9])
                curr_pc = master_list[1][8]
                bs1,bs2,bs3=decode(master_list[1],stallflag)        
                window.tableWidget.setItem(k+t,count-1,QTableWidgetItem("Decode"))
                t=t+1
                hj=get_inst(master_list[1][7])
                if hj_prev!=hj:
                    hj=get_inst(master_list[1][7])
                    item=QTableWidgetItem(hj)
                    window.tableWidget.setVerticalHeaderItem(j,item)
                    j=j+1
                    hj_prev=hj
                # print("Test : ",master_list[1][0],)
                if master_list[1][0] != 'NIL':
                    pr_de[0]=regs[int(master_list[1][0],2)]
                if master_list[1][1] != 'NIL':
                    pr_de[1]=regs[int(master_list[1][1],2)]
                if master_list[1][3]!='NIL':
                    pr_de[2]=master_list[1][3]
                if master_list[1][2] != 'NIL':
                    pr_de[3]=master_list[1][2]
                if (int(master_list[1][8],2) == knob5*4):
                    if master_list[1][0] != 'NIL':
                        pr_printing[1]=regs[int(master_list[1][0],2)]
                    if master_list[1][1] != 'NIL':
                        pr_printing[2]=regs[int(master_list[1][1],2)]
                    if master_list[1][3]!='NIL':
                        pr_printing[3]=master_list[1][3]
                    if master_list[1][2] != 'NIL':
                        pr_printing[4]=master_list[1][2]
            
            else:
                bs1,bs2,bs3 = -1,-1,[-1,-1]

            print_pipelined(pr_fd,pr_de,pr_em,pr_mw,knob4,count)
            printregs(knob3,count)
            if master_list[4][8] != 'NIL' and int(master_list[4][8],2)==knob5*4:
                printknob5(pr_printing,knob5)
            
            # for i in range(5):
            #     if(master_list[i][8]!='NIL'):
            #         print(i,"-->",master_list[i],' **** ',hex(int(master_list[i][8],2)))
            #     else:
            #         print(i,"-->",master_list[i],' **** ')
            window.tableWidget.setItem(k+t,count-1,QTableWidgetItem("Fetch"))
            if app_flag==1:
                k=k+1
                app_flag=0 

            if(nextflagMM==1):
                # print("inside nextFLAGMM\tpr_mem=",pr_mem)
                regs[pr_mem[1]] = pr_mem[0]
                pr_mem[3]='skip'
                nextflagMM=0

            if(nextflagMD==1): # 1 or 2 cycle stalls
                # regs[pr_mem[1]] = pr_mem[0]
                # print('just changed in MD',pr_mem[1], 'to',pr_mem[0] )
                if(stallflag!=0):
                    if(stallflag==2):
                        regs[pr_mem[1]] = pr_mem[0]
                        pr_mem[3]='skip'
                        stalling(2)
                    stallflag-=1

                #print(">>> \t ENTER--->",list[9],"initial pc=",hex(int(list[8],2)))
            
            fetchedInst = master_list[0][7]
            
            if(returnlist[0]!=-1):
                if   (returnlist[0][0]=='E' and returnlist[0][1]=='E'): 
                    regs[pr_exe[1]] = pr_exe[0] #writing the value into the register 
                    pr_exe[3]='skip'
                
                elif (returnlist[0][0]=='M' and returnlist[0][1]=='E'):
                    if(returnlist[0][3]==[3,1]):
                        # nextflagMM=1
                        regs[pr_mem[1]] = pr_mem[0]
                        pr_mem[3]='skip'
                    elif(returnlist[0][3]==[2,1]):
                        stalling(2)
                        stallflag=1
                        nextflagMM=1
                        no_of_stalls+=1
                        stalls_by_DF+=1
                        # continue
                
                elif (returnlist[0][0]=='M' and returnlist[0][1]=='M'):
                    nextflagMM=1
                    
                elif (returnlist[0][0]=='E' and returnlist[0][1]=='D'): #for branch resolution we need data at decode stage
                    if(returnlist[0][3]==[2,1]): # 1 cycle stalls
                        nextflagED=1
                        stalling(2)
                        regs[pr_exe[1]]=pr_exe[0] # we already have values from E stage of instruction at index 2
                        stallflag=1
                        no_of_stalls+=1
                        stalls_by_DF+=1
                        pr_exe[3]='skip'
            
                    elif(returnlist[0][3]==[3,1]): #no stall required
                        regs[pr_mem[1]] = pr_mem[0] #as it was dependent on E stage of instruction at index 3 but it has now completed its memory stage so we can take regs value from it
                        pr_mem[3]='skip'
                
                elif (returnlist[0][0]=='M' and returnlist[0][1]=='D'):
                    if(returnlist[0][3]==[3,1]): # 1 cycle stalls
                        stalling(2)
                        stallflag=1
                        nextflagMD=1
                        regs[pr_mem[1]] = pr_mem[0] #because mem of 3rd is already done but we need a stall to decode the instruction again
                        pr_mem[3]='skip'
                        no_of_stalls+=1
                        stalls_by_DF+=1
                        
                    elif(returnlist[0][3]==[2,1]): #2 cycle stalls
                        stalling(2)
                        nextflagMD=1
                        stallflag=2
                        no_of_stalls+=2
                        stalls_by_DF+=2
                        
            
            if lemme[1] == -1:                        
                # print('lemme [1] == -1')
                if ((bs3[0] == "SB" or bs3[0] == "JAL" or bs3[0] == "JALR") and stallflag==0 and com_32(bin(int(master_list[0][8],2)-4)[2::])!=com_32(bs2) ):    
                    flush_dada(bs2)
                    flushflag=1
                    no_of_stalls+=flushflag
                    stalls_by_BP+=flushflag
                    no_of_mispred+=1
                elif((bs3[0] == "SB" or bs3[0] == "JAL" or bs3[0] == "JALR") and stallflag==0 and com_32(bin(int(master_list[0][8],2)-4)[2::])==com_32(bs2)):
                    insert_carr()
                    continue
            else:                                    
                if ((bs3[0] == "SB" or bs3[0] == "JAL" or bs3[0] == "JALR") and com_32(bin(int(master_list[0][8],2)-4)[2::])!=com_32(bs2) and stallflag==0):# and bin(int(master_list[0][8],2)-4)[2::]!=bs2):                          #predictin mesed up
                    flush_dada(bs2)
                    flushflag=1                   #flush it, call new target
                    no_of_stalls+=flushflag
                    stalls_by_BP+=flushflag
                    no_of_mispred+=1
                elif((bs3[0] == "SB" or bs3[0] == "JAL" or bs3[0] == "JALR") and stallflag==0 and com_32(bin(int(master_list[0][8],2)-4)[2::])==com_32(bs2)):# bin(int(master_list[0][8],2)-4)[2::]==bs2):
                    insert_carr()
                    continue

            # if(master_list[4][9]=='jalr'):
            #     sys.exit()
            
            if(stallflag==0):
                if(flushflag==0):
                    insert_carr()
                if lemme[0] != -1:                                  
                    master_list[0][8] = lemme[0]                    
                    # print("master_list[0][8], pc = ",master_list[0][8])
                if(bs3[0] == "SB" or bs3[0] == "JAL" or bs3[0] == "JALR"):
                    update_bht(bin(int(curr_pc,2)-4)[2::],bs3[1],bs2)
                    master_list[0][8] = bs2
                   
            if flushflag==1:
                blank.append(j)
            
                if(fetchedInst!=-1 and fetchedInst!=-2):
                    blank2.append(get_inst(fetchedInst))
                else:
                    blank2.append('NONONO')
                blank3.append(count)
            flushflag=0
            elapsed = time.time()-start
            # print('register x1 =',regs[1])
                    
    if(elapsed > 60):
        print("Something is wrong, program took too long too execute, might be an infinite loop")
