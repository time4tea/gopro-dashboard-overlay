
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

{{ <component type="bar" metric="accl.y" units="m/s^2" fill="255,255,255,128" /> }}

{{ <component type="bar" metric="accl.y" units="m/s^2" outline="255,0,255" /> }}

To get rid of the outline completely, specify an alpha of `0`

{{ <component type="bar" metric="accl.y" units="m/s^2" outline="255,0,255,0" /> }}

Use `zero` to change the colour of the zero marker

{{ <component type="bar" metric="accl.y" units="m/s^2" zero="255,0,255" /> }}

Use `bar` to change the colour of the bar itself

{{ <component type="bar" metric="accl.y" units="m/s^2" bar="255,0,255" /> }}

Use `h-neg` and `h-pos` as rgba values to control the highlight colours of ends of the bar

{{ <component type="bar" metric="accl.y" units="m/s^2" h-neg="255,0,255" /> }}

{{ <component type="bar" metric="accl.y" units="m/s^2" h-pos="255,0,255" /> }}

## Outline Width

Use `outline-width` to control the width of the outline

{{ <component type="bar" metric="accl.y" units="m/s^2" outline-width="3" /> }}


## Max & Min Values

Use `max` and `min` to control the max and min values that the bar will display

{{ <component type="bar" metric="accl.y" units="m/s^2" max="5" min="-1" /> }}

{{ <component type="bar" metric="accl.y" units="m/s^2" max="10" min="0" /> }}


## Example Composite Bar Component

For example to plot acceleration values for all three axes

{{
    <composite>
        <translate y="0">
          <component type="bar" width="400" height="50" metric="accl.x"/>
          <component type="text" x="10" y="10" size="24" rgb="255,255,255">X Accl</component>
          <component type="metric" x="200" y="15" metric="accl.x" size="24" rgb="255,255,255" dp="2" align="centre" />
        </translate>
        <translate y="50">
            <component type="bar" width="400" height="50" metric="accl.y" />
            <component type="text" x="10" y="10" size="24" rgb="255,255,255">Y Accl</component>
            <component type="metric" x="200" y="15" metric="accl.y" size="24" rgb="255,255,255" dp="2"  align="centre"/>
        </translate>
        <translate y="100">
            <component type="bar" width="400" height="50" metric="accl.z" />
            <component type="text" x="10" y="10" size="24" rgb="255,255,255">Z Accl</component>
            <component type="metric" x="200" y="15" metric="accl.z" size="24" rgb="255,255,255" dp="2" align="centre"/>
        </translate>
    </composite>
}}
