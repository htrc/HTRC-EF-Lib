"""Object API to the Extracted Features API."""

__version__ = '0.1.0'

from collections import Counter
from urllib.parse import urlparse
import uuid
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
        return f"{self.__class__.__name__}({self.id})"

    @property
    def url(self):
        return "/".join((self.base_url, self.id))

    @property
    def data(self):
        """
        Fetches all data for the Volume.

        This can be expensive if the Volume is large,
        so most of the time one should use the individual
        field properties.
        """
        if not self._data:
            url = "/".join((self.base_url, self.id))
            r = requests.get(url)
            json = r.json()
            try:
                self._data = json["data"]
            except KeyError:
                logging.warning(r.json()["message"])
        return self._data

    def fetch_metadata(self, field):
        """Fetches metadata field via the EF API."""
        url = f"{self.url}/metadata?fields=metadata.{field}"
        r = requests.get(url)
        json = r.json()
        return json['data']['metadata'][field]

    def fetch_feature(self, field):
        """Fetches metadata field via the EF API."""
        url = f"{self.url}?fields=features.{field}"
        r = requests.get(url)
        json = r.json()
        return json['data']['features'][field]

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
            json = r.json()
            seq_nums = [page['seq'] for page in json['data']['pages']]
            self._pages = [Page(self, seq_num) for seq_num in seq_nums]
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


class WorkSet:
    def __init__(self, **kwargs):
        self.id = str(uuid.uuid1())
        self.type = None
        self.description = None
        self.created = None
        self.extent = None
        self.title = None
        self.visibility = None
        self.intent = None
        self.gathers = []
        self._volumes = {}
        self._tokens = {}

        if 'url' in kwargs:
            self.load_workset(kwargs['url'])

    def load_workset(self, url):
        try:
            r = requests.get(url)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)

        self._json = r.json()
        self.id = urlparse(url).path.split('/')[-1]
        # self.id = self._json['id']
        self.description = self._json['description']
        self.type = self._json['type']
        self.created = self._json['created']
        self.extent = self._json['extent']
        self.title = self._json['title']
        self.visibility = self._json['visibility']
        self.intent = self._json['intent']
        self.gathers = self._json['gathers']

    @property
    def metadata(self):
        return {
            "id": self.id,
            "description": self.description,
            "created": self.created,
            "extent": self.extent,
            "title": self.title,
            "visibility": self.visibility,
            "intent": self.intent,
        }

    @property
    def volumes(self):
        if not self._volumes:
            self._volumes = {}
            for gathered in self.gathers:
                v_id = urlparse(gathered['id']).path.split('/')[-1]
                self.add_volume(v_id)
        return self._volumes

    def add_volume(self, volume_id):
        self._volumes[volume_id] = Volume(volume_id)

    def get_volume(self, volume_id):
        return self.volumes[volume_id]

    def delete_volume(self, volume_id):
        del self.volumes[volume_id]
        return self.volumes

    @property
    def tokens(self):
        if not self._tokens:
            for volume in self.volumes.values():
                for token in volume.tokens.keys():
                    try:
                        tok = self._tokens[token]
                    except KeyError:
                        self._tokens[token] = {"pos": Counter()}
                        tok = self._tokens[token]
                    tok["pos"].update(volume.tokens[token]["pos"])
        return self._tokens


class Page:
    def __init__(self, volume, seq):
        self._volume = volume
        self.seq = seq
        self._properties = {}
        self._tokens = {}

    def get_property(self, property):
        if property not in self._properties:
            url = f"{self._volume.url}/pages?seq={self.seq}&fields=pages.{property}"
            r = requests.get(url)
            json = r.json()
            try:
                page_data = json["data"]["pages"]
                duff = [p[property] for p in page_data][0]
                self._properties[property] = duff

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
