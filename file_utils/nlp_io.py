import os
import pickle as pkl


def make_dir(mdir):
    if not os.path.isdir(mdir):
        os.mkdir(mdir)


def pkl_dump(data, file):
    with open(file, "wb") as f:
        pkl.dump(data, f)


def pkl_load(file):
    with open(file, "rb") as f:
        data = pkl.load(f)
    return data


def read_file(file, encoding="utf-8"):
    with open(file, "r", encoding=encoding) as f:
        text = f.read().strip()
    return text


def write_file(text, file, encoding="utf-8"):
    with open(file, "w", encoding=encoding) as f:
        f.write(text)
