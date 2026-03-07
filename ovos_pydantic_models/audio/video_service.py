from typing import Dict, Any, List, Optional, Union, Tuple

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


class OvosVideoServicePlayData(BaseModel):
    """Payload for starting video playback via the OVOS video service."""
    tracks: List[Union[str, Tuple[str, str]]] = Field(
        ..., description="List of video tracks (URI strings or (URI, MIME) tuples)."
    )
    repeat: bool = Field(False, description="Whether to repeat the playlist.")
    utterance: Optional[str] = Field(None, description="Original utterance for backend selection.")


class OvosVideoServicePlayMessage(OpenVoiceOSMessage):
    """Start video playback via the OVOS video service.

    Emitted by OCP skills when the selected media type is video. The video
    service selects an appropriate backend (e.g. mpv, VLC) and begins
    playback. The GUI video player is also activated automatically.
    """
    message_type: str = "ovos.video.service.play"
    data: OvosVideoServicePlayData


class OvosVideoServiceStopMessage(OpenVoiceOSMessage):
    """Stop video playback and dismiss the video player.

    Emitted by skills, the stop service, or the GUI dismiss button. The
    video backend halts playback and any GUI overlay is hidden.
    """
    message_type: str = "ovos.video.service.stop"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosVideoServicePauseMessage(OpenVoiceOSMessage):
    """Pause the currently playing video.

    Emitted by skills or GUI controls. The video backend suspends playback;
    resume with `ovos.video.service.resume`.
    """
    message_type: str = "ovos.video.service.pause"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosVideoServiceResumeMessage(OpenVoiceOSMessage):
    """Resume video playback after a pause.

    Emitted by skills or GUI controls. The video backend continues from
    the paused position.
    """
    message_type: str = "ovos.video.service.resume"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosVideoServiceNextMessage(OpenVoiceOSMessage):
    """Skip to the next video track in the playlist.

    Emitted by skills or transport controls. The video backend advances
    to the next queued URI.
    """
    message_type: str = "ovos.video.service.next"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosVideoServicePrevMessage(OpenVoiceOSMessage):
    """Skip back to the previous video track in the playlist.

    Emitted by skills or transport controls. The video backend returns
    to the previously played URI.
    """
    message_type: str = "ovos.video.service.prev"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosVideoServiceSeekForwardData(BaseModel):
    """Relative forward seek amount for the video player."""
    seconds: float = Field(1.0, description="Seconds to seek forward.")


class OvosVideoServiceSeekForwardMessage(OpenVoiceOSMessage):
    """Seek the video forward by a relative number of seconds.

    Emitted by skills handling 'skip forward' voice commands or GUI scrub
    gestures. The video backend advances the playback position by `seconds`.
    """
    message_type: str = "ovos.video.service.seek_forward"
    data: OvosVideoServiceSeekForwardData


class OvosVideoServiceSeekBackwardData(BaseModel):
    """Relative backward seek amount for the video player."""
    seconds: float = Field(1.0, description="Seconds to seek backward.")


class OvosVideoServiceSeekBackwardMessage(OpenVoiceOSMessage):
    """Seek the video backward by a relative number of seconds.

    Emitted by skills handling 'go back' voice commands or GUI scrub
    gestures. The video backend rewinds the playback position by `seconds`.
    """
    message_type: str = "ovos.video.service.seek_backward"
    data: OvosVideoServiceSeekBackwardData


class OvosVideoServiceSetTrackPositionData(BaseModel):
    """Absolute seek target for the video player."""
    position: int = Field(..., description="Position in milliseconds.")


class OvosVideoServiceSetTrackPositionMessage(OpenVoiceOSMessage):
    """Seek the currently playing video to an absolute position.

    Emitted by skills implementing precise voice-controlled seek
    (e.g. 'jump to the 10-minute mark'). The video backend seeks immediately.
    """
    message_type: str = "ovos.video.service.set_track_position"
    data: OvosVideoServiceSetTrackPositionData


class OvosVideoServiceGetTrackPositionMessage(OpenVoiceOSMessage):
    """Query the current playback position of the active video.

    Emitted by skills and GUIs showing a progress bar. The video backend
    replies with the current position in milliseconds.
    """
    message_type: str = "ovos.video.service.get_track_position"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosVideoServiceGetTrackLengthMessage(OpenVoiceOSMessage):
    """Query the total duration of the currently playing video.

    Emitted by skills and GUIs that need to display total length or
    calculate seek percentages. The video backend replies with duration in ms.
    """
    message_type: str = "ovos.video.service.get_track_length"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosVideoServiceTrackInfoMessage(OpenVoiceOSMessage):
    """Request metadata for the currently playing video.

    Emitted by skills or GUIs that display now-playing information
    (title, episode, thumbnail). The video backend replies with available metadata.
    """
    message_type: str = "ovos.video.service.track_info"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosVideoServiceListBackendsMessage(OpenVoiceOSMessage):
    """Request a list of all available video backends.

    Emitted by settings GUIs and configuration tools. The video service
    replies with the names and capabilities of each installed backend.
    """
    message_type: str = "ovos.video.service.list_backends"
    data: Dict[str, Any] = Field(default_factory=dict)
