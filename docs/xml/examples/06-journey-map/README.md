<!-- 

Auto Generated File DO NOT EDIT 

-->
<!-- Dimension(256,256) -->

# Journey Map

Shows an 'overall' journey map, with the entire GPS trace shown over a map. The map is scaled appropriately to fit the
entire journey.


```xml
<component type="journey_map" size="256" />
```
<kbd>![06-journey-map-0.png](06-journey-map-0.png)</kbd>



## Sizing

Moving map is always the same width as its height, use `size` to set the size


```xml
<component type="journey_map" size="64" />
```
<kbd>![06-journey-map-1.png](06-journey-map-1.png)</kbd>


## Positioning

Use `x` and `y` to set the position on screen


```xml
<component type="journey_map" x="64" y="64" size="64" />
```
<kbd>![06-journey-map-2.png](06-journey-map-2.png)</kbd>


## Opacity

Set the opacity using `opacity`. It defaults to 1.0 which is completely opaque. 0.0 would be completely transparent.
The gopro video will be visible through the component, if it is not completely opaque.


```xml
<component type="journey_map" opacity="0.6" />
```
<kbd>![06-journey-map-3.png](06-journey-map-3.png)</kbd>


## Rounded Corners

Corners can be rounded with `corner_radius`.


```xml
<component type="journey_map" size="256" corner_radius="40" />
```
<kbd>![06-journey-map-4.png](06-journey-map-4.png)</kbd>


if `corner_radius` == half the width (ie. the radius) then the corners will be so rounded that the map becomes a circle


```xml
<component type="journey_map" size="256" corner_radius="128"/>
```
<kbd>![06-journey-map-5.png](06-journey-map-5.png)</kbd>


## Journey Path and Location Styling

Set `fill` and `line-width` to control the journey path style.


```xml
<component type="journey_map" size="256" fill="255,255,0" line-width="3" />
```
<kbd>![06-journey-map-6.png](06-journey-map-6.png)</kbd>


Set `line-width` to `0` to hide the journey line completely.


```xml
<component type="journey_map" size="256" line-width="0" loc-fill="255,0,255" loc-outline="255,255,255" loc-size="10" />
```
<kbd>![06-journey-map-7.png](06-journey-map-7.png)</kbd>


Set `loc-fill`, `loc-outline` and `loc-size` to control the current location marker style.


```xml
<component type="journey_map" size="256" loc-fill="255,0,255" loc-outline="255,255,255" loc-size="10" />
```
<kbd>![06-journey-map-8.png](06-journey-map-8.png)</kbd>


All journey/map marker style options can be used together.


```xml
<component type="journey_map" size="256" fill="0,255,0" line-width="7" loc-fill="255,0,255" loc-outline="255,255,255" loc-size="10" />
```
<kbd>![06-journey-map-9.png](06-journey-map-9.png)</kbd>


## Fade out

Corners can be faded out using parent frame's `fo` where you can specify how many pixels to use for the fade out.


```xml
<frame width="200" height="200" bg="255,255,255">
    <frame width="200" height="200" cr="50" fo="40">
      <component type="journey_map" size="200"/>
    </frame>
</frame>
```
<kbd>![06-journey-map-10.png](06-journey-map-10.png)</kbd>


## Copyright

All maps are © OpenStreetMap contributors

Please see Copyright https://www.openstreetmap.org/copyright



