
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
