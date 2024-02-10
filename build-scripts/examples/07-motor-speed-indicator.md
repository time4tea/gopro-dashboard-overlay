
# Motor Speed Indicator

The Motor Speed Indicator component draws a circular speed indicator


{{  <component type="msi" end="100" /> }}



# Sections

The following sections can be set 

| Attribute | Description        | 
|-----------|--------------------|
| green     | Green Section Max  |
| yellow    | Yellow Section Max |
| end       | End of Dial        |


{{ <component type="msi" green="30" yellow="60" end="100" /> }}


# Metrics & Conversions

The MSI defaults to speed in knots, but like a text metric, can access any available information, and convert it to
other units

{{  <component type="msi" units="mph" end="100" /> }}

{{  <component type="msi" metric="alt" units="feet" /> }}

# Size

The component can be sized - sizes that are too small or big might not render quite right

{{ <component type="msi" size="128" /> }}

# Rotation

Can rotate the entire gauge clockwise using `rotate`

{{ <component type="msi" rotate="45" /> }}
{{ <component type="msi" rotate="90" /> }}
{{ <component type="msi" rotate="180" /> }}


# Needle or no needle

The MSI component has a needle-less form which has a different style

{{ <component type="msi" needle="no" rotate="45" /> }}

# Variant

The MSI component has a variant "msi2", which doesn't have a needle, it has the same other attributes 
`green`, `yellow`, `end`

{{ <component type="msi2" /> }}



# Font

The text font can be changed in size

{{ <component type="msi" textsize="24" /> }}

