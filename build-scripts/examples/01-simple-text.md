
# Simple Text

The text to render is just the element contents

{{ <component type="text">Simple Text</component> }}

## Positioning

Use `x` and `y` to position text on the dashboard

{{ <component type="text" x="50" y="50">Simple Text</component> }}

## Colour

Use `rgb` to control the colour of the text 

{{ <component type="text" rgb="255,255,0">Simple Text</component> }}

## Size

Use `size` to control the font size.

{{ <component type="text" size="64">Simple Text</component> }}

## Alignment

Use `align` to align

{{ 
<composite>
  <component type="text" x="50" y="0" align="left">Left</component> 
  <component type="text" x="50" y="20" align="right">Right</component> 
</composite>
}}

More complex alignments are possible. See [full documentation](https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html)

## Direction

Use `direction` to change text direction. Right now, you need to specify `align` too. Here `lt` means "left-top"

{{ <component type="text" align="lt" direction="ttb">Vertical</component> }}

