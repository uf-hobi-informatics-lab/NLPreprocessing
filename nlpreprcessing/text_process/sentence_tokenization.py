
import os
import re
import traceback
# import ftfy
import tqdm

try:
    from text_special_cases import (SYMBOLS, PREP, DET, NON_STOP_PUNCT, STOP_PUNCT,
                                    SENT_WORD, UNIT, NAME_PREFIX_SUFFIX, PROFESSIONAL_TITLE,
                                    WHITE_LIST, SPECIAL_ABBV, SPECIAL_UPPERCASE_WORD, BREAK_SYMBOLS)
except Exception as ex:
    from .text_special_cases import (SYMBOLS, PREP, DET, NON_STOP_PUNCT, STOP_PUNCT, SENT_WORD, UNIT,
                                     NAME_PREFIX_SUFFIX, PROFESSIONAL_TITLE, WHITE_LIST, SPECIAL_ABBV,
                                     SPECIAL_UPPERCASE_WORD, BREAK_SYMBOLS)
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger('sentence_tokenization')
# logger.disabled = True


def _only_dots(word):
    return re.match("^[.]{2,}$", word)


def _text_dots(word):
    m = re.search("[.]{2,}$", word)
    if m:
        return m.span()[0]
    else:
        return None


class SentenceBoundaryDetection:
    """
        This the python3 version of the sentence.py originally created by Dr. Wu
        The class is used to sentence-tokenize the raw text, especially for the clinical notes or EHRs
    """
    def __init__(self):
        # deid pattern is regex for de-identified information pattern (such in [**name**], the [** is the pattern)
        self.deid_pattern = None
        # using medical special rules
        self.special = True
        # the deid pattern replacement, if not set, using ""
        self.replace_pattern = ""
        self.input_file = None
        # self.__stop_symbol = {".", "\n"}
        # self.__stop_list = []
        self.raw_txt = None
        # constants init
        abs_path = os.path.abspath(__file__)
        abs_path = abs_path[:abs_path.rfind("/")]
        self.__abbr = self.__load_resource("/".join([abs_path, "resource/abbr.txt"]))
        self.__english = self.__load_resource("/".join([abs_path, "resource/word.txt"]))
        self.__abbr = self.__abbr - self.__english
        # these symbols will be seperated with words
        self.__sep_symbol = SYMBOLS
        # The prep and det are borrowed from Josh's perl edition.  These words are posiblely not a sentence boundary
        self.__prep = PREP
        self.__det = DET
        self.__non_stop_punct = NON_STOP_PUNCT
        self.__stop_punct = STOP_PUNCT
        self.__sentence_word = SENT_WORD
        self.__units = UNIT
        self.__units_re = "|".join(self.__units)
        self.__name_prefix_suffix = NAME_PREFIX_SUFFIX
        self.__prof_title = PROFESSIONAL_TITLE
        self.__special_abbv = SPECIAL_ABBV
        self.__white_list = WHITE_LIST
        self.__suw = SPECIAL_UPPERCASE_WORD
        self.__special_uppercase_words = "|".join(self.__suw)
        logger.info("sentence boundary detection class initiated.")

    @staticmethod
    def __load_resource(src_file):
        with open(src_file, "r") as f:
            src_cont = set(map(lambda x: x.strip().lower(), f.read().strip().split("\n")))
        return src_cont

    @staticmethod
    def __is_num_list(word):
        if re.match('\d+\.$', word):
        # if re.match('\d+\.$|^\d+\)$', word):
            return True
        return False

    @staticmethod
    def __dot_index(word):
        # Return the position of '.' in a word. -1 denote there are no '.' appeared
        if "." in word:
            return word.index(".")
        else:
            return -1

    @staticmethod
    def __num_dot(word):
        return len(re.findall("\\.", word))

    def __is_stop_punct(self, ch):
        return ch in self.__stop_punct

    @staticmethod
    def __is_digit(word):
        # Identify all numbers
        num_pattern = '[+-]?\d*[.]?\d+$'
        if re.match(num_pattern, word):
            return True
        return False

    def __is_punct(self, ch):
        return (ch in self.__stop_punct) or (ch in self.__non_stop_punct)

    @staticmethod
    def __clean_attached_TNM(intput_text):
