import os
import re
try:
    from text_special_cases import SYMBOLS, PREP, DET, NON_STOP_PUNCT, STOP_PUNCT, SENT_WORD, UNIT, NAME_PREFIX_SUFFIX, PROFESSIONAL_TITLE, WHITE_LIST
except:
    from .text_special_cases import SYMBOLS, PREP, DET, NON_STOP_PUNCT, STOP_PUNCT, SENT_WORD, UNIT, NAME_PREFIX_SUFFIX, PROFESSIONAL_TITLE, WHITE_LIST    
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger('sentence_tokenization')
# logger.disabled = True


class SentenceBoundaryDetection:
    """
        This the python3 version of the sentence.py originally created by Dr. Wu
        The class is used to sentence-tokenize the raw text, especially for the clinical notes or EHRs
    """
    def __init__(self):
        # deid pattern is regex for de-identified information pattern (such in [**name**], the [** is the pattern)
        self.deid_pattern = None
        # using medical special rules
        self.special = False
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
        self.__white_list = WHITE_LIST
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
                    line = re.sub('[ ]{2,}', ' ', line).strip()
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

    def set_special_rules(self, param):
        self.special = param

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
                    if word in self.__prof_title:
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
                    if re.match("^[A-Z]{2,}[A-Z][a-z]+$", word) and not re.match("[A-Z]+[s|x|i]", word) and word not in self.__white_list and not word.startswith("Mc"):
                        logger.info(word)
                        rm = re.match("(^[A-Z]{2,})([A-Z][a-z]+$)", word)
                        w1, w2 = w1, w2 = rm.group(1), rm.group(2)
                        word_list.extend([w1, " ", w2, " "])
                        logger.warning(f"'{word}' => '{w1}' '{w2}'")
                        continue

                    # deal with name abbreviation like pattern: Xxxx X. Xxxx
                    if re.match("[A-Z]\\.", word):
                        if 0 < j < len(words)-1 and re.match("^[A-Z][a-z]+", words[j-1]) \
                                and re.match("^[A-Z][a-z]+", words[j+1]):
                            word_list.extend([word, " "])
                            continue
                    # ********* process special cases **********
                
                dot_pos = self.__dot_index(word)
                if dot_pos >= 0:
                    # if word in self.__special_abbv:
                    #     word_list.extend([word, " "])
                    if self.__num_dot(word) == 1:
                        if self.__is_stop_punct(word):
                            word_list.extend([word, "\n"])
                        elif dot_pos == 0:
                            word_list.extend([word, " "])
                        elif word[0: dot_pos] in self.__name_prefix_suffix:
                            # if it is Mr., Mrs., Dr. etc., should we keep the dot? remove dot for now
                            # word_list.extend([word[0: dot_pos], " . ", word[dot_pos+1:]])
                            word_list.extend([word[0: dot_pos+1], " ", word[dot_pos + 1:], " "])
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
                            elif re.match(f"^[0-9]+[.]?[0-9]*[{self.__units_re}]$", word):
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
                                m1 = re.match("^[0-9]+[.]?[0-9]*x[0-9]*", word)
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
                            # separate a.b to a . b for all cases?
                            lword_seg = lword.split(".")
                            nlword = []
                            for each in lword_seg:
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
                    elif re.match(f"^[0-9]+[{self.__units_re}]$", word):
                        num = re.match("^[0-9]+", word).group(0)
                        word_list.extend([num, " ", word.replace(num, ""), " "])
                    elif re.match("^[A-Za-z]*[0-9]+[A-Za-z]*$", word):
                        #match number with word then insert a space
                        rm = re.match('([A-Za-z]*)([0-9]+)([A-Za-z]*)', word)
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
                    elif re.match("[^A-Za-z0-9]|\?|!", cur_line_last_word_lower):
                        tokenized_text_lines.append("".join([tmp, ' ']))
                    elif f"{cur_line_last_word}." in self.__name_prefix_suffix or f"{cur_line_last_word}." in self.__prof_title:
                        tokenized_text_lines.append("".join([tmp, ' ']))
                    elif self.__is_num_list(word_list[0]):
                        if self.__is_num_list(next_line_first_word):
                            tokenized_text_lines.append("".join([tmp, '\n']))
                        else:
                            tokenized_text_lines.append("".join([tmp, ' ']))
                        # tokenized_text_lines.append("".join([tmp, ' ']))
                    else:
                        tokenized_text_lines.append("".join([tmp, '\n']))
            else:
                tokenized_text_lines.append("".join([tmp, '\n']))
                # tokenized_text_lines.append("".join([tmp, ' ']))

        return "".join(tokenized_text_lines)

    @staticmethod
    def __mapping(tokens, txt):
        offset_original = 0
        token_offsets = []
        for line in tokens:
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

    def sent_word_tokenization_and_mapping(self, txt=None, min_len=0, replace_number=False):
        normalized_txt = self.sent_tokenizer(txt=txt, min_len=min_len, replace_number=replace_number)
        tokens = list(map(lambda x: x.split(), normalized_txt.strip().split("\n")))

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


