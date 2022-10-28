# NLPpreprocessing
A comprehensive NLP preprocessing package for clinical notes sentence boundary detection, tokenization

## install
```
git clone https://github.com/uf-hobi-informatics-lab/NLPreprocessing
python -m pip install NLPreprocessing
```

## use after install
```
from nlpreprcessing.annotation2BIO import pre_processing, generate_BIO
txt, sents = pre_processing("./test.txt")
generate_BIO(sents, [])


from nlpreprcessing.text_process.sentence_tokenization import SentenceBoundaryDetection
processor = SentenceBoundaryDetection()
processor.sent_tokenizer("this is a test!")
```

## dev 
most new features are implemented in dev branch, we need to make a comprehensive tests on the new features before merge to master
use at your own risk
