from typing import Dict, Any, List, Optional, Union, Tuple

from pydantic import BaseModel, Field, ConfigDict

from ovos_pydantic_models.message import OpenVoiceOSMessage


# --- Audio Service Message Models ---

class AudioServicePlayData(BaseModel):
    """Payload for starting audio playback via the legacy audio service."""
    tracks: List[Union[str, Tuple[str, str]]] = Field(
        ..., description="List of tracks to play. Each track can be a URI string or a tuple of (URI, MIME_type)."
    )
    repeat: bool = Field(False, description="Whether the playlist should repeat.")
    utterance: Optional[str] = Field(
        None, description="Original utterance, used to determine preferred service."
    )


class AudioServicePlayMessage(OpenVoiceOSMessage):
    """Start audio playback via the legacy `mycroft.audio.service` layer.

    Emitted by skills (via `self.CPS_play()` or the AudioService helper) to
    begin playing one or more tracks. `ovos-audio` selects the appropriate
    backend (vlc, mpv, simple, etc.) based on `utterance` and URI MIME type.
    For OCP-based playback prefer `ovos.audio.service.play` instead.
    """
    message_type: str = "mycroft.audio.service.play"
    data: AudioServicePlayData


class AudioServiceQueueData(BaseModel):
    """Payload for appending tracks to the current audio queue."""
    tracks: List[Union[str, Tuple[str, str]]] = Field(
        ..., description="List of tracks to queue. Each track can be a URI string or a tuple of (URI, MIME_type)."
    )


class AudioServiceQueueMessage(OpenVoiceOSMessage):
    """Append tracks to the active audio queue without interrupting playback.

    Emitted by skills that want to enqueue additional content after the
    currently playing track. Handled by `ovos-audio`.
    """
    message_type: str = "mycroft.audio.service.queue"
    data: AudioServiceQueueData


class AudioServicePauseMessage(OpenVoiceOSMessage):
    """Pause the currently playing audio track.

    Emitted by skills or external components. The active audio backend
    suspends playback; state can be resumed with `mycroft.audio.service.resume`.
    """
    message_type: str = "mycroft.audio.service.pause"
    data: Dict[str, Any] = Field(default_factory=dict)


class AudioServiceResumeMessage(OpenVoiceOSMessage):
    """Resume playback after a `mycroft.audio.service.pause`.

    Emitted by skills or external components. The active audio backend
    continues from the paused position.
    """
    message_type: str = "mycroft.audio.service.resume"
    data: Dict[str, Any] = Field(default_factory=dict)


class AudioServiceNextMessage(OpenVoiceOSMessage):
    """Skip to the next track in the audio queue.

    Emitted by skills or transport controls. The active audio backend
    advances to the next queued URI immediately.
    """
    message_type: str = "mycroft.audio.service.next"
    data: Dict[str, Any] = Field(default_factory=dict)


class AudioServicePrevMessage(OpenVoiceOSMessage):
    """Skip back to the previous track in the audio queue.

    Emitted by skills or transport controls. The active audio backend
    returns to the previously played URI.
    """
    message_type: str = "mycroft.audio.service.prev"
    data: Dict[str, Any] = Field(default_factory=dict)


class AudioServiceStopMessage(OpenVoiceOSMessage):
    """Stop audio playback and clear the queue.

    Emitted by skills, the stop service, or external components. The active
    audio backend halts playback and discards any remaining queued tracks.
    """
    message_type: str = "mycroft.audio.service.stop"
    data: Dict[str, Any] = Field(default_factory=dict)


class AudioPlayingTrackData(BaseModel):
    """Notification payload identifying the track that just started playing."""
    track: str = Field(..., description="The URI of the track that is about to start playing.")


class AudioPlayingTrackMessage(OpenVoiceOSMessage):
    """Broadcast that a new audio track has started playing.

    Emitted by `ovos-audio` each time the active backend advances to a new
    URI. Useful for skills and GUI that display now-playing information.
    """
    message_type: str = "mycroft.audio.playing_track"
    data: AudioPlayingTrackData


