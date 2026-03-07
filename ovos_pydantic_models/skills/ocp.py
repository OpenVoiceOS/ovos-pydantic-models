from typing import Dict, Any, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


class MediaType(str, Enum):
    """Content category of a media item.

    OCP uses this to route search queries to skills that specialize in a
    particular content type and to select appropriate GUI templates.
    """
    GENERIC = "generic"
    AUDIO = "audio"
    MUSIC = "music"
    VIDEO = "video"
    SILENCE = "silence"
    PODCAST = "podcast"
    RADIO = "radio"
    NEWS = "news"
    AD = "advertisement"
    ANNOUNCEMENT = "announcement"
    COMMUNICATION = "communication"
    ALARM = "alarm"
    TIMER = "timer"
    NOTIFICATION = "notification"
    OTHER = "other"
    GAME = "game"


class MediaState(str, Enum):
    """High-level OCP playback lifecycle state visible to skills.

    Distinct from `OcpMediaState` (IntEnum) in `audio/ocp.py`, which mirrors
    Qt's low-level `QMediaPlayer.MediaStatus`. This enum tracks the logical
    state of the OCP player from the skill's perspective.
    """
    IDLE = "idle"
    LOADING = "loading"
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    END_OF_STREAM = "eos"
    BUFFERING = "buffering"
    ERROR = "error"


class MatchConfidence(float, Enum):
    """Confidence tiers for OCP search result scoring.

    OCP skills return a `match_confidence` value from `search()`. OCP picks
    the result with the highest confidence across all skills. Use these
    constants for consistent scoring rather than raw floats.
    """
    EXACT = 1.0
    VERY_HIGH = 0.9
    HIGH = 0.8
    AVERAGE = 0.5
    LOW = 0.3
    NO_MATCH = 0.0


class PlaybackType(str, Enum):
    """The rendering method an OCP media entry requires.

    OCP uses this to decide which player backend (audio, video, web, or
    skill-internal) handles the entry.
    """
    VIDEO = "video"
    AUDIO = "audio"
    WEBVIEW = "webview"
    SKILL = "skill"


class PlaybackMode(str, Enum):
    """How OCP should cycle through the playlist."""
    NORMAL = "normal"
    LOOP = "loop"
    SHUFFLE = "shuffle"
    SINGLE_LOOP = "single_loop"


class PlayerState(str, Enum):
    """Observable state of the OCP player as a whole."""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    LOADING = "loading"
    BUFFERING = "buffering"


class LoopState(str, Enum):
    """Repeat/loop mode for the OCP playlist."""
    NONE = "none"
    PLAYLIST = "playlist"
    TRACK = "track"


class TrackState(str, Enum):
    """Lifecycle state of an individual track within the OCP queue."""
    QUEUED = "queued"
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    BUFFERING = "buffering"


class BaseMediaEntry(BaseModel):
    """Base schema for a single playable media item in OCP.

    All OCP search results and playlist entries are represented as
    `MediaEntry` (or `PluginStream`) instances. The `playback` field
    tells OCP which renderer to use; `match_confidence` determines
    which result wins when multiple skills respond.
    """
    uri: str = Field(..., description="The URI of the media.")
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    image: Optional[str] = None
    playback: PlaybackType = PlaybackType.AUDIO
    match_confidence: MatchConfidence = MatchConfidence.AVERAGE
    media_type: MediaType = MediaType.GENERIC
    skill_id: Optional[str] = None
    length: Optional[int] = None  # milliseconds
    position: Optional[int] = None  # milliseconds
    bg_image: Optional[str] = None
    model_config = ConfigDict(extra='allow')


class MediaEntry(BaseMediaEntry):
    """A single playable media item returned by an OCP skill search.

    Returned from `OVOSCommonPlaybackSkill.search()` inside an
    `ovos.common_play.query.response` message. OCP sorts all results by
    `match_confidence` and `media_type` relevance, then starts the winner.
    """
    pass


class PluginStream(BaseMediaEntry):
    """A media entry that is resolved at play-time by an OCP plugin.

    Used when the actual stream URI is not known until playback starts
    (e.g. it requires a login token or real-time URL generation). OCP
    invokes the plugin identified by `plugin_id` to resolve the stream.
    """
    plugin_id: str
    stream_id: str


class Playlist(BaseModel):
    """An ordered collection of OCP media entries.

    Returned by OCP skills that want to hand OCP a full playlist rather
    than individual tracks. OCP loads all entries into its queue.
    """
    title: Optional[str] = None
    author: Optional[str] = None
    image: Optional[str] = None
    thumbnail: Optional[str] = None
    url: Optional[str] = None
    entries: List[MediaEntry] = Field(default_factory=list)
    model_config = ConfigDict(extra='allow')


# --- OVOS Common Playback Skill Message Models ---

class OvosCommonPlayQueryData(BaseModel):
    """Payload for broadcasting a media search query to all OCP skills."""
    phrase: str = Field(..., description="The search phrase from the user utterance.")
    question_type: MediaType = Field(MediaType.GENERIC, description="The media type being queried.")
    model_config = ConfigDict(extra='allow')