<<<<<<< HEAD
        T_gen = "T[0-9]"
        T_candidates = "[p|c]?T[1-9|X](?:a|b|c)?[/]?(?:a|b|c)?"
        N_candidates = "p?N(?:0|1|X)"
        M_candidates = "p?M(?:0|1|X)"
=======
        T_gen = "T[0-9]{2,}"
        T_candidates = "[p|c]?T[1-9|X|o](?:a|b|c)?[/]?(?:a|b|c)?"
        N_candidates = "p?N(?:0|1|X|o)"
        M_candidates = "p?M(?:0|1|X|o)"
>>>>>>> 0c6fac8 (support pip install)
        pattern = re.compile("|".join([T_gen, T_candidates, N_candidates, M_candidates]), re.IGNORECASE)
        text = intput_text
        all_matched = re.findall(pattern, text)

        new_text = ""
        while all_matched:
            ww = all_matched.pop(0)
            idx = text.index(ww)
            ll = len(ww)
            ee = idx + ll
            new_text += text[:idx]
            new_text += f" {ww} "
            text = text[ee:]
        new_text += text

        return new_text

    @staticmethod
    def __return_last_non_space_word(words):
        for word in reversed(words):
            if word != " ":
                return word

    @staticmethod
    def __return_next_word_from_words_list(words, index):
        return words[index + 1] if index < len(words) - 1 else ""

    def __is_sep(self, c):
        return c == ' ' or c == '\n' or self.__is_punct(c)

    def __preprocessing(self, txt, replace_number):
        """
        :param txt: raw text for sentence tokenization
        :return: a list of pre-processed text pieces
        """
        try:
            if self.deid_pattern:
                txt = re.sub(self.deid_pattern, self.replace_pattern, txt)

            if replace_number:
                txt = re.sub("[0-9]", "0", txt)

            # clean TNM mention: T1aN0M0 => T1a N0 M0
            txt = self.__clean_attached_TNM(txt)
            
            # replace not UTF-8 char with " " 
            txt = re.sub("\x20| |\xc2|\xa0|\xb0", " ", txt)
            txt = re.sub(r'[^\x00-\x7F]+', ' ', txt)

            lines = map(lambda x: x.strip(), txt.strip().split("\n"))
            preprocessed_text_list = []

            for line in lines:
                if len(line) > 0:
                    line = re.sub('\t|_{4,}|-{4,}|\*{6,}|={4,}', ' ', line)
                    chs = []
                    for ch in line:
                        if ch in self.__sep_symbol:
                            chs.extend([' ', ch, ' '])
                        else:
                            chs.append(ch)
                    line = "".join(chs)
                    line = re.sub(' +', ' ', line).strip()
                    if len(line) > 0:
                        preprocessed_text_list.append(line)
            return preprocessed_text_list
        except Exception as ex:
            logger.error(ex)
            raise RuntimeError(f'No input text, check the input file {self.input_file} content.')

    def set_input_file(self, input_file):
        self.input_file = input_file

    def set_deid_pattern(self, deid_pattern, replace_pattern=" "):
        self.deid_pattern = deid_pattern
        self.replace_pattern = replace_pattern

    # def set_special_rules(self, param):
    #     self.special = param

    def sent_tokenizer(self, txt=None, min_len=0, replace_number=False):
        """
        The function uses a series rules to define how to detect the sentence boundary and split the text to sentences
        The current rules are suit for mimiciii data; change accordingly if apply to new clinical notes; some special
        text pieces are defined in text_special_cases.py; if necessary, add new sepcial cases and add to __init__ function
        :param txt: text input for sentence boundary detection
        :param min_len: minimum length of a sentence
        :param replace_number: flag to indicate whether all the numbers are replaced with 0
        :return: tokenized sentences
        """
        if not self.input_file and not txt:
            raise RuntimeError('Must provide a text input source for sentence tokenization, '
                               'specify a text file or text string.')

        if self.input_file and (not txt):
            logger.info(f"current processing {self.input_file} ...")
            with open(self.input_file, "r") as f:
                txt = f.read()
                self.raw_txt = txt

        text = self.__preprocessing(txt, replace_number)
        tokenized_text_lines = []

        for i, line in enumerate(text):
            words = line.split(" ")

            if min_len > 0 and len(words) <= min_len:
                line = "".join([line, "\n"])
                continue

            word_list = []
            for j, word in enumerate(words):
                if self.special:
                    # ********* process special cases **********
                    # keep M.D. or Ph.D. as it is
                    if word.lower() in self.__special_abbv:
                        word_list.extend([word, " "])
                        continue

                    if j + 1 < len(words):
                        # used to solve cases like "E. coli" or  "E. coli."
                        peek_next_word = words[j+1]
                        check_word = word + peek_next_word
                        if check_word.lower() in self.__special_abbv:
                            word_list.extend([word + " " + peek_next_word, " "])
                            words.pop(j+1)
                            continue
                        elif check_word[-1] == "." and check_word[:-1].lower() in self.__special_abbv:
                            word_list.extend([word + " " + peek_next_word[:-1], " ", ".", " "])
                            words.pop(j+1)
                            continue

                    if word in self.__units:
                        word_list.extend([word, " "])
                        continue

                    if word in self.__prof_title:
                        word_list.extend([word, " "])
                        continue

                    # need to figure out what this is for A1
                    if re.match("^[A-Za-z][1-9]$|[+][0-9]+$|[0-9]+[+]$", word):
                        word_list.extend([word, " "])
                        continue

                    # process two words without space in between like "HospitalEmergency" => "Hospital Emergency"
                    if re.match("^[A-Z]?[a-z]+[A-Z][a-z]+$", word) and word not in self.__units and word not in self.__white_list and not word.startswith("Mc"):
                        logger.info(word)
                        rm = re.match("(^[A-Z]?[a-z]+)([A-Z][a-z]+$)", word)
                        w1, w2 = rm.group(1), rm.group(2)
                        word_list.extend([w1, " ", w2, " "])
                        logger.warning(f"'{word}' => '{w1}' '{w2}'")
                        continue

                    # process a special merge words two case: XXXxx except case: XXX(s|x)
                    # rules
                    if re.match("^[A-Z]{2,}[A-Z][a-z]+$", word) and \
                            not re.match("[A-Z]+[s|x]", word) and \
                            word not in self.__white_list and \
                            not word.startswith("Mc"):
                        logger.info(word)
                        # case: upper case part has a special word like AUC
                        swc = re.search(f"^({self.__special_uppercase_words})", word)
                        # case: just random
                        rm = re.match("(^[A-Z]{2,})([A-Z][a-z]+$)", word)
                        if swc:
                            w1, w2 = w1, w2 = swc.group(1), word.replace(swc.group(1), "")
                            word_list.extend([w1, " ", w2, " "])
                            logger.warning(f"'{word}' => '{w1}' '{w2}'")
                        elif rm:
                            w1, w2 = w1, w2 = rm.group(1), rm.group(2)
                            word_list.extend([w1, " ", w2, " "])
                            logger.warning(f"'{word}' => '{w1}' '{w2}'")
                        continue

                    # process a special merge words reverse to the case above: xxxXX
                    # rules

                    # deal with name abbreviation like pattern: Xxxx X. Xxxx
                    if re.match("[A-Z]\\.", word):
                        if 0 < j < len(words)-1 and re.match("^[A-Z][a-z]+", words[j-1]) \
                                and re.match("^[A-Z][a-z]+", words[j+1]):
                            word_list.extend([word, " "])
                            continue
                    # ********* process special cases **********
                try:
                    dot_pos = self.__dot_index(word)
                    if dot_pos >= 0:
                        # handle "...+" case
                        if _only_dots(word):
                            word_list.extend([word, " "])
                            continue

                        # xxx.. => xxx .. => word = xxx; add .. back to words (words.insert(j+1, ..)
                        temp_i = _text_dots(word)
                        if temp_i is not None:
                            words.insert(j+1, word[temp_i:])
                            word = word[:temp_i]

                        if self.__num_dot(word) == 1:
                            if self.__is_stop_punct(word):
                                word_list.extend([word, "\n"])
                            elif dot_pos == 0:
                                word_list.extend([word, " "])
                            elif word[0: dot_pos] in self.__name_prefix_suffix:
                                # if it is Mr., Mrs., Dr. etc., should we keep the dot? remove dot for now
                                # word_list.extend([word[0: dot_pos], " . ", word[dot_pos+1:]])
                                w1 = word[0: dot_pos+1]
                                w2 = word[dot_pos+1: ]
                                if len(w2.strip()) > 0:
                                    word_list.extend([w1, " ", w2, " "])
                                else:
                                    word_list.extend([w1, " "])
                            elif dot_pos == len(word) - 1:
                                if self.__is_num_list(word):
                                    if j == 0:
                                        word_list.extend([word[:-1], " . "])
                                    # elif 0<j<len(words)-1:
                                    #     word_list.extend(["\n", word, " "])
                                    else:
                                        if word_list[-1][-1] == "\n":
                                            word_list.extend([word[:-1], " . "])
                                        else:
                                            word_list.extend([word[:-1], " ", ".\n"])
                                elif word[:-1].lower() not in self.__abbr and word.lower() not in self.__abbr:
                                    word_list.extend([word[:-1], " ", ".\n"])
                                else:
                                    next_word = self.__return_next_word_from_words_list(words, j)
                                    lword = word[:-1]
                                    if lword in self.__units:
                                        word_list.extend([lword, " ", ".\n"])
                                    # TODO this rule is ambiguous; consider a better way (e.g., St. Augestine)
                                    elif next_word and next_word[0].isupper():# and next_word.lower() not in self.__sentence_word:
                                        word_list.extend([lword, " ", ".\n"])
                                    else:
                                        word_list.extend([lword, " ", ".", " "])
                            else:
                                if re.match("^[0-9]+[.][0-9]+$", word):
                                    word_list.extend([word, " "])
                                elif re.match("^[A-Za-z]+", word):
                                    ntk1, ntk2 = word.split(".")
                                    word_list.extend([ntk1, " . ", ntk2, " "])
                                elif re.match("^[0-9]+[.][A-Za-z]", word):
                                    new_tokens = word.split(".")
                                    word_list.extend([" ".join([new_tokens[0], "."]), " "])
                                    word_list.extend([new_tokens[1], " "])
                                # handle number mix with text
                                elif re.match(f"^[0-9]+[.]?[0-9]*({self.__units_re})$", word):
                                    num = re.match("^[0-9]+[.]?[0-9]*", word).group(0)
                                    word_list.extend([num, " ", word.replace(num, ""), " "])
                                elif re.match("^[A-Za-z]*[0-9]+[.]?[0-9]*[A-Za-z]*$", word):
                                    # match number with word then insert a space
                                    rm = re.match('([A-Za-z]*)([0-9]+[.]?[0-9]*)([A-Za-z]*)', word)
                                    num_proc = []
                                    if rm.group(1):
                                        num_proc.append(rm.group(1))
                                        num_proc.append(" ")
                                    num_proc.append(rm.group(2))
                                    if rm.group(3):
                                        num_proc.append(" ")
                                        num_proc.append(rm.group(3))
                                    word_list.extend(num_proc)
                                    word_list.append(" ")
                                else:
                                    m = re.match("^[0-9]+[.][0-9]+", word)
                                    m1 = re.match("^[0-9]+[.]?[0-9]*x[0-9]*$", word)
                                    if m and word.replace(m.group(0), "") in self.__units:
                                        word_list.extend([m.group(0), " ", word.replace(m.group(0), ""), " "])
                                    elif m1:
                                        w1, w2 = word.split("x")
                                        word_list.extend([w1, " ", "x", " "])
                                        m = re.match("^[0-9]+[.]?[0-9]*", w2)
                                        if m:
                                            if w2.replace(m.group(0), "") in self.__units:
                                                word_list.extend([m.group(0), " ", w2.replace(m.group(0), ""), " "])
                                            else:
                                                word_list.extend([m.group(0), " "])
                                    else:
                                        logger.warning(f"'{word}' cannot be parsed by current rule.")
                                        word_list.extend([word, " "])
                        else:
                            if word[-1] == ".":
                                next_word = self.__return_next_word_from_words_list(words, j)
                                lword = word[:-1]
                                # TODO: separate a.b to a . b for all cases; how to handle a..b case
                                lword_seg = lword.split(".")
                                nlword = []
                                for each in lword_seg:
                                    if each == "":
                                        nlword.extend([each, ". "])
                                    else:
                                        nlword.extend([each, " . "])
                                nlword[-1] = " "
                                if self.__is_digit(lword):
                                    word_list.extend([lword, " ", ".\n"])
                                elif re.match('^\d*[.]?\d+[a-zA-Z]+$', lword) or \
                                        re.match('^\d{1,2}:\d{1,2}[a-zA-Z]+$', lword):
                                    ch_pos = 0
                                    while ch_pos < len(lword) and \
                                            (lword[ch_pos].isdigit() or lword[ch_pos] == "." or lword[ch_pos] == ":"):
                                        ch_pos += 1
                                    w1 = lword[:ch_pos]
                                    w2 = lword[ch_pos:]
                                    if w2 in self.__units:
                                        word_list.extend([w1, " ", w2, " ", ".\n"])
                                    elif len(next_word) > 0 and next_word[0].isupper():
                                        word_list.extend([lword, " ", ".\n"])
                                    else:
                                        word_list.extend([lword, " ", ".", " "])
                                elif len(next_word) > 0 and next_word[0].isupper() and \
                                        next_word.lower() in self.__sentence_word:
                                    # word_list.extend([lword, " ", ".\n"])
                                    word_list.extend(nlword + [".\n"])
                                else:
                                    # logger.warning(f"'{word}' cannot be parsed by current rule.")
                                    # word_list.extend([lword, " ", ".", " "])
                                    word_list.extend(nlword + [".", " "])
                            else:
                                # word_list.extend([word, " "])
                                if re.match("^[0-9]+[.][0-9]+x[0-9]+[.][0-9]+$", word):
                                    w1, w2 = word.split("x")
                                    word_list.extend([w1, " ", "x", " ", w2, " "])
                                else:
                                    # TODO: a.b  a...b  two cases
                                    word_seg = word.split(".")
                                    word = []
                                    for each in word_seg:
                                        word.append(each)
                                        word.append(" . ")
                                    word_list.extend(word[:-1])
                                    word_list.append(" ")
                    else:
                        if re.match("^x[0-9]+$", word):
                            word_list.extend(["x", " ", word[1:], " "])
                        elif re.match("^[0-9]+x[0-9]+$", word):
                            w1, w2 = word.split("x")
                            word_list.extend([w1, " ", "x", " ", w2, " "])
                        elif re.match(f"^[0-9]+({self.__units_re})$", word):
                            num = re.match("^[0-9]+", word).group(0)
                            word_list.extend([num, " ", word.replace(num, ""), " "])
                        # elif re.match("^[A-Za-z]+[0-9]+[A-Za-z]+$", word):
                        #     # match number with word then insert a space xx1xx => xx 1 xx HA1c
                        #     rm = re.match('([A-Za-z]*)([0-9]+)([A-Za-z]*)', word)
                        #     num_proc = []
                        #     if rm.group(1):
                        #         num_proc.append(rm.group(1))
                        #         num_proc.append(" ")
                        #     num_proc.append(rm.group(2))
                        #     if rm.group(3):
                        #         num_proc.append(" ")
                        #         num_proc.append(rm.group(3))
                        #     word_list.extend(num_proc)
                        #     word_list.append(" ")
                        else:
                            word_list.extend([word, " "])
                except Exception as ex:
                    logger.error("error at {}".format(word))
                    logger.error("{}".format(traceback.format_exc()))
                    word_list.extend([word, " "])

            # print(word_list)
            tmp = "".join(word_list).strip()
            if i < len(text) - 1:
                next_line = text[i+1]
                words = next_line.split(" ")
                len_next_line = len(words)
                next_line_first_word = words[0]
                cur_line_last_word = self.__return_last_non_space_word(word_list)
                cur_line_last_word_lower = cur_line_last_word.lower()
                if tmp[-1] == ".":
                    if cur_line_last_word[:-1] in self.__name_prefix_suffix:
                        tokenized_text_lines.append("".join([tmp, ' ']))
                    elif len(tmp) >= 2 and tmp[-2] != " " and not next_line_first_word == "-" and \
                            not next_line_first_word == "----" and not self.__is_num_list(next_line_first_word) and \
                            not next_line_first_word[0].isupper():
                        tokenized_text_lines.append("".join([tmp, ' ']))
                    else:
                        tokenized_text_lines.append("".join([tmp, '\n']))
                elif tmp[-1] == ":":
                    # if re.match("[0-9]+[.][ ]", next_line[:3]):
                    if self.__is_num_list(next_line_first_word):
                        tokenized_text_lines.append("".join([tmp, '\n']))
                    else:
                        tokenized_text_lines.append("".join([tmp, ' ']))
                # elif line[-1] != "." and line[-1] != ":":
                else:
                    if min_len > 0 and len_next_line <= min_len:
                        tokenized_text_lines.append("".join([tmp, '\n']))
                    elif cur_line_last_word_lower in self.__prep or cur_line_last_word_lower in self.__det or \
                            cur_line_last_word_lower in self.__non_stop_punct or cur_line_last_word_lower in self.__sentence_word:
                        tokenized_text_lines.append("".join([tmp, ' ']))
                    elif not next_line_first_word == "-" and not next_line_first_word == "----" and \
                            not self.__is_num_list(next_line_first_word) and not next_line_first_word[0].isupper():
                            # and not next_line_first_word.lower() in self.__english:
                        tokenized_text_lines.append("".join([tmp, ' ']))
                    elif f"{cur_line_last_word}." in self.__name_prefix_suffix or f"{cur_line_last_word}." in self.__prof_title:
                        tokenized_text_lines.append("".join([tmp, ' ']))
                    # elif self.__is_num_list(word_list[0]):
                    #     if self.__is_num_list(next_line_first_word):
                    #         tokenized_text_lines.append("".join([tmp, '\n']))
                    #     else:
                    #         tokenized_text_lines.append("".join([tmp, ' ']))
                    #     # tokenized_text_lines.append("".join([tmp, ' ']))
                    elif self.__is_num_list(next_line_first_word):
                        tokenized_text_lines.append("".join([tmp, '\n']))
                    elif cur_line_last_word_lower in self.__stop_punct:
                        tokenized_text_lines.append("".join([tmp, '\n']))
                    elif re.match("[^A-Za-z0-9]", cur_line_last_word_lower):
                        tokenized_text_lines.append("".join([tmp, ' ']))
                    else:
                        tokenized_text_lines.append("".join([tmp, ' ']))
            else:
                tokenized_text_lines.append("".join([tmp, '\n']))
                # tokenized_text_lines.append("".join([tmp, ' ']))

        return "".join(tokenized_text_lines)

    @staticmethod
    def __mapping(tokens, txt):
        offset_original = 0
        token_offsets = []
        for line in tqdm.tqdm(tokens, disable=True):
            token_offset = []
            for each in line:
                try:
                    index = txt.index(each)
                except ValueError as ex:
                    logger.error(f"the {each} cannot be find in original text.")
                    continue

                offset_original += index
                original_start = offset_original
                tk_len = len(each)
                new_pos = index + tk_len
                offset_original += tk_len
                original_end = offset_original
                txt = txt[new_pos:]
                token_offset.append((original_start, original_end))
            token_offsets.append(token_offset)
        return token_offsets

    def find_sep(self, tokens, idx):
        index = idx
        while index >= (idx//2):
            if tokens[index] in BREAK_SYMBOLS:
                break
            index -= 1

        return index+1

    def sent_word_tokenization_and_mapping(self, txt=None, min_len=0, replace_number=False, max_len=100):
        normalized_txt = self.sent_tokenizer(txt=txt, min_len=min_len, replace_number=replace_number)

        # limit sentence len to max_len words
        tokens = []
        normed_sents = normalized_txt.strip().split("\n")
        for sent in normed_sents:
            toks = sent.split(" ")
            ll = len(toks)
            if ll <= max_len:
                tokens.append(toks)
            elif max_len < ll <= 2*max_len:
                cut = self.find_sep(toks, ll//2)
                if len(toks[:cut]) > 0:
                    tokens.append(toks[:cut])
                if len(toks[cut:]) > 0:
                    tokens.append(toks[cut:])
            else:
                while ll > max_len:
                    cut = self.find_sep(toks, max_len-1)
                    tokens.append(toks[:cut])
                    toks = toks[cut:]
                    ll = len(toks)
                if len(toks) > 0:
                    tokens.append(toks)
        # tokens = list(map(lambda x: x.split(), normalized_txt.strip().split("\n")))

        if not txt:
            txt = self.raw_txt

        original_offsets = self.__mapping(tokens, txt)
        normalized_offsets = self.__mapping(tokens, normalized_txt)

        # each sent in sents is a list; each word in sent is (word, (original start; end), (new start; end))
        sents = []
        for line in zip(tokens, original_offsets, normalized_offsets):
            sent = []
            for each in zip(line[0], line[1], line[2]):
                sent.append(list(each))
            sents.append(sent)

        return normalized_txt, sents
