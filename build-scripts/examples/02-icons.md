
# Icons

Icons are *square* images that can be placed anywhere.

## Built-In

Render an icon using the `icon` component

{{ <component type="icon" file="bicycle.png" /> }}

## Inverse

Right now, all icons have their colour scheme inverted by default. This is a bit odd, and will change... but to keep 
the icon's actual colour scheme, use `invert`.

{{ <component type="icon" file="bicycle.png" invert="false" /> }}


## Size

To rescale the icon use `size`

{{ <component type="icon" file="bicycle.png" invert="false" size="128"/> }}

## Positioning

This component supports positioning with `x` and `y`.

{{ 
<component type="icon" x="0" y="0" file="bicycle.png"/> 
<component type="icon" x="30" y="30" file="mountain.png" invert="false"/> 
}}

## Bundled

Bundled icons are:

`bicycle.png` `car.png` `gauge-1.png` `gauge.png` `heartbeat.png` `ice-cream-van.png` `mountain.png` `mountain-range.png` `ruler.png` `slope.png` `slope-triangle.png` `speedometer-variant-tool-symbol.png` `thermometer-1.png`
`thermometer.png` `user.png` `van-black-side-view.png`