class OvosCommonPlayQueryMessage(OpenVoiceOSMessage):
    """Broadcast a media search query to all registered OCP skills.

    Emitted by OCP (via `ovos-workshop`) when a user asks to play something.
    Every skill that extends `OVOSCommonPlaybackSkill` receives this and
    calls `search()`. Results are returned via `ovos.common_play.query.response`.
    OCP collects all responses, picks the best match, and sends
    `ovos.common_play.skill.play` to the winning skill.
    """
    message_type: str = "ovos.common_play.query"
    data: OvosCommonPlayQueryData


class OvosCommonPlayFeaturedTracksPlayData(BaseModel):
    """Payload for requesting a skill to play its featured/default content."""
    skill_id: str = Field(..., description="The ID of the skill to request featured tracks from.")
    model_config = ConfigDict(extra='allow')


class OvosCommonPlayFeaturedTracksPlayMessage(OpenVoiceOSMessage):
    """Ask a specific OCP skill to play its featured/editorial content.

    Emitted by the OCP home screen when the user taps a skill tile without
    speaking a search phrase. The skill starts playing its default or
    recommended playlist (e.g. 'top hits', 'recently played').
    """
    message_type: str = "ovos.common_play.featured_tracks.play"
    data: OvosCommonPlayFeaturedTracksPlayData


class OvosCommonPlaySkillsGetMessage(OpenVoiceOSMessage):
    """Request information about all registered OCP skills.

    Emitted by the OCP GUI home screen to build the skill grid. Each OCP
    skill replies with `ovos.common_play.announce` containing its name,
    icon, and supported media types.
    """
    message_type: str = "ovos.common_play.skills.get"
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class OvosCommonPlaySkillPlayData(BaseModel):
    """Payload for telling a specific OCP skill to begin playback.

    Sent to the skill after it wins an OCP query. Contains the selected
    media entry, the full disambiguation list, and the intended playlist.
    """
    media: Union[MediaEntry, PluginStream, Dict[str, Any]] = Field(..., description="The media entry to play.")
    disambiguation: List[Union[MediaEntry, PluginStream, Dict[str, Any]]] = Field(
        ..., description="List of media entries for disambiguation."
    )
    playlist: List[Union[MediaEntry, PluginStream, Dict[str, Any]]] = Field(
        ..., description="The playlist of media entries."
    )
    model_config = ConfigDict(extra='allow')


class OvosCommonPlaySkillPlayMessage(OpenVoiceOSMessage):
    """Tell a specific OCP skill to begin playing a selected media entry.

    Dynamic message type: `ovos.common_play.{skill_id}.play`. Emitted by
    OCP after selecting the winning search result. The skill's
    `OVOSCommonPlaybackSkill.play()` method is called; the skill handles
    handoff to the audio/video backend.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'ovos.common_play.my-skill-id.play'.")
    data: OvosCommonPlaySkillPlayData


class OvosCommonPlaySkillPauseData(BaseModel):
    """Empty payload for a targeted skill pause command."""
    model_config = ConfigDict(extra='allow')


class OvosCommonPlaySkillPauseMessage(OpenVoiceOSMessage):
    """Tell a specific OCP skill to pause its active playback.

    Dynamic message type: `ovos.common_play.{skill_id}.pause`. Emitted by
    OCP when a global pause command arrives and the skill owns the current
    media. The skill should pause its backend and update its state.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'ovos.common_play.my-skill-id.pause'.")
    data: OvosCommonPlaySkillPauseData = Field(default_factory=OvosCommonPlaySkillPauseData)


class OvosCommonPlaySkillResumeData(BaseModel):
    """Empty payload for a targeted skill resume command."""
    model_config = ConfigDict(extra='allow')


class OvosCommonPlaySkillResumeMessage(OpenVoiceOSMessage):
    """Tell a specific OCP skill to resume its paused playback.

    Dynamic message type: `ovos.common_play.{skill_id}.resume`. Emitted by
    OCP when a global resume command arrives and the skill owns the current
    media. The skill should resume its backend from the paused position.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'ovos.common_play.my-skill-id.resume'.")
    data: OvosCommonPlaySkillResumeData = Field(default_factory=OvosCommonPlaySkillResumeData)


class OvosCommonPlaySkillNextData(BaseModel):
    """Empty payload for a targeted skill next-track command."""
    model_config = ConfigDict(extra='allow')


class OvosCommonPlaySkillNextMessage(OpenVoiceOSMessage):
    """Tell a specific OCP skill to advance to the next track.

    Dynamic message type: `ovos.common_play.{skill_id}.next`. Emitted by
    OCP when a global next command arrives and the skill owns the queue.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'ovos.common_play.my-skill-id.next'.")
    data: OvosCommonPlaySkillNextData = Field(default_factory=OvosCommonPlaySkillNextData)


class OvosCommonPlaySkillPreviousData(BaseModel):
    """Empty payload for a targeted skill previous-track command."""
    model_config = ConfigDict(extra='allow')


