## Dashboard Configuration

The dashboard is configured by an XML file. There are built-in dashboards, and these use the XML configuration. Have a
look at the [example file](../../gopro_overlay/layouts/example.xml) to see an example, or see the
[default layout](../../gopro_overlay/layouts/default-1920x1080.xml)

### Tiny Example

The main element is `layout`: everything is contained within these tags.

```xml

<layout>
    <translate name="bob" x="200" y="200">
        <component type="text" x="0" y="0" size="32" cache="False">Bob</component>
        <translate x="180">
            <component type="compass" size="300" fg="255,255,255" text="0,255,255" textsize="32"/>
        </translate>
    </translate>
</layout>
```

## Containers

Some components can contain other components, these are called "containers".


## Components

Components are simple widgets that draw something onto the screen.

[Text](#text-component), [Metric](#metric-component), [Datetime](#datetime)
[Moving Map](#moving-map), [Journey Map](#journey-map)
[Icon](#icon)



### Gradient Chart

This component will be made more generic in a future version to chart any metric.

```xml
<component type="gradient_chart" name="some-name" x="400" y="980"/>
```
### Metric Component


##### Metric Units

Metrics all are associated with a given unit. For example, speed is always in `m/s`. Metrics can be converted to
different units using the `units` attribute.

```xml

<component type="metric" metric="temp" units="degreeF" dp="1"/>
```

The following units are supported: `mph`, `kph`, `mps`, `knots`, `degreeF`, `degreeC`, `feet`, `miles`, `nautical_miles`, `radian`

Conversions that don't make sense for a given metric will fail with a suitable message.



