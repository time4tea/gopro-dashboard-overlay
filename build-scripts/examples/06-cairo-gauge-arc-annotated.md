
# Cairo Gauge Arc Annotated

_Requires Cairo to be installed_

Shows a round gauge, with a needle pointing to the current value of some metric. Additionally,
a sector of the display can show "high" and "low" values of some other metric, or a fixed range.

Any supported metric or unit can be used. The arc will only be drawn if a value or metric name is given for `arc-value-upper`.
If a metric name is given using `arc-metric-upper` then it will need to be convertible to the units of the gauge. The intended use for this,
is to allow (to be implemented) metric which is the moving average/max/min of a given metric.

The arc can be useful for target speed, cadence, power or altitude - using a value here for the lower and upper bound of the target range.

{{ <component type="cairo-gauge-arc-annotated" metric="speed" units="mph"
            arc-value-lower="15" arc-value-upper="25" /> 
}}

# Size

Use `size` to change the size.

# Max and Min Values

Use `max` and `min` to set maximum and minimum values.

{{ <component type="cairo-gauge-arc-annotated" metric="speed" units="mph" max="30" arc-value-upper="12" /> }}

# Rotation and Length

The gauge by default starts at the bottom left, this can be changed using `start`, which is the number of degrees to rotate clockwise. The default `start` is 143.

{{ <component type="cairo-gauge-arc-annotated" metric="speed" units="mph"  start="270" arc-value-upper="25"/> }}

The gauge is normally 254 degrees "long". This can be changed using `length`

{{ <component type="cairo-gauge-arc-annotated" metric="speed" units="mph"  length="90" arc-value-upper="25" /> }}
{{ <component type="cairo-gauge-arc-annotated" metric="speed" units="mph"  length="180" arc-value-upper="25" /> }}

# Number of Ticks / Sectors

There are 5 sectors by default. This can be changed with `sectors`

{{ <component type="cairo-gauge-arc-annotated" metric="speed" units="mph"  length="90" sectors="20" arc-value-upper="25" /> }}
{{ <component type="cairo-gauge-arc-annotated" metric="speed" units="mph"  length="180" sectors="6" arc-value-upper="25" /> }}

# Colours

Various colours can be set, either as RGB, or RGBA values.

The following are available to change: `background-rgb`, `major-ann-rgb`, `minor-ann-rgb`, `needle-rgb`, `major-tick-rgb`, `minor-tick-rgb`

{{ <component type="cairo-gauge-arc-annotated" metric="speed" units="mph"  background-rgb="255,0,0" arc-value-upper="25"/> }}
{{ <component type="cairo-gauge-arc-annotated" metric="speed" units="mph"  major-ann-rgb="255,0,0" arc-value-upper="25"/> }}
{{ <component type="cairo-gauge-arc-annotated" metric="speed" units="mph"  minor-ann-rgb="255,0,0" arc-value-upper="25"/> }}
{{ <component type="cairo-gauge-arc-annotated" metric="speed" units="mph"  major-tick-rgb="255,0,0" arc-value-upper="25"/> }}
{{ <component type="cairo-gauge-arc-annotated" metric="speed" units="mph"  minor-tick-rgb="255,0,0" arc-value-upper="25"/> }}
{{ <component type="cairo-gauge-arc-annotated" metric="speed" units="mph"  needle-rgb="255,0,255" arc-value-upper="25"/> }}

{{ <component type="cairo-gauge-arc-annotated" metric="speed" units="mph"  arc-inner-rgb="255,0,255,50" arc-outer-rgb="255,0,0,250" arc-value-upper="25"/> }}

# Transparency

Any colour that is completely transparent will disappear... this can be used to change the appearance of the widget quite a bit.

{{ <component type="cairo-gauge-arc-annotated" metric="speed" units="mph"  background-rgb="255,0,0,0" arc-value-upper="25"/> }}
{{ <component type="cairo-gauge-arc-annotated" metric="speed" units="mph"  major-ann-rgb="255,0,0,0" arc-value-upper="25"/> }}
{{ <component type="cairo-gauge-arc-annotated" metric="speed" units="mph"  minor-ann-rgb="255,0,0,0" arc-value-upper="25"/> }}
{{ <component type="cairo-gauge-arc-annotated" metric="speed" units="mph"  major-tick-rgb="255,0,0,0" arc-value-upper="25"/> }}
{{ <component type="cairo-gauge-arc-annotated" metric="speed" units="mph"  minor-tick-rgb="255,0,0,0" arc-value-upper="25"/> }}
{{ <component type="cairo-gauge-arc-annotated" metric="speed" units="mph"  needle-rgb="255,0,255,40" arc-value-upper="25"/> }}

