from typing import Dict, Any, List, Optional, Union, Tuple

from pydantic import BaseModel, Field, ConfigDict

from ovos_pydantic_models.message import OpenVoiceOSMessage


# --- Audio Service Message Models ---

class AudioServicePlayData(BaseModel):
    """Data for `mycroft.audio.service.play` message."""
    # Corrected type hint: List can contain a mix of strings or (str, str) tuples
    tracks: List[Union[str, Tuple[str, str]]] = Field(
        ..., description="List of tracks to play. Each track can be a URI string or a tuple of (URI, MIME_type)."
    )
    repeat: bool = Field(False, description="Whether the playlist should repeat.")
    utterance: Optional[str] = Field(
        None, description="Original utterance, used to determine preferred service."
    )


class AudioServicePlayMessage(OpenVoiceOSMessage):
    """Message for `mycroft.audio.service.play`."""
    message_type: str = "mycroft.audio.service.play"
    data: AudioServicePlayData


class AudioServiceQueueData(BaseModel):
    """Data for `mycroft.audio.service.queue` message."""
    # Corrected type hint: List can contain a mix of strings or (str, str) tuples
    tracks: List[Union[str, Tuple[str, str]]] = Field(
        ..., description="List of tracks to queue. Each track can be a URI string or a tuple of (URI, MIME_type)."
    )


class AudioServiceQueueMessage(OpenVoiceOSMessage):
    """Message for `mycroft.audio.service.queue`."""
    message_type: str = "mycroft.audio.service.queue"
    data: AudioServiceQueueData


class AudioServicePauseMessage(OpenVoiceOSMessage):
    """Message for `mycroft.audio.service.pause`."""
    message_type: str = "mycroft.audio.service.pause"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for pause command.")


class AudioServiceResumeMessage(OpenVoiceOSMessage):
    """Message for `mycroft.audio.service.resume`."""
    message_type: str = "mycroft.audio.service.resume"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for resume command.")


class AudioServiceNextMessage(OpenVoiceOSMessage):
    """Message for `mycroft.audio.service.next`."""
    message_type: str = "mycroft.audio.service.next"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for next track command.")


class AudioServicePrevMessage(OpenVoiceOSMessage):
    """Message for `mycroft.audio.service.prev`."""
    message_type: str = "mycroft.audio.service.prev"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for previous track command.")


class AudioServiceStopMessage(OpenVoiceOSMessage):
    """Message for `mycroft.audio.service.stop`."""
    message_type: str = "mycroft.audio.service.stop"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for stop command.")


class AudioPlayingTrackData(BaseModel):
    """Data for `mycroft.audio.playing_track` message."""
    track: str = Field(..., description="The URI of the track that is about to start playing.")


class AudioPlayingTrackMessage(OpenVoiceOSMessage):
    """Message for `mycroft.audio.playing_track`."""
    message_type: str = "mycroft.audio.playing_track"
    data: AudioPlayingTrackData


class AudioQueueEndMessage(OpenVoiceOSMessage):
    """Message for `mycroft.audio.queue_end`."""
    message_type: str = "mycroft.audio.queue_end"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for queue end event.")


class AudioServiceTrackInfoReplyData(BaseModel, extra='allow'):
    """Data for `mycroft.audio.service.track_info_reply` message."""
    # This can be any dictionary, as the `track_info()` method returns a dict.
    # A more specific schema could be defined if the structure of track_info is known.


class AudioServiceTrackInfoReplyMessage(OpenVoiceOSMessage):
    """Message for `mycroft.audio.service.track_info_reply`."""
    message_type: str = "mycroft.audio.service.track_info_reply"
    data: AudioServiceTrackInfoReplyData


class AudioServiceListBackendsReplyData(BaseModel, extra='allow'):
    """Data for `mycroft.audio.service.list_backends` response message."""
    # The keys are backend names (str), and values are dictionaries
    # with 'supported_uris', 'default', 'remote'.
    backends: Dict[str, Dict[str, Any]] = Field(
        ..., description="Dictionary of available audio backends and their properties."
    )


class AudioServiceListBackendsMessage(OpenVoiceOSMessage):
    """Message for `mycroft.audio.service.list_backends`."""
    message_type: str = "mycroft.audio.service.list_backends"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for list backends command.")


class AudioServiceListBackendsResponseMessage(OpenVoiceOSMessage):
    """Response message for `mycroft.audio.service.list_backends`."""
    message_type: str = "mycroft.audio.service.list_backends.response"
    data: AudioServiceListBackendsReplyData


class AudioServiceGetTrackLengthReplyData(BaseModel):
    """Data for `mycroft.audio.service.get_track_length` response message."""
    length: Optional[int] = Field(
        None, description="The length of the current track in milliseconds, or None if not available."
    )


