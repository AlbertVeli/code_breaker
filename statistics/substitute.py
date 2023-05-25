#!/usr/bin/env python3

import fileinput

def subst(s, table):
    """
    Substitutes characters in a string using a substitution table.

    Args:
        s (str): The input string to be processed.
        table (dict): A dictionary representing the substitution table, where
            the keys are the characters to be replaced, and the values are the
            substitution characters.

    Returns:
        rs (str): A new string where each character in the input string is
        replaced according to the substitution table. If a character is not
        found in the table, it is left unchanged.
    """
    rs = ''
    for c in s:
        if c in table:
            rs += table[c]
        else:
            rs += c
    return rs

# Cleartext alphabet, lowercase [a-z]
clr = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
# Ciphertext alphabet, the letters in clr permuted
cph = ['w', 'e', 's', 't', 'r', 'm', 'o', 'a', 'b', 'c', 'd', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'n', 'p', 'q', 'u', 'v', 'x', 'y', 'z']

enc_table = dict(zip(clr, cph))
#dec_table = {v: k for k, v in enc_table.items()}

c = ''
for line in fileinput.input():
    c += subst(line, enc_table)
print(c)
