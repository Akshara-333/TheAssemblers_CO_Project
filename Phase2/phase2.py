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

#listof_functions=[add, and1, or1, sll, slt, sra, srl, sub, xor, mul, div, rem,addi, andi, ori, lb, ld, lh, lw, jalr,sb, sw, sd, sh,beq, bne, bge, blt, lui,jal]


def add():
    #print(list)
    m=int(list[0],2)#values in registers and list are in binary format
    n=int(list[1],2)
    x=extract(registers[m],32) + extract(registers[n],32)
    o=int(list[3],2)
    registers[o]=convert(x,32)

def and1():
    m = int(list[0],2)
    n = int(list[1],2)
    # print(int(registers[m],2),int(registers[n],2))
    x = extract(registers[m],32) & extract(registers[n],32)
    # print(x,"ans")
    o=int(list[3],2)
    # print(o)
    registers[o]=convert(x,32)
    # print(registers[o])

def or1():
    m = int(list[0],2)
    n = int(list[1],2)
    x = extract(registers[m],32) | extract(registers[n],32)
    o = int(list[3],2)
    registers[o]=convert(x,32)

def slt():
    m = int(list[0],2)
    n = int(list[1],2)
    o=int(list[3],2)
    if extract(registers[m],32) < extract(registers[n],32):
        registers[o]=convert(1,32)
    else:
        registers[o]=convert(0,32)

def sll():
    m = int(list[0],2) #rs1
    n = int(list[1],2) #rs2
    if(extract(registers[n],32)<0):
        print("error: negative shift not allowed")
        return "error: negative shift not allowed"
    if(extract(registers[n],32)>32):
        x=0
    else:
        x = extract(registers[m],32) << extract(registers[n],32)
    # print(int(registers[m],2),int(registers[n],2))
    o=int(list[3],2)
    # print(x)
    registers[o]=convert(x,32)
    
def sra():
    m = int(list[0],2)
    n = int(list[1],2)
    if(extract(registers[n],32)<0):
        print("error: negative shift not allowed")
        return "error: negative shift not allowed"
    elif(extract(registers[n],32)<=32):
        x = extract(registers[m],32)>>extract(registers[n],32)
    else:
        x= -1
    # x = int(registers[m],2) >> int(registers[n],2)
    o = int(list[3],2)
    # print(x)
    registers[o]=convert(x,32)
    
def srl():
    m = int(list[0],2) #rs1
    n = int(list[1],2) #rs2
    o = int(list[3],2)
    if(extract(registers[n],32)<0):
        print("error: negative shift not allowed")
        return "error: negative shift not allowed"
    elif(extract(registers[n],32)<=32):
        v = registers[m]
        for _ in range(int(registers[n],2)):
            v = ('0'+v)[:32]
            registers[o]=com_32(v)
    else:
        x=0
        registers[o]=convert(v,32)
    
def sub():
    m=int(list[0],2)
    n=int(list[1],2)
    x=extract(registers[m],32) - extract(registers[n],32)
    o=int(list[3],2)
    registers[o]=convert(x,32)
    # print("yo1")

def xor():
    m = int(list[0],2)
    n = int(list[1],2)
    x = extract(registers[m],32) ^ extract(registers[n],32)
    o=int(list[3],2)
    registers[o]=convert(x,32)

def mul():
    m = int(list[0],2)
    n = int(list[1],2)
    x = extract(registers[m],32) * extract(registers[n],32)
    o=int(list[3],2)
    registers[o]=convert(x,32)

def div():
    m = int(list[0],2)
    n = int(list[1],2)
    if(extract(registers[n],32)==0):
        print("division by zero not allowed")
        return "error : division by zero not allowed"
    x = int(extract(registers[m],32) / extract(registers[n],32))
    o=int(list[3],2)
    registers[o]=convert(x,32)

def rem():
    m = int(list[0],2)
    n = int(list[1],2)
    x = extract(registers[m],32) % extract(registers[n],32)
    o=int(list[3],2)
    registers[o]=convert(x,32)

def addi():
    m = int(list[0],2)
    n = str(list[2])
    # print("immediate value =",n,extract(n,12))
    # print(registers[m],extract(registers[m],32))
    x = extract(registers[m],32) + extract(n,12)
    # print((x))
    # print(convert(x,32))
    o = int(list[3],2)
    registers[o]=convert(x,32)

def andi():
    # print(list)
    m = int(list[0],2)
    n = str(list[2])
    # print("debug",m,n)
    x = extract(registers[m],32) & extract(n,12)
    o = int(list[3],2)
    registers[o]=convert(x,32)

def ori():
    m = int(list[0],2)
    n = str(list[2])
    x = extract(registers[m],32) | extract(n,12)
    o = int(list[3],2)
    registers[o]=convert(x,32)

