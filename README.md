# hri-test-integration

`hri_probe` is a Home Assistant custom integration written only to test
[hass-remote-integration](https://github.com/trailro/hass-remote-integration) (HRI) end to end.
It has no real use: every release breaks something on purpose, or gives the container something
to publish, command and call.

## Releases

| Release | What it is for | Config entry | Minimum HA |
|---|---|---|---|
| 1.0.0 | YAML only (`hri_probe:` with `name`, `value`) | none | 2024.1.0 |
| 2.0.0 | config flow; YAML is imported into a config entry | version 1 (`name`, `value`) | 2024.1.0 |
| 3.0.0 | config flow + options flow; YAML is no longer read | version 2 (`name`, `initial`, options `step`), migrated from 1 | 2024.1.0 |
| 3.1.0 | as 3.0.0, but the minimum HA version is raised | version 2 | 2026.9.0 |
| 4.0.0 | imports `imp`, a module Python removed | version 2 | 2026.9.0 |
| 4.1.0 | ships `legacy.py` with Python 2 syntax | version 2 | 2026.9.0 |
| 4.2.1 | requires `netifaces`: C code, no compiler in the image | version 2 | 2026.9.0 |
| 4.3.1 | requires `docopt`: a pure-Python sdist that builds fine | version 2 | 2026.9.0 |
| 4.4.1 | requires `aiohttp==3.9.0`: conflicts with Home Assistant's constraints | version 2 | 2026.9.0 |
| 4.5.1 | requires `scipy`: a heavy wheel | version 2 | 2026.9.0 |
| 5.0.0 | service `hri_probe.stuck`: blocks one executor thread forever | version 2 | 2026.9.0 |
| 6.0.0 | one entity on every platform Home Assistant has, test services, persistent notifications | version 2 | 2026.9.0 |

**Use the `v4.x.1` tags, never `v4.2.0`-`v4.5.0`:** those are contaminated with `legacy.py`, so they
stop at the syntax blocker instead of reaching the dependency case they were made for.

Releases 1.0.0 to 5.0.0 create a single sensor, `sensor.probe_<name>`, with the same unique id in
every release and the attributes `source` (yaml, entry) and `version`.

## 6.0.0: the full surface

One config entry named `demo` creates 40 entities on 34 platforms (27 native, 7 mirrored), split over four devices
(`core`, `comfort`, `security`, `media`) so device grouping is exercised too. Every entity is
named `Probe <entry name> <label>`, so its entity id, and therefore every MQTT topic, follows from
the entry name.

Entities are interactive: the normal Home Assistant service changes the state, so a command that
travels over MQTT can be checked by reading the state back.

### Platforms Home Assistant's MQTT integration also has

HRI publishes these natively, with command topics.

| Entity | What it is there to test |
|---|---|
| `alarm_control_panel.probe_demo_alarm` | arm home/away/night/vacation/custom bypass, disarm, trigger; code `1234` is required and a wrong code must fail |
| `binary_sensor.probe_demo_motion` | a read-only state that flips on `hri_probe.tick` |
| `button.probe_demo_button` | press; the state is only a timestamp, the count is in the `presses` attribute |
| `climate.probe_demo_climate` | a single target temperature and a high/low range, hvac mode, preset, fan mode, swing mode; `hvac_action` follows the mode, so one command changes two published values. `preset_modes` contains `none` on purpose: HRI must filter it out |
| `cover.probe_demo_cover` | open, close, stop, position and tilt |
| `cover.probe_demo_cover_tilt` | tilt only: no position is published at all |
| `date.probe_demo_date`, `datetime.probe_demo_datetime`, `time.probe_demo_alarm` | set value on the three date/time platforms |
| `device_tracker.probe_demo_tracker` | a GPS tracker that walks out of the home zone on every tick |
| `event.probe_demo_event` | `event_types` single/double/hold, fired by the tick; a retained document must not replay the last event |
| `fan.probe_demo_fan` | percentage, preset, oscillation, direction; percentage and preset exclude each other |
| `humidifier.probe_demo_humidifier` | target humidity, mode, and an `action` that follows both |
| `lawn_mower.probe_demo_lawn_mower` | start mowing, pause, dock |
| `light.probe_demo_light` | brightness and colour temperature (2200-6500 K) |
| `light.probe_demo_light_rgb` | rgb colour and an effect list |
| `lock.probe_demo_lock` | lock, unlock and `open`: the only entity that exercises the open payload |
| `notify.probe_demo_notify` | send message; the text arrives in the `last_message` attribute |
| `number.probe_demo_number` | set value between 0 and 100, step 0.5, unit `%` |
| `scene.probe_demo_scene` | activate; the state is only the activation timestamp |
| `select.probe_demo_select` | options `idle`, `eco mode`, `boost`: the space must survive the round trip |
| `sensor.probe_demo_sensor_power` | numeric with device class, state class and unit; moves on every tick |
| `sensor.probe_demo_sensor_mode` | an enum sensor with `options` |
| `sensor.probe_demo_sensor_timestamp` | a timestamp sensor |
| `sensor.probe_demo_sensor_flaky` | goes `unknown` on every third tick: a stale value on the other side is visible |
| `siren.probe_demo_siren` | tone (`slow whoop` has a space), duration and volume |
| `switch.probe_demo_main` | on and off, with a command counter |
| `text.probe_demo_note` | set value, 3 to 32 characters |
| `update.probe_demo_firmware` | install with backup and progress; it re-arms afterwards, so the install is repeatable |
| `vacuum.probe_demo_bot` | start, pause, stop, return to base, clean spot, locate, fan speed, and `send_command` with its payload kept in an attribute |
| `valve.probe_demo_position` | open, close, stop and set position |
| `valve.probe_demo_plain` | the same valve without position reporting: its stop behaviour differs |
| `water_heater.probe_demo_tank` | target temperature, operation mode, away mode |

### Platforms MQTT has no equivalent for

HRI can only mirror these as read-only sensors on the consuming side: the state and the attributes
arrive, commands do not.

| Entity | State on the other side |
|---|---|
| `calendar.probe_demo_agenda` | `on` while an event runs; one current and one upcoming event |
| `camera.probe_demo_still` | `idle`; the picture itself stays behind |
| `image.probe_demo_badge` | the timestamp of the last image |
| `media_player.probe_demo_deck` | `playing`, with title, artist, position, volume and source list |
| `remote.probe_demo_hub` | `on`/`off` plus the last command sent |
| `todo.probe_demo_list` | the number of open items |
| `weather.probe_demo_local` | the condition, plus a compact `forecast_preview` attribute (Home Assistant no longer publishes forecasts as attributes, so the full forecast is only available locally through `weather.get_forecasts`) |

## Services

| Service | What it is for |
|---|---|
| `hri_probe.tick` | moves the entities that have no service of their own: the sensors, the binary sensor, the event and the tracker |
| `hri_probe.flap` | every entity goes unavailable for a few seconds and comes back |
| `hri_probe.notify` | creates or dismisses a persistent notification |
| `hri_probe.echo` | a service that returns a response, so the answer can be followed back through MQTT |
| `hri_probe.fail` | raises an error: how is a failed call reported? |
| `hri_probe.slow` | takes 90 s by default, longer than `HRI_CALL_TIMEOUT`: the caller must time out, not hang |
| `hri_probe.stuck` | blocks one executor thread forever (kept from 5.0.0): the container must still restart |

A persistent notification is also created every time the config entry is set up, and dismissed when
it is unloaded.

## Traps on purpose

- Option values with spaces (`eco mode`, `slow whoop`): anything that slugifies or splits them fails loudly.
- `climate` lists a preset literally named `none`, which the MQTT climate platform refuses.
- The flaky sensor returns to `unknown`, which several MQTT platforms reject as a raw state.
- Two valves and two covers differ only in what they report, so a bridge that assumes position is always present breaks on one of them.
- The alarm needs a code, so a command that drops the code must fail visibly.
