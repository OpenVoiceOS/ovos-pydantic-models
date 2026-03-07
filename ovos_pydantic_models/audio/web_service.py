from typing import Dict, Any, List, Optional, Union, Tuple

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


class OvosWebServicePlayData(BaseModel):
    """Payload for loading a web page or web-based media via the OVOS web service."""
    tracks: List[Union[str, Tuple[str, str]]] = Field(
        ..., description="List of web tracks (URI strings or (URI, MIME) tuples)."
    )
    repeat: bool = Field(False, description="Whether to repeat the playlist.")
    utterance: Optional[str] = Field(None, description="Original utterance for backend selection.")


class OvosWebServicePlayMessage(OpenVoiceOSMessage):
    """Open a URL or web-based media in the OVOS web service.

    Emitted by OCP skills when the selected media type is a web page or
    web stream (e.g. a YouTube embed, a web radio player). The web service
    renders the URL in the embedded browser and activates the GUI web view.
    """
    message_type: str = "ovos.web.service.play"
    data: OvosWebServicePlayData


class OvosWebServiceStopMessage(OpenVoiceOSMessage):
    """Stop the web service and dismiss the web view.

    Emitted by skills, the stop service, or the GUI. The web backend
    navigates away and the GUI overlay is hidden.
    """
    message_type: str = "ovos.web.service.stop"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosWebServicePauseMessage(OpenVoiceOSMessage):
    """Pause media playing inside the web view.

    Emitted by skills or GUI controls. The web backend attempts to pause
    in-page media (e.g. via JavaScript). Not all web pages support this.
    """
    message_type: str = "ovos.web.service.pause"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosWebServiceResumeMessage(OpenVoiceOSMessage):
    """Resume media playing inside the web view after a pause.

    Emitted by skills or GUI controls. The web backend resumes in-page
    media from the paused position.
    """
    message_type: str = "ovos.web.service.resume"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosWebServiceNextMessage(OpenVoiceOSMessage):
    """Navigate to the next URL in the web service playlist.

    Emitted by skills or transport controls. The web backend loads the
    next URI from the queue.
    """
    message_type: str = "ovos.web.service.next"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosWebServicePrevMessage(OpenVoiceOSMessage):
    """Navigate to the previous URL in the web service playlist.

    Emitted by skills or transport controls. The web backend loads the
    previously visited URI.
    """
    message_type: str = "ovos.web.service.prev"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosWebServiceSeekForwardData(BaseModel):
    """Relative forward seek amount for in-page web media."""
    seconds: float = Field(1.0, description="Seconds to seek forward.")


class OvosWebServiceSeekForwardMessage(OpenVoiceOSMessage):
    """Seek in-page web media forward by a relative number of seconds.

    Emitted by skills. The web backend injects JavaScript to advance the
    in-page media player. Support depends on the loaded web page.
    """
    message_type: str = "ovos.web.service.seek_forward"
    data: OvosWebServiceSeekForwardData


class OvosWebServiceSeekBackwardData(BaseModel):
    """Relative backward seek amount for in-page web media."""
    seconds: float = Field(1.0, description="Seconds to seek backward.")


class OvosWebServiceSeekBackwardMessage(OpenVoiceOSMessage):
    """Seek in-page web media backward by a relative number of seconds.

    Emitted by skills. The web backend injects JavaScript to rewind the
    in-page media player. Support depends on the loaded web page.
    """
    message_type: str = "ovos.web.service.seek_backward"
    data: OvosWebServiceSeekBackwardData


class OvosWebServiceSetTrackPositionData(BaseModel):
    """Absolute seek target for in-page web media."""
    position: int = Field(..., description="Position in milliseconds.")


class OvosWebServiceSetTrackPositionMessage(OpenVoiceOSMessage):
    """Seek in-page web media to an absolute position.

    Emitted by skills implementing voice-controlled seek. The web backend
    injects JavaScript to seek to the requested position.
    """
    message_type: str = "ovos.web.service.set_track_position"
    data: OvosWebServiceSetTrackPositionData


class OvosWebServiceGetTrackPositionMessage(OpenVoiceOSMessage):
    """Query the current position of in-page web media.

    Emitted by skills or GUIs. The web backend reads the current playback
    position via JavaScript and replies with the value in milliseconds.
    """
    message_type: str = "ovos.web.service.get_track_position"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosWebServiceGetTrackLengthMessage(OpenVoiceOSMessage):
    """Query the total duration of in-page web media.

    Emitted by skills or GUIs. The web backend reads the media duration
    via JavaScript and replies with the value in milliseconds.
    """
    message_type: str = "ovos.web.service.get_track_length"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosWebServiceTrackInfoMessage(OpenVoiceOSMessage):
    """Request metadata for the currently loaded web page or in-page media.

    Emitted by skills or GUIs. The web backend returns available page
    metadata (title, URL, media duration).
    """
    message_type: str = "ovos.web.service.track_info"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosWebServiceListBackendsMessage(OpenVoiceOSMessage):
    """Request a list of all available web backends.

    Emitted by settings GUIs and configuration tools. The web service
    replies with the names and capabilities of each installed web backend.
    """
    message_type: str = "ovos.web.service.list_backends"
    data: Dict[str, Any] = Field(default_factory=dict)
