# NLPpreprocessing
A comprehensive NLP preprocessing package for clinical notes sentence boundary detection, tokenization

## install
```sh
git clone https://github.com/uf-hobi-informatics-lab/NLPreprocessing
python -m pip install NLPreprocessing
```


## use after install
```python
from nlpreprcessing.annotation2BIO import pre_processing, generate_BIO
txt, sents = pre_processing("./test.txt")
generate_BIO(sents, [])


from nlpreprcessing.text_process.sentence_tokenization import SentenceBoundaryDetection
python -m pip install https://github.com/uf-hobi-informatics-lab/NLPreprocessing
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

## python version
> python-version>=3.6

## dev 
most new features are implemented in dev branch, we need to make comprehensive tests on the new features before merging to master
use at your own risk.