class OvosCommonPlaySkillPreviousMessage(OpenVoiceOSMessage):
    """Tell a specific OCP skill to go back to the previous track.

    Dynamic message type: `ovos.common_play.{skill_id}.previous`. Emitted
    by OCP when a global previous command arrives and the skill owns the queue.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'ovos.common_play.my-skill-id.previous'.")
    data: OvosCommonPlaySkillPreviousData = Field(default_factory=OvosCommonPlaySkillPreviousData)


class OvosCommonPlaySkillStopData(BaseModel):
    """Empty payload for a targeted skill stop command."""
    model_config = ConfigDict(extra='allow')


class OvosCommonPlaySkillStopMessage(OpenVoiceOSMessage):
    """Tell a specific OCP skill to stop playback completely.

    Dynamic message type: `ovos.common_play.{skill_id}.stop`. Emitted by
    OCP when a global stop command arrives and the skill owns the current
    media. The skill should halt its backend and clear its state.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'ovos.common_play.my-skill-id.stop'.")
    data: OvosCommonPlaySkillStopData = Field(default_factory=OvosCommonPlaySkillStopData)


class OvosCommonPlaySearchStopMessage(OpenVoiceOSMessage):
    """Cancel an in-progress OCP media search.

    Emitted by OCP when the user cancels a search before results arrive
    (e.g. says 'cancel' while OCP is searching). All skills that are
    still processing `ovos.common_play.query` should abort their search.
    """
    message_type: str = "ovos.common_play.search.stop"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlayAnnounceData(BaseModel):
    """An OCP skill's self-description, broadcast to the OCP home screen."""
    skill_id: str = Field(..., description="The ID of the skill announcing its OCP capabilities.")
    skill_name: str = Field(..., description="The primary name of the skill.")
    aliases: List[str] = Field(default_factory=list, description="List of aliases for the skill name.")
    thumbnail: str = Field(..., description="URL or path to the skill's icon/thumbnail.")
    media_type: Union[MediaType, List[MediaType]] = Field(
        ..., description="The media type(s) supported by the skill."
    )
    featured_tracks: bool = Field(False, description="True if the skill provides featured tracks.")
    model_config = ConfigDict(extra='allow')


class OvosCommonPlayAnnounceMessage(OpenVoiceOSMessage):
    """An OCP skill announces its capabilities to the OCP home screen.

    Emitted by OCP skills in reply to `ovos.common_play.skills.get`, and
    also at startup to register with OCP. The home screen uses this data
    to build the skill grid with icons and supported media types.
    """
    message_type: str = "ovos.common_play.announce"
    data: OvosCommonPlayAnnounceData


class OvosCommonPlayPlayData(BaseModel):
    """Payload for OCP to start playing a fully selected media entry."""
    media: Union[MediaEntry, PluginStream, Dict[str, Any]] = Field(..., description="The media entry to play.")
    disambiguation: List[Union[MediaEntry, PluginStream, Dict[str, Any]]] = Field(
        ..., description="List of media entries for disambiguation."
    )
    playlist: List[Union[MediaEntry, PluginStream, Dict[str, Any]]] = Field(
        ..., description="The playlist of media entries."
    )
    model_config = ConfigDict(extra='allow')


class OvosCommonPlayPlayMessage(OpenVoiceOSMessage):
    """Tell OCP to start playing a specific, fully resolved media entry.

    Emitted by skills (or external components) that have already resolved a
    media entry and want OCP to play it immediately without going through
    the full search pipeline. OCP routes to the appropriate skill backend.
    """
    message_type: str = "ovos.common_play.play"
    data: OvosCommonPlayPlayData


class OvosCommonPlayPlayerStateData(BaseModel):
    """Current high-level OCP player state broadcast to subscribers."""
    state: PlayerState = Field(..., description="The current state of the OCP player.")


class OvosCommonPlayPlayerStateMessage(OpenVoiceOSMessage):
    """Broadcast the OCP player's state whenever it changes.

    Emitted by OCP each time its player transitions between states
    (playing, paused, stopped, etc.). Skills and GUIs subscribe to keep
    their transport controls synchronized.
    """
    message_type: str = "ovos.common_play.player.state"
    data: OvosCommonPlayPlayerStateData


class OvosCommonPlaySkillSearchStartData(BaseModel):
    """Payload identifying the skill that has begun searching."""
    skill_id: str = Field(..., description="The ID of the skill starting a search.")
    skill_name: str = Field(..., description="The name of the skill starting the search.")
    thumbnail: str = Field(..., description="URL or path to the skill's icon/thumbnail.")
    model_config = ConfigDict(extra='allow')


class OvosCommonPlaySkillSearchStartMessage(OpenVoiceOSMessage):
    """Signal that a specific OCP skill has started processing a search query.

    Emitted by each skill at the beginning of its `search()` call. The OCP
    GUI shows a 'searching...' indicator for the skill's tile while waiting
    for results.
    """
    message_type: str = "ovos.common_play.skill.search_start"
    data: OvosCommonPlaySkillSearchStartData


