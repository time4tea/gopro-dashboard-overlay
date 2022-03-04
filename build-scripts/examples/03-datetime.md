
# DateTime

The datetime component renders the GPS date or time. It is fully controllable, using a format string
to control which parts of the date to render.

## Dates


{{ <component type="datetime" format="%Y-%m-%d"/> }}

{{ <component type="datetime" format="%d/%m/%Y"/> }}

{{ <component type="datetime" format="%m/%d/%Y"/> }}


## Times

{{ <component type="datetime" format="%H:%M:%S" /> }}

Showing fractional seconds, shows microseconds

{{ <component type="datetime" format="%H:%M:%S.%f" /> }}

Truncating fractional seconds to show only 10ths or 100ths of a second 

{{ <component type="datetime" format="%H:%M:%S.%f" truncate="5" /> }}

{{ <component type="datetime" format="%H:%M:%S.%f" truncate="4" /> }}

## Performance

Because rendering text is quite slow, text is cached, and the reused, rather than re-rendering
it all the time. For text that changes a lot, this will be inefficient, and will eventually cause 
some memory problems. For this reason, its better to split up things that change a lot (times...) from
things that don't change much (dates...)

If you experience memory issues, use the `cache` directive, explained below.

## Combination of Dates and Times

It may be better to combine a `text` and `datetime` component rather than rendering everything together.

{{ <component type="datetime" format="Date: %d/%m/%Y Time: %H:%M:%S" cache="false" /> }}

{{
    <composite>
        <component x="0" y="0" type="text">Date</component>
        <component x="50" y="0" type="datetime" format="%Y/%m/%d"/>
        <component x="0" y="20" type="text">Time</component>
        <component x="50" y="20" type="datetime" format="%H:%M:%S.%f" truncate="5" cache="false" />
    </composite>
}}