<!-- 

Auto Generated File DO NOT EDIT 

-->
# Zone Bar

Draws a simple horizontal bar with current metric value, with 4 zones - so suitable for
`hr`, `cadence`, `speed`, or `power`

Here we use `alt` as the sample data has a good value. Any metric can be used, and should be
converted to whatever unit you would like to display.



```xml
<component type="zone-bar"  metric="alt" units="feet" />
```
<kbd>![07-zone-bar-0.png](07-zone-bar-0.png)</kbd>



## Positioning

Place the bar component inside a `translate` to move it around

## Size

Use `width` and `height` to control the size of the component, in pixels


```xml
<component type="zone-bar" width="100" height="100" metric="alt" units="feet" />
```
<kbd>![07-zone-bar-1.png](07-zone-bar-1.png)</kbd>


## Colours

Use `fill` and `outline` to change the fill and outline colours

Specify the colours, as usual, in r,g,b or r,g,b,a


```xml
<component type="zone-bar" metric="alt" units="feet" fill="255,255,255,128" />
```
<kbd>![07-zone-bar-2.png](07-zone-bar-2.png)</kbd>



```xml
<component type="zone-bar" metric="alt" units="feet" outline="255,0,255" />
```
<kbd>![07-zone-bar-3.png](07-zone-bar-3.png)</kbd>


To get rid of the outline completely, specify an alpha of `0`


```xml
<component type="zone-bar" metric="alt" units="feet" outline="255,0,255,0" />
```
<kbd>![07-zone-bar-4.png](07-zone-bar-4.png)</kbd>


Use `divider` to change the colour of the zone dividers


```xml
<component type="zone-bar" metric="alt" units="feet" marker="255,0,255" />
```
<kbd>![07-zone-bar-5.png](07-zone-bar-5.png)</kbd>


## Outline Width

Use `outline-width` to control the width of the outline


```xml
<component type="zone-bar" metric="alt" units="feet" outline-width="3" />
```
<kbd>![07-zone-bar-6.png](07-zone-bar-6.png)</kbd>



## Max & Min Values

Use `max` and `min` to control the max and min values that the bar will display. The default `min` is 0.


```xml
<component type="zone-bar" metric="alt" units="feet" max="500" />
```
<kbd>![07-zone-bar-7.png](07-zone-bar-7.png)</kbd>



```xml
<component type="zone-bar" metric="alt" units="feet" max="500" min="0" />
```
<kbd>![07-zone-bar-8.png](07-zone-bar-8.png)</kbd>


## Setting Zones

Use `z1`, `z2`, and `z3` to set the start value of each of the zones. There is an implied
zone-0 which lies between `min` and `z1`.


```xml
<component type="zone-bar" metric="alt" units="feet" max="50" z1="10" z2="20" z3="30" />
```
<kbd>![07-zone-bar-9.png](07-zone-bar-9.png)</kbd>


## Setting Colours

Use `z0-col`, `z1-col`, `z2-col`, and `z3-col` to control the colours of the various zones. The colours will 
be used to create a lineir gradient. Like all colours, either `r,g,b`, or `r,g,b,a` can be used. Currently, all must be specified
in the same format - you'll likely get an error mixing and matching colours with and without alpha.


```xml
<component type="zone-bar" metric="alt" units="feet" max="50" z1="10" z2="20" z3="30" z0-col="255,255,255" z1-col="255,0,0" z2-col="0,255,0" z3-col="0,0,255" />
```
<kbd>![07-zone-bar-10.png](07-zone-bar-10.png)</kbd>




