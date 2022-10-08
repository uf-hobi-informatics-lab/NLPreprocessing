from annotation2BIO import generate_BIO
from text_process.sentence_tokenization import SentenceBoundaryDetection


def test():
    text = """below).A.  (0/3).F. PSA at diagnosis (7.57, 2/17) . ?pT3a ?N0 ?MX . ?G"""
    sent_tokenizer = SentenceBoundaryDetection()
    entities = [['pT3a', 'T3a', (33, 37)], ['N0 ', 'N0', (39, 42)], ['MX', 'MX', (43, 45)], ['no', 'Not_a_stage', (439, 441)]]
    _, sents = sent_tokenizer.sent_word_tokenization_and_mapping(text)
    print(sents)
    nsents, sent_bound = generate_BIO(sents, entities, no_overlap=False)
    print(nsents)


if __name__ == '__main__':
    test()