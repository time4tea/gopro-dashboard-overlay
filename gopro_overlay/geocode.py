
import requests

from gopro_overlay.log import log


def geocode_location(lat, lon):

    url = f"https://geocode.xyz/{lat},{lon}?json=1&geojson=1"
    log(f"Calling: {url}")
    response = requests.get(url)
    response.raise_for_status()

    return response.json()



