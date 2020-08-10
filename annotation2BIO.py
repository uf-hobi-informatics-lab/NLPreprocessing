"""
This script aims to convert BRAT format data into BIO format data for NER
Entities will be mapped from their original offsets to the new offsets after sentence tokenization
Two sentences are separated by a empty line
entities and relations information are also provided in json format
"""

import os
import sys
import logging
from .text_process.sentence_tokenization import SentenceBoundaryDetection
logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__file__)
# logger.disabled = True
MIMICIII_PATTERN = "\[\*\*|\*\*\]"


def __ann_info(ann):
    en_info = ann.split(" ")
    return en_info[0], int(en_info[1]), int(en_info[-1])


def __rel_info(rel_id, rel, rep):
    info = rel.split(" ")
    assert len(info) == 3, f"{rel_id}\t{rel} is not a valid relation"

    arg1 = info[1].split(":")[1]
    arg2 = info[2].split(":")[1]
    rel_type = info[0]

    if rep:
        rel_type = rel_type.replace("-", "_") # format rel_type replace - with _

    return rel_type, arg1, arg2


def read_annotation_brat(ann_file, rep=False):
    """
    load annotation data
    entity_id2index_map -> {'T1': 0}
    entites -> ('T1', 'anticoagulant medications', 'Drug', (1000, 1025))
    relations -> ('Route-Drug', 'T3', 'T2')
    """
    # map the entity id (e.g., T1) to its index in entities list
    entity_id2index_map = dict()
    entites = []
    relations = []
    with open(ann_file, "r") as f:
        for line in f:
            anns = line[:-1].split("\t")
            ann_id = anns[0]
            if ann_id.startswith("T"):
                t_type = anns[-1]
                # for each in __ann_info(anns[1]):
                #     entites.append((t_type, each[0], each[1]))
                entity_words, offset_s, offset_e = __ann_info(anns[1])
                entites.append((t_type,  entity_words, (offset_s, offset_e)))
                entity_id2index_map[ann_id] = len(entites) - 1
            elif ann_id.startswith("R"):
                relations.append(__rel_info(ann_id, anns[1], rep))

    # sort entities list
    # entites = sorted(entites, key=lambda x: x[2][1])

    return entity_id2index_map, entites, relations


def pre_processing(abs_file_path, deid_pattern=None, word_level=True, replace_number=False):
    sent_tokenizer = SentenceBoundaryDetection()

    if replace_number and not word_level:
        logger.info("sentence level tokenization")
        return sent_tokenizer.sent_tokenizer(replace_number)

    if deid_pattern:
        sent_tokenizer.set_deid_pattern(deid_pattern)

    sent_tokenizer.set_input_file(abs_file_path)

    logger.info(f"word level tokenization with replace_number set to {replace_number}")

    return sent_tokenizer.sent_word_tokenization_and_mapping(replace_number)


def __remove_overlap_entity(sorted_entities):
    valid_en = []
    for idx, en in enumerate(sorted_entities):
        if idx == 0:
            valid_en.append(en)
            continue
        pre_en = sorted_entities[idx-1]
        c_s = en[2][0]
        c_e = en[2][1]
        p_s = pre_en[2][0]
        p_e = pre_en[2][1]
        if c_s > p_e:
            valid_en.append(en)
    return valid_en