class OvosCommonPlayQueryResponseData(BaseModel):
    """A single OCP skill's search results for a given query."""
    phrase: str = Field(..., description="The original search phrase.")
    skill_id: str = Field(..., description="The ID of the skill responding to the query.")
    skill_name: str = Field(..., description="The name of the skill responding.")
    thumbnail: str = Field(..., description="URL or path to the skill's icon/thumbnail.")
    results: List[Union[MediaEntry, Playlist, PluginStream, Dict[str, Any]]] = Field(
        default_factory=list, description="List of search results found by the skill."
    )
    searching: bool = Field(..., description="True if the skill is still searching, False if done.")
    timeout: Optional[float] = Field(None, description="Optional timeout extension for searching.")
    model_config = ConfigDict(extra='allow')


class OvosCommonPlayQueryResponseMessage(OpenVoiceOSMessage):
    """An OCP skill returns its search results for the current query.

    Emitted by OCP skills in reply to `ovos.common_play.query`. Skills may
    emit this multiple times: first with `searching=True` and empty results
    (to claim the query slot), then with `searching=False` and `results`
    populated. OCP waits for all skills to finish before selecting the best
    result by `match_confidence`.
    """
    message_type: str = "ovos.common_play.query.response"
    data: OvosCommonPlayQueryResponseData


class OvosCommonPlaySkillSearchEndData(BaseModel):
    """Payload identifying the skill that has finished its search."""
    skill_id: str = Field(..., description="The ID of the skill ending a search.")
    model_config = ConfigDict(extra='allow')


class OvosCommonPlaySkillSearchEndMessage(OpenVoiceOSMessage):
    """Signal that a specific OCP skill has finished processing a search.

    Emitted by each skill after its `search()` call returns the final
    response with `searching=False`. The OCP GUI hides the 'searching...'
    indicator for the skill's tile.
    """
    message_type: str = "ovos.common_play.skill.search_end"
    data: OvosCommonPlaySkillSearchEndData


class OvosCommonPlayRegisterKeywordData(BaseModel):
    """Payload for an OCP skill to register media-type-specific trigger keywords."""
    skill_id: str = Field(..., description="The ID of the skill registering the keyword.")
    label: str = Field(..., description="The label for the keyword (e.g., 'movie_name').")
    media_type: MediaType = Field(..., description="The media type associated with the keyword.")
    samples: Optional[List[str]] = Field(None, description="List of keyword samples (if not using CSV).")
    csv: Optional[str] = Field(None, description="Path to a CSV file containing keywords (if many samples).")
    model_config = ConfigDict(extra='allow')


class OvosCommonPlayRegisterKeywordMessage(OpenVoiceOSMessage):
    """Register media-type-specific trigger keywords with the OCP pipeline.

    Emitted by OCP skills during `initialize()` to teach the intent pipeline
    about content-specific entity names (e.g. podcast names, artist names).
    OCP uses these to improve entity extraction from user utterances.
    """
    message_type: str = "ovos.common_play.register_keyword"
    data: OvosCommonPlayRegisterKeywordData


class OvosCommonPlayDeregisterKeywordData(BaseModel):
    """Payload for removing previously registered OCP trigger keywords."""
    skill_id: str = Field(..., description="The ID of the skill deregistering the keyword.")
    label: str = Field(..., description="The label of the keyword to deregister.")
    media_type: MediaType = Field(..., description="The media type associated with the keyword.")
    model_config = ConfigDict(extra='allow')


class OvosCommonPlayDeregisterKeywordMessage(OpenVoiceOSMessage):
    """Deregister media-type-specific trigger keywords from the OCP pipeline.

    Emitted by OCP skills during `shutdown()` or when their keyword set
    changes. OCP removes the named keywords from its entity extractor.
    """
    message_type: str = "ovos.common_play.deregister_keyword"
    data: OvosCommonPlayDeregisterKeywordData


class OvosCommonPlaySkillsDetachData(BaseModel):
    """Payload identifying the skill that is leaving the OCP ecosystem."""
    skill_id: str = Field(..., description="The ID of the skill detaching from OCP.")
    model_config = ConfigDict(extra='allow')


class OvosCommonPlaySkillsDetachMessage(OpenVoiceOSMessage):
    """Signal that an OCP skill is unregistering from the OCP framework.

    Emitted by OCP skills during `shutdown()`. OCP removes the skill from
    its registry so it no longer receives search queries or playback commands.
    """
    message_type: str = "ovos.common_play.skills.detach"
    data: OvosCommonPlaySkillsDetachData


# --- OCP Extended Playback Control ---

class OvosCommonPlayPauseMessage(OpenVoiceOSMessage):
    """Pause OCP playback globally.

    Emitted by skills handling 'pause' voice commands, the stop service,
    or transport controls. OCP forwards the pause to the active skill backend
    via `ovos.common_play.{skill_id}.pause`.
    """
    message_type: str = "ovos.common_play.pause"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlayResumeMessage(OpenVoiceOSMessage):
    """Resume OCP playback globally.

    Emitted by skills handling 'resume' or 'continue' voice commands, or
    transport controls. OCP forwards the resume to the active skill backend
    via `ovos.common_play.{skill_id}.resume`.
    """
    message_type: str = "ovos.common_play.resume"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlayStopMessage(OpenVoiceOSMessage):
    """Stop OCP playback and clear the queue globally.

    Emitted by the stop service or skills. OCP halts the active backend via
    `ovos.common_play.{skill_id}.stop` and clears its internal queue state.
    OCP replies with `ovos.common_play.stop.response`.
    """
    message_type: str = "ovos.common_play.stop"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlayStopResponseData(BaseModel):
    """Result of an OCP stop command."""
    result: bool = Field(..., description="True if stop succeeded.")


