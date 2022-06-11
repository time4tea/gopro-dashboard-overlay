# Compass

**Experimental**

The `compass-arrow` component draws a simple compass, with a needle pointing in the current direction

{{    <component type="compass-arrow" size="250" /> }}

## Positioning

Compass does not support `x` and `y` co-ordinates. Put `compass` inside a `translate` to move it around

{{
<translate x="50" y="50">
<component type="compass-arrow" size="250"/>
</translate>
}}

## Colours

Colours can be controlled with `bg`, `text`, `arrow`, `outline` and `arrow-outline` attributes

{{ <component type="compass-arrow" size="100" bg="128,128,128"/> }} {{ <component type="compass-arrow" size="100" text="128,128,128"/>
}} {{ <component type="compass-arrow" size="100" arrow="128,128,255"/> }} {{ <component type="compass-arrow" size="100" outline="128,128,255"/> }} {{ <component type="compass-arrow" size="100" arrow-outline="128,128,255"/> }}

## Fonts

Text size can be controlled with the `textsize` attribute

{{ <component type="compass-arrow" size="100" textsize="8"/> }}

{{ <component type="compass-arrow" size="100" textsize="32"/> }}

## Transparency

By default the `bg` is fully transparent, but like the `text` component, the transparency 
of the `bg` and `text` can be controlled with an alpha component in the colour.


{{
<component type="text" size="64" rgb="255,255,0">Hello</component>
<component type="compass-arrow" size="256" textsize="32"/>
}}

{{
<component type="text" size="64" rgb="255,255,0">Hello</component>
<component type="compass-arrow" size="256" textsize="32" bg="0,0,0,128"/>
}}

{{
<component type="text" size="64" rgb="255,255,0">Hello</component>
<component type="compass-arrow" size="256" textsize="32" bg="0,0,0,128" text="0,255,255,128"/>
}}
