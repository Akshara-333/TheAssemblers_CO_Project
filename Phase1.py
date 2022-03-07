import re
import sys
# Definig a command function for .word
def command(a, n):
    x = len(a)
    if x == n:
        return a
    else:
        p = a[::-1]
        # i=0
        for y in range(0, n-x):
            p = p + '0'
        p = p[::-1]
        return p

#Making a memory class for all necessary functions
class Memory:
    data = {}
    text = []
    pointer = 268435456
#Adding details 
    def add_details(s, add, val):
        # add = hex(add).zfill(8)
        add = '0x'+(hex(add)[2::].zfill(8))
        s.data[add] = hex(int(val, 2)).replace('0x', '').zfill(2)
        
#Checking for directives and removing "," " "
    def adddata(s, type, val):
        if(type != '.asciiz'):
            val = val.replace(",", ' ')
        arr = val.split(' ')
        myreturnvalue = len(s.data)
        
        if(type == '.word'):
            ret_value = s.pointer
            for x in arr:
                if(len(x) > 1):  # If already in hex no need to convert
                    if(x[0] == '0' and x[1] == 'x'):
                        if(len(x) <= 10):
                            y = command(x[2::], 8)
                        else:
                            print("value", x, " too large to fit in a word, storing 4 least sign. bytes")
                            y=x[2::][-8:]
                    else:  # not hex
                        y = hex(int(x) & 0xffffffff)[2::].zfill(8)
                        # print(y)
                        if(len(y) <= 8):
                            y = command(y, 8)
                        else:
                            print("can't store", x, "in a word, because value is too large. truncating the value and storing 4 least significant bytes")
                            y = y[-8:]
                else:  # length <=1
                    y = hex(int(x.strip()))[2::]
                    y = command(y, 8)
                y1 = y[0:2]
                y2 = y[2:4]
                y3 = y[4:6]
                y4 = y[6:8]
                s.data[hex(s.pointer)] = (y4)
                s.pointer += 1
                s.data[hex(s.pointer)] = (y3)
                s.pointer += 1
                s.data[hex(s.pointer)] = (y2)
                s.pointer += 1
                s.data[hex(s.pointer)] = (y1)
                s.pointer += 1  
            return hex(ret_value)   
        
        elif(type == '.asciiz'):
            ret_value = s.pointer
            for x in range(len(val)):
                s.data[hex(s.pointer)] = (hex(ord(val[x]))[2::])
                s.pointer+=1
            s.data[hex(s.pointer)] = '00'
            s.pointer+=1
            return hex(ret_value)
        else:
            print("Unrecognized datatype directive",type)
            return
        	# return hex(int(myreturnvalue+268435456))
    def get_data(s, add ):
     
        # print (self.data[hex(add & 0xffffffff).zfill(8)])
        try:
            return s.data[hex(add & 0xffffffff).zfill(8)]
        except:
            return '00'
#Appending value to it    
def add_text(s, val):
        s.text.append(val)

def Memo(s):
        print("data segment---------------------------------------------------------------------------------------------------------\n", s.data)
        data = []
        '''
        for x in range(len(self.data)):
            # print(hex(268435456 + x)," ",self.data[x])
            data_out.append( str(hex(268435456 + x))+ " : " + str(self.data[x]) )
        '''
        print("text segment"+"("+str(len(s.text))+")",
              "---------------------------------------------------------------------------------------------------------\n", s.text, "\n\n")
        return data
#Making dictionaries for add slt sub addi lw sw beq bne bge jal for bubble sort
dict3 = {
    "add": "000", "slt": "010",  "sub": "000", "addi": "000",  "lw": "010", "sw": "010","beq": "000", "bne": "001", "bge": "101", "auipc": "",
    "jal": ""
}

dict7 = {
    "add": "0000000",  "slt": "0000000", "sub": "0100000"}

dict_for = {
    'add': 'r',  'slt': 'r', 'sub': 'r', 'addi': 'i',  'lw': 'i', 'sw': 's', 'beq': 'sb', 'bne': 'sb', 'bge': 'sb', 'auipc': 'u',
    'jal': 'uj'
}

dict_opcode = {
    'add': '0110011', 'slt': '0110011','sub': '0110011', 'addi': '0010011', 'lw': '0000011', 'sw': '0100011', 'beq': '1100011', 'bne': '1100011', 'bge': '1100011', 
    'jal': '1101111' 
    
}