class OvosCommonPlayStopResponseMessage(OpenVoiceOSMessage):
    """Confirm or deny whether the OCP stop command succeeded.

    Emitted by OCP in response to `ovos.common_play.stop`. If `result` is
    False it indicates no media was playing when the stop arrived.
    """
    message_type: str = "ovos.common_play.stop.response"
    data: OvosCommonPlayStopResponseData


class OvosCommonPlayResetMessage(OpenVoiceOSMessage):
    """Reset the OCP player to its initial idle state.

    Emitted by the OCP pipeline plugin when a media search completes with no
    results, or when the player needs to be cleared without a full stop cycle.
    Clears the current queue, resets playback state, and returns OCP to idle.
    """
    message_type: str = "ovos.common_play.reset"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlayNextMessage(OpenVoiceOSMessage):
    """Skip to the next track in the OCP queue.

    Emitted by skills handling 'next song' voice commands or GUI next
    buttons. OCP advances its playlist and calls the active skill's next
    handler or begins playing the next queued entry.
    """
    message_type: str = "ovos.common_play.next"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlayPreviousMessage(OpenVoiceOSMessage):
    """Skip back to the previous track in the OCP queue.

    Emitted by skills handling 'previous song' voice commands or GUI back
    buttons. OCP rewinds its playlist and plays the previously active entry.
    """
    message_type: str = "ovos.common_play.previous"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlaySeekData(BaseModel):
    """Absolute seek target for the OCP player."""
    position: int = Field(..., description="Seek position in milliseconds.")


class OvosCommonPlaySeekMessage(OpenVoiceOSMessage):
    """Seek the OCP player to an absolute position in the current track.

    Emitted by skills implementing voice-controlled seek ('jump to two
    minutes in'). OCP forwards the seek to the active backend.
    """
    message_type: str = "ovos.common_play.seek"
    data: OvosCommonPlaySeekData


class OvosCommonPlaySetTrackPositionData(BaseModel):
    """Absolute track position to seek to."""
    position: int = Field(..., description="Track position in milliseconds.")


class OvosCommonPlaySetTrackPositionMessage(OpenVoiceOSMessage):
    """Set the OCP player's position to an absolute offset in the current track.

    Emitted by the GUI seek bar or skills. Functionally equivalent to
    `ovos.common_play.seek` but uses a different message type for
    compatibility with backends that distinguish 'set position' from 'seek'.
    """
    message_type: str = "ovos.common_play.set_track_position"
    data: OvosCommonPlaySetTrackPositionData


class OvosCommonPlayGetTrackPositionMessage(OpenVoiceOSMessage):
    """Query the current playback position from the OCP player.

    Emitted by GUIs rendering a progress bar or skills that need to
    announce elapsed time. The OCP player replies with position in ms.
    """
    message_type: str = "ovos.common_play.get_track_position"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlayGetTrackLengthMessage(OpenVoiceOSMessage):
    """Query the total duration of the currently playing OCP track.

    Emitted by GUIs or skills that need total length for percentage
    calculations. The OCP player replies with duration in ms.
    """
    message_type: str = "ovos.common_play.get_track_length"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlayPlaybackTimeData(BaseModel):
    """Periodic playback position and total length from the OCP player."""
    position: int = Field(..., description="Current position in milliseconds.")
    length: int = Field(..., description="Total track length in milliseconds.")


class OvosCommonPlayPlaybackTimeMessage(OpenVoiceOSMessage):
    """Periodic position update broadcast from the OCP player.

    Emitted by OCP at regular intervals during playback so GUIs can animate
    a progress bar without polling. Skills that track elapsed time also
    subscribe to this message.
    """
    message_type: str = "ovos.common_play.playback_time"
    data: OvosCommonPlayPlaybackTimeData


class OvosCommonPlayPlayPauseMessage(OpenVoiceOSMessage):
    """Toggle OCP playback between playing and paused states.

    Emitted by single-button transport controls (hardware play/pause key,
    headphone remote). OCP checks the current state and applies the
    appropriate action.
    """
    message_type: str = "ovos.common_play.play_pause"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlaySimplePlayData(BaseModel):
    """Payload for playing a URI directly without going through the search pipeline."""
    uri: str = Field(..., description="Media URI to play directly.")
    mime_type: Optional[str] = Field(None, description="MIME type of the media.")


class OvosCommonPlaySimplePlayMessage(OpenVoiceOSMessage):
    """Play a media URI directly without an OCP search.

    Emitted by skills or external integrations that already have a resolved
    URI and want OCP to play it immediately. OCP picks the appropriate
    backend based on `mime_type` and starts playback.
    """
    message_type: str = "ovos.common_play.simple.play"
    data: OvosCommonPlaySimplePlayData


