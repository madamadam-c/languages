import json
from typing import Dict
import json
import time
import math
from language_models import get_lang_models, get_reverse_mappings

PROB_EXP = 0.27
LENGTH_EXP = 0.09

MIN_NGRAM = 1
MAX_NGRAM = 4

LANGS = open("../scripts/langs.txt", "r").read().split("\n")

# language_models = get_lang_models()
reverse_mappings = get_reverse_mappings()

def gen_test_data():
    test_set = []

    for lang in LANGS:
        data = json.load(open(f"./excerpts/{lang}/extracts.json", "r"))
        extracts = [data[key]["extract"] for key in data.keys()]
        extracts = extracts[400:] # for test data

        test_set.extend([(lang, ex[:100]) for ex in extracts])

    json.dump(test_set, open("./excerpts/test_data.json", "w"), indent=4)

def test_data():
    return json.load(open("./excerpts/test_data.json", "r"))

def extract_ngrams(extract: str, min_ngram = MIN_NGRAM, max_ngram = MAX_NGRAM):
    ngrams = []

    for i in range(min_ngram, max_ngram + 1):
        for j in range(len(extract) - i + 1):
            ngrams.append(extract[j: j + i])
    
    return ngrams

def classify_extract(extract: str, min_ngram = MIN_NGRAM, max_ngram = MAX_NGRAM) -> str:
    ngrams = extract_ngrams(extract, min_ngram=min_ngram, max_ngram=max_ngram)
    
    lscore = {lang: 0 for lang in LANGS}
    for ngram in ngrams:
        # lmut = (len(ngram) ** LENGTH_EXP) # helmet
        mapping = reverse_mappings.get(ngram, {})
        for lang in mapping.keys():
            # lscore[lang] += (mapping[lang] ** PROB_EXP) * lmut
            lscore[lang] += mapping[lang] # precalculate weights

    return max(lscore.keys(), key=lambda x: lscore[x])

def score_model(min_ngram = MIN_NGRAM, max_ngram = MAX_NGRAM):
    data = test_data()
    correct = 0

    for lang, extract in data:
        guess = classify_extract(extract, min_ngram=min_ngram, max_ngram=max_ngram)
        if guess == lang:
            correct += 1
    
    return round(correct / len(data) * 100, 2)

# gen_test_data()
# d = test_data()

print(score_model(max_ngram=4))
# ng = extract_ngrams(d[0][1], max_ngram=1)
# print(ng)
# print(language_models[d[0][0]])