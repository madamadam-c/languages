import json
from collections import defaultdict
from typing import Dict
import json
import pathlib
import msgpack
import orjson
from collections import defaultdict

MIN_NGRAM = 1
MAX_NGRAM = 4

PROB_EXP = 0.27
LENGTH_EXP = 0.09

LANGS = open("../scripts/langs.txt", "r").read().split("\n")

def model_language(lang: str, min_ngram: int = MIN_NGRAM, max_ngram: int = MAX_NGRAM):
    data = json.load(open(f"./excerpts/{lang}/extracts.json", "r"))
    extracts = [data[key]["extract"] for key in data.keys()]
    extracts = extracts[:400] # for test data

    n_grams = {}

    for i in range(min_ngram, max_ngram + 1):
        n_grams[i] = defaultdict(int)

        for extract in extracts:
            for j in range(len(extract) - i + 1):
                ngram = extract[j: j + i]
                n_grams[i][ngram] += 1
    
    model_dir = pathlib.Path(f"./models/{lang}")
    model_dir.mkdir(exist_ok=True)

    json.dump(n_grams, open(model_dir.joinpath(f"model.json"), "w"), indent=4)

    return n_grams

def load_model(lang: str):
    model = json.load(open(f"./models/{lang}/model.json", "r"))
    keys = list(model.keys())

    for key in keys:
        model[int(key)] = model.pop(key)

    return model

def top_ngrams(model: Dict[int, Dict], min_ngram: int = MIN_NGRAM, max_ngram: int = MAX_NGRAM):
    top = {}
    
    for i in range(min_ngram, max_ngram + 1):
        top[i] = {
            key: model[i][key] 
            for key in sorted(model[i].keys(), key=lambda x: model[i][x], reverse=True)[:10]
        }
    
    return top

def reverse_mappings(min_ngram=MIN_NGRAM, max_ngram=MAX_NGRAM):
    rmap = {}
    lang_counts = {lang: defaultdict(int) for lang in LANGS}

    for lang in LANGS:
        data = json.load(open(f"./excerpts/{lang}/extracts.json", "r"))
        extracts = [data[key]["extract"] for key in data.keys()]
        extracts = extracts[:400] # for test data

        for i in range(min_ngram, max_ngram + 1):
            for extract in extracts:
                for j in range(len(extract) - i + 1):
                    lang_counts[lang][i] += 1

                    ngram = extract[j: j + i]
                    if rmap.get(ngram, None) == None:
                        rmap[ngram] = defaultdict(int)
                    rmap[ngram][lang] += 1
    
    for ngram in rmap.keys():
        l = len(ngram)
        lmut = l ** LENGTH_EXP

        for lang in rmap[ngram].keys():
            prob = rmap[ngram][lang] / lang_counts[lang][l]
            weight = (prob ** PROB_EXP) * lmut
            rmap[ngram][lang] = int(weight * 10_000_000)
    
    with open("./models/reverse_mapping.ojson", "wb") as f:
        f.write(orjson.dumps(rmap))
    # json.dump(rmap, open("./models/reverse_mapping.json", "w"), indent=4)
    # with open("./models/reverse_mapping.msgpack", "wb") as f:
    #     msgpack.pack(rmap, f, use_bin_type=True)

def get_lang_models():
    return {lang: load_model(lang) for lang in LANGS}

def get_reverse_mappings():
    # return json.load(open("./models/reverse_mapping.json", "r"))
    # rmap = msgpack.unpack(open("./models/reverse_mapping.msgpack", "rb"), raw=False)
    # for ngram in rmap.keys():
    #     for lang in rmap[ngram]:
    #         rmap[ngram][lang] = rmap[ngram][lang] / (10_000_000)
    rmap = orjson.loads(open("./models/reverse_mapping.ojson", "r").read())
    return rmap

reverse_mappings(max_ngram=4)

# lang_models = {lang: model_language(lang) for lang in LANGS}
# lang_models = {lang: load_model(lang) for lang in LANGS}
# print(top_ngrams(lang_models["en"]))

# print(top_ngrams(model_language("en", max_ngram=10), max_ngram=10))
