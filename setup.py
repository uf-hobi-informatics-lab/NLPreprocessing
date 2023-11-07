import setuptools

requires = "tqdm"


def get_requirements():
    ret = [x for x in requires.split("\n") if len(x) > 0]
    return ret


setuptools.setup(
    name="NLPreprocessing",
    version="1.0.1",
    description="NLP package for text preprocessing",
    url="https://github.com/uf-hobi-informatics-lab/NLPreprocessing",
    python_requires=">=3.6.0",
    install_requires=get_requirements(),
    packages=["nlpreprcessing"] + setuptools.find_packages("nlpreprcessing"),
    include_package_data=True,
    author="hobi",
)
