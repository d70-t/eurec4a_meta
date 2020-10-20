from urllib.parse import urlparse, urlunparse
import requests
from bs4 import BeautifulSoup
import crossref_commons.retrieval
import hashlib
import json

import os
if "XDG_CACHE_HOME" in os.environ:
    CACHE_HOME = os.environ["XDG_CACHE_HOME"]
else:
    CACHE_HOME = os.path.join(os.environ["HOME"], ".cache")

CACHEDIR = os.path.join(CACHE_HOME, "eurec4a_meta", "uri_meta")

class URI:
    kind = "unknown"
    def __init__(self, parsed_uri):
        self.o = parsed_uri

    def __repr__(self):
        return urlunparse(self.o)

class HTTP(URI):
    kind = "http"
    __soup = None

    @property
    def _soup(self):
        if self.__soup is None:
            res = requests.get(self.url)
            res.raise_for_status()
            self.__soup = BeautifulSoup(res.text, "html.parser")
        return self.__soup

    @property
    def title(self):
        return self._soup.head.title.get_text()

    @property
    def url(self):
        return urlunparse(self.o)

class DOI(URI):
    kind = "doi"
    __metadata = None

    @property
    def _doi(self):
        return self.o.path

    @property
    def _metadata(self):
        meta_hash = hashlib.sha256(("doi_meta+" + self._doi).encode("utf-8")).hexdigest()
        print(meta_hash)
        cache_file = os.path.join(CACHEDIR, meta_hash + ".json")
        if os.path.exists(cache_file):
            with open(cache_file) as cf:
                return json.load(cf)
        else:
            os.makedirs(CACHEDIR, exist_ok=True)
            res = crossref_commons.retrieval.get_publication_as_json(self._doi)
            with open(cache_file, "w") as cf:
                json.dump(res, cf)
            return res

    @property
    def title(self):
        return self._metadata["title"][0]

    @property
    def url(self):
        return "https://doi.org/{}".format(self._doi)


HANDLED_URIS = {
    "http": HTTP,
    "https": HTTP,
    "doi": DOI,
}

def parse_uri(uri):
    o = urlparse(uri)
    if o.scheme not in HANDLED_URIS:
        raise ValueError("unknown URI scheme {} in {}".format(o.scheme, uri))
    return HANDLED_URIS[o.scheme](o)
