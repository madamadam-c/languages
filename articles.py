import requests
from tqdm import tqdm
import json

LANGS = open("/home/david/Development/language/scripts/langs.txt", "r").read().split("\n")

for lang in tqdm(LANGS):
    file = f"./random_pages/{lang}.json"
    wp_api = f"https://{lang}.wikipedia.org/w/api.php"

    r = requests.get(
        wp_api,
        params={
            'action': 'query',
            'list': 'random',
            'format': 'json',
            'rnnamespace': 0,
            'rnlimit': 500,
        }
    ).json()

    json.dump(r, open(file, "w"), indent=4)
    