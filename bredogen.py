#!/usr/bin/env python3

import random
import re
from sys import argv, stdin

SYMBOLS=",.:!?"

REPLACEMENTS=[
    "например",
    "тассзать",
    "тащемта",
    "значит",
    "грубо говоря",
    "образно говоря",
    "образно выражаясь",
    "положа руку на сердце",
    "к примеру",
    "к слову",
    "что характерно",
    "как-бы",
    "опять же",
    "между тем",
    "промежду прочим",
    "возможно",
    "наверно",
    "может быть",
    "то есть",
    "походу",
    "собственно",
    "кажется",
    "зачем-то",
    "с позволения сказать",
    "судя по всему",
    "к сожалению",
    "как вариант",
    "кстати",
    "неожиданно",
    "внезапно",
    "казалось-бы"
]

ENDINGS=[
    "как вариант например",
    "или наоборот например",
    "как вариант",
    "или наоборот, как вариант, например",
    "или примерно так, например",
    "или нет",
    "примерно так",
    "примерно как-то так",
    "возможно, например",
    "кажется",
    "возможно",
    "вроде как",
    "оказывается",
    "к слову",
    "наверно",
    "или как-то так",
    "но это не точно",
    "как оказалось",
    "образно говоря",
    "зачем-то",
    "кстати",
    "неожиданно",
    "внезапно",
    "надо же",
    "однозначно",
    "с другой стороны",
    "простите",
    "вот",
    "значит",
    "так или иначе",
    "да"
]

SYMBOLS_RE=re.compile(r"["+SYMBOLS+"]+")
SPACES_RE=re.compile(r"\s+")

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
        ret += ' '
        ret += text[start:m.start()]
        ret += ' '
        ret += random_repl()
        ret += m.group(0)
        ret += ' '
        start = m.end()
        m = SYMBOLS_RE.search(text, start) 

    ret += text[start:]
    return ret

def process(src):
    repl = replace(src)
    repl = repl.rstrip()
    if len(repl) == 0:
        return src
    if repl != src and random.random() <= 0.90:
        if repl[-1] not in ('.','?',',',';',':','0','1','2','3','4','5','6','7','8','9'):
            repl += ", " + random_ending()
        elif repl[-1] not in ('0','1','2','3','4','5','6','7','8','9'):
            repl = repl[:-1] + ' ' + random_ending() + repl[-1]
    elif random.random() < 0.75:
        if repl[-1] not in ('.','?',',',';',':','0','1','2','3','4','5','6','7','8','9'):
            repl += ", " + random_ending()
        elif repl[-1] not in ('0','1','2','3','4','5','6','7','8','9'):
            repl = repl[:-1] + ' ' + random_ending() + repl[-1]
    return beautify(repl)

def main():
    def print_repl(text, end):
        repl = replace(text)
        beautiful = beautify(repl)
        print(beautiful, end=end)

    has_args = len(argv) > 1
    if has_args:
        for arg in argv[1:]:
            print_repl(arg, ' ')
    else:
        # this may block on stdin
        for line in stdin:
            print_repl(line, '\n')
    beautiful = beautify(random_ending())
    print(beautiful)

if __name__ == '__main__':
    main()
