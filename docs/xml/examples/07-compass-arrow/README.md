<!-- 

Auto Generated File DO NOT EDIT 

-->
# Compass

**Experimental**

The `compass-arrow` component draws a simple compass, with a needle pointing in the current direction


```xml
<component type="compass-arrow" size="250" />
```
<kbd>![07-compass-arrow-0.png](07-compass-arrow-0.png)</kbd>


## Positioning

Compass does not support `x` and `y` co-ordinates. Put `compass` inside a `translate` to move it around


```xml
<translate x="50" y="50">
<component type="compass-arrow" size="250"/>
</translate>
```
<kbd>![07-compass-arrow-1.png](07-compass-arrow-1.png)</kbd>


## Colours

Colours can be controlled with `bg`, `text`, `arrow`, `outline` and `arrow-outline` attributes


```xml
<component type="compass-arrow" size="100" bg="128,128,128"/>
```
<kbd>![07-compass-arrow-2.png](07-compass-arrow-2.png)</kbd>
 
```xml
<component type="compass-arrow" size="100" text="128,128,128"/>
```
<kbd>![07-compass-arrow-3.png](07-compass-arrow-3.png)</kbd>
 
```xml
<component type="compass-arrow" size="100" arrow="128,128,255"/>
```
<kbd>![07-compass-arrow-4.png](07-compass-arrow-4.png)</kbd>
 
```xml
<component type="compass-arrow" size="100" outline="128,128,255"/>
```
<kbd>![07-compass-arrow-5.png](07-compass-arrow-5.png)</kbd>
 
```xml
<component type="compass-arrow" size="100" arrow-outline="128,128,255"/>
```
<kbd>![07-compass-arrow-6.png](07-compass-arrow-6.png)</kbd>


## Fonts

Text size can be controlled with the `textsize` attribute


```xml
<component type="compass-arrow" size="100" textsize="8"/>
```
<kbd>![07-compass-arrow-7.png](07-compass-arrow-7.png)</kbd>



```xml
<component type="compass-arrow" size="100" textsize="32"/>
```
<kbd>![07-compass-arrow-8.png](07-compass-arrow-8.png)</kbd>


## Transparency

By default the `bg` is fully transparent, but like the `text` component, the transparency 
of the `bg` and `text` can be controlled with an alpha component in the colour.



```xml
<component type="text" size="64" rgb="255,255,0">Hello</component>
<component type="compass-arrow" size="256" textsize="32"/>
```
<kbd>![07-compass-arrow-9.png](07-compass-arrow-9.png)</kbd>



```xml
<component type="text" size="64" rgb="255,255,0">Hello</component>
<component type="compass-arrow" size="256" textsize="32" bg="0,0,0,128"/>
```
<kbd>![07-compass-arrow-10.png](07-compass-arrow-10.png)</kbd>



```xml
<component type="text" size="64" rgb="255,255,0">Hello</component>
<component type="compass-arrow" size="256" textsize="32" bg="0,0,0,128" text="0,255,255,128"/>
```
<kbd>![07-compass-arrow-11.png](07-compass-arrow-11.png)</kbd>

