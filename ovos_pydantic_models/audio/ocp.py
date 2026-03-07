from enum import IntEnum
from typing import Dict, Any

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


class OcpMediaState(IntEnum):
    """Qt-compatible media status enum for the OCP audio layer.

    Maps to Qt's `QMediaPlayer.MediaStatus` values. Used by `ovos-audio`
    to report the low-level state of the media pipeline — distinct from the
    higher-level `MediaState` str enum in `skills/ocp.py` which tracks the
    OCP playback lifecycle visible to skills.
    """
    UNKNOWN = 0
    NO_MEDIA = 1
    LOADING_MEDIA = 2
    LOADED_MEDIA = 3
    STALLED_MEDIA = 4
    BUFFERING_MEDIA = 5
    BUFFERED_MEDIA = 6
    END_OF_MEDIA = 7
    INVALID_MEDIA = 8


# Keep backward-compatible alias
MediaState = OcpMediaState


class OvosCommonPlayMediaStateData(BaseModel):
    """Current low-level media pipeline state from the OCP audio layer."""
    state: OcpMediaState = Field(..., description="The current media state.")


class OvosCommonPlayMediaStateMessage(OpenVoiceOSMessage):
    """Broadcast the current low-level media pipeline state.

    Emitted by `ovos-audio` whenever the OCP audio backend transitions
    between states (loading, buffering, playing, end-of-media, etc.).
    OCP skills and the GUI subscribe to update progress indicators and
    handle end-of-track events.
    """
    message_type: str = "ovos.common_play.media.state"
    data: OvosCommonPlayMediaStateData


class OvosCommonPlayCorkMessage(OpenVoiceOSMessage):
    """Pause OCP audio output to make room for TTS speech.

    Emitted by `ovos-audio` before speaking — OCP audio is suspended
    ('corked') so the TTS output is clearly audible. Counterpart:
    `ovos.common_play.uncork` resumes audio after speech ends.
    """
    message_type: str = "ovos.common_play.cork"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlayDuckMessage(OpenVoiceOSMessage):
    """Lower OCP audio volume to make TTS speech audible over music.

    Emitted by `ovos-audio` as an alternative to full corking — audio
    continues at reduced volume while TTS plays. The TTS plugin decides
    whether to cork or duck based on configuration.
    Counterpart: `ovos.common_play.unduck`.
    """
    message_type: str = "ovos.common_play.duck"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlayUncorkMessage(OpenVoiceOSMessage):
    """Resume OCP audio output after a cork pause.

    Emitted by `ovos-audio` when TTS speech finishes and the OCP audio
    stream can resume at full volume. Counterpart: `ovos.common_play.cork`.
    """
    message_type: str = "ovos.common_play.uncork"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlayUnduckMessage(OpenVoiceOSMessage):
    """Restore OCP audio to full volume after ducking.

    Emitted by `ovos-audio` when TTS speech finishes and the volume
    reduction applied by `ovos.common_play.duck` should be lifted.
    """
    message_type: str = "ovos.common_play.unduck"
    data: Dict[str, Any] = Field(default_factory=dict)