class OvosCommonPlayHomeMessage(OpenVoiceOSMessage):
    """Navigate the OCP GUI to its home screen.

    Emitted by skills or the GUI shell when the user explicitly asks to
    see the OCP home (e.g. 'show music player'). The OCP GUI renders
    the skill grid and featured content.
    """
    message_type: str = "ovos.common_play.home"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlayPingMessage(OpenVoiceOSMessage):
    """Check whether the OCP service is running and responsive.

    Emitted by skills or test harnesses that need to verify OCP is alive
    before sending playback commands. OCP replies with a pong-style response.
    """
    message_type: str = "ovos.common_play.ping"
    data: Dict[str, Any] = Field(default_factory=dict)


# --- Repeat / Shuffle ---

class OvosCommonPlayRepeatSetMessage(OpenVoiceOSMessage):
    """Enable playlist repeat mode in the OCP player.

    Emitted by skills handling 'repeat' voice commands or the GUI repeat
    button. OCP loops the current playlist continuously.
    """
    message_type: str = "ovos.common_play.repeat.set"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlayRepeatUnsetMessage(OpenVoiceOSMessage):
    """Disable playlist repeat mode in the OCP player.

    Emitted by skills handling 'stop repeating' voice commands or toggling
    the GUI repeat button off. OCP stops looping after the last track.
    """
    message_type: str = "ovos.common_play.repeat.unset"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlayRepeatToggleMessage(OpenVoiceOSMessage):
    """Toggle playlist repeat mode in the OCP player.

    Emitted by single-action repeat controls. OCP enables repeat if it was
    off, or disables it if it was on.
    """
    message_type: str = "ovos.common_play.repeat.toggle"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlayShuffleSetMessage(OpenVoiceOSMessage):
    """Enable shuffle mode in the OCP player.

    Emitted by skills handling 'shuffle' voice commands or the GUI shuffle
    button. OCP randomizes the play order of the current queue.
    """
    message_type: str = "ovos.common_play.shuffle.set"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlayShuffleUnsetMessage(OpenVoiceOSMessage):
    """Disable shuffle mode in the OCP player.

    Emitted by skills handling 'stop shuffling' commands or toggling the
    GUI shuffle button off. OCP returns to sequential play order.
    """
    message_type: str = "ovos.common_play.shuffle.unset"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlayShuffleToggleMessage(OpenVoiceOSMessage):
    """Toggle shuffle mode in the OCP player.

    Emitted by single-action shuffle controls. OCP enables shuffle if it
    was off, or disables it if it was on.
    """
    message_type: str = "ovos.common_play.shuffle.toggle"
    data: Dict[str, Any] = Field(default_factory=dict)


# --- Playlist Management ---

class OvosCommonPlayPlaylistQueueData(BaseModel):
    """Payload for appending a single entry to the OCP queue."""
    media: Union[MediaEntry, Dict[str, Any]] = Field(..., description="MediaEntry to add to the queue.")


class OvosCommonPlayPlaylistQueueMessage(OpenVoiceOSMessage):
    """Append a media entry to the end of the OCP play queue.

    Emitted by skills implementing 'add to queue' or 'play next' voice
    commands. The entry is added without interrupting the current track.
    """
    message_type: str = "ovos.common_play.playlist.queue"
    data: OvosCommonPlayPlaylistQueueData


class OvosCommonPlayPlaylistSetData(BaseModel):
    """Payload for replacing the OCP queue with a new playlist."""
    playlist: List[Union[MediaEntry, Dict[str, Any]]] = Field(..., description="Full playlist to set.")


class OvosCommonPlayPlaylistSetMessage(OpenVoiceOSMessage):
    """Replace the OCP play queue with a new set of media entries.

    Emitted by OCP skills that want to hand OCP a complete playlist to
    manage (e.g. a full album, a radio station queue). The existing queue
    is discarded and replaced.
    """
    message_type: str = "ovos.common_play.playlist.set"
    data: OvosCommonPlayPlaylistSetData


class OvosCommonPlayPlaylistClearMessage(OpenVoiceOSMessage):
    """Clear all entries from the OCP play queue.

    Emitted by skills handling 'clear queue' voice commands or by OCP
    itself when stopping playback. The queue is emptied without affecting
    the currently playing track.
    """
    message_type: str = "ovos.common_play.playlist.clear"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlayPlaylistPlayMessage(OpenVoiceOSMessage):
    """Start playing the current OCP queue from the beginning.

    Emitted by GUIs or skills that have populated the queue via
    `ovos.common_play.playlist.set` or `ovos.common_play.playlist.queue`
    and now want OCP to begin playback.
    """
    message_type: str = "ovos.common_play.playlist.play"
    data: Dict[str, Any] = Field(default_factory=dict)


# --- Track Info / Status ---

