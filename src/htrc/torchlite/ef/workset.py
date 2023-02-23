from collections import Counter
import requests
import logging
from htrc.torchlite.ef.volume import Volume


class WorkSet:
    base_url = "https://tools.htrc.illinois.edu/ef-api/worksets"

    def __init__(self, htid):
        self.htid = htid
        self.volumes = []
        self._tokens = None

        try:
            r = requests.get(f"{self.base_url}/{htid}")
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)

        self._volume_ids = r.json()['data']['htids']
        self.volumes = [Volume(vid) for vid in self._volume_ids]

    @property
    def tokens(self):
        if not (self._tokens):
            url = f"{self.base_url}/{self.htid}/volumes?pos=false&fields=features.pages.body.tokensCount"
            try:
                r = requests.get(url)
                r.raise_for_status()
            except requests.exceptions.HTTPError as err:
                raise SystemExit(err)

            volume_data = r.json()['data']
            self._tokens = Counter()
            for volume in volume_data:
                for page in volume['features']['pages']:
                    cntr = Counter()
                    tokens = page['body']['tokensCount']
                    if tokens:
                        for k in tokens.keys():
                            cntr[k.lower()] = 0
                        for k, v in tokens.items():
                            cntr[k.lower()] += v
                        self._tokens.update(cntr)
        return self._tokens

    @property
    def titles(self):
        try:
            r = requests.get(
                f"{self.base_url}/{self.htid}/metadata?fields=htid,metadata.title"
            )
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)

        return r.json()['data']
