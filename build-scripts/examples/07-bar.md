
# Bar

Draws a very simple horizontal bar with current metric value

{{ <component type="bar" metric="accl.x" units="m/s^2" /> }}


## Positioning

Place the bar component inside a `translate` to move it around

## Size

Use `width` and `height` to control the size of the component, in pixels

{{ <component type="bar" width="100" height="100" metric="speed" units="kph" /> }}

## Colours

Use `fill` and `outline` to change the fill and outline colours

Specify the colours, as usual, in r,g,b or r,g,b,a

{{ <component type="bar" metric="accl.x" units="m/s^2" fill="255,255,255,128" /> }}

{{ <component type="bar" metric="accl.x" units="m/s^2" outline="255,0,255" /> }}

To get rid of the outline completely, specify an alpha of `0`

{{ <component type="bar" metric="accl.x" units="m/s^2" outline="255,0,255,0" /> }}


## Drawing