class AudioServiceGetTrackLengthMessage(OpenVoiceOSMessage):
    """Message for `mycroft.audio.service.get_track_length`."""
    message_type: str = "mycroft.audio.service.get_track_length"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for get track length command.")


class AudioServiceGetTrackLengthResponseMessage(OpenVoiceOSMessage):
    """Response message for `mycroft.audio.service.get_track_length`."""
    message_type: str = "mycroft.audio.service.get_track_length.response"
    data: AudioServiceGetTrackLengthReplyData


class AudioServiceGetTrackPositionReplyData(BaseModel):
    """Data for `mycroft.audio.service.get_track_position` response message."""
    position: Optional[int] = Field(
        None, description="The current position of the track in milliseconds, or None if not available."
    )


class AudioServiceGetTrackPositionMessage(OpenVoiceOSMessage):
    """Message for `mycroft.audio.service.get_track_position`."""
    message_type: str = "mycroft.audio.service.get_track_position"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for get track position command.")


class AudioServiceGetTrackPositionResponseMessage(OpenVoiceOSMessage):
    """Response message for `mycroft.audio.service.get_track_position`."""
    message_type: str = "mycroft.audio.service.get_track_position.response"
    data: AudioServiceGetTrackPositionReplyData


class AudioServiceSetTrackPositionData(BaseModel):
    """Data for `mycroft.audio.service.set_track_position` message."""
    position: int = Field(..., description="The position to set the track to, in milliseconds.")


class AudioServiceSetTrackPositionMessage(OpenVoiceOSMessage):
    """Message for `mycroft.audio.service.set_track_position`."""
    message_type: str = "mycroft.audio.service.set_track_position"
    data: AudioServiceSetTrackPositionData


class AudioServiceSeekForwardData(BaseModel):
    """Data for `mycroft.audio.service.seek_forward` message."""
    seconds: int = Field(1, description="Number of seconds to seek forward.")


class AudioServiceSeekForwardMessage(OpenVoiceOSMessage):
    """Message for `mycroft.audio.service.seek_forward`."""
    message_type: str = "mycroft.audio.service.seek_forward"
    data: AudioServiceSeekForwardData


class AudioServiceSeekBackwardData(BaseModel):
    """Data for `mycroft.audio.service.seek_backward` message."""
    seconds: int = Field(1, description="Number of seconds to seek backward.")


class AudioServiceSeekBackwardMessage(OpenVoiceOSMessage):
    """Message for `mycroft.audio.service.seek_backward`."""
    message_type: str = "mycroft.audio.service.seek_backward"
    data: AudioServiceSeekBackwardData


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Demonstrating Audio Service Message Models ---")

    # Example: mycroft.audio.service.play
    play_msg_data = AudioServicePlayData(
        tracks=["file:///path/to/song.mp3", ("http://stream.url/radio", "audio/mpeg")],
        repeat=True,
        utterance="play some music with vlc"
    )
    play_message = AudioServicePlayMessage(data=play_msg_data)
    print(f"\nPlay Message:\n{play_message.model_dump_json(indent=2)}")

    # Example: mycroft.audio.playing_track
    playing_track_msg_data = AudioPlayingTrackData(track="file:///path/to/current_song.mp3")
    playing_track_message = AudioPlayingTrackMessage(data=playing_track_msg_data)
    print(f"\nPlaying Track Message:\n{playing_track_message.model_dump_json(indent=2)}")

    # Example: mycroft.audio.service.get_track_length and its response
    get_length_message = AudioServiceGetTrackLengthMessage()
    print(f"\nGet Track Length Request Message:\n{get_length_message.model_dump_json(indent=2)}")

    get_length_response_data = AudioServiceGetTrackLengthReplyData(length=180000)  # 3 minutes
    get_length_response_message = AudioServiceGetTrackLengthResponseMessage(data=get_length_response_data)
    print(f"\nGet Track Length Response Message:\n{get_length_response_message.model_dump_json(indent=2)}")

    # Example: mycroft.audio.service.list_backends and its response
    list_backends_request = AudioServiceListBackendsMessage()
    print(f"\nList Backends Request Message:\n{list_backends_request.model_dump_json(indent=2)}")

    list_backends_response_data = AudioServiceListBackendsReplyData(
        backends={
            "VLC": {"supported_uris": ["file", "http"], "default": True, "remote": False},
            "OCP": {"supported_uris": ["youtube", "spotify"], "default": False, "remote": True}
        }
    )
    list_backends_response = AudioServiceListBackendsResponseMessage(data=list_backends_response_data)
    print(f"\nList Backends Response Message:\n{list_backends_response.model_dump_json(indent=2)}")
