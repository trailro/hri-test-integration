"""HRI Probe 2.0.0 config flow (entry version 1)."""
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow

from .const import DOMAIN


class ProbeConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            await self.async_set_unique_id(user_input["name"])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=user_input["name"], data=user_input)
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({vol.Required("name"): str, vol.Optional("value", default=1): int})
        )

    async def async_step_import(self, import_data):
        await self.async_set_unique_id(import_data["name"])
        self._abort_if_unique_id_configured(updates=import_data)
        return self.async_create_entry(title=f"{import_data['name']} (from YAML)", data=import_data)
