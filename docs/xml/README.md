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

# Custom Data (Experimental)

Custom data can be inserted into components using `extension` tags in a GPX file. Global data is inserted inside the `metadata` tag, and data for a specific GPX trackpoint is inserted inside the trackpoint. They can be accessed in the XML configuration using the metric `custom.metadata.<key>` and `custom.field.<key>` respectively. For example, in the GPX file below, global data `("transit_headsign", "route_length")` and `("transit_next_stop", "transit_distance")` for the first trackpoint are defined.
Note: The GPX parser does not seem to parse `extension` tags without another tag beside it, so `name` is used as a dummy tag.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<gpx>
	<metadata>
		<extensions>
			<transit_headsign><![CDATA[Route 1 to Place]]></transit_headsign>
			<route_length><![CDATA[5.2]]></route_length>
		</extensions>
		<name><![CDATA[Route 1]]></name>
	</metadata>
	<trk>
		<trkseg>
			<trkpt lat="50.000" lon="-100.000">
				<extensions>
					<transit_next_stop><![CDATA[Stop C]]></transit_next_stop>
					<transit_distance><![CDATA[0.5]]></transit_distance>
				</extensions>
				<ele>232.0</ele>
				<time>2024-04-02T13:03:37Z</time>
			</trkpt>
		</trkseg>
	</trk>
</gpx>
```

### Custom Data Formatting

By default custom data is inserted as a string, which means formatting attributes like `format` and `dp` cannot be used, and the data cannot be used in components that expect a number, like `chart`. To insert custom data as a float, specify `units="custom.float"` in the configuration file. 

Display the `transit_distance` field in a `chart`

```xml
<component type="chart" metric="custom.field.transit_distance" units="custom.float" />
```

Format the `route_length` metadata to 3 decimal places

```xml
<component type="metric" metric="custom.metadata.route_length" units="custom.float" dp="3" />
```