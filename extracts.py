import requests
from tqdm import tqdm
import json
import pathlib

LANGS = open("/home/david/Development/language/scripts/langs.txt", "r").read().split("\n")
LANGS = LANGS[10:]

for lang in tqdm(LANGS):
    articles = f"./random_pages/{lang}.json"
    wp_api = f"https://{lang}.wikipedia.org/w/api.php"

    path = pathlib.Path(f"./excerpts/{lang}")
    path.mkdir(exist_ok=True)

    data = json.load(open(articles, "r"))
    ids = [obj["id"] for obj in data["query"]["random"]]
    process = [ids[i: i + 20] for i in range(0, len(ids), 20)]

    reqs = {}

    for i, chunk in tqdm(enumerate(process)):
        response = requests.get(
            wp_api,
            params={
                'action': 'query',
                'format': 'json',
                'pageids': '|'.join([str(c) for c in chunk]),
                'prop': 'extracts',
                'exintro': True,
                'explaintext': True,
            }
        ).json()
        
        reqs.update(response["query"]["pages"])
        
    json.dump(reqs, open(path.joinpath("extracts.json"), "w"), indent=4)