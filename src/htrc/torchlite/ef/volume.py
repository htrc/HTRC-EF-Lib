import logging
from collections import Counter

import requests

from htrc.torchlite.ef.page import Page


class Volume:
    base_url = "https://tools.htrc.illinois.edu/ef-api/volumes"

    def __init__(self, htid):
        self.htid = htid
        self._metadata = {}
        self._data = {}
        self._pages = []
        self._tokens = {}
        self._type = None
        self._date_created = None
        self._title = None
        self._contributor = None
        self._pub_date = None
        self._publisher = None
        self._pub_place = None
        self._language = None
        self._category = None
        self._genre = None

    def __repr__(self):
        return f"{self.__class__.__name__}({self.htid})"

    @property
    def url(self):
        return "/".join((self.base_url, self.htid))

    @property
    def metadata(self):
        if not self._metadata:
            r = requests.get(f"{self.url}/metadata")
            try:
                self._metadata = r.json()['data']['metadata']
            except KeyError:
                logging.warning(r.json()['message'])
        return self._metadata

    @property
    def data(self):
        """
        Fetches all data for the Volume.

        This can be expensive if the Volume is large,
        so most of the time one should use the individual
        field properties.
        """
        if not self._data:
            url = "/".join((self.base_url, self.htid))
            r = requests.get(url)
            try:
                self._data = r.json()["data"]
            except KeyError:
                logging.warning(r.json()["message"])
        return self._data

    def fetch_metadata(self, field):
        """Fetches metadata field via the EF API."""
        url = f"{self.url}/metadata?fields=metadata.{field}"
        r = requests.get(url)
        return r.json()['data']['metadata'][field]

    def fetch_feature(self, field):
        """Fetches metadata field via the EF API."""
        url = f"{self.url}?fields=features.{field}"
        r = requests.get(url)
        return r.json()['data']['features'][field]

    @property
    def title(self):
        if not self._title:
            self._title = self.fetch_metadata('title')
        return self._title

    @property
    def type(self):
        if not self._type:
            self._type = self.fetch_metadata('type')
        return self._type

    @property
    def pub_date(self):
        if not self._pub_date:
            self._pub_date = self.fetch_metadata('pubDate')
        return self._pub_date

    @property
    def publisher(self):
        if not self._publisher:
            self._publisher = self.fetch_metadata('publisher')
        return self._publisher

    @property
    def pub_place(self):
        if not self._pub_place:
            self._pub_place = self.fetch_metadata('pubPlace')
        return self._pub_place

    @property
    def language(self):
        if not self._language:
            self._language = self.fetch_metadata('language')
        return self._language

    @property
    def category(self):
        if not self._category:
            self._category = self.fetch_metadata('category')
        return self._category

    @property
    def genre(self):
        if not self._genre:
            self._genre = self.fetch_metadata('genre')
        return self._genre

    @property
    def contributor(self):
        if not self._contributor:
            self._contributor = self.fetch_metadata('contributor')
        return self._contributor

    @property
    def date_created(self):
        if not self._date_created:
            self._date_created = self.fetch_metadata('dateCreated')
        return self._date_created

    @property
    def page_count(self):
        if not self._date_created:
            self._date_created = self.fetch_feature('pageCount')
        return self._date_created

    @property
    def pages(self):
        if not self._pages:
            pages_url = f"{self.url}/pages?fields=pages.seq"
            r = requests.get(pages_url)
            seq_nums = [page['seq'] for page in r.json()['data']['pages']]
            self._pages = [Page(self, seq_num) for seq_num in seq_nums]
        return self._pages

    @property
    def tokens(self):
        if not self._tokens:
            url = f"{self.base_url}/{self.htid}/pages?pos=false&fields=pages.body.tokensCount"
            try:
                r = requests.get(url)
                r.raise_for_status()
            except requests.exceptions.HTTPError as err:
                raise SystemExit(err)
            self._tokens = Counter()
            for page in r.json()['data']['pages']:
                tokens = page['body']['tokensCount']
                if tokens:
                    cntr = Counter()
                    for k in tokens.keys():
                        cntr[k.lower()] = 0
                    for k, v in tokens.items():
                        cntr[k.lower()] += v
                    self._tokens.update(cntr)
        return self._tokens
