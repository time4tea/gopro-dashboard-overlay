
# Chart

Chart draws a chart of some metric, with a configurable window before and after the current point.

The default metric is `alt`, with a default window of `5` minutes (2.5 mins around the current point in each direction)

{{ <component type="chart" name="chart" /> }}

The component used to be called 'gradient_chart', and type `gradient_chart` will still work, but is now deprecated and may be removed in 
a future version.


{{ <component type="gradient_chart" name="chart" /> }}


## Positioning

use `x` and `y` to set the position of the chart

{{ <component type="chart" name="gradient_chart" x="100" /> }}

# Window Size

Set the window size in seconds, defaults to 5*60 = `300`.

The chart is not currently terribly performant, so redrawing frequently ( smaller window )  will slow down rendering, but 
smaller windows have a bit more of a scroll effect, so look nicer.

{{ <component type="chart" metric="speed" units="kph" seconds="30" /> }}
{{ <component type="chart" metric="speed" units="kph" seconds="60" /> }}
{{ <component type="chart" metric="speed" units="kph" seconds="90" /> }}

# Metric & Units

Use any standard metric, with any standard unit. See [04-metrics](04-metrics.md) for more details

{{ <component type="chart" metric="speed" units="kph" /> }}

{{ <component type="chart" metric="accl.x" units="m/s^2" /> }}

## Colours / Sizing

These attributes are not currently configurable.