class OvosCommonPlayTrackInfoMessage(OpenVoiceOSMessage):
    """Request metadata for the track currently playing in OCP.

    Emitted by skills or GUIs that display now-playing information. OCP
    replies with `ovos.common_play.track_info.response`.
    """
    message_type: str = "ovos.common_play.track_info"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlayTrackInfoResponseData(BaseModel):
    """Track metadata returned by OCP for the currently playing entry.

    Content is backend-dependent — may include title, artist, album, image,
    duration, and current position fields from the `MediaEntry` schema.
    """
    model_config = ConfigDict(extra='allow')


class OvosCommonPlayTrackInfoResponseMessage(OpenVoiceOSMessage):
    """Return metadata for the currently playing OCP track.

    Emitted by OCP in response to `ovos.common_play.track_info`. The payload
    mirrors the `MediaEntry` fields of the active track.
    """
    message_type: str = "ovos.common_play.track_info.response"
    data: OvosCommonPlayTrackInfoResponseData


class OvosCommonPlayTrackStateData(BaseModel):
    """Current per-track state from the OCP queue."""
    state: TrackState = Field(..., description="Current track state.")


class OvosCommonPlayTrackStateMessage(OpenVoiceOSMessage):
    """Broadcast the state of the currently active OCP track.

    Emitted by OCP when a track's state changes (queued → playing,
    playing → paused, etc.). Useful for skills and GUIs that show
    per-track status indicators.
    """
    message_type: str = "ovos.common_play.track.state"
    data: OvosCommonPlayTrackStateData


class OvosCommonPlayStatusMessage(OpenVoiceOSMessage):
    """Request the full OCP player status (state + current media).

    Emitted by GUIs or skills that need to initialize their display after
    connecting to the bus. OCP replies with `ovos.common_play.status.response`.
    """
    message_type: str = "ovos.common_play.status"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlayStatusResponseData(BaseModel):
    """Full OCP player status including state and currently playing entry."""
    state: Optional[PlayerState] = None
    media: Optional[Union[MediaEntry, Dict[str, Any]]] = None
    model_config = ConfigDict(extra='allow')


class OvosCommonPlayStatusResponseMessage(OpenVoiceOSMessage):
    """Return the full OCP player status.

    Emitted by OCP in response to `ovos.common_play.status`. Includes the
    current `PlayerState` and the active `MediaEntry` (if any).
    """
    message_type: str = "ovos.common_play.status.response"
    data: OvosCommonPlayStatusResponseData


class OvosCommonPlayPlayerStatusData(BaseModel):
    """Player state update broadcast proactively by OCP."""
    state: Optional[PlayerState] = None
    model_config = ConfigDict(extra='allow')


class OvosCommonPlayPlayerStatusMessage(OpenVoiceOSMessage):
    """Broadcast OCP player state changes proactively to all subscribers.

    Emitted by OCP whenever its player state changes. Distinct from
    `ovos.common_play.player.state` (which uses the `PlayerState` enum
    directly) — this message includes additional context fields.
    """
    message_type: str = "ovos.common_play.player.status"
    data: OvosCommonPlayPlayerStatusData


class OvosCommonPlayListBackendsMessage(OpenVoiceOSMessage):
    """Request a list of all OCP-compatible audio/video backends.

    Emitted by settings GUIs and configuration tools. OCP replies with
    the names and capabilities of each registered backend.
    """
    message_type: str = "ovos.common_play.list_backends"
    data: Dict[str, Any] = Field(default_factory=dict)


# --- Likes ---

class OvosCommonPlayLikeMessage(OpenVoiceOSMessage):
    """Mark the currently playing OCP track as liked.

    Emitted by skills handling 'I like this song' voice commands or the
    GUI heart/thumbs-up button. OCP records the like and may inform the
    originating skill so it can sync with a backend service.
    """
    message_type: str = "ovos.common_play.like"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlayUnlikeMessage(OpenVoiceOSMessage):
    """Remove the 'liked' mark from the currently playing OCP track.

    Emitted by skills handling 'I don't like this' voice commands or
    toggling the GUI like button off. OCP removes the like record.
    """
    message_type: str = "ovos.common_play.unlike"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlayLikedTracksPlayMessage(OpenVoiceOSMessage):
    """Tell OCP to play the user's liked tracks playlist.

    Emitted by skills handling 'play my liked songs' voice commands.
    OCP loads the user's liked tracks into the queue and starts playing.
    """
    message_type: str = "ovos.common_play.liked_tracks.play"
    data: Dict[str, Any] = Field(default_factory=dict)


# --- Search ---

class OvosCommonPlaySearchData(BaseModel):
    """Payload for requesting an OCP media search without immediate playback."""
    phrase: str = Field(..., description="Search phrase.")


class OvosCommonPlaySearchMessage(OpenVoiceOSMessage):
    """Trigger an OCP media search and display results in the GUI.

    Emitted by skills or the GUI search bar. Unlike `ovos.common_play.query`,
    this message requests a search for display purposes only — results are
    shown in the OCP GUI without automatically starting playback.
    """
    message_type: str = "ovos.common_play.search"
    data: OvosCommonPlaySearchData


class OvosCommonPlayPlaySearchData(BaseModel):
    """Payload for triggering an OCP search that immediately plays the best result."""
    phrase: str = Field(..., description="Search phrase to search and immediately play.")


