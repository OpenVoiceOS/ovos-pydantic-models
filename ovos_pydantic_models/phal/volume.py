from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


# --- OVOS Audio Volume Message Models ---

class MycroftVolumeGetMessage(OpenVoiceOSMessage):
    """Query the current volume level from the PHAL volume plugin.

    Emitted by the volume skill or settings GUI when it needs the current
    volume and mute state. The PHAL volume plugin replies with
    `mycroft.volume.get.response`.
    """
    message_type: str = "mycroft.volume.get"
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MycroftVolumeGetReplyData(BaseModel):
    """Current volume level and mute state from the PHAL volume plugin."""
    percent: int = Field(..., description="Current volume percentage (0-100).")
    muted: bool = Field(..., description="True if the volume is currently muted, False otherwise.")


class MycroftVolumeGetResponseMessage(OpenVoiceOSMessage):
    """Return the current volume level and mute state.

    Emitted by the PHAL volume plugin in response to `mycroft.volume.get`.
    The volume skill uses this to report the current level to the user.
    """
    message_type: str = "mycroft.volume.get.response"
    data: MycroftVolumeGetReplyData


class VolumeSetPercentData(BaseModel):
    """Payload for setting an absolute volume as a 0.0–1.0 fraction."""
    percent: float = Field(..., ge=0.0, le=1.0, description="Volume percentage (0.0-1.0).")


class VolumeSetPercentMessage(OpenVoiceOSMessage):
    """Set the system volume to an absolute level expressed as a fraction.

    Emitted by the volume skill or slider controls. The PHAL volume plugin
    converts the 0.0–1.0 value to the platform-native volume range and
    applies it immediately.
    """
    message_type: str = "volume.set.percent"
    data: VolumeSetPercentData


class MycroftVolumeIncreaseDecreaseData(BaseModel):
    """Relative volume change amount (0.0–1.0 fraction)."""
    percent: float = Field(..., description="Percentage change in volume (e.g., 0.1 for 10%).")


class MycroftVolumeIncreaseMessage(OpenVoiceOSMessage):
    """Increase the system volume by a relative percentage.

    Emitted by the volume skill in response to 'turn it up' commands. The
    PHAL volume plugin raises the current level by `percent` (clamped to 100%).
    """
    message_type: str = "mycroft.volume.increase"
    data: MycroftVolumeIncreaseDecreaseData


class MycroftVolumeDecreaseMessage(OpenVoiceOSMessage):
    """Decrease the system volume by a relative percentage.

    Emitted by the volume skill in response to 'turn it down' commands. The
    PHAL volume plugin lowers the current level by `percent` (clamped to 0%).
    """
    message_type: str = "mycroft.volume.decrease"
    data: MycroftVolumeIncreaseDecreaseData


class MycroftVolumeSetData(BaseModel):
    """Payload for setting an absolute volume as an integer percentage."""
    percent: Optional[int] = Field(None, ge=0, le=100, description="Volume percentage to set (0-100).")
    play_sound: bool = Field(False, description="Whether to play a sound when setting the volume.")


class MycroftVolumeSetMessage(OpenVoiceOSMessage):
    """Set the system volume to an absolute integer percentage (0–100).

    Emitted by the volume skill in response to 'set volume to 50%' commands.
    If `play_sound` is True the PHAL volume plugin plays a brief chime after
    adjusting to confirm the new level.
    """
    message_type: str = "mycroft.volume.set"
    data: MycroftVolumeSetData


class MycroftVolumeUnmuteMessage(OpenVoiceOSMessage):
    """Restore audio output after a mute.

    Emitted by the volume skill in response to 'unmute' voice commands or
    a hardware unmute button press. The PHAL volume plugin restores the
    previous volume level.
    """
    message_type: str = "mycroft.volume.unmute"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftVolumeMuteMessage(OpenVoiceOSMessage):
    """Silence audio output without changing the volume level.

    Emitted by the volume skill in response to 'mute' voice commands or a
    hardware mute button press. The PHAL volume plugin sets volume to zero
    but preserves the previous level for unmute restoration.
    """
    message_type: str = "mycroft.volume.mute"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftVolumeMuteToggleMessage(OpenVoiceOSMessage):
    """Toggle the mute state — mute if currently unmuted, unmute if muted.

    Emitted by hardware mute buttons, media key bindings, or GUI controls
    that act as a single toggle. The PHAL volume plugin flips the current
    mute state and restores the previous volume level when unmuting.
    """
    message_type: str = "mycroft.volume.mute.toggle"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftVolumeSetGuiData(BaseModel):
    """Payload for a GUI-initiated volume change."""
    percent: int = Field(..., ge=0, le=100, description="Target volume level (0–100).")


class MycroftVolumeSetGuiMessage(OpenVoiceOSMessage):
    """Set the system volume from a GUI slider or on-screen control.

    Functionally identical to `mycroft.volume.set` but emitted specifically
    by GUI volume sliders rather than voice commands. The PHAL volume plugin
    applies the new level without triggering any verbal confirmation or OSD,
    since the user is already interacting with the GUI.
    """
    message_type: str = "mycroft.volume.set.gui"
    data: MycroftVolumeSetGuiData


class MycroftVolumeGetSlidingPanelMessage(OpenVoiceOSMessage):
    """Request the current volume level when the GUI sliding panel opens.

    Emitted by the GUI sliding volume panel on open to ensure the slider
    reflects the current hardware volume before the user drags it.
    The PHAL volume plugin responds with `mycroft.volume.get.response`.
    """
    message_type: str = "mycroft.volume.get.sliding.panel"
    data: Dict[str, Any] = Field(default_factory=dict)
