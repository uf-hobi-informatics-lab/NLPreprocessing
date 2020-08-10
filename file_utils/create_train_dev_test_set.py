import sys
import os
from numpy import random
from shutil import copyfile
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger('train_test_split')


def __create_files_list(src_dir):
    assert os.path.isdir(src_dir), f"{src_dir} is not exist."
    return list(map(lambda x: "/".join([src_dir, x]), os.listdir(src_dir))), os.listdir(src_dir)


def train_test_ids_to_file(fids, dir, cate='train'):
    file_name = f"{cate}_set_all_ids.txt"

    fids = list(map(lambda x: x.split('/')[-1], fids))

    with open(f"{dir}/{file_name}", "w") as f:
        f.write("\n".join(fids))


def __write2file(file_list, output_dir, output_file_name):
    with open("/".join([output_dir, output_file_name]), "w") as f_tr:
        for file in file_list:
            file_id = file.split("/")[-1]
            # f_tr.write("\t".join([f"__doc {file_id}__", "-1", "-1", "-1", "-1", "O", "\n\n"]))
            f_tr.write(f"-DOCSTART- __doc {file_id}__\n\n")
            with open(file, "r") as fr:
                txt = fr.read().strip()
            f_tr.write(txt)
            f_tr.write("\n\n")


def create_train_test_sets(src_dir, test_proportion=0.2, merge=True, shuffle_num=3):
    file_list, file_id_list = __create_files_list(src_dir)

    for _ in range(shuffle_num):
        random.shuffle(file_list)

    slice_index = int(len(file_list) * test_proportion)

    test_set = file_list[:slice_index]
    train_set = file_list[slice_index:]
    logger.info(f"train set size: {len(train_set)}; test set size: {len(test_set)}")

    output_dir = "_".join([src_dir, "train_test_split"])

    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    # write train and test ids to files
    train_test_ids_to_file(train_set, output_dir, "train")
    train_test_ids_to_file(test_set, output_dir, "test")

    if not merge:
        train_dir = "/".join([output_dir, "training_set"])
        test_dir = "/".join([output_dir, "test_set"])
        if not os.path.isdir(train_dir):
            os.mkdir(train_dir)
        if not os.path.isdir(test_dir):
            os.mkdir(test_dir)
        for file in train_set:
            new_file = "/".join([train_dir, file.split("/")[-1]])
            copyfile(file, new_file)
        for file in test_set:
            new_file = "/".join([test_dir, file.split("/")[-1]])
            copyfile(file, new_file)

    __write2file(train_set, output_dir, "training_set.txt")
    __write2file(test_set, output_dir, "testing_set.txt")


def test():
    # create_train_test_sets("data_sample/bio", test_proportion=0.5, merge=False)
    # print(os.getcwd())
    create_train_test_sets(src_dir="/Users/alexgre/workspace/py3/2019AMIA_DEID/2019amia_train_bio",
                           test_proportion=0.25)
    pass


if __name__ == '__main__':
    test()
