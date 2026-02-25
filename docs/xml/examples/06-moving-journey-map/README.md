<!-- 

Auto Generated File DO NOT EDIT 

-->
<!-- Dimension(384,384) -->

# Moving Journey Map

This is a combination of the Moving Map and the Journey map. It shows the entire journey, but also moves - it doesn't currently rotate.

It renders the journey at a given zoom level, moving the map to fit the current location


```xml
<component type="moving_journey_map" size="256" />
```
<kbd>![06-moving-journey-map-0.png](06-moving-journey-map-0.png)</kbd>



## Sizing


```xml
<component type="moving_journey_map" size="128" />
```
<kbd>![06-moving-journey-map-1.png](06-moving-journey-map-1.png)</kbd>


```xml
<component type="moving_journey_map" size="384" />
```
<kbd>![06-moving-journey-map-2.png](06-moving-journey-map-2.png)</kbd>


## Zoom

The zoom can be set with `zoom` - Very high levels of zoom might not work reliably for long journeys, or may move too quickly on the video.


```xml
<component type="moving_journey_map" size="256" zoom="11" />
```
<kbd>![06-moving-journey-map-3.png](06-moving-journey-map-3.png)</kbd>


```xml
<component type="moving_journey_map" size="256" zoom="14" />
```
<kbd>![06-moving-journey-map-4.png](06-moving-journey-map-4.png)</kbd>


## Journey Path and Location Styling

Set `fill` and `line-width` to control the journey path style.


```xml
<component type="moving_journey_map" size="256" zoom="13" fill="255,255,0" line-width="3" />
```
<kbd>![06-moving-journey-map-5.png](06-moving-journey-map-5.png)</kbd>


Set `line-width` to `0` to hide the journey line completely.


```xml
<component type="moving_journey_map" size="256" zoom="13" line-width="0" loc-fill="255,0,255" loc-outline="255,255,255" loc-size="10" />
```
<kbd>![06-moving-journey-map-6.png](06-moving-journey-map-6.png)</kbd>


Set `loc-fill`, `loc-outline` and `loc-size` to control the current location marker style.


```xml
<component type="moving_journey_map" size="256" zoom="13" loc-fill="255,0,255" loc-outline="255,255,255" loc-size="10" />
```
<kbd>![06-moving-journey-map-7.png](06-moving-journey-map-7.png)</kbd>


All journey/map marker style options can be used together.


```xml
<component type="moving_journey_map" size="256" zoom="13" fill="0,255,0" line-width="7" loc-fill="255,0,255" loc-outline="255,255,255" loc-size="10" />
```
<kbd>![06-moving-journey-map-8.png](06-moving-journey-map-8.png)</kbd>


## Positioning, Transparency and Corners

The component should be placed in a `translate` to move it around the screen
To make the component rounded or transparent, it can be placed in a `frame`


```xml
<translate x="20" y="20">
    <frame width="256" height="256" outline="255,0,0" opacity="0.6" cr="128">
        <component type="moving_journey_map" name="moving_map" size="256" zoom="16"/>
    </frame>
</translate>
```
<kbd>![06-moving-journey-map-9.png](06-moving-journey-map-9.png)</kbd>


## Fade out

Corners can be faded out using parent frame's `fo` where you can specify how many pixels to use for the fade out.


```xml
<frame width="200" height="200" bg="255,255,255">
    <frame width="200" height="200" cr="50" fo="40">
      <component type="moving_journey_map" size="200"/>
    </frame>
</frame>
```
<kbd>![06-moving-journey-map-10.png](06-moving-journey-map-10.png)</kbd>

