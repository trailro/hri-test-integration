"""Shared constants of the hri_probe test integration."""

DOMAIN = "hri_probe"
VERSION = "6.0.0"

# Platforms Home Assistant's MQTT integration also has, so hass-remote-integration
# publishes them natively (discovery component + command topics).
NATIVE_PLATFORMS = [
    "alarm_control_panel", "binary_sensor", "button", "climate", "cover", "date",
    "datetime", "device_tracker", "event", "fan", "humidifier", "lawn_mower",
    "light", "lock", "notify", "number", "scene", "select", "sensor", "siren",
    "switch", "text", "time", "update", "vacuum", "valve", "water_heater",
]

# Platforms hass-remote-integration does not publish natively: they arrive on the consuming
# side as read-only sensor mirrors (state + attributes, no commands). Home Assistant's MQTT
# integration does have camera and image platforms; HRI simply does not use them yet.
MIRRORED_PLATFORMS = [
    "calendar", "camera", "image", "media_player", "remote", "todo", "weather",
]

PLATFORMS = NATIVE_PLATFORMS + MIRRORED_PLATFORMS

# One device per family, so device grouping and via_device are exercised too.
FAMILY_CORE = "core"          # switches, sensors, buttons, event: the everyday surface
FAMILY_COMFORT = "comfort"    # climate, humidifier, water heater, fan, cover, valve, mower, vacuum
FAMILY_SECURITY = "security"  # alarm, lock, siren, device tracker
FAMILY_MEDIA = "media"        # media player, camera, image, remote, todo, calendar, weather

FAMILY_NAMES = {
    FAMILY_CORE: "HRI Probe core",
    FAMILY_COMFORT: "HRI Probe comfort",
    FAMILY_SECURITY: "HRI Probe security",
    FAMILY_MEDIA: "HRI Probe media",
}

SIGNAL_FLAP = f"{DOMAIN}_flap"  # dispatcher: make every entity unavailable, then available again
SIGNAL_TICK = f"{DOMAIN}_tick"  # dispatcher: change the entities no service can change
