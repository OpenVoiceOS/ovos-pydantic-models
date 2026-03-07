from typing import Dict, Any, Optional

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


class ConfigurationPatchData(BaseModel):
    """Partial configuration update to apply on top of existing config."""
    config: Dict[str, Any] = Field(..., description="Configuration key-value pairs to patch.")


class ConfigurationPatchMessage(OpenVoiceOSMessage):
    """Apply a partial configuration update without a full config reload.

    Emitted by skills, PHAL plugins, or admin tools that need to change
    a specific setting at runtime. `ovos-config` merges the patch dict into
    the active config. All components that cache configuration are notified
    via `configuration.updated`.
    """
    message_type: str = "configuration.patch"
    data: ConfigurationPatchData


class ConfigurationUpdatedMessage(OpenVoiceOSMessage):
    """Notify all components that the configuration has changed.

    Broadcast by `ovos-config` after any config mutation (patch, file write,
    backend sync). Components that cache configuration values should re-read
    their relevant keys when they receive this message.
    """
    message_type: str = "configuration.updated"
    data: Dict[str, Any] = Field(default_factory=dict)


class ConfigurationPatchClearMessage(OpenVoiceOSMessage):
    """Clear all runtime configuration patches, reverting to the base config.

    Emitted by admin tools or test harnesses that previously applied patches
    and need to restore the original configuration. `ovos-config` discards
    all accumulated patch layers.
    """
    message_type: str = "configuration.patch.clear"
    data: Dict[str, Any] = Field(default_factory=dict)


class ConfigurationCacheClearMessage(OpenVoiceOSMessage):
    """Force all components to discard their cached configuration.

    Emitted after external changes to the config file that may have bypassed
    the normal patch mechanism. Components must reload their config from disk
    on the next access.
    """
    message_type: str = "configuration.cache.clear"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosLanguageOutputForceData(BaseModel):
    """Payload for overriding the TTS output language."""
    lang: str = Field(..., description="BCP-47 language code to force for TTS output.")


class OvosLanguageOutputForceMessage(OpenVoiceOSMessage):
    """Override the TTS output language for the current session.

    Emitted by skills that operate in a specific language regardless of
    the user's configured locale (e.g. a language-learning skill). `ovos-audio`
    instructs the TTS plugin to synthesize in the specified language.
    Counterpart: `ovos.language.output.reset`.
    """
    message_type: str = "ovos.language.output.force"
    data: OvosLanguageOutputForceData


class OvosLanguageOutputResetMessage(OpenVoiceOSMessage):
    """Restore the TTS output language to the user's configured default.

    Emitted by skills when they finish operating in a forced language mode.
    `ovos-audio` returns to the language specified in `mycroft.conf`.
    Counterpart: `ovos.language.output.force`.
    """
    message_type: str = "ovos.language.output.reset"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosIpGeoUpdateData(BaseModel):
    """Location data derived from IP geolocation."""
    location: Dict[str, Any] = Field(
        ..., description="Location dict from IP geolocation (city, country, lat, lon, etc.)."
    )


class OvosIpGeoUpdateMessage(OpenVoiceOSMessage):
    """Update the device's location based on IP geolocation.

    Emitted by PHAL connectivity plugins when a network connection is
    established and IP geolocation data is available. `ovos-config` updates
    the `location` section of the configuration so skills and weather
    queries use the correct coordinates automatically.
    """
    message_type: str = "ovos.ipgeo.update"
    data: OvosIpGeoUpdateData