def lb():
    m=extract(list[2],12) #immediate value
    k=int(list[0],2) #rs1
    n=m+extract(registers[k],32) #calculate r[rs1] + imm
    # print(hex(n),m,k)
    if(n<500000000):
        # print("address",hex(n))
        x=mem.get_data_at(n)  
    else:
        try:
            x=stack[hex(n)]
        except:
            x='00'
    y=int(list[3],2)
    registers[y]=convert(extract(bin(int('0x'+x,16))[2:],8),32)

def lw():
    # print("m=====",list[2])
    m=extract(list[2],12)
    # print(m)
    k=int(list[0],2)
    # print("address in register ",hex(int(registers[k],2)))
    n=m+int(registers[k],2)
    # print("n=====",(n-268435456))
    # print(hex(n),n)
    if(n+3<500000000):
        x1=mem.get_data_at(n)
        x2=mem.get_data_at(n+1)
        x3=mem.get_data_at(n+2)
        x4=mem.get_data_at(n+3)
        x=x4+x3+x2+x1
        # print("loaded value =",x)
    else:
        # print(hex(n),"address in the stack")
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
        # print("loaded value =",x)
    y=int(list[3],2)
    registers[y]=convert(extract(bin(int('0x'+x,16))[2:],32),32)

def ld():
    m=extract(list[2],12)
    k=int(list[0],2)
    n=m+int(registers[k],2)
    if(n+3<500000000):
        x1=mem.get_data_at(n)
        x2=mem.get_data_at(n+1)
        x3=mem.get_data_at(n+2)
        x4=mem.get_data_at(n+3)
        x=x4+x3+x2+x1
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
    y=int(list[3],2)
    registers[y]=convert(extract(bin(int('0x'+x,32))[2:],16),32)

def lh():
    m=extract(list[2],12)
    k=int(list[0],2)
    n=m+int(registers[k],2)
    if(n+1<500000000):
        x1=mem.get_data_at(n)
        x2=mem.get_data_at(n+1)
        x=x2+x1
    else:#they are in stack
        try:
            x2=stack[hex(n+1)]
        except:
            x2='00'
        try:
            x1=stack[hex(n)]
        except:
            x1='00'
        x = x2+x1
    y=int(list[3],2)
    registers[y]=convert(extract(bin(int('0x'+x,16))[2:],16),32)

def sb():
    m=extract(list[2],12)
    k=int(list[0],2)
    n=m+int(registers[k],2)
    y=int(list[1],2)
    #n = should be a address
    # n=500000010
    if(n<500000000):
        mem.adddata(n,registers[y][24:32])
        # mem.adddata(n,)
    else:
        stack[hex(n)]=hex(int(registers[y][24:32],2))[2::].zfill(2)

def sw():
    m=extract(list[2],12)
    k=int(list[0],2)
    n=m+int(registers[k],2)
    y=int(list[1],2)
    itit = registers[y]
    add3,add2,add1,add0=hex(n+3),hex(n+2),hex(n+1),hex(n)
    val3,val2,val1,val0=hex(int(itit[0:8],2))[2::].zfill(2), hex(int(itit[8:16],2))[2::].zfill(2),hex(int(itit[16:24],2))[2::].zfill(2),hex(int(itit[24:],2))[2::].zfill(2)
    # print(add3,add2,add1,add0)
    if(n+3<500000000): #store in data segment and append the list
        mem.adddata(n+3,registers[y][0:8])
        mem.adddata(n+2,registers[y][8:16])
        mem.adddata(n+1,registers[y][16:24])
        mem.adddata(n,registers[y][24:32])
    if(int( add3 ,16)>0x7ffffff3):
        print("can's write in memory after 0x7ffffff3")
    else: #store in stack
        stack[add3]=val3
        stack[add2]=val2
        stack[add1]=val1
        stack[add0]=val0
        
    
def sh():
    m=extract(list[2],12)
    k=int(list[0],2)
    n=m+int(registers[k],2)
    y=int(list[1],2)
    add1,add0=hex(n+1),hex(n)
    val1,val0=hex(int(registers[y][16:24],2))[2::].zfill(2),hex(int(registers[y][24:],2))[2::].zfill(2)
    if(n+1<500000000):
        mem.adddata(n+1,registers[y][16:24])
        mem.adddata(n,registers[y][24:32])
    
    else:
        stack[add1]=val1
        stack[add0]=val0

