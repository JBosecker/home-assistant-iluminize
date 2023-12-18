"""Support for Iluminize WiFi LED Controller."""
from __future__ import annotations

from typing import Any

from .controller import IluminizeController
from .const import CONF_TYPE, CONF_TYPE_RGBW, CONF_TYPE_RGB, CONF_TYPE_W, CONF_SENDER, DOMAIN, MANUFACTURER, MODEL, LOGGER, DEFAULT_NAME_RGB, DEFAULT_NAME_WHITE, CONF_MAX_RGB, CONF_MAX_W, CONF_NAME_DEFAULT, CONF_PORT_DEFAULT, CONF_MAX_W_DEFAULT, CONF_MAX_RGB_DEFAULT, ATTR_SAVED_BRIGHTNESS, ATTR_SAVED_RGB_COLOR


import voluptuous as vol

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_MODE,
    ATTR_RGB_COLOR,
    ATTR_WHITE,
    PLATFORM_SCHEMA,
    ColorMode,
    LightEntity,
    LightEntityFeature,
    ColorMode,
)
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, STATE_ON
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.restore_state import RestoreEntity
import homeassistant.util.color as color_util
from homeassistant.helpers.entity import DeviceInfo


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Iluminize WiFi LED Controller entry."""
    device_name = config_entry.data.get(CONF_NAME, CONF_NAME_DEFAULT)
    host = config_entry.data.get(CONF_HOST)
    port = config_entry.data.get(CONF_PORT, CONF_PORT_DEFAULT)
    sender = config_entry.data.get(CONF_SENDER)
    type = config_entry.data.get(CONF_TYPE)
    max_rgb = config_entry.options.get(CONF_MAX_RGB, CONF_MAX_RGB_DEFAULT)
    max_w = config_entry.options.get(CONF_MAX_W, CONF_MAX_W_DEFAULT)

    controller = IluminizeController(host, port, sender)
    
    if type == CONF_TYPE_RGBW:
        LOGGER.debug("Creating RGB entity. Host: %s, Port: %s, Sender: %s, MaxRgb: %s", host, str(port), sender, max_rgb)
        LOGGER.debug("Creating White entity. Host: %s, Port: %s, Sender: %s, MaxWhite: %s", host, str(port), sender, max_w)
        async_add_entities([IluminizeRGBLight(device_name, controller, max_rgb), IluminizeWhiteLight(device_name, controller, max_w)])
    elif type == CONF_TYPE_RGB:
        LOGGER.debug("Creating RGB entity. Host: %s, Port: %s, Sender: %s, MaxRgb: %s", host, str(port), sender, max_rgb)
        async_add_entities([IluminizeRGBLight(device_name, controller, max_rgb)])
    elif type == CONF_TYPE_W:
        LOGGER.debug("Creating White entity. Host: %s, Port: %s, Sender: %s, MaxWhite: %s", host, str(port), sender, max_w)
        async_add_entities([IluminizeWhiteLight(device_name, controller, max_w)])


class IluminizeWhiteLight(RestoreEntity, LightEntity):
    """Iluminize White WiFi LED Controller."""
    
    def __init__(self, device_name, controller, max_w):
        """Initialise Iluminize WiFi LED Controller.

        :param device_name: Name for this device to use.
        :param controller: Instance of the Iluminize controller.
        :param max_w: Maximum value for the white channel as hex string.
        """
        self._attr_unique_id = f"{DOMAIN}_{controller.host}_{controller.port}_white"
        self.entity_id = f"light.{self.unique_id}"
        self._device_name = device_name
        self._controller = controller
        self._max_w = max_w
        
        color_modes = {ColorMode.ONOFF}
        color_modes.add(ColorMode.BRIGHTNESS)
        self._attr_supported_color_modes = color_modes
        self._attr_color_mode = ColorMode.BRIGHTNESS

    async def async_added_to_hass(self) -> None:
        """Call when entity about to be added to hass."""
        # If not None, we got an initial value.
        await super().async_added_to_hass()

        is_on = False
        brightness = 127
        
        state = await self.async_get_last_state()
        if state is not None:
            is_on = state.state == STATE_ON
            brightness = state.attributes.get(ATTR_SAVED_BRIGHTNESS) or brightness

        self._attr_brightness = brightness
        self._attr_is_on = is_on

    @property
    def name(self):
        """Return the default name for the light."""
        return DEFAULT_NAME_WHITE

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                (DOMAIN, f"{self._controller.host}:{self._controller.port}")
            },
            name=self._device_name,
            manufacturer=MANUFACTURER,
            model=MODEL,
        )
        
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return attributes of the light."""
        return {
            ATTR_SAVED_BRIGHTNESS: self._attr_brightness,
        }

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        self._attr_is_on = True
        self._attr_brightness = kwargs.get(ATTR_BRIGHTNESS, self._attr_brightness)
        self._set_white(self._attr_brightness)
        self.async_write_ha_state()

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._attr_is_on = False
        self._set_white(0)
        self.async_write_ha_state()

    def _set_white(self, brightness) -> None:
        max_w = int(self._max_w, 16)
        white = brightness / 255 * max_w
        self._controller.set_white(white)