class OvosCommonPlayPlaySearchMessage(OpenVoiceOSMessage):
    """Search for media and immediately play the best result.

    Emitted by skills handling voice play commands. OCP runs the search
    pipeline and starts playing the highest-confidence result without
    waiting for user confirmation.
    """
    message_type: str = "ovos.common_play.play_search"
    data: OvosCommonPlayPlaySearchData


class OvosCommonPlaySearchStartData(BaseModel):
    """Payload announcing the start of an OCP search phase."""
    phrase: str = Field(..., description="Search phrase being started.")


class OvosCommonPlaySearchStartMessage(OpenVoiceOSMessage):
    """Signal that OCP has begun the search phase for a media query.

    Emitted by OCP before broadcasting `ovos.common_play.query` to skills.
    GUIs show a 'searching...' overlay in response.
    """
    message_type: str = "ovos.common_play.search.start"
    data: OvosCommonPlaySearchStartData


class OvosCommonPlaySearchEndMessage(OpenVoiceOSMessage):
    """Signal that OCP has finished collecting all search results.

    Emitted by OCP after all skills have replied (or timed out) in response
    to `ovos.common_play.query`. GUIs hide the 'searching...' overlay.
    """
    message_type: str = "ovos.common_play.search.end"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlaySearchPopulateData(BaseModel):
    """Payload for pushing accumulated search results to the OCP GUI."""
    results: List[Union[MediaEntry, Dict[str, Any]]] = Field(default_factory=list)


class OvosCommonPlaySearchPopulateMessage(OpenVoiceOSMessage):
    """Push the current accumulated search results to the OCP GUI for display.

    Emitted by OCP as results arrive from skills during a search. The GUI
    renders the results incrementally as each skill responds, rather than
    waiting for all skills to finish.
    """
    message_type: str = "ovos.common_play.search.populate"
    data: OvosCommonPlaySearchPopulateData


class OvosCommonPlaySearchPlayMessage(OpenVoiceOSMessage):
    """Play a result that the user selected from the OCP search results GUI.

    Emitted when the user taps a search result tile. OCP plays the selected
    entry directly without re-running the search pipeline.
    """
    message_type: str = "ovos.common_play.search.play"
    data: Dict[str, Any] = Field(default_factory=dict)


# --- GUI Timeout ---

class OvosCommonPlayGuiEnableAppTimeoutMessage(OpenVoiceOSMessage):
    """Enable the OCP GUI auto-close timeout.

    **Deprecated** — the `ovos.common_play.gui` timeout messages are no longer
    used by the current OCP GUI implementation. Documented for historical reference.
    """
    message_type: str = "ovos.common_play.gui.enable_app_timeout"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlayGuiSetAppTimeoutData(BaseModel):
    """Payload for setting the OCP GUI inactivity timeout duration."""
    timeout: int = Field(..., description="Timeout in seconds before GUI closes.")


class OvosCommonPlayGuiSetAppTimeoutMessage(OpenVoiceOSMessage):
    """Set the OCP GUI inactivity timeout duration.

    **Deprecated** — the `ovos.common_play.gui` timeout messages are no longer
    used by the current OCP GUI implementation. Documented for historical reference.
    """
    message_type: str = "ovos.common_play.gui.set_app_timeout"
    data: OvosCommonPlayGuiSetAppTimeoutData


class OvosCommonPlayGuiTimeoutModeData(BaseModel):
    """Payload for setting the OCP GUI timeout mode."""
    mode: str = Field(..., description="Timeout mode: 'auto', 'manual', etc.")


class OvosCommonPlayGuiTimeoutModeMessage(OpenVoiceOSMessage):
    """Configure how the OCP GUI timeout behaves.

    **Deprecated** — the `ovos.common_play.gui` timeout messages are no longer
    used by the current OCP GUI implementation. Documented for historical reference.
    """
    message_type: str = "ovos.common_play.gui.timeout.mode"
    data: OvosCommonPlayGuiTimeoutModeData


# --- SEI (Skill Extension Interfaces) ---

class OvosCommonPlaySeiGetMessage(OpenVoiceOSMessage):
    """Request the list of Skill Extension Interfaces registered with OCP.

    Emitted by the OCP GUI or debug tools to discover which extended
    capabilities (SEIs) are available from registered OCP skills. OCP
    replies with `ovos.common_play.SEI.get.response`.
    """
    message_type: str = "ovos.common_play.SEI.get"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosCommonPlaySeiGetResponseData(BaseModel):
    """List of Skill Extension Interfaces registered with OCP."""
    extensions: List[Dict[str, Any]] = Field(default_factory=list)


class OvosCommonPlaySeiGetResponseMessage(OpenVoiceOSMessage):
    """Return the list of Skill Extension Interfaces registered with OCP.

    Emitted by OCP in response to `ovos.common_play.SEI.get`. Each entry
    describes an SEI provided by a registered skill (e.g. lyrics, radio
    station browsing, playlist export).
    """
    message_type: str = "ovos.common_play.SEI.get.response"
    data: OvosCommonPlaySeiGetResponseData
