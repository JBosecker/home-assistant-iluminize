"""Constants for the Iluminize integration."""
import logging

from homeassistant.const import Platform

DOMAIN = "iluminize"
MANUFACTURER = "Iluminize"
MODEL = "LED Controller"

LOGGER = logging.getLogger("iluminize")

CONF_TYPE = "type"
CONF_TYPE_RGBW = "RGBW"
CONF_TYPE_RGB = "RGB"
CONF_TYPE_W = "W"
CONF_SENDER = "sender"
CONF_SENDER_REGEX = "^([0-9a-fA-F]{2})([0-9a-fA-F]{2})([0-9a-fA-F]{2})$"
CONF_NAME_DEFAULT = "Light strip"
CONF_PORT_DEFAULT = "8899"
CONF_MAX_RGB = "max_rgb"
CONF_MAX_RGB_DEFAULT = "FFFFFF"
CONF_MAX_RGB_REGEX = "^([0-9a-fA-F]{6})$"
CONF_MAX_W = "max_w"
CONF_MAX_W_DEFAULT = "FF"
CONF_MAX_W_REGEX = "^([0-9a-fA-F]{2})$"

DEFAULT_NAME_RGB = "Color"
DEFAULT_NAME_WHITE = "White"

ATTR_SAVED_BRIGHTNESS = "saved_brightness"
ATTR_SAVED_RGB_COLOR = "saved_rgb_color"

PLATFORMS = [
    Platform.LIGHT
]
