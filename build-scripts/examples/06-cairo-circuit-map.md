
# Cairo Circuit Map

_Requires Cairo to be installed_

Shows a simple plot of the path, but no map behind it...

{{ <component type="cairo_circuit_map" size="256" /> }}


# Colours

You can change the colours with

`fill`, `outline` for the path, and `loc_fill`, `loc_outline` for the "location" dot.

{{ <component type="cairo_circuit_map" size="256" fill="255,255,0" outline="255,0,255" /> }}


{{ <component type="cairo_circuit_map" size="256" loc_fill="255,255,0" loc_outline="255,0,255" /> }}


# Line width

You can change the line widths with `line_width` and `loc_size` - The numbers are relative to the size of the overall widget, so `1` 
means a line that is the whole width of the widget.

The map will be simplified to reduce the number of points as the line width increases.


{{ <component type="cairo_circuit_map" size="256" line_width="0.05" loc_size="0.05" /> }}

# Rotation

You can rotate the drawing with `rotate` and specify the clockwise rotation angle in degrees.

{{ <component type="cairo_circuit_map" size="256" rotate="45" /> }}
