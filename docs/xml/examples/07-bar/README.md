<!-- 

Auto Generated File DO NOT EDIT 

-->

# Bar

Draws a very simple horizontal bar with current metric value


```xml
<component type="bar" metric="accl.x" units="m/s^2" />
```
<kbd>![07-bar-0.png](07-bar-0.png)</kbd>



## Positioning

Place the bar component inside a `translate` to move it around

## Size

Use `width` and `height` to control the size of the component, in pixels


```xml
<component type="bar" width="100" height="100" metric="speed" units="kph" />
```
<kbd>![07-bar-1.png](07-bar-1.png)</kbd>


## Colours

Use `fill` and `outline` to change the fill and outline colours

Specify the colours, as usual, in r,g,b or r,g,b,a


```xml
<component type="bar" metric="accl.x" units="m/s^2" fill="255,255,255,128" />
```
<kbd>![07-bar-2.png](07-bar-2.png)</kbd>



```xml
<component type="bar" metric="accl.x" units="m/s^2" outline="255,0,255" />
```
<kbd>![07-bar-3.png](07-bar-3.png)</kbd>


To get rid of the outline completely, specify an alpha of `0`


```xml
<component type="bar" metric="accl.x" units="m/s^2" outline="255,0,255,0" />
```
<kbd>![07-bar-4.png](07-bar-4.png)</kbd>



## Drawing



