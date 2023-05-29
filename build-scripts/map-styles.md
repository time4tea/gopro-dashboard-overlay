# Map Styles

`gopro-dashboard.py` supports a number of map styles and providers.

The providers are:

- OSM/OpenStreetmap
- ThunderForest 
- Geoapify

# Selecting the Map Style

Use the command line option `--map-style` to choose the map style

Example:

`--map-style tf-cycle `

# API Keys

There are three ways that the API key can be supplied for the map. You'll need to sign up with the map provider.
The styles supported by the program all have free plans that are big enough to render a video. The program maintains a local
cache of the tiles.

### Command Line
API Keys can be provided on the command line, with `--api-key xxxxx`, 


### Totally Custom Map Tiles

Since v0.97.0

If you'd like to use a hand drawn map, or a scan of some printed map, or similar this can be done relatively straightforwardly.
To do this, get a high-resolution image of the map you'd like to use. It should be to scale... but the scale itself doesn't matter.

- Download the "maptiler engine" from https://www.maptiler.com/engine/download/
- Generate map tile locally, by opening the file, geolocating it, and exporting. Ensure to use *png* format.
- In a terminal window, go to the folder where the map tiles were exported, and run `python3 -mhttp.server`
- Use `--map-style local` when using `gopro-dashboard`
- You'll probably get a load of HTTP errors output, as this feature is experimental right now, but the video generation should work ok.

- See https://github.com/time4tea/gopro-dashboard-overlay/discussions/132 for more details.

### Configuration File

A file can be created `~/.gopro-graphics/map-api-keys.json`, which contains the api keys

Example

```json
{
        "thunderforest": "abcd1234",
        "geoapify": "1234abcd"
}
```

### Environment Variable

The environment will be searched for `API_KEY_<provider>`

Example:
`API_KEY_THUNDERFOREST=abcd1234`


# Style Examples

Here are examples of the various styles.

| .    | .            | . | . |
|------|--------------| --- | --- |
{{ table }}

## Attribution

Please ensure that you attribute the map correctly

{{ attribution }}