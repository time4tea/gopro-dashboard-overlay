
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

Smaller windows have a bit more of a scroll effect, so look nicer.

{{ <component type="chart" metric="speed" units="kph" seconds="30" /> }}
{{ <component type="chart" metric="speed" units="kph" seconds="60" /> }}
{{ <component type="chart" metric="speed" units="kph" seconds="90" /> }}

# Metric & Units

Use any standard metric, with any standard unit. See [04-metrics](../04-metrics) for more details

{{ <component type="chart" metric="speed" units="kph" /> }}
{{ <component type="chart" metric="accl.x" units="m/s^2" /> }}

# Max and Min Values

By default the chart will draw the max and min values in the window. This can be disabled with `values`

{{ <component type="chart" metric="speed" units="kph" /> }}
{{ <component type="chart" metric="speed" units="kph" values="false" /> }}

The current value could be overlaid with a `metric` somewhere over the chart if that was wanted

{{
            <component type="chart" name="chart" metric="speed" units="mph" fill="177,26,22" values="false"/>
            <translate x="230" y="40">
                <component type="metric" metric="speed" units="mph" dp="1"/>
            </translate>
}}

## Colours / Sizing

Set the height using `height`

{{ <component type="chart" height="100" /> }}

Set colours using `bg`, `fill`, `line` and `text`. These can be "r,g,b", or "r,g,b,a".

{{ <component type="chart" bg="255,255,0" fill="0,255,255" line="255,0,255" text="0,0,255" /> }}

Set alpha/transparency using `alpha`, between 0 and 255.

{{ <component type="chart" alpha="20" /> }}
{{ <component type="chart" alpha="200" /> }}
