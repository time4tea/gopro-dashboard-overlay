# Compass

**Experimental**

The `compass` component draws a compass, rotated to the current heading.

{{    <component type="compass" size="250" /> }}

## Positioning

Compass does not support `x` and `y` co-ordinates. Put `compass` inside a `translate` to move it around

{{
<translate x="50" y="50">
<component type="compass" size="250"/>
</translate>
}}

## Colours

Colours can be controlled with `fg`, `bg` and `text` attributes

{{ <component type="compass" size="100" fg="128,128,128"/> }} {{ <component type="compass" size="100" bg="128,128,128"/>
}} {{ <component type="compass" size="100" text="128,128,255"/> }}

## Fonts

Text size can be controlled with the `textsize` attribute

{{ <component type="compass" size="100" textsize="8"/> }}

{{ <component type="compass" size="100" textsize="32"/> }}

## Transparency

By default the `bg` is fully transparent

{{
<component type="text" size="64" rgb="255,255,0">Hello</component>
<component type="compass" size="256" textsize="32"/>
}}

{{
<component type="text" size="64" rgb="255,255,0">Hello</component>
<component type="compass" size="256" textsize="32" bg="0,0,0"/>
}}

To make it partially transparent, use a `frame`, with `cr` (corner radius) set appropriately

{{
<component type="text" size="64" rgb="255,255,0">Hello</component>
<frame width="256" height="256" opacity="0.3" cr="128">
<component type="compass" size="256" textsize="32" bg="0,0,0"/>
</frame>
}}


