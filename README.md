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
| 4.0.0 | imports `imp`, a module Python removed | version 2 | 2024.1.0 |
| 4.1.0 | ships `legacy.py` with Python 2 syntax | version 2 | 2024.1.0 |
| 4.2.1 | requires `netifaces`: C code, no compiler in the image | version 2 | 2024.1.0 |
| 4.3.1 | requires `docopt`: a pure-Python sdist that builds fine | version 2 | 2024.1.0 |
| 4.4.1 | requires `aiohttp==3.9.0`: conflicts with Home Assistant's constraints | version 2 | 2024.1.0 |
| 4.5.1 | requires `scipy`: a heavy wheel | version 2 | 2024.1.0 |
| 5.0.0 | service `hri_probe.stuck`: blocks one executor thread forever | version 2 | 2024.1.0 |
| 6.0.0 | one entity on every platform Home Assistant has, test services, persistent notifications | version 2 | 2026.9.0 |
| 7.0.0 | as 6.0.0, plus every config flow shape: a menu, every selector, errors and aborts, reconfigure, reauth, progress, a two-branch options flow | version 3, migrated from 2 (and from 1) | 2026.9.0 |
| 7.1.0 | as 7.0.0, plus the selector shapes a form renderer is most likely to get wrong: a select that takes a typed value, a multi-select whose default holds one, and two fractional durations | version 3 | 2026.9.0 |
| 7.2.0 | as 7.1.0, plus a text field that takes several values whose default holds an item with a comma (`aliases`), and the same shape on a service (`hri_probe.echo` field `words`) | version 3 | 2026.9.0 |
| 7.3.0 | as 7.2.0, plus a service multi-select that takes typed values whose example holds an item with a comma and one with surrounding spaces (`hri_probe.echo` field `names`) | version 3 | 2026.9.0 |

The 4.x and 5.0.0 releases ask for Home Assistant 2024.1.0, so they run on the
image's own baseline as well — handy for testing a dependency case without
updating Home Assistant first. 3.1.0, 6.0.0 and 7.0.0 ask for 2026.9.0.

**Use the `v4.x.1` tags, never `v4.2.0`-`v4.5.0`:** those are contaminated with `legacy.py`, so they
stop at the syntax blocker instead of reaching the dependency case they were made for.

Entry data and options are migrated forward: an entry created by 2.0.0 (version 1) or by 3.0.0-6.0.0
(version 2) is brought to version 3 on the first start of 7.0.0, keeps its entities and its unique id,
and never has to be deleted and made again.

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

## 7.0.0: the flows

6.0.0 gave the consuming side every entity and service shape. 7.0.0 does the same for config flows:
every branch below exists so a flow renderer meets the shape here first, not in a real integration.

### The user flow

| Step | What it is there to test |
|---|---|
| `user` | name and initial value. The name is also the unique id, so it decides the three exits below |
| `path` | `async_show_menu` with three options (`basic`, `advanced`, `probe`): a menu is not a form and has to be rendered as one choice, not as a field |
| `basic` | a menu branch that creates the entry immediately: menu straight to `create_entry`, with no form in between |
| `advanced` | one field per selector shape (below) |
| `probe` | `async_show_progress` with a real progress task: four seconds of nothing, then the entry. A renderer that does not poll the flow again sits there forever |

### Every selector the advanced step asks for

| Field | Selector | Why |
|---|---|---|
| `label` | text | the plain case |
| `note` | text, `multiline` | must become a textarea, not a one-line input |
| `level` | number, `mode: slider`, unit `%` | min 0, max 100, step 5: a renderer that ignores `mode` still has to honour the range |
| `retries` | number, `mode: box` | step 1: the value must come back as a whole number |
| `verbose` | boolean | a checkbox, and `false` must be sent, not omitted |
| `profile` | select, `mode: dropdown` | the options are plain strings and one of them, `eco mode`, has a space in it |
| `speed` | select, `mode: list` | options are `{value, label}` pairs: a radio list whose labels differ from its values |
| `families` | select, `multiple` | a multiple choice; the answer is a list, even with one item |
| `extra` | object | free-form JSON; every value has to be a number, which is what the per-field error below checks |
| `window` | duration | **on purpose a selector no renderer is obliged to know**: this is the field that finds out what happens at the edge of the supported set |
| `limits` | a form `section` | `ceiling` and `strict` arrive as one nested object under `limits`, not as two top-level fields |

