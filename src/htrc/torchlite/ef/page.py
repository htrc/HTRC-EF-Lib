import logging
from collections import Counter

import requests


class Page:
    def __init__(self, volume, seq):
        self._volume = volume
        self.seq = seq
        self._properties = {}
        self._tokens = {}

    @property
    def url(self):
        return f"{self._volume.url}/pages?seq={self.seq}"

    def get_property(self, property):
        if property not in self._properties:
            url = f"{self._volume.url}/pages?seq={self.seq}&fields=pages.{property}"
            r = requests.get(url)
            try:
                page_data = r.json()["data"]["pages"]
                self._properties[property] = [p[property] for p in page_data][0]

            except KeyError:
                logging.warning(r.json()["message"])
        return self._properties[property]

    @property
    def tokenCount(self):
        return self.get_property('tokenCount')

    @property
    def emptyLineCount(self):
        return self.get_property('emptyLineCount')

    @property
    def lineCount(self):
        return self.get_property('lineCount')

    @property
    def sentenceCount(self):
        return self.get_property('sentenceCount')

    @property
    def tokenPosCount(self):
        return self.get_property('body')['tokenPosCount']

    @property
    def tokens(self):
        if not self._tokens and self.tokenCount > 0:
            self._tokens = Counter()
            for k in self.tokenPosCount.keys():
                self._tokens[k.lower()] = 0
            for k, v in self.tokenPosCount.items():
                self._tokens[k.lower()] = sum(v.values())
        return self._tokens
