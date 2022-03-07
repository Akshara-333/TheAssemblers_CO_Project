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