### Errors and aborts

| Trigger | Result |
|---|---|
| `level` outside 0-100 | the schema itself refuses it: Home Assistant answers `InvalidData`, per field, before the step ever runs |
| `extra` with a value that is not a number | the step answers `errors={"extra": "invalid_object"}` and shows the form again with what was typed |
| `speed` = `fast` with more than 5 retries | `errors={"base": "incompatible"}`: an error that belongs to no field |
| a name that starts or ends with a space | `errors={"name": "invalid_name"}` on the first step |
| a name that already has an entry | abort `already_configured` |
| a name that already has a flow open | abort `already_in_progress` |
| the name `crash` | the step raises, catches its own error and aborts with `unknown`: an unexpected failure must reach the caller as an abort, never as a traceback |

### Reconfigure, reauth, options

| Flow | What it is there to test |
|---|---|
| `reconfigure` | changes `initial` and `label` on the existing entry through `async_update_reload_and_abort`; the entry keeps its id, its unique id and its entities, and the flow ends in abort `reconfigure_successful`, not in a new entry |
| `reauth` | `hri_probe.expire_auth` marks the entry unauthenticated and reloads it, so setup raises `ConfigEntryAuthFailed` and **Home Assistant starts the reauth flow itself** - the only way a real one starts. The flow is then waiting to be continued, not to be started. The wrong token comes back as `errors={"token": "invalid_auth"}`; `probe-token` ends it with abort `reauth_successful` and the entry loads again |
| options `init` | `async_show_menu` again, this time in an options flow: `tuning` and `reporting` |
| options `tuning` | a number and a select; the profile chosen here decides the schema of the next step |
| options `tuning_detail` | `aggressive` asks for a slider and a boolean, anything else asks for one number: a step whose form cannot be known before the previous answer |
| options `reporting` | a multiple select and a boolean, the shorter branch |

## Services

| Service | What it is for |
|---|---|
| `hri_probe.tick` | moves the entities that have no service of their own: the sensors, the event and the tracker once per tick, and the binary sensor once per call (so any `count` moves it) |
| `hri_probe.flap` | every entity goes unavailable for a few seconds and comes back |
| `hri_probe.notify` | creates or dismisses a persistent notification |
| `hri_probe.echo` | a service that returns a response, so the answer can be followed back through MQTT |
| `hri_probe.fail` | raises an error: how is a failed call reported? |
| `hri_probe.slow` | takes 90 s by default, longer than `HRI_CALL_TIMEOUT`: the caller must time out, not hang |
| `hri_probe.stuck` | blocks one executor thread forever (kept from 5.0.0): the container must still restart |
| `hri_probe.expire_auth` | makes the config entry fail authentication and reloads it, so Home Assistant starts the reauth flow by itself |

A persistent notification is also created every time the config entry is set up, and dismissed when
it is unloaded.

## Traps on purpose

- Option values with spaces (`eco mode`, `slow whoop`): anything that slugifies or splits them fails loudly.
- `climate` lists a preset literally named `none`, which the MQTT climate platform refuses.
- The flaky sensor returns to `unknown`, which several MQTT platforms reject as a raw state.
- Two valves and two covers differ only in what they report, so a bridge that assumes position is always present breaks on one of them.
- The alarm needs a code, so a command that drops the code must fail visibly.
- The `window` field of the advanced step is a duration selector, which is outside the set a simple flow renderer covers: it is there to be the field that does not fit.
- The config flow name `crash` aborts with `unknown`, and `hri_probe.expire_auth` breaks the entry until the reauth flow is finished: both leave the integration in a state a test has to get out of.
