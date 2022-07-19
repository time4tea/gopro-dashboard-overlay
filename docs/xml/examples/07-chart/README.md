<!-- 

Auto Generated File DO NOT EDIT 

-->

# Chart

Used to be called 'gradient_chart'

Chart draws a chart of some metric, with a configurable window before and after the current point.

The default metric is `alt`, with a default window of `5` minutes (2.5 mins around the current point in each direction)


```xml
<component type="chart" name="chart" />
```
<kbd>![07-chart-0.png](07-chart-0.png)</kbd>


## Positioning

use `x` and `y` to set the position of the chart


```xml
<component type="gradient_chart" name="gradient_chart" x="100" />
```
<kbd>![07-chart-1.png](07-chart-1.png)</kbd>


# Window Size

Set the window size in seconds, defaults to 5*60 = `300`.

The chart is not currently terribly performant, so redrawing frequently ( smaller window )  will slow down rendering, but 
smaller windows have a bit more of a scroll effect, so look nicer.


```xml
<component type="chart" metric="speed" units="kph" seconds="30" />
```
<kbd>![07-chart-2.png](07-chart-2.png)</kbd>


```xml
<component type="chart" metric="speed" units="kph" seconds="60" />
```
<kbd>![07-chart-3.png](07-chart-3.png)</kbd>


```xml
<component type="chart" metric="speed" units="kph" seconds="90" />
```
<kbd>![07-chart-4.png](07-chart-4.png)</kbd>


# Metric & Units

Use any standard metric, with any standard unit. See [04-metrics](04-metrics.md) for more details


```xml
<component type="chart" metric="speed" units="kph" />
```
<kbd>![07-chart-5.png](07-chart-5.png)</kbd>



```xml
<component type="chart" metric="accl.x" units="m/s^2" />
```
<kbd>![07-chart-6.png](07-chart-6.png)</kbd>


## Colours / Sizing

These attributes are not currently configurable.
