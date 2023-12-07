"""Voluptuous schemas for Iluminize WiFi LED Controller."""

from abc import ABC
from typing import ClassVar
import voluptuous as vol


from homeassistant.const import (
    CONF_NAME,
    CONF_HOST,
    CONF_PORT,
    Platform,
)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import ENTITY_CATEGORIES_SCHEMA

from .const import CONF_TYPE, CONF_TYPE_RGBW, CONF_TYPE_RGB, CONF_TYPE_W, CONF_SENDER, CONF_SENDER_REGEX, CONF_NAME_DEFAULT, CONF_PORT_DEFAULT, CONF_MAX_RGB, CONF_MAX_W, CONF_MAX_RGB_DEFAULT, CONF_MAX_W_DEFAULT, CONF_MAX_RGB_REGEX, CONF_MAX_W_REGEX

class IluminizePlatformSchema(ABC):
    """Voluptuous schema for Iluminize platform entity configuration."""
    PLATFORM: ClassVar[Platform | str]
    ENTITY_SCHEMA: ClassVar[vol.Schema]

    @classmethod
    def platform_node(cls) -> dict[vol.Optional, vol.All]:
        """Return a schema node for the platform."""
        return {
            vol.Optional(str(cls.PLATFORM)): vol.All(
                cv.ensure_list, [cls.ENTITY_SCHEMA]
            )
        }

class LightSchema(IluminizePlatformSchema):
    """Voluptuous schema for Iluminize lights."""
    PLATFORM = Platform.LIGHT

    ENTITY_SCHEMA = vol.All(
        vol.Schema(
            {
                vol.Required(CONF_HOST): cv.string,
                vol.Optional(CONF_PORT, default=CONF_PORT_DEFAULT): cv.port,
                vol.Required(CONF_SENDER): cv.matches_regex(CONF_SENDER_REGEX),
                vol.Required(CONF_NAME, default=CONF_NAME_DEFAULT): cv.string,
                vol.Required(CONF_TYPE): vol.In([CONF_TYPE_RGBW, CONF_TYPE_RGB, CONF_TYPE_W]),
                vol.Optional(CONF_MAX_RGB, default=CONF_MAX_RGB_DEFAULT): cv.matches_regex(CONF_MAX_RGB_REGEX),
                vol.Optional(CONF_MAX_W, default=CONF_MAX_W_DEFAULT): cv.matches_regex(CONF_MAX_W_REGEX),
            }
        ),
    )
