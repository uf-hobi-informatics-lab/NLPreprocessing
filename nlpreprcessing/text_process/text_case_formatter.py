import sys


def all2lower(ifn):
    idx = ifn.rfind(".")
    ofn = ifn[:idx] + ".lower.txt"

    with open(ifn, "r") as fr, open(ofn, "w") as fw:
        for i, line in enumerate(fr):
            nline = " ".join([w.lower() for w in line.split(" ")])
            fw.write(nline)


def all2upper(ifn):
    idx = ifn.rfind(".")
    ofn = ifn[:idx] + ".upper.txt"

    with open(ifn, "r") as fr, open(ofn, "w") as fw:
        for i, line in enumerate(fr):
            nline = " ".join([w.upper() for w in line.split(" ")])
            fw.write(nline)


def all2capitalized(ifn):
    idx = ifn.rfind(".")
    ofn = ifn[:idx] + ".capitalized.txt"

    with open(ifn, "r") as fr, open(ofn, "w") as fw:
        for i, line in enumerate(fr):
            nline = " ".join([w.capitalize() for w in line.split(" ")])
            fw.write(nline)