class AudioQueueEndMessage(OpenVoiceOSMessage):
    """Signal that all tracks in the audio queue have finished playing.

    Emitted by `ovos-audio` when the last track in the queue ends and
    `repeat` is False. Skills that launched playback can subscribe to know
    when to clean up state.
    """
    message_type: str = "mycroft.audio.queue_end"
    data: Dict[str, Any] = Field(default_factory=dict)


class AudioServiceTrackInfoReplyData(BaseModel, extra='allow'):
    """Track metadata returned by the active audio backend.

    Content varies by backend — VLC returns duration/title/artist;
    simpler backends may return only the URI.
    """


class AudioServiceTrackInfoMessage(OpenVoiceOSMessage):
    """Request metadata for the currently playing track.

    Emitted by the OCP bus API or skills that need to display or log
    now-playing information. `ovos-audio` replies with
    `mycroft.audio.service.track_info_reply`.
    """
    message_type: str = "mycroft.audio.service.track_info"
    data: Dict[str, Any] = Field(default_factory=dict)


class AudioServiceTrackInfoReplyMessage(OpenVoiceOSMessage):
    """Return metadata for the currently playing track.

    Emitted by `ovos-audio` in response to `mycroft.audio.service.track_info`.
    The payload is backend-dependent and may contain title, artist, album,
    duration, and URI fields.
    """
    message_type: str = "mycroft.audio.service.track_info_reply"
    data: AudioServiceTrackInfoReplyData


class AudioServiceListBackendsReplyData(BaseModel, extra='allow'):
    """Available audio backends and their capabilities."""
    backends: Dict[str, Dict[str, Any]] = Field(
        ..., description="Dictionary of available audio backends and their properties."
    )


class AudioServiceListBackendsMessage(OpenVoiceOSMessage):
    """Request a list of all available audio backends from `ovos-audio`.

    Any component may send this; `ovos-audio` replies with
    `mycroft.audio.service.list_backends.response`. Useful for GUI settings
    panels and skill configuration helpers.
    """
    message_type: str = "mycroft.audio.service.list_backends"
    data: Dict[str, Any] = Field(default_factory=dict)


class AudioServiceListBackendsResponseMessage(OpenVoiceOSMessage):
    """Return the list of available audio backends.

    Emitted by `ovos-audio` in response to `mycroft.audio.service.list_backends`.
    Each backend entry includes `supported_uris`, `default`, and `remote` keys.
    """
    message_type: str = "mycroft.audio.service.list_backends.response"
    data: AudioServiceListBackendsReplyData


class AudioServiceGetTrackLengthReplyData(BaseModel):
    """Track duration returned by the active audio backend."""
    length: Optional[int] = Field(
        None, description="The length of the current track in milliseconds, or None if not available."
    )


class AudioServiceGetTrackLengthMessage(OpenVoiceOSMessage):
    """Query the duration of the currently playing track.

    Emitted by skills that need to display progress bars or calculate
    seek positions. `ovos-audio` replies with
    `mycroft.audio.service.get_track_length.response`.
    """
    message_type: str = "mycroft.audio.service.get_track_length"
    data: Dict[str, Any] = Field(default_factory=dict)


class AudioServiceGetTrackLengthResponseMessage(OpenVoiceOSMessage):
    """Return the duration of the currently playing track in milliseconds.

    Emitted by `ovos-audio` in response to `mycroft.audio.service.get_track_length`.
    `length` is None if the backend cannot determine duration (e.g. live streams).
    """
    message_type: str = "mycroft.audio.service.get_track_length.response"
    data: AudioServiceGetTrackLengthReplyData


class AudioServiceGetTrackPositionReplyData(BaseModel):
    """Current playback position returned by the active audio backend."""
    position: Optional[int] = Field(
        None, description="The current position of the track in milliseconds, or None if not available."
    )


