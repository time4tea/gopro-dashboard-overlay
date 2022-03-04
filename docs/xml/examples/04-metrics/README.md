<!-- 

Auto Generated File DO NOT EDIT 

-->
# Metrics

Metrics are fields that are extracted or derived from the GoPro or GPX data.

The metric component draws the value of a bit of data on the screen at the given co-ordinate.


```xml
<component type="metric" metric="speed" />
```
<kbd>![04-metrics-0.png](04-metrics-0.png)</kbd>


## Conversions

Every metric knows its units, and can be converted to another unit easily.  See [below](#supported-metrics) for the base unit 
for each metric.


```xml
<component type="metric" metric="speed" />
```
<kbd>![04-metrics-1.png](04-metrics-1.png)</kbd>


```xml
<component type="metric" metric="speed" units="kph" />
```
<kbd>![04-metrics-2.png](04-metrics-2.png)</kbd>


```xml
<component type="metric" metric="speed" units="mph" />
```
<kbd>![04-metrics-3.png](04-metrics-3.png)</kbd>


```xml
<component type="metric" metric="speed" units="knots" />
```
<kbd>![04-metrics-4.png](04-metrics-4.png)</kbd>


The following units are supported: `mph`, `kph`, `mps`, `knots`, `degreeF`, `degreeC`, `feet`, `miles`, `nautical_miles`, `radian`

Conversions that don't make sense for a given metric will fail with a suitable message.

## Lat & Lon

GPS Location is just another metric...

`cache="false"` is suggested for lat & lon metrics, as they will rarely repeat. By default text glyphs are cached, as they are
quite slow to render. This can be ignored really unless there are memory errors while rendering.


```xml
<component type="metric" metric="lat" dp="6" size="16" cache="false"/>
```
<kbd>![04-metrics-5.png](04-metrics-5.png)</kbd>



## Formatting

Either a number of decimal places, or a specific python formatting string can be used.


### Decimal Places

use the `dp` attribute


```xml
<component type="metric" metric="speed" dp="0" />
```
<kbd>![04-metrics-6.png](04-metrics-6.png)</kbd>


```xml
<component type="metric" metric="speed" dp="2" />
```
<kbd>![04-metrics-7.png](04-metrics-7.png)</kbd>


```xml
<component type="metric" metric="speed" dp="5" />
```
<kbd>![04-metrics-8.png](04-metrics-8.png)</kbd>


### Format string

Use the `format` attribute.


```xml
<component type="metric" metric="speed" format=".4f" />
```
<kbd>![04-metrics-9.png](04-metrics-9.png)</kbd>


## Positioning

The same positioning as in the [text](01-simple-text.md) component


```xml
<component type="metric" x="40" metric="speed" />
```
<kbd>![04-metrics-10.png](04-metrics-10.png)</kbd>


## Alignment

The same alignment as in the [text](01-simple-text.md) component


```xml
<component type="metric" x="40" metric="speed" align="right" />
```
<kbd>![04-metrics-11.png](04-metrics-11.png)</kbd>


## Colour

The same colour as in the [text](01-simple-text.md) component


```xml
<component type="metric" metric="speed" rgb="255,255,0" />
```
<kbd>![04-metrics-12.png](04-metrics-12.png)</kbd>


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
