from urllib.parse import urlparse, urlunparse
import requests
from bs4 import BeautifulSoup

class URI:
    def __init__(self, parsed_uri):
        self.o = parsed_uri

class HTTP(URI):
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
    __metadata = None

    @property
    def _doi(self):
        return self.o.path

    @property
    def _metadata(self):
        if self.__metadata is None:
            res = requests.get(self.url,
                               headers={"Accept": "application/citeproc+json"})
            res.raise_for_status()
            self.__metadata = res.json()
        return self.__metadata

    @property
    def title(self):
        return self._metadata["title"]

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
