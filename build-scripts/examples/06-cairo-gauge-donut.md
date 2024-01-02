
# Cairo Gauge Donut

_Requires Cairo to be installed_

Shows a gauge which is some sector of a donut..

Any supported metric or unit can be used

{{ <component type="cairo-gauge-donut" metric="speed" units="mph" /> }}

# Size

Use `size` to change the size.

# Max and Min Values

Use `max` and `min` to set maximum and minimum values.

{{ <component type="cairo-gauge-donut" metric="speed" units="mph"  /> }}

# Rotation and Length

The gauge by default starts at the bottom left, this can be changed using `start`, which is the number of degrees to rotate clockwise. The default `start` is 143.

{{ <component type="cairo-gauge-donut" metric="speed" units="mph"  start="270"/> }}

The gauge is normally 254 degrees "long". This can be changed using `length`

{{ <component type="cairo-gauge-donut" metric="speed" units="mph"  length="90" /> }}
{{ <component type="cairo-gauge-donut" metric="speed" units="mph"  length="180" /> }}

You can use -ve length to make the gauge draw anti-clockwise

{{ <component type="cairo-gauge-donut" metric="speed" units="mph"  length="-90" /> }}
{{ <component type="cairo-gauge-donut" metric="speed" units="mph"  length="-180" /> }}


# Number of Ticks / Sectors

There are 5 sectors by default. This can be changed with `sectors`

{{ <component type="cairo-gauge-donut" metric="speed" units="mph"  length="90" sectors="20" /> }}
{{ <component type="cairo-gauge-donut" metric="speed" units="mph"  length="180" sectors="6" /> }}

# Colours

Various colours can be set, either as RGB, or RGBA values.

The following are available to change: `background-inner-rgb`, `background-outer-rgb`, `major-ann-rgb`, `minor-ann-rgb`, `needle-rgb`, `major-tick-rgb`, `minor-tick-rgb`

{{ <component type="cairo-gauge-donut" metric="speed" units="mph"  background-inner-rgb="255,0,0"/> }}
{{ <component type="cairo-gauge-donut" metric="speed" units="mph"  background-outer-rgb="0,255,0"/> }}
{{ <component type="cairo-gauge-donut" metric="speed" units="mph"  major-ann-rgb="255,0,0"/> }}
{{ <component type="cairo-gauge-donut" metric="speed" units="mph"  minor-ann-rgb="255,0,0"/> }}
{{ <component type="cairo-gauge-donut" metric="speed" units="mph"  major-tick-rgb="255,0,0"/> }}
{{ <component type="cairo-gauge-donut" metric="speed" units="mph"  minor-tick-rgb="255,0,0"/> }}
{{ <component type="cairo-gauge-donut" metric="speed" units="mph"  needle-rgb="255,0,255"/> }}

# Transparency

Any colour that is completely transparent will disappear... this can be used to change the appearance of the widget quite a bit.

{{ <component type="cairo-gauge-donut" metric="speed" units="mph"  background-inner-rgb="255,0,0,0"/> }}
{{ <component type="cairo-gauge-donut" metric="speed" units="mph"  major-ann-rgb="255,0,0,0"/> }}
{{ <component type="cairo-gauge-donut" metric="speed" units="mph"  minor-ann-rgb="255,0,0,0"/> }}
{{ <component type="cairo-gauge-donut" metric="speed" units="mph"  major-tick-rgb="255,0,0,0"/> }}
{{ <component type="cairo-gauge-donut" metric="speed" units="mph"  minor-tick-rgb="255,0,0,0"/> }}
{{ <component type="cairo-gauge-donut" metric="speed" units="mph"  needle-rgb="255,0,255,40"/> }}

