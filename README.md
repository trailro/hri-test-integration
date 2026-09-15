# hri-test-integration

`hri_probe` is a tiny Home Assistant custom integration used to test
[hass-remote-integration](https://github.com/trailro/hass-remote-integration) end to end:
version switches up and down, YAML-only to config flow, config entry migrations and a
minimum Home Assistant version. It has no real use.

| Release | Configuration | Config entry | Minimum HA |
|---|---|---|---|
| 1.0.0 | YAML only (`hri_probe:` with `name`, `value`) | none | 2024.1.0 |
| 2.0.0 | config flow; YAML is imported into a config entry | version 1 (`name`, `value`) | 2024.1.0 |
| 3.0.0 | config flow + options flow; YAML is no longer read | version 2 (`name`, `initial`, options `step`), migrated from 1 | 2024.1.0 |
| 3.1.0 | as 3.0.0 | version 2 | 2026.9.0 |

Each release creates one sensor, `sensor.probe_<name>`, with the same unique id in every
release, and attributes `source` (yaml, entry) and `version`.
