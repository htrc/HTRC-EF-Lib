from collections import Counter
import requests
import logging

class WorkSet:
    def __init__(self, volume_list):
        self.volumes = [Volume(htid) for htid in volume_list]
        self._tokens = {}

    @property
    def tokens(self):
        if not self._tokens:
            for volume in self.volumes:
                for token in volume.tokens.keys():
                    try:
                        tok = self._tokens[token]
                    except KeyError:
                        self._tokens[token] = {"pos": Counter()}
                        tok = self._tokens[token]
                    tok["pos"].update(volume.tokens[token]['pos'])
        return self._tokens


class Volume:
    base_url = "https://tools.htrc.illinois.edu/ef-api/volumes"

    def __init__(self, htid):
        self.id = htid
        self._data = {}
        self._pages = []
        self._tokens = {}

    def __repr__(self):
        return f"{self.__class__.__name__}({self.id})"

    @property
    def data(self):
        if not self._data:
            url = "/".join((self.base_url, self.id))
            r = requests.get(url)
#            breakpoint()
            json = r.json()
            try:
                self._data = json["data"]
            except KeyError:
                logging.warning(r.json()['message'])
        return self._data

    @property
    def features(self):
        return self.data["features"]

    @property
    def pageCount(self):
        return self.features["pageCount"]

    @property
    def pages(self):
        if not self._pages:
            self._pages = [Page(page) for page in self.features["pages"]]
        return self._pages

    @property
    def tokens(self):
        if not self._tokens:
            for page in self.pages:
                for token in page.tokens.keys():
                    try:
                        tok = self._tokens[token]
                    except KeyError:
                        self._tokens[token] = {"pos": Counter()}
                        tok = self._tokens[token]
                    tok["pos"].update(page.tokens[token]["pos"])
        return self._tokens


class Page:
    def __init__(self, kwargs):
        self._kwargs = kwargs
        self._tokens = {}

    def __repr__(self):
        return f"{self.__class__.__name__}({self.seq})"

    @property
    def seq(self):
        return self._kwargs["seq"]

    @property
    def tokenCount(self):
        return self._kwargs["tokenCount"]

    @property
    def lineCount(self):
        return self._kwargs["lineCount"]

    @property
    def emptyLineCount(self):
        return self._kwargs["emptyLineCount"]

    @property
    def sentenceCount(self):
        return self._kwargs["sentenceCount"]

    @property
    def header(self):
        return self._kwargs["header"]

    @property
    def body(self):
        return self._kwargs["body"]

    @property
    def footer(self):
        return self._kwargs["footer"]

    @property
    def calculatedLanguage(self):
        return self._kwargs["calculatedLanguage"]

    # The following values are hoisted from the body section;
    # TODO make them the sum of values from header, body, and footer

    @property
    def capAlphaSeq(self):
        try:
            return self.body["capAlphaSeq"]
        except TypeError:
            return 0

    @property
    def beginCharCount(self):
        try:
            return self.body["beginCharCount"]
        except TypeError:
            return {}

    @property
    def endCharCount(self):
        try:
            return self.body["endCharCount"]
        except TypeError:
            return {}

    @property
    def tokenPosCount(self):
        try:
            return self.body["tokenPosCount"]
        except TypeError:
            return {}

    @property
    def tokens(self):
        if not self._tokens:
            for k in self.tokenPosCount.keys():
                token = k.lower()
                pos = list(self.tokenPosCount[k])[0]
                count = self.tokenPosCount[k][pos]
                try:
                    self._tokens[token]["pos"].update({pos: count})
                except KeyError:
                    self._tokens[token] = {"pos": Counter({pos: count})}
        return self._tokens

    @property
    def tokens_old(self):
        if not self._tokens:
            for k in self.tokenPosCount.keys():
                token = k.lower()
                pos = list(self.tokenPosCount[k])[0]
                count = self.tokenPosCount[k][pos]
                try:
                    self._tokens[token]["pos"][pos] = count
                except KeyError:
                    self._tokens[token] = {"pos": {pos: count}}
        return self._tokens


htid = "loc.ark+=13960=t46q23w14"
v = Volume(htid)
p = v.pages[0]

workset = [
    "uc1.32106011187561",
    "mdp.35112103187797",
    "uc1.$b684263"
]
