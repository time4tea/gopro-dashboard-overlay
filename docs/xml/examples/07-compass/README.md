<!-- 

Auto Generated File DO NOT EDIT 

-->
# Compass

**Experimental**

The `compass` component draws a compass, rotated to the current heading.


```xml
<component type="compass" size="250" />
```
<kbd>![07-compass-0.png](07-compass-0.png)</kbd>


## Positioning

Compass does not support `x` and `y` co-ordinates. Put `compass` inside a `translate` to move it around


```xml
<translate x="50" y="50">
<component type="compass" size="250"/>
</translate>
```
<kbd>![07-compass-1.png](07-compass-1.png)</kbd>


## Colours

Colours can be controlled with `fg`, `bg` and `text` attributes


```xml
<component type="compass" size="100" fg="128,128,128"/>
```
<kbd>![07-compass-2.png](07-compass-2.png)</kbd>
 
```xml
<component type="compass" size="100" bg="128,128,128"/>
```
<kbd>![07-compass-3.png](07-compass-3.png)</kbd>
 
```xml
<component type="compass" size="100" text="128,128,255"/>
```
<kbd>![07-compass-4.png](07-compass-4.png)</kbd>


## Fonts

Text size can be controlled with the `textsize` attribute


```xml
<component type="compass" size="100" textsize="8"/>
```
<kbd>![07-compass-5.png](07-compass-5.png)</kbd>



```xml
<component type="compass" size="100" textsize="32"/>
```
<kbd>![07-compass-6.png](07-compass-6.png)</kbd>


## Transparency

By default the `bg` is fully transparent


```xml
<component type="text" size="64" rgb="255,255,0">Hello</component>
<component type="compass" size="256" textsize="32"/>
```
<kbd>![07-compass-7.png](07-compass-7.png)</kbd>



```xml
<component type="text" size="64" rgb="255,255,0">Hello</component>
<component type="compass" size="256" textsize="32" bg="0,0,0"/>
```
<kbd>![07-compass-8.png](07-compass-8.png)</kbd>


To make it partially transparent, use a `frame`, with `cr` (corner radius) set appropriately


```xml
<component type="text" size="64" rgb="255,255,0">Hello</component>
<frame width="256" height="256" opacity="0.3" cr="128">
<component type="compass" size="256" textsize="32" bg="0,0,0"/>
</frame>
```
<kbd>![07-compass-9.png](07-compass-9.png)</kbd>



