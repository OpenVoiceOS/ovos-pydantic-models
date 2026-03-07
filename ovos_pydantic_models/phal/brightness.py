from typing import Dict, Any

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


class PhalBrightnessControlGetMessage(OpenVoiceOSMessage):
    """Query the current display brightness level from the PHAL brightness plugin.

    Emitted by the settings GUI or skills handling 'what's the brightness' voice
    commands. The brightness PHAL plugin replies with
    `phal.brightness.control.get.response`.
    """
    message_type: str = "phal.brightness.control.get"
    data: Dict[str, Any] = Field(default_factory=dict)


class PhalBrightnessControlGetResponseData(BaseModel):
    """Current display brightness level from the PHAL brightness plugin."""
    brightness: int = Field(..., description="Current brightness level (0-100).")


class PhalBrightnessControlGetResponseMessage(OpenVoiceOSMessage):
    """Return the current display brightness level.

    Emitted by the PHAL brightness plugin in response to
    `phal.brightness.control.get`. The settings GUI uses this to initialize
    its brightness slider position.
    """
    message_type: str = "phal.brightness.control.get.response"
    data: PhalBrightnessControlGetResponseData


class PhalBrightnessControlSetData(BaseModel):
    """Payload for setting the display brightness to an absolute level."""
    brightness: int = Field(..., description="Brightness level to set (0-100).")


class PhalBrightnessControlSetMessage(OpenVoiceOSMessage):
    """Set the display brightness to a specific level.

    Emitted by the settings GUI slider, skills handling 'set brightness to 50%'
    voice commands, or the auto-dim feature. The PHAL brightness plugin applies
    the change to the display hardware immediately.
    """
    message_type: str = "phal.brightness.control.set"
    data: PhalBrightnessControlSetData


class PhalBrightnessControlSyncMessage(OpenVoiceOSMessage):
    """Synchronize the software brightness state with the current hardware level.

    Emitted by the PHAL brightness plugin on startup or after an external
    change to the display brightness (e.g. via ambient light sensor). The
    settings GUI re-reads the brightness level to update its slider.
    """
    message_type: str = "phal.brightness.control.sync"
    data: Dict[str, Any] = Field(default_factory=dict)


class PhalBrightnessControlAutoDimUpdateData(BaseModel):
    """Payload for enabling or disabling display auto-dim."""
    auto_dim: bool = Field(..., description="True to enable auto-dim, False to disable.")


class PhalBrightnessControlAutoDimUpdateMessage(OpenVoiceOSMessage):
    """Enable or disable the display auto-dim feature.

    Emitted by the settings GUI or a skills when the user toggles automatic
    brightness reduction. When enabled, the PHAL brightness plugin dims the
    display after a period of inactivity and restores it on interaction.
    """
    message_type: str = "phal.brightness.control.auto.dim.update"
    data: PhalBrightnessControlAutoDimUpdateData


class PhalBrightnessControlAutoNightModeEnabledMessage(OpenVoiceOSMessage):
    """Signal that the display has automatically switched to night mode.

    Emitted by the PHAL brightness plugin when ambient light or time-of-day
    conditions trigger automatic night mode activation (dimmer, warmer
    colour temperature). Skills and GUIs can adapt their appearance accordingly.
    """
    message_type: str = "phal.brightness.control.auto.night.mode.enabled"
    data: Dict[str, Any] = Field(default_factory=dict)
