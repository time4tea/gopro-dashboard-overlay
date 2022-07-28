
# Frame

Frame is a __container__ and can contain other components.

The `frame` component will clip its children to the given frame size, and
draw them, optionally with an outline, rounding, background, and opacity into the dashboard.

Some examples might make this clearer.

The `outline` and `bg` parameters can also accept a "colour-with-alpha" (r,g,b,a) to allow a bit more
more control over the transparency of the various bits.

Use `fo` to have a nice fade-out effect at the edge of the frame.

{{
<component type="text" size="64">Background</component>
<frame width="100" height="100">
  <component type="text">Hello</component>
</frame>
}}

{{
<component type="text" size="64">Background</component>
<frame width="100" height="100" cr="50">
  <component type="text">Hello</component>
</frame>
}}

{{
<component type="text" size="64">Background</component>
<frame width="100" height="100" cr="50" bg="255,255,0" opacity="0.6">
  <component type="text">Hello</component>
</frame>
}}

{{
<component type="text" size="64">Background</component>
<frame width="100" height="100" cr="50" outline="255,0,0">
  <component type="text">Hello</component>
</frame>
}}

{{
<component type="text" size="64">Background</component>
<frame width="100" height="100" cr="50" outline="255,0,0">
  <component type="journey_map" size="100"/>
</frame>
}}


{{
<frame width="600" height="100" bg="255,255,255">
    <component type="text" size="64">Background</component>
    <frame width="100" height="100" cr="50" fo="20">
      <component type="journey_map" size="100"/>
    </frame>
</frame>
}}


{{
<frame width="200" height="200" bg="255,255,255">
    <component type="text" size="64">Background</component>
    <frame width="200" height="200" cr="10" fo="40" opacity="0.6">
      <component type="journey_map" size="200"/>
    </frame>
</frame>
}}

