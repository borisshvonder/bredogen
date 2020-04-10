#!/usr/bin/env python3

import random
import re
from sys import argv, stdin

SYMBOLS=",.:!?"

REPLACEMENTS=[
    "например",
    "например",
    "например",
    "например",
    "например",
    "например",
    "например",
    "например",
    "например",
    "например",
    "например",
    "тассзать",
    "тащемта",
    "образно говоря",
    "положа руку на сердце",
    "промежду прочим строго говоря",
    "между нами, девочками",
    "хотелось бы отметить",
    "собственно говоря",
    "таким образом",
    "в натуре",
    "типа в натуре",
    "в некотором роде",
    "на хрен в принципе",
    "в самом деле",
    "всё такое конкретно",
    "конкретно походу",
]

ENDINGS=[
    "как вариант например",
    "или наоборот например",
    "или наоборот, как вариант например",
    "или примерно так например",
    "возможно например"
]

SYMBOLS_RE=re.compile(r"["+SYMBOLS+"]+")
SPACES_RE=re.compile(r"[ \t\f]+")

def random_repl():
    return random.choice(REPLACEMENTS)

def random_ending():
    return random.choice(ENDINGS)

def beautify(text):
    ret = text.strip()
    ret = SPACES_RE.sub(' ', ret)
    return ret

def replace(text):
    ret = ""
    start = 0
    m = SYMBOLS_RE.search(text, start)
    while m:
        ret += text[start:m.start()]
        ret += ' '
        ret += random_repl()
        ret += m.group(0)
        ret += ' '
        start = m.end()
        m = SYMBOLS_RE.search(text, start) 

    ret += text[start:]
    return ret

def replace_with_disclaimer(text):
    repl = replace(text)
    repl += random_ending()
    return beautify(repl)

def main():
    random.seed()
    cmdline = " ".join(argv[1:])
    print(replace_with_disclaimer(cmdline))

if __name__ == '__main__':
    main()
