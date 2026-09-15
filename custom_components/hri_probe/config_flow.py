"""HRI Probe 3.0.0 config flow (entry version 2) and options flow."""
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, OptionsFlow
from homeassistant.core import callback

from .const import DOMAIN


class ProbeConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 2

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            await self.async_set_unique_id(user_input["name"])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=user_input["name"], data=user_input, options={"step": 1})
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({vol.Required("name"): str, vol.Optional("initial", default=1): int})
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ProbeOptionsFlow()


class ProbeOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({vol.Optional("step", default=self.config_entry.options.get("step", 1)): int}),
        )
