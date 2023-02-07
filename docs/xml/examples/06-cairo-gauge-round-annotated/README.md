<!-- 

Auto Generated File DO NOT EDIT 

-->

# Cairo Gauge Round Annotated

_Requires Cairo to be installed_

Shows a gauge like a car speedometer, which gauges some metric.

Any supported metric or unit can be used


```xml
<component type="cairo-gauge-round-annotated" metric="speed" units="mph" />
```
<kbd>![06-cairo-gauge-round-annotated-0.png](06-cairo-gauge-round-annotated-0.png)</kbd>


# Size

Use `size` to change the size.

# Max and Min Values

Use `max` and `min` to set maximum and minimum values.


```xml
<component type="cairo-gauge-round-annotated" metric="speed" units="mph"  />
```
<kbd>![06-cairo-gauge-round-annotated-1.png](06-cairo-gauge-round-annotated-1.png)</kbd>


# Rotation and Length

The gauge by default starts at the bottom left, this can be changed using `start`, which is the number of degrees to rotate clockwise. The default `start` is 143.


```xml
<component type="cairo-gauge-round-annotated" metric="speed" units="mph"  start="270"/>
```
<kbd>![06-cairo-gauge-round-annotated-2.png](06-cairo-gauge-round-annotated-2.png)</kbd>


The gauge is normally 254 degrees "long". This can be changed using `length`


```xml
<component type="cairo-gauge-round-annotated" metric="speed" units="mph"  length="90" />
```
<kbd>![06-cairo-gauge-round-annotated-3.png](06-cairo-gauge-round-annotated-3.png)</kbd>


```xml
<component type="cairo-gauge-round-annotated" metric="speed" units="mph"  length="180" />
```
<kbd>![06-cairo-gauge-round-annotated-4.png](06-cairo-gauge-round-annotated-4.png)</kbd>


# Number of Ticks / Sectors

There are 5 sectors by default. This can be changed with `sectors`


```xml
<component type="cairo-gauge-round-annotated" metric="speed" units="mph"  length="90" sectors="20" />
```
<kbd>![06-cairo-gauge-round-annotated-5.png](06-cairo-gauge-round-annotated-5.png)</kbd>


```xml
<component type="cairo-gauge-round-annotated" metric="speed" units="mph"  length="180" sectors="6" />
```
<kbd>![06-cairo-gauge-round-annotated-6.png](06-cairo-gauge-round-annotated-6.png)</kbd>


# Colours

Various colours can be set, either as RGB, or RGBA values.

The following are available to change: `background-rgb`, `major-ann-rgb`, `minor-ann-rgb`, `needle-rgb`, `major-tick-rgb`, `minor-tick-rgb`


```xml
<component type="cairo-gauge-round-annotated" metric="speed" units="mph"  background-rgb="255,0,0"/>
```
<kbd>![06-cairo-gauge-round-annotated-7.png](06-cairo-gauge-round-annotated-7.png)</kbd>


```xml
<component type="cairo-gauge-round-annotated" metric="speed" units="mph"  major-ann-rgb="255,0,0"/>
```
<kbd>![06-cairo-gauge-round-annotated-8.png](06-cairo-gauge-round-annotated-8.png)</kbd>


```xml
<component type="cairo-gauge-round-annotated" metric="speed" units="mph"  minor-ann-rgb="255,0,0"/>
```
<kbd>![06-cairo-gauge-round-annotated-9.png](06-cairo-gauge-round-annotated-9.png)</kbd>


```xml
<component type="cairo-gauge-round-annotated" metric="speed" units="mph"  needle-rgb="255,0,255"/>
```
<kbd>![06-cairo-gauge-round-annotated-10.png](06-cairo-gauge-round-annotated-10.png)</kbd>


```xml
<component type="cairo-gauge-round-annotated" metric="speed" units="mph"  needle-rgb="255,0,255"/>
```
<kbd>![06-cairo-gauge-round-annotated-11.png](06-cairo-gauge-round-annotated-11.png)</kbd>


```xml
<component type="cairo-gauge-round-annotated" metric="speed" units="mph"  major-tick-rgb="255,0,0"/>
```
<kbd>![06-cairo-gauge-round-annotated-12.png](06-cairo-gauge-round-annotated-12.png)</kbd>


```xml
<component type="cairo-gauge-round-annotated" metric="speed" units="mph"  minor-tick-rgb="255,0,0"/>
```
<kbd>![06-cairo-gauge-round-annotated-13.png](06-cairo-gauge-round-annotated-13.png)</kbd>


# Transparency

Any colour that is completely transparent will disappear... this can be used to change the appearance of the widget quite a bit.


```xml
<component type="cairo-gauge-round-annotated" metric="speed" units="mph"  background-rgb="255,0,0,0"/>
```
<kbd>![06-cairo-gauge-round-annotated-14.png](06-cairo-gauge-round-annotated-14.png)</kbd>


```xml
<component type="cairo-gauge-round-annotated" metric="speed" units="mph"  major-ann-rgb="255,0,0,0"/>
```
<kbd>![06-cairo-gauge-round-annotated-15.png](06-cairo-gauge-round-annotated-15.png)</kbd>


```xml
<component type="cairo-gauge-round-annotated" metric="speed" units="mph"  minor-ann-rgb="255,0,0,0"/>
```
<kbd>![06-cairo-gauge-round-annotated-16.png](06-cairo-gauge-round-annotated-16.png)</kbd>


```xml
<component type="cairo-gauge-round-annotated" metric="speed" units="mph"  needle-rgb="255,0,255,40"/>
```
<kbd>![06-cairo-gauge-round-annotated-17.png](06-cairo-gauge-round-annotated-17.png)</kbd>


```xml
<component type="cairo-gauge-round-annotated" metric="speed" units="mph"  major-tick-rgb="255,0,0,0"/>
```
<kbd>![06-cairo-gauge-round-annotated-18.png](06-cairo-gauge-round-annotated-18.png)</kbd>


```xml
<component type="cairo-gauge-round-annotated" metric="speed" units="mph"  minor-tick-rgb="255,0,0,0"/>
```
<kbd>![06-cairo-gauge-round-annotated-19.png](06-cairo-gauge-round-annotated-19.png)</kbd>