def test():
    sent_tokenizer = SentenceBoundaryDetection()
    sent_tokenizer.set_deid_pattern("\[\*\*|\*\*\]")

    text = '''
        Test: 
        1.  Lymphoplasmacytoid lymphoma involving bone marrow and spleen diagnosed  
        initially in [** Date **], associated with progressively increasing IgG kappa  
        paraprotein.  
        2.  Compression fractures of the spine secondary to lymphoma.  In the past,  
        it has been associated with significant back pain.  He is status post three  
        kyphoplasties.
        Test Again:
        should be in the same line 
    '''
    text1 = "INDUCTION TREATMENT\nSystemic chemotherapy :\nPREDNISOLONE 60 mg/m2 /day , oral or i.v. x 21 days ( 1 to "\
           "22 ) 30 mg/m2 /day , oral or i.v. x 7 days ( 23 to 29 )\nDAUNORUBICIN 30 mg/m2 , i.v. days 1 , 8 , " \
           "15 and 22\nVINCRISTINE 1 , 5 mg/m2 , i.v. days 1 , 8 , 15 and 22\nL-ASPARAGINASE 10.000U/m2 i.m or i.v " \
           "day 9 , 11 , 13 , 16 , 18 , 20 , 23 , 25 and 27\nCYCLOPHOSPHAMIDE 500 mg/m2 i.v. days 1 , " \
           "2 and 29\nIntrathecal chemotherapy :\nDays 1 and 22 according age :\nAge < 1 years 1-3 years > 3 " \
           "years\nMethotrexate ( MTX ) , mg 5 8 12 Ara-C , mg 16 20 30 Hydrocortisone , mg 10 10 20\nPatients with < "\
           "10% blasts in M.O ( day 14 ) , and in complete response on week 5 or 6 , and without MDR , " \
           "start consolidation-intensification phase.\nPatients with > 10% blasts in MO day +14 or without CR after " \
           "induction treatment , start consolidation-intensification phase and identifier a donor for a " \
           "transplantation.\nCONSOLIDATION/INTENSIFICATION ( C.I. )\nTwo sequential cycles , alternating bloc I and " \
           "bloc II\nBLOC I\nDEXAMETHASONE 10 mg/m2/d vo. days 1 to 5 and 5 mg/m2/d vo. days 6 and 7\nVINCRISTINE 1.5 "\
           "mg/m2/d , i.v. days 1 and 8\nMETHOTREXATE 5 g/m2 24 hours infusion + AF , day 1\nARA-C 1 g/m2/12 h , " \
           "i.v. , days 5 and 6\nMERCAPTOPURINE 100 mg/m2/d , oral , days 1 to 5\nCYCLOPHOSPHAMIDE 500 mg/m2 i.v. el " \
           "day +8\nINTRATHECAL CHEMOTHERAPY day 1.\nBLOC II\nDEXAMETHASONE 10 mg/m2/d , v o. days 1-5 and 5 mg/m2/d " \
           ", v o. days 6 and 7\nVINCRISTINE 1.5 mg/m2/d , days 1 and 8\nMETHOTREXATE 5 g/m2 24 h infusion + AF , " \
           "day 1\nARA-C 1 g/m2 i.v/12 h , days 5 and 6\nDAUNORUBICINE 30 mg/m2 i.v.day 1\nL-ASPARAGINASE 20.000 " \
           "u/m2/d , i.m. or i.v. day 7\nINTRATHECAL CHEMOTHERAPY day 1\nPatients with CR and MRD negative , " \
           "follow chemotherapy. Patients with MDR > 0.01% after second cycle or considered previously MRD are " \
           "candidates to allogenic transplantation after second cycle.\nREINDUCTION/INTENSIFICATION TREATMENT ( R.I. "\
           ")\nPREDNISOLONE 60 mg/m2/d , oral x 14 days ( 1-14 ) 30 mg/m2/d , oral x 7 days ( 15-22 )\nVINCRISTINE " \
           "1.5 mg/m2 , i.v. x 2 days 1 and 8\nDAUNORUBICINE 30 mg/m2 i.v x 2 , days 1 and 8\nCYCLOPHOSPHAMIDE 500 " \
           "mg/m2 I.V. day 15\n\nMETHOTREXATE 3 g/m2 /24 h infusion + AF day 29\nMERCAPTOPURINE 50 mg/m2/d , oral , " \
           "days 29-35 and 43-50\nARA-C 1 g/m2/12 h. , i.v. , days 43 and 44\nINTRATHECAL CHEMOTHERAPY , days 1 , " \
           "15 , 29 and 43\nMAINTENANACE TREATMENT ( M1 )\nSix cycles of :\nMERCAPTOPURINE 50 mg/m2/d , " \
           "oral x 21 days ( 1-21 )\nMETHOTREXATE 20 mg/m2/d , i.m. /week x 3 ( 1 , 7 , 14 )\nPREDNISOLONE 60 mg/m2/d "\
           ", oral x 7 days ( 22-28 )\nVINCRISTINE 1.5 mg/m2 i.v.day 22\nASPARAGINASE 20.000 u/m2 i.m. day " \
           "22\nINTRATHECAL CHEMOTHERAPY day 22\nMAINTENANCE TREATMENT ( M2 )\nDiary mercaptopurine and weekly " \
           "methotrexate at previous doses , until complete 24 months. "
    text2 = '''
        Patient: [** Name **], [** Name **]       Acct.#:     [** Medical_Record_Number **]       MR #:     [** Medical_Record_Number **]  
        D.O.B:   [** Date **]            Date of     [** Date **]        Location: [** Location **]  
                                       Visit:  
        Dictated [** Date **]  8:17 P    Transcribed [** Date **]  9:45  
        :                              :           P  
          
                                        CLINIC NOTE  
          
        DIAGNOSES:  
        1.  Lymphoplasmacytoid lymphoma involving bone marrow and spleen diagnosed  
        initially in [** Date **], associated with progressively increasing IgG kappa  
        paraprotein.  
        2.  Compression fractures of the spine secondary to lymphoma.  In the past,  
        it has been associated with significant back pain.  He is status post three  
        kyphoplasties.  The first in [** Date **] and two in [** Date **].  The first  
        procedure was complicated by acute hemoglobin decrease for which he was  
        hospitalized.  Hemorrhagic pericardial effusion was diagnosed and drained.  
        It was not malignant.  He received 5 units of red cells at that time.  
        2.  Extended hospitalization in [** Date **].  Then he was admitted for  
        significant back pain and then developed Salmonella sepsis with necrotizing  
        fasciitis of right gastrocnemius, which required debridement.  He had a  
        residual ulcer on the medial malleolus of the right ankle, which is now  
        fully healed.  He has required several hospitalizations for recurrent  
        cellulitis of right leg and most recently in [** Date **].  During the  
        prolonged hospitalization in [** Date **], he had respiratory arrest requiring  
        prolonged intubation and renal dialysis.  
        3.  Bilateral DVT with right leg DVT in [** Date **].  He finished 6-month  
        course of Coumadin after initially being treated with Lovenox.  
        4.  Psoriasis, which is quiescent.  
        5.  Hypertension.  
        6.  Hypothyroidism.  
        7.  Chronic renal insufficiency, which is multifactorial.  
          
        CURRENT THERAPY:  
        1.  He is on thalidomide 200 mg once daily for 2 weeks on and 2 weeks off.  
        He also takes prednisone 5 mg twice daily.  
        2.  Pamidronate 90 mg intravenously once a month.  
        3.  He has been on Velcade two weeks out of each month with reduced dosing  
        schedule of 1 mg/m2 once a week.  It was then discontinued secondary to  
        neuropathy.  It should be noted that did not respond to Velcade and  
        thalidomide.  
          
        PAST CHEMOTHERAPY:  
        1.  He has received 6 cycles of Rituxan plus CVP completed in [** Date **].  
        2.  Maintenance Rituxan completed in [** Date **].  
        3.  Revlimid, which was discontinued secondary to skin rash.  
        4.  Fludarabine in [** Date **], which rendered him profoundly  
        pancytopenic.  
          
        ADDITIONAL MEDICATIONS:  MS Contin 15 mg p.o. b.i.d., MSIR 30 mg every 4  
        hours for breakthrough pain.  Cartia XT, doxazosin, Protonix, Lasix,  
        Levoxyl, multivitamins and Neurontin 200 mg b.i.d.  He received his refills  
        for MS Contin and MSIR today.  
          
        INTERIM HISTORY:  Mr. [** Name **] returns for followup of his lymphoma.  He  
        recently sustained a fall secondary to slipping on ice.  He hurt his lower  
        back and has moderate, 4/10 back pain.  He is currently on MS Contin and  
        MSIR with relief of his symptoms.  He continues to have neuropathy from  
        Velcade, which is relieved with Neurontin 200 mg p.o. b.i.d.  He also has  
        constipation and is taking Colace 100 mg p.o. b.i.d. with relief of  
        symptoms.  
          
        He is also being followed by endocrinology for weight gain.  He has low  
        testosterone levels and has been started on replacement over the last 10  
        days.  
          
        REVIEW OF SYSTEMS:  He denies any history of fevers, night sweats, chills,  
        headache or visual blurring.  He denies any chest pain, cough, dyspnea,  
        orthopnea and no peripheral edema.  He denies any abdominal pain, nausea or  
        vomiting.  He has constipation.  He denies any episodes of diarrhea, bright  
        red blood per rectum or melena.  He has significant peripheral neuropathy  
        secondary to Velcade and is on Neurontin.  
          
        FAMILY HISTORY:  Acute leukemia in his father.  His father also had bladder  
        cancer.  He has one sibling who is not HLA match.  He has no family history  
        of lymphoma or multiple myeloma.  
          
        His ECOG performance status is 1, which is unchanged.  He is limited due to  
        back pain and cannot stand for prolonged periods of time.  He, however,  
        lives independently and is independent with all ADLs.  
          
        PHYSICAL EXAMINATION:  
        GENERAL:  He is alert and oriented x3.  
        VITAL SIGNS:  Stable.  Temperature 98.3, pulse 72, blood pressure 140/90,  
        respiratory rate 16 and weight is 117 kilograms.  No cervical,  
        supraclavicular or axillary lymphadenopathy.  
        LUNGS:  Clear to auscultation bilaterally.  
        CARDIOVASCULAR:  S1, S2 present, no murmurs.  
        ABDOMEN:  Soft, nontender and nondistended.  Good bowel sounds.  No  
        hepatosplenomegaly is palpable.  
        EXTREMITIES:  There is 2+ peripheral edema.  He is wearing compression  
        stocking on the right leg.  
        NEUROLOGICAL:  Nonfocal.  His gait is abnormal secondary to pain.  
          
        LABORATORY DATA:  WBC 3.7, hemoglobin 12.4, hematocrit 36.2, platelet count  
        is 143,000, BUN is 22, creatinine is 1.35, calcium is 9.4, kappa 328.39,  
        lambda light chain 1.46, ratio 224.92,  
        IgG 3580, which has increased from before.  
          
        ASSESSMENT AND PLAN:  Mr. [** Name **] is a 53-year-old male with  
        lymphoplasmacytoid lymphoma that is acting more like multiple myeloma and  
        affecting his bones.  His disease is currently stable.  He was better  
        controlled on Velcade, but developed significant peripheral neuropathy.  He  
        is getting better with Neurontin.  
          
        The patient is worried about losing his long-term disability.  He is unable  
        to stand for prolonged period of time and would like to return to work but  
        is unable to.  He will continue to receive Zometa once monthly.  He will  
        continue on thalidomide 100 mg once daily, 2 weeks on and 2 weeks off.  He  
        will also continue prednisone 5 mg twice daily.  
          
        He will follow up with Dr. [** Name **] at [** Hospital **].  He is  
        not a transplant candidate because his disease is minimally responsive to  
        chemotherapy.  He would be a good candidate for clinical trials.  
          
        He will follow up with us in 1 month.  
          
          
          
        I saw and evaluated the patient.  I discussed the case with the fellow and  
        agree with the findings and plan as documented in the fellow's note.  
          
        Reviewed  
        [** Name **] [** Name **], MD [** Date **] 16:26  
          
        E-Signed By  
        [** Name **] [** Name **] [** Name **], MD [** Date **] 18:49  
        ____________________________  
        [** Name **] [** Name **] [** Name **], MD  
          
        Patient evaluated by and note dictated by: [** Name **] [** Name **], MD  
          
        [** Medical_Record_Number **]  
          
        cc:    [** Name **] [** Name **], MD 
    '''

    text3 ='''
BLOOD PRESSURE 130/70PULSE 70WEIGHT 207 lbExam
       
    '''


    # print(sent_tokenizer.sent_tokenizer(text1))
    # print(sent_tokenizer.sent_tokenizer(text2))
    print(sent_tokenizer.sent_tokenizer(text3))


def test1():
    sent_tokenizer = SentenceBoundaryDetection()
    sent_tokenizer.set_deid_pattern("\[\*\*|\*\*\]")

    sent_tokenizer.set_input_file("../test/test_mimiciii_10/mimiciii_1.txt")
    print(sent_tokenizer.sent_word_tokenization_and_mapping())

def test2():
    # from file_utils.nlp_io import read_file
    # print(read_file('../../../2019amia_train/100-02.txt'))
    sent_tokenizer = SentenceBoundaryDetection()
    sent_tokenizer.set_deid_pattern(None)
    sent_tokenizer.special = True
    # sent_tokenizer.set_input_file("../../../2019amia_train/100-02.txt")
    # for each in sent_tokenizer.sent_word_tokenization_and_mapping():
    #     print(each)

    text3 = '''
M.D. (1) Chronic pancreatitis with multiple admissions   review. (2) Herniated disk.  (3)  Degenerative joint disease.  (4)  History of alcoholism.  (5)  Bipolar disorder.  (6)  Anxiety disorder.  (7) Normocytic anemia.
        '''

    print(sent_tokenizer.sent_tokenizer(text3))


if __name__ == '__main__':
    # test()
    # test1()
    test2()
