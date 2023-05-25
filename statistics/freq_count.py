#!/usr/bin/env python3

# Plot bar chart of letter frequencies.
# Try for instance:
#
#   ./freq_count.py 1984_lowercase.txt
#   ./substitute.py 1984_lowercase.txt | ./freq_count.py
#
# to get bar charts of english and substituted ciphertext.
###

from string import ascii_lowercase
from collections import defaultdict
import fileinput
import sys
try:
    import plotext as plt
except:
    print ('%s depends on plotext, try:' % (sys.argv[0]))
    print ('  pip install plotext')
    sys.exit(1)

alphabet = ascii_lowercase
d = defaultdict(int)
total = 0

# Read from stdin or file(s)
for line in fileinput.input():
    for c in line:
        if c in alphabet:
            d[c] += 1
            total += 1

percentages = []
for c in alphabet:
    percentages.append(d[c] / total)

plt.bar(alphabet, percentages)
plt.title("Letter frequencies")
plt.show()