class IluminizeRGBLight(RestoreEntity, LightEntity):
    """Iluminize RGB WiFi LED Controller."""

    def __init__(self, device_name, controller, max_rgb):
        """Initialise Iluminize WiFi LED Controller.

        :param device_name: Name for this device to use.
        :param type: The type for this entity. e.g. RGBW
        :param controller: Instance of the Iluminize controller.
        :param max_w: Maximum value for RGB as hex string.
        """
        self._attr_unique_id = f"{DOMAIN}_{controller.host}_{controller.port}_rgb"
        self.entity_id = f"light.{self.unique_id}"
        self._device_name = device_name
        self._controller = controller
        self._max_rgb = max_rgb

        color_modes = {ColorMode.ONOFF}
        color_modes.add(ColorMode.BRIGHTNESS)
        color_modes.add(ColorMode.RGB)
        self._attr_supported_color_modes = color_modes
        self._attr_color_mode = ColorMode.RGB
        
    async def async_added_to_hass(self) -> None:
        """Call when entity about to be added to hass."""
        # If not None, we got an initial value.
        await super().async_added_to_hass()
        
        is_on = False
        brightness = 127
        rgb_color = (255, 255, 255)
        
        state = await self.async_get_last_state()
        if state is not None:
            is_on = state.state == STATE_ON
            brightness = state.attributes.get(ATTR_SAVED_BRIGHTNESS) or brightness
            rgb_color = state.attributes.get(ATTR_SAVED_RGB_COLOR) or rgb_color

        self._attr_rgb_color = rgb_color
        self._attr_brightness = brightness
        self._attr_is_on = is_on

    @property
    def name(self):
        """Return the default name for the light."""
        return DEFAULT_NAME_RGB

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                (DOMAIN, f"{self._controller.host}:{self._controller.port}")
            },
            name=self._device_name,
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return attributes of the light."""
        return {
            ATTR_SAVED_BRIGHTNESS: self._attr_brightness,
            ATTR_SAVED_RGB_COLOR: self._attr_rgb_color,
        }

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        self._attr_is_on = True
        self._attr_rgb_color = kwargs.get(ATTR_RGB_COLOR, self._attr_rgb_color)
        self._attr_brightness = kwargs.get(ATTR_BRIGHTNESS, self._attr_brightness)
        
        (red, green, blue) = self._attr_rgb_color
        brightness = self._attr_brightness
        red = red / 255 * brightness
        green = green / 255 * brightness
        blue = blue / 255 * brightness

        self._set_rgb((red, green, blue))
        self.async_write_ha_state()


    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self._attr_is_on = False
        self._set_rgb((0, 0, 0))
        self.async_write_ha_state()
    
    def _set_rgb(self, rgb) -> None:
        max_rgb = self._max_rgb
        max_red = int(max_rgb[0:2], 16)
        max_green = int(max_rgb[2:4], 16)
        max_blue = int(max_rgb[4:6], 16)
            
        red = rgb[0] / 255 * max_red
        green = rgb[1] / 255 * max_green
        blue = rgb[2] / 255 * max_blue
            
        self._controller.set_rgb(red, green, blue)
