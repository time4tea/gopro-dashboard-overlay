
import requests

from gopro_overlay.log import log


class GeoCode:

    def __init__(self, key=None):
        self.key = key

    def geocode_location(self, lat, lon):

        url = f"https://geocode.xyz/{lat},{lon}"

        params = {
            "json": 1,
            "geojson": 1
        }

        if self.key:
            params.update({"auth": self.key})

        log(f"Calling: {url}")
        response = requests.get(url=url, params=params)
        response.raise_for_status()

        return response.json()



