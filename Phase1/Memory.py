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
class Memory:
    data = {}
    text = []
    stack = []
    pointer = 268435456

    def add_details(s, add, val):
        # add = hex(add).zfill(8)
        add = '0x'+(hex(add)[2::].zfill(8))
        s.data[add] = hex(int(val, 2)).replace('0x', '').zfill(2)
        
def adddata(s, type, val):
        if(type != '.asciiz'):
            val = val.replace(",", ' ')
        arr = val.split(' ')
        myreturnvalue = len(s.data)
        
        if(type == '.word'):
            ret_value = s.pointer
            for x in arr:
                if(len(x) > 1):  # NO need to convert if passed value is already in hex
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
        	# print(val,"stored at =" ,hex(myreturnvalue+268435456))
        	# print(self.data)
        	# return hex(int(myreturnvalue+268435456))

def get_data(s, add ):
        # x=int(0x10000000)
        # y=int(add)
        # z=y-x
        # print (self.data[hex(add & 0xffffffff).zfill(8)])
        try:
            return s.data[hex(add & 0xffffffff).zfill(8)]
        except:
            return '00'
    
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

mo = Memory()
mo.adddata('.asciiz','Hello World')
mo.Memo()