# dict_labels = {}
#Getting registers from string
def get_reg(string):
    if (string[0] == 'x'):
        s1 = int(string[1::])
        if (-1 < s1 and s1 < 32 ):
            return format(s1, '05b')
        else:
            print ("Register not Identified. Assuming the register to be x0\n")
            return -1
    elif (string[0] == 'a'):
        s1 = int(string[1::])
        if ( -1 < s1 and s1 < 8):
            return format(s1+10, '05b')
        else:
            print ("Register not Identified. Assuming the register to be a0\n")
            return -1
    else:
        print ("Register not Identified. Assuming the register to be x0\n")
        return -1

#Function for adding 12 bit immediate
def imm12bit(string):
    #print(string)
    if(len(string) > 1):
        if(string[0] == '0' and string[1] == 'x'):
            if(len(string) > 5):
                print ("Immediate value  must be 12 bit wide . Assuming the Immediate value as zero\n")
                return ("000000000000")
            else:
                return bin(int(string[2::], 16))[2::].zfill(12)  # 33333
   #being a hexadecimal number we need to convert it to a 12 bit value
    #	n = int(string) - 2**12
        elif (string[0] == '-'):  # eg.  -16
            n = int(string[1::])
            if (n<2049):
                n = 2**12 - n
                return (format(n, '012b'))
            else:
                print ("Immediate value  must be 12 bit wide. Assuming the Immediate value as zero\n")
                return ("000000000000")
        else:
            check = int(string)
            if (check < 2048):
                return (format(int(string), '012b'))
            else:
                print ("Immediate value must be 12 bit wide . Assuming the Immediate value as zero\n")
                return ("000000000000")
    else:
        if (len(string) == 1):
            if (string[0] != '0' and string[0] != '1' and string[0] != '2' and string[0] != '3' and string[0] != '4' and string[0] != '5' and string[0] != '6' and string[0] != '7' and string[0] != '8' and string[0] != '9'):
                print ("Immediate value must be a digit . Assuming the Immediate value as zero\n")
                return ("000000000000")
        check = int(string)
        if (check < 2048):
            return (format(int(string), '012b'))
        else:
            print ("Immediate value  must be 12 bit wide . Assuming the Immediate value as zero\n")
            return ("000000000000")

#Function for adding 20 bit immediate
def imm20bit(string):
    if(len(string) > 1):
        if(string[0] == '0' and string[1] == 'x'):
            if(len(string) > 7):
                return ("Immediate value  must be 20 bit wide . Assuming the Immediate value as zero\n")
                return ("00000000000000000000")
            else:  # return  as it is
                return bin(int(string[2::], 16))[2::].zfill(20)
        elif(string[0] == '-'):
            n = int(string[1::])
            if (n < 524289):
                n = 2**20 - n
                return format(n, '020b')
            else:
                return ("Immediate value  must be 20 bit wide. Assuming the Immediate value as zero\n")
                return ("00000000000000000000")
        else:
            big_check = int(string)
            if (big_check < 524288):
                return format(int(string), '020b')
            else:
                print ("Immediate value  must be 20 bit wide . Assuming the Immediate value as zero\n")
                return ("00000000000000000000")
    else:
        if (len(string) == 1):
            if (string[0] != '0' and string[0] != '1' and string[0] != '2' and string[0] != '3' and string[0] != '4' and string[0] != '5' and string[0] != '6' and string[0] != '7' and string[0] != '8' and string[0] != '9'):
                print ("Immediate value must be a digit . Assuming the Immediate value as zero\n")
                return ("00000000000000000000")
        big_check = int(string)
        if (big_check < 524288):
            return format(int(string), '020b')
        else:
            print ("Immediate value  must be 20 bit wide . Assuming the Immediate value as zero\n")
            return ("00000000000000000000")
