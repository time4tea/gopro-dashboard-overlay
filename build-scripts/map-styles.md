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