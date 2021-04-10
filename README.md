# Ankify
Translate movie/tv subtitles into csv dictonary in anki-compatible format. Currently supports only German -> English translation.

### Installing
Install spacy and requered language model.
```bash
pip install spacy
python -m spacy download de_core_news_sm
```
Download and format dictionary.
```bash
python create_dict.py
```

### Command Line Arguments
```
usage: ankify.py [--input INPUT_DIR] [--output OUTPUT_DIR] [--ignore_top]

optional arguments: 
	--input INPUT_DIR
  		Path to directory with subtitles. Defaults to "./input/"

	--output OUTPUT_DIR
  		Path to output directory. Defaults to "./output/"

	--ignore_top
		Ignore top 1000 words of the language. Defaults to True.