class AudioServiceGetTrackPositionMessage(OpenVoiceOSMessage):
    """Query the current playback position of the active track.

    Emitted by skills and GUIs showing playback progress. `ovos-audio`
    replies with `mycroft.audio.service.get_track_position.response`.
    """
    message_type: str = "mycroft.audio.service.get_track_position"
    data: Dict[str, Any] = Field(default_factory=dict)


class AudioServiceGetTrackPositionResponseMessage(OpenVoiceOSMessage):
    """Return the current playback position in milliseconds.

    Emitted by `ovos-audio` in response to `mycroft.audio.service.get_track_position`.
    `position` is None if the backend cannot report position.
    """
    message_type: str = "mycroft.audio.service.get_track_position.response"
    data: AudioServiceGetTrackPositionReplyData


class AudioServiceSetTrackPositionData(BaseModel):
    """Seek target for the active audio backend."""
    position: int = Field(..., description="The position to set the track to, in milliseconds.")


class AudioServiceSetTrackPositionMessage(OpenVoiceOSMessage):
    """Seek the currently playing track to an absolute position.

    Emitted by skills implementing voice-controlled seek (e.g. 'jump to
    two minutes'). The active audio backend seeks immediately.
    """
    message_type: str = "mycroft.audio.service.set_track_position"
    data: AudioServiceSetTrackPositionData


class AudioServiceSeekForwardData(BaseModel):
    """Relative forward seek amount."""
    seconds: int = Field(1, description="Number of seconds to seek forward.")


class AudioServiceSeekForwardMessage(OpenVoiceOSMessage):
    """Seek forward by a relative number of seconds.

    Emitted by skills handling 'skip forward' voice commands. The active
    audio backend advances the playback position by `seconds`.
    """
    message_type: str = "mycroft.audio.service.seek_forward"
    data: AudioServiceSeekForwardData


class AudioServiceSeekBackwardData(BaseModel):
    """Relative backward seek amount."""
    seconds: int = Field(1, description="Number of seconds to seek backward.")


class AudioServiceSeekBackwardMessage(OpenVoiceOSMessage):
    """Seek backward by a relative number of seconds.

    Emitted by skills handling 'go back' voice commands. The active audio
    backend rewinds the playback position by `seconds`.
    """
    message_type: str = "mycroft.audio.service.seek_backward"
    data: AudioServiceSeekBackwardData


# --- OVOS namespace aliases (ovos.audio.service.*) ---
# These mirror mycroft.audio.service.* exactly, using the modern ovos.* prefix.

class OvosAudioServicePlayMessage(OpenVoiceOSMessage):
    """Start audio playback via the modern `ovos.audio.service` namespace.

    Functionally identical to `AudioServicePlayMessage` (`mycroft.audio.service.play`)
    but uses the OVOS-native prefix. Prefer this over the legacy `mycroft.*` form
    in new skills and components.
    """
    message_type: str = "ovos.audio.service.play"
    data: AudioServicePlayData


class OvosAudioServiceQueueMessage(OpenVoiceOSMessage):
    """Append tracks to the audio queue (OVOS namespace).

    OVOS-native alias for `AudioServiceQueueMessage`. See that class for full docs.
    """
    message_type: str = "ovos.audio.service.queue"
    data: AudioServiceQueueData