#Getting commands from labels and implementing them
def get_command(l, pc, labels,data):
    if(dict_for.get(l[0],-1)==-1):
        print("incorrect command",l[0],end='')
        return -2,-2,''
    elif dict_for[l[0]] == 'r':
        #If enough values {mc1,mc2 will be returned as -2,-2 if not}
        e = 4
        land = len(l)
        if (land != e):
            print ("Expected",e - 1,"arguments but received",land - 1,end='')
            return -2,-2,''
        f7 = dict7[l[0]]
        f3 = dict3[l[0]]
        rd = get_reg(l[1])
        rs1 = get_reg(l[2])
        rs2 = get_reg(l[3])
        if(rd==-1 or rs1==-1 or rs2==-1):
            print(" Undefined register in R-format instruction",l[0])
            sys.exit()
        opcode = dict_opcode[l[0]]
        mc = f7 + rs2 + rs1 + f3 + rd + opcode
        return '%#010x' % (int('0b'+mc, 0)),-1,l[0]+" "+l[1]+" "+l[2]+" "+l[3]+"   "
    if(dict_for[l[0]] == 'i'):
        opcode = dict_opcode[l[0]]
        rd = get_reg(l[1])
        f3 = dict3[l[0]]
        if(opcode !='0000011'): #not a load instruction
            rs1 = get_reg(l[2])
            if(rs1==-1 or rd==-1):
                print(" undefined register in load instruction",l[0])
                sys.exit()
            imm = imm12bit(l[3])
        else: #load instruction
            if(len(l)==4):
                rs1 = get_reg(l[2])
                if(rs1==-1 or rd==-1):
                    print("undefined register in",l[0])
                    sys.exit()
                imm = imm12bit(str(l[3]))
            elif(len(l)==3 and data.get(l[2],-1)!=-1): #load of a variable and variable is defined
                new_l = ['auipc',l[1],'0x10000']
                mc1 = get_command(new_l,pc,labels,data)
                print(mc1[2])
                pc+=4
                print("value",data[l[2]])
                new_l = [l[0],l[1],l[1],int(data[l[2]],16) - 268435456 - pc + 4] # load x1 , x1 , offset and offset = data[l[2]] - int(0x10000000) - pc 
                # print(int(data[l[2]],16) - 268435456 - pc + 4)
                mc2 = get_command(new_l,pc,labels,data)
                # print(l)
                return mc1[0],mc2[0],mc1[2]+" $ "+l[0]+" "+ l[1]+" " + str(int(data[l[2]],16) - 268435456 - pc + 4) +"("+l[1]+")"
            else:
                print("incorrect format for the instruction. either",l[2],"not defined")
        # print(imm,rs1,f3,rd,opcode)
        mc = imm + rs1 + f3 + rd + opcode
        rep = str(l[0]) +" "+ str(l[1])+ " " +str(l[2])+ " " +str(l[3])+ "   "
        if(opcode=='0000011'):
            rep = str(l[0])+" "+str(l[1])+" "+str(l[3])+"("+l[2]+")   "
        # print(mc,'0x'+'%.*x'%(8,int('0b'+mc,0)), format(int(mc,2),"#010x"))
        return '%#010x' % (int('0b'+mc, 0)),-1,rep
    if(dict_for[l[0]] == 's'):
        #If enough values {mc1,mc2 will be returned as -2,-2 if not}
        exp = 4
        land = len(l)
        if (land != exp):
            print ("Expected",e - 1,"arguments but received",land - 1,end='')
            return -2,-2,''
        imm = imm12bit(l[3])
        rs1 = get_reg(l[2])
        rs2 = get_reg(l[1])
        if(rs1==-1 or rs2==-2):
            print(" undefined register in Store instruction",l[0])
            sys.exit()
        f3 = dict3[l[0]]
        opcode = dict_opcode[l[0]]
        #print(imm[0:7:],rs2,rs1,f3,imm[7::],opcode)
        mc = imm[0:7:] + rs2 + rs1 + f3 + imm[7::] + opcode
        #print(mc)
        return '%#010x' % (int('0b'+mc, 0)),-1,l[0] + " "+l[1]+" "+l[3]+"("+l[2]+")   "
    elif(dict_for[l[0]] == 'sb'):
        #If enough values {mc1,mc2 will be returned as -2,-2 if not}
        exp = 4
        land = len(l)
        if (land != exp):
            print ("Expected",e - 1,"arguments but received",land - 1,end='')
            return -2,-2,''
        # print(labels)
        imm = int((labels[l[3]]*4 - pc)/2)
        rs1 = get_reg(l[1])
        rs2 = get_reg(l[2])
        if(rs1==-1 or rs2==-2):
            print("undefined register in Branch instruction",l[0])
            sys.exit()
        f3 = dict3[l[0]]
        opcode = dict_opcode[l[0]]
        # print((labels[l[3]]*4 - pc))
        if(str(imm)[0] != '-'):
            imm = format(int(imm), '#014b')[2::]
        else:
            imm = format(2**12 - abs(int(imm)), '#014b')[2::] 
        #  rs2, rs1, f3, imm[7::], opcode)
        mc = imm[0] + imm[2:8:] + rs2 + rs1 + f3 + imm[8::] + imm[1] + opcode
        # print(mc,'%#010x'%(int('0b'+mc,0)))#, format(int(mc,2),"#010x"))
        return '%#010x' % (int('0b'+mc, 0)),-1,l[0]+" "+l[1]+" "+l[2]+" "+str((labels[l[3]]*4 - pc))+"   "
    if(dict_for[l[0]] == 'u'):
        #If enough values {mc1,mc2 will be returned as -2,-2 if not}
        exp = 3
        land = len(l)
        if (land != exp):
            print ("Expected",e - 1,"arguments but received",land - 1,end='')
            return -2,-2,''
        #continue making mc
        imm = imm20bit(l[2])
        rd = get_reg(l[1])
        if(rd==-1):
            print(" undefined register in instruction",l[0])
            sys.exit()
        opcode = dict_opcode[l[0]]
        #print(l,imm,rd,opcode)
        mc = imm+rd+opcode
        tttt = l[2]
        if(l[2][0]=='0' and l[2][1]=='x'):
            tttt = int(l[2],16)
        return '%#010x' % (int('0b'+mc, 0)),-1,l[0]+" "+l[1]+" "+str(tttt)+"  "
    if(dict_for[l[0]] == 'uj'): 
         # jal x1,label
        #If enough values {mc1,mc2 will be returned as -2,-2 if not}
        exp = 3
        land = len(l)
        if (land != exp):
            print ("Expected",e - 1,"arguments but received",land - 1,end='')
            return -2,-2,''
        opcode = dict_opcode[l[0]]
        rd = get_reg(l[1])
        if(rd==-1):
            print("Undefined register in jal instruction")
            sys.exit()
        #print("label[l[2]] =", labels[l[2]], "current pc =", pc)
        imm = int(labels[l[2]])*4 - pc
        # print("imm = ", imm)
        tttt = imm
        #relative value from address of current instructionAddress of label - PC(considerin PC is at current instruction)
        if(str(imm)[0] != '-'):
            imm = format(imm, "#022b")[2::]
        else:
            imm = format(2**20 - abs(imm), '#022b')[2::]
        #print(imm,rd,opcode)
        # because jal takes imm[20:1] ignores the first bit(0 index) as all instruction jumps are a multiple of 4 and 2 thus reducing redundancy
        imm = imm[0] + imm[0:19]
        imm = imm[0] + imm[10::] + imm[9] + imm[1:9:]
        #print(imm)
        mc = str(imm) + rd + opcode
        return '%#010x' % (int('0b'+mc, 0)),-1,l[0]+" "+l[1]+" "+str(tttt)+"   "

    #Converting to MC