def sd(): 
    m=extract(list[2],12)
    k=int(list[0],2)
    n=m+int(registers[k],2)
    y=int(list[1],2)
    # mem.adddata(n+7,'00000000')
    # mem.adddata(n+6,'00000000')
    # mem.adddata(n+5,'00000000')
    # mem.adddata(n+4,'00000000')
    itit = registers[y]
    add3,add2,add1,add0=hex(n+3),hex(n+2),hex(n+1),hex(n)
    val3,val2,val1,val0=hex(int(itit[0:8],2))[2::].zfill(2),hex(int(itit[8:16],2))[2::].zfill(2),hex(int(itit[16:24],2))[2::].zfill(2),hex(int(itit[24:],2))[2::].zfill(2)
    if(n+3<500000000):
        mem.adddata(n+3,registers[y][0:8])
        mem.adddata(n+2,registers[y][8:16])
        mem.adddata(n+1,registers[y][16:24])
        mem.adddata(n,registers[y][24:32])
    else:
        stack[add3]=val3
        stack[add2]=val2
        stack[add1]=val1
        stack[add0]=val0


def beq():
    m=int(list[0],2)
    n=int(list[1],2)
    o=extract(list[2],12)*2
    if (extract(registers[m],32)==extract(registers[n],32)):
        if(o>0):
            list[8]=bin(int(list[8],2)+ o -4).replace("0b","")
        else:
            list[8]=bin(int(list[8],2)+ o - 4).replace("0b","")

def bge():
    m=int(list[0],2)
    n=int(list[1],2)
    o=extract(list[2],12)*2
    if extract(registers[m],32)>=extract(registers[n],32):
        if(o>0):
            list[8]=bin(int(list[8],2)+ o -4).replace("0b","")
        else:
            list[8]=bin(int(list[8],2)+ o- 4).replace("0b","")

def bne():
    m=int(list[0],2)
    n=int(list[1],2)
    o=extract(list[2],12)*2
    if extract(registers[m],32)!=extract(registers[n],32):
        if(o>0):
            list[8]=bin(int(list[8],2)+ o -4).replace("0b","")
        else:
            list[8]=bin(int(list[8],2)+ o - 4).replace("0b","")

def blt():
    m=int(list[0],2)
    n=int(list[1],2)
    o=extract(list[2],12)*2
    if extract(registers[m],32)<extract(registers[n],32):
        if(o>0):
            list[8]=bin(int(list[8],2)+ o -4).replace("0b","")
        else:
            list[8]=bin(int(list[8],2)+ o - 4).replace("0b","")

def lui():
    m=int(list[2],2)
    n=int(list[3],2)
    registers[n]=bin(m).replace("0b","")+"000000000000"
    registers[n]=com_32(registers[n])
   

def jal():
    m=extract(list[2],20)*2 
    n=int(list[3],2)
    registers[n]=com_32(bin(int(list[8],2)).replace("0b",""))#storing return address in register
    
    list[8]=bin(int(list[8],2)+m - 4).replace("0b","") #updating program counter
def jalr(): #jalr x0,0(x1)
    m=extract(list[2],12) 
    k=int(list[0],2) #rs1
    n=m+int(registers[k],2) #relative address to load from memory
    o=int(list[3],2)
    registers[o]=com_32(bin(int(registers[8],2)+4).replace("0b",""))
    # list[8]=bin(n).replace("0b","").zfill(32)
    list[8] = convert(n,32)
    # print(list[8])

def run():
    start=time.time()
    elapsed=0
    count=0
    while elapsed < 4:
        #print(list[7])
        string=fetch(list)
        #print(string)
        if string=="continue":
            count=count+1  #for GUI
            
            decode(list)
            print(">>> \t ENTER--->",list[9],"initial pc=",hex(int(list[8],2)))
            execute(list,registers)
            registers[0] = '00000000000000000000000000000000'
            # printregisters()
            elapsed=time.time()-start
        else:
            print("Code successfully Executed")
            break
    if(elapsed>2):
        print("Something is wrong, program took too long too execute, might be an infinite loop")
    print("run")
    return count
    
def step():
    
    string=fetch(list)
    if string=="continue":
        decode(list)
        execute(list,registers)
        #execute one step of code
    else:
        print("code successfully Executed")
    #print(list)
    x=int(list[8],2)
    print("step")
    return x-4

def reset():
    global list
    list=['00000000000000000000000000000000', '00000000000000000000000000000000', '00000000000000000000000000000000', '00000000000000000000000000000000',
 '00000000000000000000000000000000', '00000000000000000000000000000000', '00000000000000000000000000000000', '00000000000000000000000000000000', '00000000000000000000000000000000',
 '00000000000000000000000000000000'] 
    global registers
    registers=['00000000000000000000000000000000','00000000000000000000000000000000','01111111111111111111111111110000','00010000000000000000000000000000','00000000000000000000000000000000',
'00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000',
'00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000',
'00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000',
'00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000',
'00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000','00000000000000000000000000000000',
'00000000000000000000000000000000','00000000000000000000000000000000']

    #print(list)
    print("reset")
def stop():
    print("execution stopped")

def previous():
    print("previous")
run()
print(registers)
mem.Memo()
print(stack)
