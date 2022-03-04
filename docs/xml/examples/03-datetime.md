<!-- 

Auto Generated File DO NOT EDIT 

-->
# DateTime

The datetime component renders the GPS date or time. It is fully controllable, using a format string
to control which parts of the date to render.

## Dates



```xml
<component type="datetime" format="%Y-%m-%d"/>
```
<kbd>![03-datetime-0.png](03-datetime-0.png)</kbd>



```xml
<component type="datetime" format="%d/%m/%Y"/>
```
<kbd>![03-datetime-1.png](03-datetime-1.png)</kbd>



```xml
<component type="datetime" format="%m/%d/%Y"/>
```
<kbd>![03-datetime-2.png](03-datetime-2.png)</kbd>



## Times


```xml
<component type="datetime" format="%H:%M:%S" />
```
<kbd>![03-datetime-3.png](03-datetime-3.png)</kbd>


Showing fractional seconds, shows microseconds


```xml
<component type="datetime" format="%H:%M:%S.%f" />
```
<kbd>![03-datetime-4.png](03-datetime-4.png)</kbd>


Truncating fractional seconds to show only 10ths or 100ths of a second 


```xml
<component type="datetime" format="%H:%M:%S.%f" truncate="5" />
```
<kbd>![03-datetime-5.png](03-datetime-5.png)</kbd>



```xml
<component type="datetime" format="%H:%M:%S.%f" truncate="4" />
```
<kbd>![03-datetime-6.png](03-datetime-6.png)</kbd>


## Performance

Because rendering text is quite slow, text is cached, and the reused, rather than re-rendering
it all the time. For text that changes a lot, this will be inefficient, and will eventually cause 
some memory problems. For this reason, its better to split up things that change a lot (times...) from
things that don't change much (dates...)

If you experience memory issues, use the `cache` directive, explained below.

## Combination of Dates and Times

It may be better to combine a `text` and `dateime` component rather than rendering everything together.


```xml
<component type="datetime" format="Date: %d/%m/%Y Time: %H:%M:%S" cache="false" />
```
<kbd>![03-datetime-7.png](03-datetime-7.png)</kbd>



```xml
<composite>
        <component x="0" y="0" type="text">Date</component>
        <component x="50" y="0" type="datetime" format="%Y/%m/%d"/>
        <component x="0" y="20" type="text">Time</component>
        <component x="50" y="20" type="datetime" format="%H:%M:%S.%f" truncate="5" cache="false" />
    </composite>
```
<kbd>![03-datetime-8.png](03-datetime-8.png)</kbd>
