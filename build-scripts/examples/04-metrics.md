
# Metrics

Metrics are fields that are extracted or derived from the GoPro or GPX data.

The metric component draws the value of a bit of data on the screen at the given co-ordinate.

{{ <component type="metric" metric="speed" /> }}

## Conversions

Every metric knows its units, and can be converted to another unit easily.  See [below](#supported-metrics) for the base unit 
for each metric.

{{ <component type="metric" metric="speed" /> }}
{{ <component type="metric" metric="speed" units="kph" /> }}
{{ <component type="metric" metric="speed" units="mph" /> }}
{{ <component type="metric" metric="speed" units="knots" /> }}

The following units are supported: `mph`, `kph`, `mps`, `knots`, `degreeF`, `degreeC`, `feet`, `miles`, `nautical_miles`, `radian`

Conversions that don't make sense for a given metric will fail with a suitable message.

## Formatting

Either a number of decimal places, or a specific python formatting string can be used.


### Decimal Places

use the `dp` attribute

{{ <component type="metric" metric="speed" dp="0" /> }}
{{ <component type="metric" metric="speed" dp="2" /> }}
{{ <component type="metric" metric="speed" dp="5" /> }}

### Format string

Use the `format` attribute.

{{ <component type="metric" metric="speed" format=".4f" /> }}

## Positioning

The same positioning as in the [text](01-simple-text.md) component

{{ <component type="metric" x="40" metric="speed" /> }}

## Alignment

The same alignment as in the [text](01-simple-text.md) component

{{ <component type="metric" x="40" metric="speed" align="right" /> }}

## Colour

The same colour as in the [text](01-simple-text.md) component

{{ <component type="metric" metric="speed" rgb="255,255,0" /> }}

## Supported Metrics

The following metrics are supported:
`hr`, `cadence`, `speed`, `cspeed`, `temp`,
`gradient`, `alt`, `odo`, `dist`, `azi`, `lat`, `lon`,

| Metric   | Description                                                       | Unit                 |
|----------|-------------------------------------------------------------------|----------------------|
| hr       | Heart Rate                                                        | beats / minute       |
| cadence  | Cadence                                                           | revolutions / minute |
| speed    | Speed (as reported by device if available, or fallback to cspeed) | metres / second      |
| cspeed   | Computed Speed  (derived from location delta)                     | metres / second      |
| temp     | Ambient Temperature                                               | degrees C            |
| gradient | Gradient of Ascent                                                | -                    |
| alt      | Height above sea level                                            | metres               |
| odo      | Distance since start                                              | metres               |
| dist     | Distance since last point                                         | metres               |
| azi      | Azimuth                                                           | degree               |
| cog      | Course over Ground                                                | degree               |
| lat      | Latitude                                                          | -                    | 
| lon      | Longitude                                                         | -                    | 
