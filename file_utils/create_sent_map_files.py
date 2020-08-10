import sys
import os
from annotation2BIO import pre_processing
import logging
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger('pre_processing clinical notes')


def token2file(fw, sents):
    for sent in sents:
        for word in sent:
            new_line = "\t".join(map(lambda x: str(x),
                                     [word[0], word[1][0], word[1][1], word[2][0], word[2][1], "\n"]))
            fw.write(new_line)


def output_mapping_sent_files(raw_data_dir, output_dir, deid_pattern=None):
    raw_data_dir = raw_data_dir
    output_dir = output_dir

    if not os.path.isdir(raw_data_dir):
        raise RuntimeError("Input data source directory is not exist.")

    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    for input_file in os.listdir(raw_data_dir):
        logger.info(f'Current processing {input_file}')

        output_sent_file = "".join([output_dir, "/", input_file.split(".")[0], ".sent.txt"])
        output_map_file = "".join([output_dir, "/", input_file.split(".")[0], ".map.txt"])
        input_file = "".join([raw_data_dir, "/", input_file])

        with open(output_map_file, "w") as fw_map, open(output_sent_file, "w") as fw_sent:
            sents, tokens = pre_processing(input_file, deid_pattern=deid_pattern)
            fw_sent.write(sents)
            token2file(fw_map, tokens)


if __name__ == '__main__':
    # output_mapping_sent_files("data_sample/test", "data_sample/test_output", deid_pattern="\[\*\*|\*\*\]")
    assert len(sys.argv) == 4, "must provide input, output file directories and de-identifier pattern using # if None"
    if sys.argv[3] == '#':
        dp = None
    else:
        dp = sys.argv[3]
    output_mapping_sent_files(sys.argv[1], sys.argv[2], deid_pattern=dp)
