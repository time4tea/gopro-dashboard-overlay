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


## Colours

The `pos_rgb`, `pos_size`, `path_rgb`, `path_size`, `wpt_rgb`, and `wpt_size` attributes can be used to set the colour and size/thickness of the current position, the path, and waypoints respectively.

The default values are blue/size 6 for the current position, red/size 4 for the path, and green/size 6 for waypoints.

```xml
<component type="moving_journey_map" zoom="15" pos_rgb="255,128,0" pos_size="12" path_rgb="0,128,0" path_width="2" wpt_rgb="0,0,0" wpt_size="20" />
```
<kbd>![06-moving-journey-map-7.png](06-moving-journey-map-7.png)</kbd>


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
<kbd>![06-moving-journey-map-5.png](06-moving-journey-map-5.png)</kbd>


## Fade out

Corners can be faded out using parent frame's `fo` where you can specify how many pixels to use for the fade out.


```xml
<frame width="200" height="200" bg="255,255,255">
    <frame width="200" height="200" cr="50" fo="40">
      <component type="moving_journey_map" size="200"/>
    </frame>
</frame>
```
<kbd>![06-moving-journey-map-6.png](06-moving-journey-map-6.png)</kbd>

