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


# Examples

Please see the extensive collection of examples - [here](examples/README.md)