def generate_BIO(sents, entities, file_id="", no_overlap=False, record_pos=False, tag_types=None,
                 exclude_tag_types=None):
    """
    assign annotation information to each token
    if two token have overlapped offsets, the second one will be discarded
    if define tag_types (iterable type), only the types in the tag_types list will be labeled to the corpus
    if define exclude_tag_types (iterable type), the tags will not be annotated
    """
    nsents = []
    if file_id:
        logger.info(f"process {file_id} file")

    entities = sorted(entities, key=lambda x: x[2][0])
     
    if tag_types:
        entities = list(filter(lambda x: x[1] in tag_types, entities))

    if exclude_tag_types:
        entities = list(filter(lambda x: x[1] not in exclude_tag_types, entities))

    if no_overlap:
        entities = __remove_overlap_entity(entities)

    entities_iter = iter(entities)
    entity = next(entities_iter, None)
    for i, sent in enumerate(sents):
        nsent = []
        for j, token in enumerate(sent):
            if record_pos:
                token.append((i, j))
            if not entity:
                token.append('O')
            else:
                # token: ('Admission', (0, 9), (0, 9))
                offset_start = token[1][0]
                offset_end = token[1][1]
                en_s = entity[2][0]
                en_e = entity[2][1]
                en_type = entity[1]
                if offset_start < en_s and offset_end < en_e:
                    token.append('O')
                elif offset_start == en_s:
                    token.append("-".join(['B', en_type]))
                    if offset_end >= en_e:
                        entity = next(entities_iter, None)
                elif offset_start > en_s and offset_end < en_e:
                    token.append("-".join(['I', en_type]))
                elif offset_start > en_s and offset_end == en_e:
                    token.append("-".join(['I', en_type]))
                    entity = next(entities_iter, None)
                else:
                    # check entity position and token position
                    logger.warning(f"{entity} offset is overlapped with previous entity; current tok not overlap")
                    entity = next(entities_iter, None)
                    if not entity:
                        token.append('O')
                        continue
                    if offset_start > en_e:
                        # logger.warning(f"{entity} offset is overlapped with previous entity; current tok not overlap")
                        # entity = next(entities_iter, None)
                        en_s = entity[2][0]
                        en_e = entity[2][1]
                        en_type = entity[1]
                        if offset_end <= en_s:
                            token.append('O')
                        else:
                            if offset_start == en_s:
                                token.append("-".join(['B', en_type]))
                                if offset_end >= en_e:
                                    entity = next(entities_iter, None)
                            else:
                                logger.error(f"{token}\t{entity} not matched by their offsets.")
                                token.append('O')
                                entity = next(entities_iter, None)
                    else:
                        # logger.warning(f"{entity} offset is overlapped with previous entity; current tok not overlap")
                        # entity = next(entities_iter, None)
                        en_s = entity[2][0]
                        en_e = entity[2][1]
                        en_type = entity[1]
                        if offset_start == en_s:
                            token.append("-".join(['B', en_type]))
                            if offset_end >= en_e:
                                entity = next(entities_iter, None)
                        elif offset_end < en_s:
                            token.append('O')
                        else:
                            logger.error(f"{token}\t{entity} not matched by their offsets.")
                            # token.append("-".join(['B', en_type]))
                            token.append('O')
                            entity = next(entities_iter, None)
            nsent.append(token)
        nsents.append(nsent)

    sent_bound_range = dict()  # key: sent id; value: boundary range
    for i, each in enumerate(nsents):
        try:
            sent_start_index = each[0][1][0]
            sent_end_index = each[-1][1][1]
            sent_bound_range[i] = (sent_start_index, sent_end_index)
        except Exception as ex:
            if i != len(nsents) - 1:
                raise RuntimeError(f'The {i}th sentence is an empty sentence')

    # if record_pos:
    #     nsents = [w for e in nsents for w in e]

    return nsents, sent_bound_range


def __flat(data, to_str=False):
    flatted = []

    for each in data:
        if isinstance(each, list) or isinstance(each, tuple):
            for e in each:
                flatted.append(e)
        else:
            flatted.append(each)

    if to_str:
        flatted = list(map(lambda x: str(x), flatted))

    return flatted


def BIOdata_to_file(file_name, sents, sep=" "):
    # the data must be list of list
    assert isinstance(sents, list), "the data object must be list and generated from generate_BIO()."
    with open(file_name, "w") as fw:
        # 'anticoagulant', (1000, 1013), (976, 989), 'B-Drug'
        for sent in sents:
            for word in sent:
                word = __flat(word, to_str=True)
                # word.append("\n")
                fw.write(sep.join(word)+"\n")
            fw.write("\n")


def load_mapping_file(mapping_file, sep=" "):
    with open(mapping_file, "r") as f:
        txt = f.read().strip()
        sents = txt.split("\n\n")
        nsents = []
        for sent in sents:
            words = sent.split("\n")
            for word in words:
                info = word.strip().split(sep)
                ninfo = list(map(lambda x: int(x) if x.isdigit() else x, info))
                nsents.append(ninfo)

        mapping_dict = {(each[-2], each[-1]): each for each in nsents}

    return nsents, mapping_dict


def __find_B_tag(word_seq, c_index):
    for k in range(c_index, -1, -1):
        c_tag = word_seq[k][-1].split("-")[0]
        if c_tag == 'B':
            return k
        elif c_tag == 'O':
            raise RuntimeError(f'check {word_seq[k]} since the label should be either I or B not O')
    raise RuntimeError("No B-tag has been labeled in the data.")


def window_sliding_sample_creation(bio_data, window_size):
    pass


def test():
    pass

if __name__ == '__main__':
    test()