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

### Containers

Some elements can contain other elements, these are called "containers".

#### Translate Component

The `translate` component moves its child elements around on the screen. For example, the `compass` component doesn't
take an x/y co-ordinate to indicate where it should be drawn on the screen, so by default it will draw at (0,0) - the
top-left of the screen. By placing the `compass` inside a `translate` the compass can be drawn anywhere on the screen

```xml

<translate x="180" y="50">
    <component type="compass" size="300" fg="255,255,255" text="0,255,255" textsize="32"/>
</translate>
```

#### Frame Component

A `frame` is a box that can contain other components. It can optionally be filled with a background colour, and have an
outline drawn around it. The corners of the box can be rounded with `cr` and opacity with `opacity`.

Any child can be placed inside a `frame` - much like a `composite` - however, child components will be clipped to the
size of the frame. This could be used to create some interesting effects. A square `frame` with `cr` set to half the
width (i.e. the radius) will create a circular frame!

```xml

<frame width="200" height="200" cr="100" opacity="0.5" outline="255,255,255">
    <!-- child components ... -->
</frame>
```

#### Composite Component

This works identically to the `translate` component

#### Naming Containers

Optionally, any container component can be named, this allows you to include or exclude it for a given rendering run on
the command line Names don't have to be unique, so a dashboard could have a number of different containers all named "
with-hr", which could be excluded when rendering a GPX track that doesn't have any heartrate data in it.

```xml

<translate name="with-hr" x="180" y="50">
    <component type="text">HR</component>
    <component type="metric" x="-70" y="18" metric="hr" dp="0" size="32" align="right"/>
</translate>
```

If you didn't want to render the metric and the text, you could add `--exclude with-hr` when running the program, and
this container would be skipped.

### Components

Components are simple widgets that draw something onto the screen.

TODO - List Components

#### Text Component

Draws some text on the screen at the given co-ordinates.

```xml

<component type="text" x="50" y="100" size="32" rbg="255,255,255">Hello</component>
```

#### Metric Component

Draws the value of a bit of meta-data on the screen at the given co-ordinate.

```xml

<component type="metric" x="-70" y="18" metric="cadence" dp="0" size="32" rgb="255,255,0" align="right"/>
```

The following metrics are supported:
`hr`, `cadence`, `speed`, `cspeed`, `temp`,
`gradient`, `alt`, `odo`, `dist`, `azi`, `lat`, `lon`,


| Metric | Description | Unit |
| --- | --- | --- |
| hr | Heart Rate | beats / minute |
| cadence | Cadence | beats / minute |
| speed | Speed | metres / second |
| cspeed | Computed Speed | metres / second |
| temp | Ambient Temperature | degrees C |
| gradient | Gradient of Ascent | degrees |
| alt | Height above sea level | metres |
| odo | Distance since start | metres |
| dist | Distance since last point | metres |
| azi | Azimuth | degrees |
| lat | Latitude | Nothing |
| lon | Longitude | Nothing | 

##### Metric Units

Metrics all are associated with a given unit. For example, speed is always in `m/s`. Metrics can be converted to
different units using the `units` attribute.

```xml

<component type="metric" metric="temp" units="degreeF" dp="1"/>
```

The following units are supported: `mph`, `kph`, `mps`, `knots`, `degreeF`, `degreeC`, `feet`, `miles`, `nautical_miles`
- Conversions that don't make sense for a given metric will fail.

TODO - Docs on the other components

