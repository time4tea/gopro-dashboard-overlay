
# Icons

Icons are *square* images that can be placed anywhere. Custom icons must be in `RGB` or `RGBA` format.

## Built-In

Render an icon using the `icon` component

{{ <component type="icon" file="bicycle.png" /> }}

## Inverse

Right now, all icons have their colour scheme inverted by default. This is a bit odd, and will change... but to keep 
the icon's actual colour scheme, use `invert`.

(As the icon is black, you might not see this well in GitHub 'dark' mode ! )

{{ <component type="icon" file="bicycle.png" invert="false" /> }}


## Size

To rescale the icon use `size`

{{ <component type="icon" file="bicycle.png" invert="false" size="128"/> }}

*If `size` is 0, the icon will be rendered at its original size. This also allows for non-square icons to be rendered at their original aspect ratio.*

***Make sure `invert="false"` is used if you want to display the original icon.***

## Positioning

This component supports positioning with `x` and `y`.

{{ 
<component type="icon" x="0" y="0" file="bicycle.png"/> 
<component type="icon" x="30" y="30" file="mountain.png" invert="false"/> 
}}

## Bundled

Bundled icons are:

`bicycle.png` `car.png` `gauge-1.png` `gauge.png` `heartbeat.png` `ice-cream-van.png` `mountain.png` `mountain-range.png` `ruler.png` `slope.png` `slope-triangle.png` `speedometer-variant-tool-symbol.png` `thermometer-1.png`
`thermometer.png` `user.png` `van-black-side-view.png` `power.png`
