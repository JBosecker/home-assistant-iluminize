"""Config flows for the Iluminize integration."""

import voluptuous as vol
from typing import Any

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import SelectSelector, SelectSelectorConfig, SelectSelectorMode

import re

from .const import DOMAIN, LOGGER, CONF_SENDER, CONF_SENDER_REGEX, CONF_TYPE, CONF_TYPE_RGBW, CONF_TYPE_RGB, CONF_TYPE_W, CONF_NAME_DEFAULT, CONF_PORT_DEFAULT, CONF_MAX_RGB, CONF_MAX_W, CONF_MAX_RGB_DEFAULT, CONF_MAX_W_DEFAULT, CONF_MAX_RGB_REGEX, CONF_MAX_W_REGEX


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle the options flows."""
    
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors = {}
        
        if user_input is not None:
            self._validate_input(user_input, errors)
            if not errors:
                return self.async_create_entry(title="", data=user_input)
        
        type = self.config_entry.data.get(CONF_TYPE)
        if type == CONF_TYPE_W:
            data_schema = vol.Schema({
                vol.Optional(CONF_MAX_W, default=CONF_MAX_W_DEFAULT): cv.string,
            })
        elif type == CONF_TYPE_RGB:
            data_schema = vol.Schema({
                vol.Optional(CONF_MAX_RGB, default=CONF_MAX_RGB_DEFAULT): cv.string,
            })
        else:
            data_schema = vol.Schema({
                vol.Optional(CONF_MAX_RGB, default=CONF_MAX_RGB_DEFAULT): cv.string,
                vol.Optional(CONF_MAX_W, default=CONF_MAX_W_DEFAULT): cv.string,
            })
        
        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )
    
    def _validate_input(self, user_input, errors):
        if user_input.get(CONF_MAX_RGB, None) is not None and not re.match(CONF_MAX_RGB_REGEX, user_input[CONF_MAX_RGB]):
            errors[CONF_MAX_RGB] = "invalid_max_rgb_format"
        else:
            errors.pop(CONF_MAX_RGB, None)

        if user_input.get(CONF_MAX_W, None) is not None and not re.match(CONF_MAX_W_REGEX, user_input[CONF_MAX_W]):
            errors[CONF_MAX_W] = "invalid_max_w_format"
        else:
            errors.pop(CONF_MAX_W, None)

class ConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the config flows."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the config flow start."""
        return await self.async_step_manual()

    async def async_step_manual(self, user_input=None):
        """Request manual device configuration."""
        errors = {}
        
        if user_input is not None:
            self._validate_input(user_input, errors)
            if not errors:
                await self.async_set_unique_id(f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=f"Iluminize LED Controller ({user_input[CONF_NAME]})", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Optional(CONF_PORT, default=CONF_PORT_DEFAULT): cv.port,
                vol.Required(CONF_SENDER): cv.string,
                vol.Required(CONF_TYPE, default=CONF_TYPE_RGBW): SelectSelector(
                    SelectSelectorConfig(options=[CONF_TYPE_RGBW, CONF_TYPE_RGB, CONF_TYPE_W],
                                                  mode=SelectSelectorMode.DROPDOWN),
                    ),
                vol.Required(CONF_NAME, default=CONF_NAME_DEFAULT): cv.string,
            }
        )
        return self.async_show_form(
            step_id="manual",
            data_schema=data_schema,
            errors=errors,
        )
    
    def _validate_input(self, user_input, errors):
        if not re.match(CONF_SENDER_REGEX, user_input[CONF_SENDER]):
            errors[CONF_SENDER] = "invalid_sender_format"
        else:
            errors.pop(CONF_SENDER, None)

