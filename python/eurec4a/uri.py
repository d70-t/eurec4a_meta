from urllib.parse import urlparse, urlunparse
import requests
from bs4 import BeautifulSoup
from PIL import Image
import crossref_commons.retrieval
import hashlib
import json
import io

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
        self.extra_attrs = {}

    def __repr__(self):
        return urlunparse(self.o)

    @property
    def title(self):
        if "title" in self.extra_attrs:
            return self.extra_attrs["title"]
        try:
            return self._title
        except AttributeError:
            return ""

    def to_link_object(self):
        return {
            **self.extra_attrs,
            "href": self.url,
            "title": self.title,
            "kind": self.kind,
        }

class HTTP(URI):
    kind = "http"
    __content = None

    @property
    def _content(self):
        if self.__content is None:
            res = requests.get(self.url)
            res.raise_for_status()
            self.__content = res.content
        return self.__content

    @property
    def _soup(self):
        try:
            return BeautifulSoup(self._content.decode("utf-8"), "html.parser")
        except:
            return None

    @property
    def _file_meta(self):
        return {
            "filesize": len(self._content),
        }

    @property
    def _image_meta(self):
        try:
            bio = io.BytesIO(self._content)
            img = Image.open(bio)
        except Exception as e:
            return {}
        else:
            return {
                "type": Image.MIME[img.format],
                "imagesize": list(img.size),
            }

    @property
    def _title(self):
        return self._soup.head.title.get_text()

    def to_link_object(self):
        return {
            **super(HTTP, self).to_link_object(),
            **self._file_meta,
            **self._image_meta,
        }

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
    def _title(self):
        return self._metadata["title"][0]

    @property
    def url(self):
        return "https://doi.org/{}".format(self._doi)

    def to_link_object(self):
        return {**super(DOI, self).to_link_object(), "doi": self._doi}


HANDLED_URIS = {
    "http": HTTP,
    "https": HTTP,
    "doi": DOI,
}

def parse_uri(uri):
    if isinstance(uri, dict):
        o = _parse_uri(uri["href"])
        o.extra_attrs.update({k: v for k, v in uri.items() if k != "href"})
    else:
        o = _parse_uri(uri)
    return o

def _parse_uri(uri):
    o = urlparse(uri)
    if o.scheme not in HANDLED_URIS:
        raise ValueError("unknown URI scheme {} in {}".format(o.scheme, uri))
    return HANDLED_URIS[o.scheme](o)
