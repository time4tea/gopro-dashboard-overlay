
# Changelog

Newest changes are always in [README.md](README.md)

- 0.25.0
    - (Change in behaviour) - Will now use speed from datasource, in preference to calculated. This should make it much
      more stable, if the datasource supplies it. (GoPro does, GPX not)
- 0.24.0
    - Big internal restructuring of metadata parsing. Will make it easier to import GYRO/ACCL data soon. Incidentally,
      should be a bit faster.
    - Hopefully no externally visible effects.
- 0.23.0
    - Rename --no-overlay to --overlay-only as it was too confusing
- 0.22.0
    - Filter points that have DOP too large.
- 0.21.0
    - Built-in support for 4k videos, with a supporting overlay. Feedback welcomed.
    - Use --overlay-size with --layout xml to use custom overlay sizes and layouts
    - Minor Bugfixes
- 0.20.0
  - Add "opacity"  and "corner_radius" to maps xml components (H/T [@KyleGW](https://github.com/KyleGW))
  - New Utility: gopro-cut.py - Extract a section of a GoPro recording, with metadata
- 0.19.0
  - Load custom XML layouts correctly on command line. 
- 0.18.0
  - BUGFIX: pypi distribution was still broken. :-(
- 0.17.0
  - BUGFIX: pypi distribution was broken. :-(
- 0.16.0
  - Add support for degrees F for temp. 
- 0.15.0
  - XML Layouts improved. Probably good/stable enough to make custom layouts
  - Include/Exclude named components using command line
- 0.14.0
  - Fix for some thunderforest themes (H/T [@KyleGW](https://github.com/KyleGW))
  - XML layout support for vertical and colour text
- 0.13.0
  - Improved XML layout - text/metrics/unit conversions
- 0.12.0
  - New Utility: gopro-join.py - Join multiple GoPro files from a single session together 
  - Improve Parsing Speed for GoPro Metadata
- 0.11.0 
  - Allow XML layout definitions 
