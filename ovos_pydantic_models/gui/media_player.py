from typing import Dict, Any, Optional, Union

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


class GuiPlayerMediaPlayData(BaseModel):
    """Payload for loading and playing a media track in the GUI media player."""
    track: Union[str, Dict[str, Any]] = Field(..., description="Track URI string or media dict.")
    mime_type: Optional[str] = Field(None, description="MIME type of the media.")
    model_config = {"extra": "allow"}


class GuiPlayerMediaPlayMessage(OpenVoiceOSMessage):
    """Tell the GUI media player to load and begin playing a track.

    Emitted by OCP skills when they hand off a media track to the
    embedded GUI player (e.g. the built-in video player in ovos-shell).
    The GUI player renders the video/audio with native controls and
    reports status back via `gui.player.media.service.sync.status`.
    """
    message_type: str = "gui.player.media.service.play"
    data: GuiPlayerMediaPlayData


class GuiPlayerMediaPauseMessage(OpenVoiceOSMessage):
    """Pause the GUI media player.

    Emitted by skills, transport controls, or the TTS cork mechanism
    when speech needs to be heard over media. The GUI player suspends
    playback; resume with `gui.player.media.service.resume`.
    """
    message_type: str = "gui.player.media.service.pause"
    data: Dict[str, Any] = Field(default_factory=dict)


class GuiPlayerMediaResumeMessage(OpenVoiceOSMessage):
    """Resume the GUI media player after a pause.

    Emitted by skills, transport controls, or the TTS uncork mechanism
    when speech has finished. The GUI player continues from the paused position.
    """
    message_type: str = "gui.player.media.service.resume"
    data: Dict[str, Any] = Field(default_factory=dict)


class GuiPlayerMediaStopMessage(OpenVoiceOSMessage):
    """Stop the GUI media player and dismiss the player view.

    Emitted by skills, the stop service, or the GUI dismiss button.
    The player halts playback and may hand control back to the homescreen.
    """
    message_type: str = "gui.player.media.service.stop"
    data: Dict[str, Any] = Field(default_factory=dict)


class GuiPlayerMediaSetMetaData(BaseModel):
    """Now-playing metadata to display in the GUI media player overlay."""
    title: Optional[str] = Field(None, description="Track title.")
    image: Optional[str] = Field(None, description="URL or path to album art.")
    artist: Optional[str] = Field(None, description="Artist name.")
    model_config = {"extra": "allow"}


class GuiPlayerMediaSetMetaMessage(OpenVoiceOSMessage):
    """Push now-playing metadata to the GUI media player overlay.

    Emitted by OCP skills after starting playback to populate the
    player's title, artist, and album art display. The GUI player
    renders the metadata alongside the media.
    """
    message_type: str = "gui.player.media.service.set.meta"
    data: GuiPlayerMediaSetMetaData


class GuiPlayerMediaGetMetaMessage(OpenVoiceOSMessage):
    """Request the currently displayed now-playing metadata from the GUI player.

    Emitted by skills or GUIs that need to read the metadata the player
    is currently showing (e.g. to announce it via TTS).
    """
    message_type: str = "gui.player.media.service.get.meta"
    data: Dict[str, Any] = Field(default_factory=dict)


class GuiPlayerMediaSyncStatusData(BaseModel):
    """Sync status string from the GUI media player."""
    status: str = Field(..., description="Current sync status string.")


class GuiPlayerMediaSyncStatusMessage(OpenVoiceOSMessage):
    """Report the GUI media player's sync/buffering status.

    Emitted by the GUI media player to inform OCP skills and the audio
    service about the current buffering or synchronization state
    (e.g. 'buffering', 'synced', 'stalled').
    """
    message_type: str = "gui.player.media.service.sync.status"
    data: GuiPlayerMediaSyncStatusData


class GuiPlayerMediaCurrentStatusData(BaseModel):
    """Current playback state reported by the GUI media player."""
    status: str = Field(..., description="Current media playback status.")


class GuiPlayerMediaCurrentStatusMessage(OpenVoiceOSMessage):
    """Report the GUI media player's current playback status.

    Emitted by the GUI player whenever its state changes (playing, paused,
    stopped, end-of-media). OCP skills and the audio service use this to
    track playback progress and decide when to advance the queue.
    """
    message_type: str = "gui.player.media.service.current.media.status"
    data: GuiPlayerMediaCurrentStatusData


class GuiPlayerMediaGetNextMessage(OpenVoiceOSMessage):
    """Request the GUI media player to advance to the next track.

    Emitted by OCP skills or transport controls when the user says
    'next' or taps the skip button in the GUI player.
    """
    message_type: str = "gui.player.media.service.get.next"
    data: Dict[str, Any] = Field(default_factory=dict)


class GuiPlayerMediaGetPreviousMessage(OpenVoiceOSMessage):
    """Request the GUI media player to go back to the previous track.

    Emitted by OCP skills or transport controls when the user says
    'previous' or taps the back button in the GUI player.
    """
    message_type: str = "gui.player.media.service.get.previous"
    data: Dict[str, Any] = Field(default_factory=dict)


class GuiPlayerMediaGetRepeatMessage(OpenVoiceOSMessage):
    """Request the current repeat mode from the GUI media player.

    Emitted by OCP skills that need to sync their repeat state with
    the GUI player's repeat button state.
    """
    message_type: str = "gui.player.media.service.get.repeat"
    data: Dict[str, Any] = Field(default_factory=dict)


class GuiPlayerMediaGetShuffleMessage(OpenVoiceOSMessage):
    """Request the current shuffle mode from the GUI media player.

    Emitted by OCP skills that need to sync their shuffle state with
    the GUI player's shuffle button state.
    """
    message_type: str = "gui.player.media.service.get.shuffle"
    data: Dict[str, Any] = Field(default_factory=dict)
