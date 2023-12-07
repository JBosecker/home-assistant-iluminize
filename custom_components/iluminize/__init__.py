"""The Iluminize component."""

from homeassistant.core import HomeAssistant
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.reload import async_integration_yaml_config

from .const import PLATFORMS

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Iluminize component."""
    return True

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Iluminize component for the given entry."""
    config_entry.async_on_unload(config_entry.add_update_listener(options_update_listener))
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload Iluminize config entry."""
    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)

async def options_update_listener(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)
