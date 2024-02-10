<!-- Dimension(256,256) -->

# Cairo Gauge Marker

_Requires Cairo to be installed_

Shows a simple gauge, with a marker at the end, which gauges some metric.

Any supported metric or unit can be used

{{ <component type="cairo-gauge-marker" metric="speed" units="mph" /> }}

# Max and Min Values

Use `max` and `min` to set maximum and minimum values.

{{ <component type="cairo-gauge-marker" metric="speed" units="mph" max="3" /> }}

# Rotation and Length

The gauge by default starts at the right, this can be changed using `start`, which is the number of degrees to rotate clockwise

{{ <component type="cairo-gauge-marker" metric="speed" units="mph" max="3" start="90"/> }}

The gauge is normally 270 degrees "long". This can be changed using `length`

{{ <component type="cairo-gauge-marker" metric="speed" units="mph" max="3" length="90" /> }}
{{ <component type="cairo-gauge-marker" metric="speed" units="mph" max="3" length="180" /> }}

You can use -ve length to get the gauge to run anti-clockwise

{{ <component type="cairo-gauge-marker" metric="speed" units="mph" max="3" length="-90" /> }}
{{ <component type="cairo-gauge-marker" metric="speed" units="mph" max="3" length="-180" /> }}

# Number of Ticks / Sectors

There are 6 sectors by default. This can be changed with `sectors`

{{ <component type="cairo-gauge-marker" metric="speed" units="mph" max="3" length="90" sectors="2" /> }}
{{ <component type="cairo-gauge-marker" metric="speed" units="mph" max="3" length="180" sectors="3" /> }}

# Colours

Various colours can be set, either as RGB, or RGBA values.

The following are available to change: `tick-rgb`, `background-rgb`, `gauge-rgb`, `dot-outer-rgb`, `dot-inner-rgb`

Changing the tick-colour will change the background colour so to get the desired effect it may be worth specifying both.

{{ <component type="cairo-gauge-marker" metric="speed" units="mph" max="3" tick-rgb="255,0,0"/> }}
{{ <component type="cairo-gauge-marker" metric="speed" units="mph" max="3" background-rgb="255,0,0,100"/> }}
{{ <component type="cairo-gauge-marker" metric="speed" units="mph" max="3" gauge-rgb="255,0,0" /> }}
{{ <component type="cairo-gauge-marker" metric="speed" units="mph" max="3" dot-outer-rgb="255,0,0" /> }}
{{ <component type="cairo-gauge-marker" metric="speed" units="mph" max="3" dot-inner-rgb="255,0,0,128" /> }}

# Transparency

Any colour that is completely transparent will disappear... this can be used to change the appearance of the widget quite a bit.

{{ <component type="cairo-gauge-marker" metric="speed" units="mph" max="3" background-rgb="0,0,0,0"/> }}
{{ <component type="cairo-gauge-marker" metric="speed" units="mph" max="3" tick-rgb="0,0,0,0"/> }}
{{ <component type="cairo-gauge-marker" metric="speed" units="mph" max="3" gauge-rgb="0,0,0,0"/> }}
{{ <component type="cairo-gauge-marker" metric="speed" units="mph" max="3" dot-inner-rgb="0,0,0,0"/> }}
{{ <component type="cairo-gauge-marker" metric="speed" units="mph" max="3" dot-outer-rgb="0,0,0,0"/> }}
