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