def convertToMC(inst, labels,datas,data_out):
    instAdd = 0
    for x in inst:
        # Switching format in case of {jalr x0,0(x1)} equating {jalr x0 x1 0}
        flag = False
        # print(x)
        if(x.strip("\r\n") == "" or x.strip()==''):
            print("no instruction here, a empty line encountered!")
            continue
        s = str(x)
        s = s.strip("\r\n")
        s = s.strip()
        l = []
        s = s.replace(",", " ")
        s = s.replace(":", " ")
        if (s.count('(') != 0):
            flag = True
            s = s.replace("(", " ")
            s = s.replace(")", "")
        l = s.split()
        if (flag == True and len(l)==4) :
            l[2], l[3] = l[3], l[2]
            s = l[0]+" " + l[1] + " " + l[2] + " " + l[3]
        Code1,Code2,basicCode = get_command(l, instAdd, labels,datas)
        if (Code1 == -2 and Code2 == -2):
            Code1 = Code2
            msg = ''
            for x in l:
                msg = msg + x+" " 
            print(", in the instruction",msg)
            sys.exit()
        else:
            # print(l)
            writefile.write(hex(instAdd) + "  \t:\t"+Code1 + "\n")
            write2.write(hex(instAdd) +" "+Code1+" "+basicCode[:basicCode.find("$")].strip()+"\n")
            M.add_text(Code1)
            instAdd += 4
            if(Code2!=-1):
                writefile.write(hex(instAdd) + "  \t:\t"+Code2 + "\n")
                write2.write(hex(instAdd) + " "+Code2+" "+basicCode[basicCode.find("$")+1:].strip() + "\n")
                M.add_text(Code2)
                instAdd+=4     
    writefile.write("\n\nDATA_SEGMENT_OF_MCFILE\n{only the contents of memory locations that were explicity set by the program are shown}\n\n")
    for k in range(len(data_out)):
        writefile.write(data_out[k]+"\n")
    writefile.close()
