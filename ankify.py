import spacy
import os
import re
import shelve
import string
import argparse
import csv


model_name = 'de_core_news_sm'
nlp = spacy.load(model_name)

DICTS_DIR = './dicts/'
LISTS_DIR = './lists/'

vocab = shelve.open(DICTS_DIR + 'deu-eng')
top1k = {}
word_list = {}
long_vocab = {}


def write_csv(name, pairs):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_DIR + name, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='\t')
        for key in pairs.keys():
            writer.writerow([key, pairs[key]])


def count(dictionary):
    return len(dictionary.keys())


def create_long_vocab():
    for key in vocab.keys():
        ls = key.split()
        if len(ls) > 1:
            long_vocab[key] = vocab[key]


def strip_punct(str):
    return str.translate(str.maketrans('', '', string.punctuation)).strip()


def create_top1k_dict():
    with open(LISTS_DIR + 'top_1k_de.txt') as words:
        for word in words.readlines():
            word = word.strip()
            top1k[word] = vocab.get(word)


def translate_file(path, name):
    pairs = {}
    ff = open(path + name)
    data = ff.read()
    data = re.sub(r'\n|\d+|-', ' ', data)
    doc = nlp(data)
    pos_list = ['PUNCT', 'X', 'SPACE']
    unique = 0
    for token in doc:
        tt = token.text
        tl = token.lemma_
        if IGNORE_TOP_1000 and (top1k.get(tt) or top1k.get(tl)):
            continue
        if token.pos_ not in pos_list and (not word_list.get(token.text)):

            unique += 1
            word_list[token.text] = True
            if vocab.get(tt):
                pairs[tt] = vocab.get(tt)
            elif vocab.get(tl):
                pairs[tl] = vocab.get(tl)
            else:
                for key in long_vocab:
                    spl = key.split()
                    if tt in spl or tl in spl:
                        snt = strip_punct(token.sent.text)
                        snt2 = strip_punct(token.sent.lemma_)
                        if all([x in snt or x in snt2 for x in spl]):
                            pairs[key] = vocab.get(key)

    csv_name = name.replace(name.split('.')[-1], 'csv')
    write_csv(csv_name, pairs)
    print(name, '{} out of {}, {:.2%}'.format(
        count(pairs),
        unique,
        count(pairs) / unique))


parser = argparse.ArgumentParser()
parser.add_argument('--input', default='./input/')
parser.add_argument('--output', default='./output/')
parser.add_argument('--ignore_top', default=True, action='store_true')
args = parser.parse_args()

INPUT_DIR = args.input
OUTPUT_DIR = args.output
IGNORE_TOP_1000 = args.ignore_top

files = os.listdir(INPUT_DIR)
files.sort()

create_long_vocab()
if IGNORE_TOP_1000:
    create_top1k_dict()
    write_csv('top1k.csv', top1k)
for f in files:
    translate_file(INPUT_DIR, f)