class OvosAudioServicePauseMessage(OpenVoiceOSMessage):
    """Pause audio playback (OVOS namespace).

    OVOS-native alias for `AudioServicePauseMessage`. See that class for full docs.
    """
    message_type: str = "ovos.audio.service.pause"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosAudioServiceResumeMessage(OpenVoiceOSMessage):
    """Resume audio playback (OVOS namespace).

    OVOS-native alias for `AudioServiceResumeMessage`. See that class for full docs.
    """
    message_type: str = "ovos.audio.service.resume"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosAudioServiceNextMessage(OpenVoiceOSMessage):
    """Skip to the next track (OVOS namespace).

    OVOS-native alias for `AudioServiceNextMessage`. See that class for full docs.
    """
    message_type: str = "ovos.audio.service.next"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosAudioServicePrevMessage(OpenVoiceOSMessage):
    """Skip to the previous track (OVOS namespace).

    OVOS-native alias for `AudioServicePrevMessage`. See that class for full docs.
    """
    message_type: str = "ovos.audio.service.prev"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosAudioServiceStopMessage(OpenVoiceOSMessage):
    """Stop audio playback and clear the queue (OVOS namespace).

    OVOS-native alias for `AudioServiceStopMessage`. See that class for full docs.
    """
    message_type: str = "ovos.audio.service.stop"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosAudioServiceSeekForwardMessage(OpenVoiceOSMessage):
    """Seek forward by a relative number of seconds (OVOS namespace).

    OVOS-native alias for `AudioServiceSeekForwardMessage`. See that class for full docs.
    """
    message_type: str = "ovos.audio.service.seek_forward"
    data: AudioServiceSeekForwardData


class OvosAudioServiceSeekBackwardMessage(OpenVoiceOSMessage):
    """Seek backward by a relative number of seconds (OVOS namespace).

    OVOS-native alias for `AudioServiceSeekBackwardMessage`. See that class for full docs.
    """
    message_type: str = "ovos.audio.service.seek_backward"
    data: AudioServiceSeekBackwardData


class OvosAudioServiceSetTrackPositionMessage(OpenVoiceOSMessage):
    """Seek to an absolute position in milliseconds (OVOS namespace).

    OVOS-native alias for `AudioServiceSetTrackPositionMessage`. See that class for full docs.
    """
    message_type: str = "ovos.audio.service.set_track_position"
    data: AudioServiceSetTrackPositionData


class OvosAudioServiceGetTrackLengthMessage(OpenVoiceOSMessage):
    """Query the duration of the currently playing track (OVOS namespace).

    OVOS-native alias for `AudioServiceGetTrackLengthMessage`. See that class for full docs.
    """
    message_type: str = "ovos.audio.service.get_track_length"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosAudioServiceGetTrackPositionMessage(OpenVoiceOSMessage):
    """Query the current playback position (OVOS namespace).

    OVOS-native alias for `AudioServiceGetTrackPositionMessage`. See that class for full docs.
    """
    message_type: str = "ovos.audio.service.get_track_position"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosAudioServiceTrackInfoMessage(OpenVoiceOSMessage):
    """Request metadata for the currently playing track (OVOS namespace).

    OVOS-native alias for requesting track info. `ovos-audio` replies with
    `mycroft.audio.service.track_info_reply`.
    """
    message_type: str = "ovos.audio.service.track_info"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosAudioServiceListBackendsMessage(OpenVoiceOSMessage):
    """Request the list of available audio backends (OVOS namespace).

    OVOS-native alias for `AudioServiceListBackendsMessage`. See that class for full docs.
    """
    message_type: str = "ovos.audio.service.list_backends"
    data: Dict[str, Any] = Field(default_factory=dict)


# --- OVOS-namespace audio service events (PIPELINE-1 §9.6 / STOP-1 §5.3) ---

class OvosAudioPlayingTrackMessage(OpenVoiceOSMessage):
    """Emitted by ovos-audio when a new track starts in the OVOS audio namespace.

    OVOS-namespace counterpart to ``mycroft.audio.playing_track``.
    """
    message_type: str = "ovos.audio.playing_track"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosAudioQueueEndMessage(OpenVoiceOSMessage):
    """Emitted by ovos-audio when the entire track queue finishes.

    OVOS-namespace counterpart to ``mycroft.audio.queue_end``.
    """
    message_type: str = "ovos.audio.queue_end"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosStopMessage(OpenVoiceOSMessage):
    """Request all OVOS subsystems to stop their current activity.

    OVOS-namespace stop broadcast (STOP-1 §5.3). ovos-audio halts both TTS
    and playback; other services that subscribe to ``mycroft.stop`` also
    listen here when ``legacy_namespace`` is disabled.
    """
    message_type: str = "ovos.stop"
    data: Dict[str, Any] = Field(default_factory=dict)
