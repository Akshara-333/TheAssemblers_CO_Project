from Phase1 import Memory
import math
import time
mem = Memory()
mem.Memo()

def printregisters():
    for i in [0,1,2,3,4,5,6,7,9,10,11,12,13,22,23,30,31]:
        print("x{}\t".format(i),'0x'+(hex(int(registers[i],2)).replace('0x','').zfill(8)))

def extract(stringin, n):
    # print("sss",stringin,len(stringin))
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
    # print(number,ans,"poop",hex(pop))
    if(number<(-1)*(2**(n-1)) or number>2**(n-1) - 1):
        print("error: overflow  =",number)
    
    return ans

'''0:rs1 1:rs2 2:imm 3:rd 4:f3 5:f7 6:opcode 7:ir 8:pc 9:current_function '''
list=['00000000000000000000000000000000', '00000000000000000000000000000000', '00000000000000000000000000000000', '00000000000000000000000000000000',
 '00000000000000000000000000000000', '00000000000000000000000000000000', '00000000000000000000000000000000', '00000000000000000000000000000000', '00000000000000000000000000000000',
 '00000000000000000000000000000000'] #list of strings

# Initialised values of all the 32 registers in binary
registers=['00000000000000000000000000000000','00000000000000000000000000000000','01111111111111111111111111110000','00010000000000000000000000000000','00000000000000000000000000000000',
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

def getIR(file_name,pc):
    f = open(file_name,'r')
    i = 0
    for x in f:
        if i==pc:
            ins_a = x.split()
            ins_a[1]=ins_a[1].replace("0x","")
            res = "{0:32b}".format(int(ins_a[1], 16))
            res=res.replace(" ","0")
            #res=int(ins_a[1],16)
            #y = bin(res).replace("0b","")
            #print(res)
            return res
        i=i+4
    return -1

i_file = "outfile.mc" 
def fetch(list):
    # print(list[8])
    list[7] = getIR(i_file,int(list[8],2))
    if(list[7]==-1):
        return "over"
    list[8]=bin(int(list[8],2)+4).replace("0b","")
    return "continue"

'''0:rs1 1:rs2 2:imm 3:rd 4:f3 5:f7 6:opcode 7:ir 8:pc 9:current_function '''
def decode(list):
    #print(list)
    ins=list[7]
    opcode = ins[25:32]
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


    elif(opcode=="0100011"):# s-format
        list[2]=ins[0:7]   
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


            '''0:rs1 1:rs2 2:imm 3:rd 4:f3 5:f7 6:opcode 7:ir 8:pc 9:current_function '''
    elif(opcode=="1100011"):#sb
        list[1]=ins[7:12]
        list[0]=ins[12:17]
        list[4]=ins[17:20]
        list[2]=(ins[0]+ins[24]+ins[1:7]+ins[20:24]) 
        if list[4]=="000":
            list[9]="beq"

        elif list[4]=="001":
            list[9]="bne"

        elif list[4]=="101":
            list[9]="bge"

        elif list[4]=="100":
            list[9]="blt"

    elif(opcode=="0000011"):#lb,lw,lh,ld
        list[2]=ins[0:12]
        list[0]=ins[12:17]
        list[3]=ins[20:25]
        list[4]=ins[17:20]

        if list[4]=="000":
            list[9]="lb"

        elif list[4]=="001":
            list[9]="lh"

        elif list[4]=="010":
            list[9]="lw"

        elif list[4]=="011":
            list[9]="ld"

    elif opcode=="0110111": #U-lui
        list[2]=ins[0:20]
        list[3]=ins[20:25]
        list[9]="lui"

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

    elif opcode=="1100111": #jalr
        list[2]=ins[0:12]
        list[0]=ins[12:17]
        list[3]=ins[20:25]
        list[4]=ins[17:20]
        list[9]="jalr"

    elif opcode=="1101111": #jal
        # list[2][0]=ins[0]
        # list[2][1:9]=ins[12:20]
        # list[2][10]=ins[11]
        list[2]=ins[0]+ins[12:20]+ins[11]+ins[1:11]
        list[3]=ins[20:25]
        list[9]="jal"
        

def execute(list,registers):
    insname=list[9]
    if(insname=="add"):
        add()
    elif(insname=="and"):
        and1()
    elif(insname=="or"):
        or1()
    elif(insname=="sll"):
        sll()
    elif(insname=="slt"):
        slt()
    elif(insname=="sra"):
        sra()
    elif(insname=="srl"):
        srl()
    elif(insname=="sub"):
        sub()
    elif(insname=="xor"):
        xor()
    elif(insname=="mul"):
        mul()
    elif(insname=="div"):
        div()
    elif(insname=="rem"):
        rem()
    elif(insname=="addi"):
        addi()
    elif(insname=="andi"):
        andi()
    elif(insname=="ori"):
        ori()
    elif(insname=="lb"):
        lb()
    elif(insname=="ld"):
        ld()
    elif(insname=="lh"):
        lh()
    elif(insname=="lw"):
        lw()
    elif(insname=="jalr"):
        jalr()
    elif(insname=="sb"):
        sb()
    elif(insname=="sw"):
        sw()
    elif(insname=="sd"):
        sd()
    elif(insname=="sh"):
        sh()
    elif(insname=="beq"):
        beq()
    elif(insname=="bne"):
        bne()
    elif(insname=="bge"):
        bge()
    elif(insname=="blt"):
        blt()
    elif(insname=="lui"):
        lui()
    elif(insname=="jal"):
        jal()

