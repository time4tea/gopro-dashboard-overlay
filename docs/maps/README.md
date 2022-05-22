<!-- 

Auto Generated File DO NOT EDIT 

-->
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

# Style Examples

Here are examples of the various styles.

| .    | .            | . | . |
|------|--------------| --- | --- |
| ![osm](map_style_osm.png) | ![tf-cycle](map_style_tf-cycle.png) | ![tf-transport](map_style_tf-transport.png) | ![tf-landscape](map_style_tf-landscape.png) |
| ![tf-outdoors](map_style_tf-outdoors.png) | ![tf-transport-dark](map_style_tf-transport-dark.png) | ![tf-spinal-map](map_style_tf-spinal-map.png) | ![tf-pioneer](map_style_tf-pioneer.png) |
| ![tf-mobile-atlas](map_style_tf-mobile-atlas.png) | ![tf-neighbourhood](map_style_tf-neighbourhood.png) | ![tf-atlas](map_style_tf-atlas.png) | ![geo-osm-carto](map_style_geo-osm-carto.png) |
| ![geo-osm-bright](map_style_geo-osm-bright.png) | ![geo-osm-bright-grey](map_style_geo-osm-bright-grey.png) | ![geo-osm-bright-smooth](map_style_geo-osm-bright-smooth.png) | ![geo-klokantech-basic](map_style_geo-klokantech-basic.png) |
| ![geo-osm-liberty](map_style_geo-osm-liberty.png) | ![geo-maptiler-3d](map_style_geo-maptiler-3d.png) | ![geo-toner](map_style_geo-toner.png) | ![geo-toner-grey](map_style_geo-toner-grey.png) |
| ![geo-positron](map_style_geo-positron.png) | ![geo-positron-blue](map_style_geo-positron-blue.png) | ![geo-positron-red](map_style_geo-positron-red.png) | ![geo-dark-matter](map_style_geo-dark-matter.png) |
| ![geo-dark-matter-brown](map_style_geo-dark-matter-brown.png) | ![geo-dark-matter-dark-grey](map_style_geo-dark-matter-dark-grey.png) | ![geo-dark-matter-dark-purple](map_style_geo-dark-matter-dark-purple.png) | ![geo-dark-matter-purple-roads](map_style_geo-dark-matter-purple-roads.png) |
| ![geo-dark-matter-yellow-roads](map_style_geo-dark-matter-yellow-roads.png) |  |  |  |

## Attribution

Please ensure that you attribute the map correctly

### OpenStreetMap 
 © OpenStreetMap contributors
http://www.openstreetmap.org/copyright

### Thunderforest Map 
 Maps © Thunderforest
http://www.thunderforest.com/
Data © OpenStreetMap contributors
http://www.openstreetmap.org/copyright

### Geoapify Map 
 Maps © Geoapify
https://www.geoapify.com/
Data © OpenStreetMap contributors
http://www.openstreetmap.org/copyright