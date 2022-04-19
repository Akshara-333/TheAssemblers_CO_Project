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
