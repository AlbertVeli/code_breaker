#!/usr/bin/env python
#
# Simple code-breaking python curses game inspired
# by the mobile phone game NSA CryptoChallenge.
#
# Albert Veli
# Setting Orange, the 64th day of Confusion in the YOLD 3181

import curses
import time
import random

# Add current directory to pythonpath
import os.path
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
# and import quotes from quotes.py
from quotes import quotes

# --- Globals ---
scr = None
fp = None
category = None
quote = None
qu = None
numquotes = None
startpos = [2, 4]
pos = None
rchar = None
perm = None
start_time = None
guessd = None
missing = 0
errors = None
timestr = None
final_time = None
label = None
state = 'Running'

# --- Gui helpers ---

def init_gui():
    global scr
    global fp
    scr = curses.initscr()
    scr.keypad(True)
    # Timeout getkey() every second
    # so time string is updated every second.
    scr.timeout(1000)
    curses.noecho()
    curses.cbreak()
    curses.curs_set(False)
    # Comment the row below to skip debug.log.
    fp = open('debug.log', 'w')

def cleanup_gui():
    global scr
    curses.nocbreak()
    scr.keypad(False)
    scr.clear()
    curses.echo()
    curses.endwin()

# --- Helpers ---

def get_numquotes():
    """ Return number of quotes in quotes """
    global numquotes

    # This will only be True the first time.
    # On following calls numquotes will be
    # returned immediately.
    if numquotes == None:
        numquotes = 0
        for line in quotes.split('\n'):
            line.strip()
            if (not line.startswith('#')) and (':' in line):
                numquotes += 1

    return numquotes

def get_quote():
    """ Choose quote number n at random """
    n = random.randrange(get_numquotes())
    i = 0
    for line in quotes.split('\n'):
        line.strip()
        if (not line.startswith('#')) and (':' in line):
            if i == n:
                break
            else:
                i += 1
    # Now line is the quote we want
    # Split it into a category and a quote part
    category, quote = line.split(':')
    category = category.strip()
    quote = quote.strip()
    return (category, quote)

def get_randperm():
    """
    Return a dictionary with mapping of A-Z
    to A-Z in random order (permutation).
    In other words, the keys of the dictionary
    are cleartext letters and the values are
    ciphertext letters.
    """
    vals = list()
    while True:
        n = random.randrange(26)
        if not n in vals:
            vals.append(n)
            if len(vals) == 26:
                break
    # Convert 0-25 to A-Z
    for i in range(len(vals)):
        vals[i] = chr(vals[i] + ord('A'))

    # Create dictionary A-Z -> vals
    keys = list()
    for i in range(len(vals)):
        keys.append(chr(i + ord('A')))
    # keys and vals must be of equal size
    # for this to work. And they are.
    return dict(zip(keys, vals))

def advance_cursor(x, nl = False):
    """
    Advance cursor x steps forward.
    If nl is True then go to beginning
    of next line.
    """
    global pos
    if nl:
        pos[0] = startpos[0]
        pos[1] += 1
    else:
        pos[0] += x
        if pos[0] >= maxx:
            pos[0] -= maxx
            pos[1] += 1

def out_msg(msg, attr = False, nl = False):
    """
    Print msg at current pos. attr can be one of:
    A_BLINK     - Blinking (not annoying at all)
    A_BOLD      - Bold
    A_DIM       - Half bright
    A_REVERSE   - Reversed
    A_STANDOUT  - Highlighted
    A_UNDERLINE - Underlined
    """
    global pos
    if attr:
        scr.addstr(pos[1], pos[0], msg, attr)
    else:
        scr.addstr(pos[1], pos[0], msg)
    advance_cursor(len(msg), nl = nl)

def print_clear(s):
    """
    Print string s in cleartext. For each char
    If char is in guessd, print it. If guess is
    wrong print in reverse. Print space if char
    is not in guessd. If char is not in A-Z, just
    print it out (numbers, special characters).
    """
    global missing
    global errors
    for c in s:
        attr = False
        if c in perm:
            p = perm[c]
            if p in guessd:
                oc = c
                c = guessd[p]
                if oc != c:
                    attr = curses.A_REVERSE
                    # Count errors at same time
                    errors.add(c)
            else:
                c = ' '
                # Count missing at same time
                missing += 1
        out_msg(c, attr)
        advance_cursor(1)
    out_msg('', nl = True)

def print_perm(s):
    """
    Print string s permuted by dict p.
    If a char is not in p, print it as is.
    """
    for c in s:
        if c in perm and perm[c] == rchar:
            attr = curses.A_REVERSE
        else:
            attr = False
        if c in perm:
            out_msg(perm[c], attr)
        else:
            out_msg(c, attr)
        advance_cursor(1)
    out_msg('', nl = True)

def get_time(ts, penalty):
    """ Add penalty to ts and return new timestring. """
    # ts in format 'mm:ss'
    m, s = ts.split(':')
    m = int(m)
    s = int(s)
    s += penalty
    while s > 59:
        s -= 60
        m += 1
    ts = "%02d:%02d" % (m, s)
    return ts