def getDirectives():
    rf = open("bubblesort.asm", "r")
    file = rf.read()
    s = ''
    ins = []
    textsegment = True
    labels = {}
    data = {}
    tocheck = []
    for x in file:
        if(x == '\n'):
            if(s.strip(" \r\n") != '' or s.strip()!=''):
                # ins.append(s)
                #print("line :", s)
                if(s.find("#")!=-1):
                    s=s[0:s.find('#'):]
                if(s.strip() == '.data'):
                    textsegment = False
                    #ins.append(s)
                elif(s.strip()== '.text'):
                    textsegment = True
                    #ins.append(s)
                elif(s.find(":") != -1 and textsegment == True):
                    # cuu = s[0:s.find(":"):].replace('\t', 'aa')
                    labels[s[0: s.find(":"):].strip()] = len(ins)
                    if(s[s.find(":")+1::].strip().replace(" ", "") != ''):
                        ins.append(s[s.find(":")+1::])
                elif(textsegment==True):
                    ins.append(s)
                    y = s
                    y = y.replace(",",' ')
                    y = y.strip()
                    yy = y.split()
                    if(len(yy)==3 and data.get(yy[2],-1)!=-1):
                        tocheck.append(len(ins))
                elif(textsegment==False):
                    s=s.strip()
                    d = s.split(":")
                    d[0]=d[0].strip()
                    d[1]=d[1].strip()
                    d.append(d[1][d[1].find(" ")::].strip())
                    
                    d[1] = d[1][:d[1].find(" "):].strip()
                    d[2] = d[2].replace('"','')
                    #print(dd)
                    data[d[0]] = d[1],d[2]
                    #print(data)
                    address_for_stored_variable = M.add_data(data[d[0]][0],data[d[0]][1])
                                    data[d[0]] = address_for_stored_variable
                    #print(data)
            s = ''
        else:
            s += x
    if(s.strip("\r\n") != '' or s.strip()!=''):  
        # print("line :", s)
        # print("textsegment=", textsegment)
        s=s.strip()
        if(textsegment == False and s.find(':')!=-1 and s.strip('\r\n')!='.data' and s.strip('\r\n')!='.text'):
            s=s.strip()
            d = s.split(":")
            d[0]=d[0].strip()
            d[1]=d[1].strip()
            d.append(d[1][d[1].find(" ")::].strip())
            d[1] = d[1][:d[1].find(" "):].strip()
            d[2] = d[2].replace('"','')
            #print(dd)
            data[d[0]] = d[1],d[2]
            #print(data)
            address_for_stored_variable = M.add_data(data[d[0]][0],data[d[0]][1])
            data[d[0]] = address_for_stored_variable
            # ins.append(s)
        elif(textsegment == True and s.find(':')==-1 and s.strip('\r\n')!='.data' and s.strip('\r\n')!='.text'):
            ins.append(s)
        elif(s.find(":") != -1 and textsegment == True and s.strip('\r\n')!='.data' and s.strip('\r\n')!='.text'):
        #print( s[s.find(":")+1::])
            labels[s[0: s.find(":"):].replace(" ",'')] = len(ins)
            if(s[s.find(":")+1::].strip("\r\n").replace(" ","")!=''):
                ins.append(s[s.find(":")+1::])
            
    #print(ins)
    #print(labels)
    # print(len(ins))
    rf.close()
    # print(ins)
    for o in tocheck:
        for k in labels.keys():
            # print(o,k,labels[k])
            if((labels[k])>=o):
                labels[k]+=1
                # print(o,k,labels[k])
    return ins, labels , data
M = Memory()
instructions, labela,dataa = getDirectives() # returns list of instructions , labels , data (containing variable with address they point to)
# print(dataa)
data_out = M.show_Memory()
convertToMC(instructions, labela,dataa,data_out)
# M.show_Memory()