def print_interleaved(s, width):
    """
    Print cleartext (s) and ciphertext
    interleaved. Break lines at first
    space before width characters.
    """
    global missing
    global errors
    global frame
    global final_time
    global pos
    global label
    global state

    i = 0
    missing = 0
    errors = set()
    while i < len(s):
        # Trim leading spaces
        while (s[i] == ' '):
            i += 1
        end = i + width
        # Last line
        if end > len(s):
            end = len(s)

        # Don't cut words in half
        if (end < len(s)) and (s[end] != ' '):
            # Move end back to last space
            while s[end] != ' ':
                end -= 1
        out_msg('', nl = True)

        # Clear text
        print_clear(s[i:end])

        # Cipher text
        print_perm(s[i:end])

        i += end - i + 1

    # Check if we're done yet
    if missing == 0:
        final_time = get_time(timestr, len(errors) * 10)
        label = 'Well done! Errors = ' + str(len(errors)) + '. Time = ' + final_time + '. 1 = new game. 4 = quit'
        state = 'Finished'

def dbg(s):
    global fp
    if fp:
        fp.write(s + '\n')
        fp.flush()

def main_game_handler():
    global pos
    global timestr

    scr.clear()
    scr.border(0)

    # Draw header
    pos = [maxx // 2 - 9, 1]
    out_msg('PYTHON CODE BREAKER', curses.A_REVERSE)

    # Category
    pos = [startpos[0], 2]
    out_msg(category)
    # Time
    pos = [maxx - 7, 2]
    elapsed = int(time.time() - start_time)
    timestr = "%02d:%02d" % (elapsed // 60, elapsed % 60)
    out_msg(timestr)

    # Line separator
    pos = [startpos[0], 3]
    for i in range(maxx - 4):
        out_msg('_')

    # Draw crypto
    pos[0] = startpos[0]
    pos[1] = startpos[1]
    print_interleaved(qu, maxx // 2 - 5)

    # Status bar
    pos = [startpos[0], maxy - 2]
    if label:
        out_msg(label, curses.A_REVERSE)
    scr.refresh()

def new_game():
    """ Run one game round """
    global category
    global quote
    global qu
    global perm
    global start_time
    global guessd
    global state

    # Init globals
    category, quote = get_quote()
    # If you really want to, you can cheat
    # by uncommenting the print lines below
    dbg(category)
    dbg(quote)
    qu = quote.upper()
    perm = get_randperm()
    guessd = dict()
    clear_handler()
    # Start with one hint
    hint_handler(False)
    start_time = time.time()
    state = 'Running'

def key_handler(key):
    global label
    global rchar
    global guessd
    key = key.upper()
    # Delete/space/backspace resets replace state
    if (key == 'KEY_DC') or (key == ' ') or (ord(key) == 8) or (ord(key) == 127):
        clear_handler()
    elif not rchar:
        if (key >= 'A') and (key <= 'Z'):
            rchar = key
            label = 'Replace ' + rchar + ' with'
    else:
        if (key >= 'A') and (key <= 'Z'):
            label = 'Replace ' + rchar + ' with ' + key
            guessd[rchar] = key
            #dbg(str(guessd))
            rchar = None
            clear_handler()

def hint_handler(penalty = True):
    global start_time
    global guessd
    if penalty:
        start_time -= 15
    while True:
        c = chr(random.randrange(26) + ord('A'))
        p = perm[c]
        if (c in qu) and (not p in guessd):
            guessd[p] = c
            return None

def clear_handler():
    """
    Remove mapping for rchar.
    """
    global guessd
    global rchar
    global label
    if rchar and (rchar in guessd):
        guessd.pop(rchar)
    rchar = None
    label = 'Type letter to replace'

def print_help():
    print """
Python Code Breaker

Keys:
 1   - New Game.
 2   - Hint (+15s).
 4   - Quit.
 Del - Clear currently highlighted letter.
       Space/Backspace also clears.
 A-Z - Letter to replace.
       Case doesn't matter.

Tips:
* Look for single-letter words, double letters
  within words and apostrophes.
* Look for common words like the, be, to, of, and,
  a, in, that, have, I, it, for, not etc.
  http://www.oxforddictionaries.com/words/the-oec-facts-about-the-language
* The more you play the more trends will become apparent.

Press Enter to start game
"""
    raw_input()

# --- Main ---

print_help()
random.seed()
init_gui()

key = '0'

new_game()

# Game loop. Fake event-driven program.
while key != '4':
    maxy, maxx = scr.getmaxyx()
    if state == 'Running':
        # This is where everything happens
        main_game_handler()

    # try/except needed to catch resize of terminal
    # window while in scr.getkey()
    try:
        key = scr.getkey()
    except:
        key = '0'
        maxy, maxx = scr.getmaxyx()
        #dbg('getkey exception, timeout/resize')
    if key == '1':
        new_game()
    elif key == '2' and state == 'Running':
        hint_handler()
    elif key != '0' and key != '4' and state == 'Running':
        #dbg('You entered ' + key)
        key_handler(key)

cleanup_gui()
