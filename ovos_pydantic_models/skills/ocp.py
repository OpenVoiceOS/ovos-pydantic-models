from typing import Dict, Any, List, Optional, Union
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session

class MediaType(str, Enum):
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

class MediaState(str, Enum):
    IDLE = "idle"
    LOADING = "loading"
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    END_OF_STREAM = "eos"
    BUFFERING = "buffering"
    ERROR = "error"

class MatchConfidence(float, Enum):
    EXACT = 1.0
    VERY_HIGH = 0.9
    HIGH = 0.8
    AVERAGE = 0.5
    LOW = 0.3
    NO_MATCH = 0.0

class PlaybackType(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"
    WEBVIEW = "webview"

class PlaybackMode(str, Enum):
    NORMAL = "normal"
    LOOP = "loop"
    SHUFFLE = "shuffle"
    SINGLE_LOOP = "single_loop"

class PlayerState(str, Enum):
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    LOADING = "loading"
    BUFFERING = "buffering"

class LoopState(str, Enum):
    NONE = "none"
    PLAYLIST = "playlist"
    TRACK = "track"

class TrackState(str, Enum):
    QUEUED = "queued"
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    BUFFERING = "buffering"

class BaseMediaEntry(BaseModel):
    uri: str = Field(..., description="The URI of the media.")
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    image: Optional[str] = None
    playback: PlaybackType = PlaybackType.AUDIO
    match_confidence: MatchConfidence = MatchConfidence.AVERAGE
    media_type: MediaType = MediaType.GENERIC
    skill_id: Optional[str] = None
    length: Optional[int] = None # in milliseconds
    position: Optional[int] = None # in milliseconds
    bg_image: Optional[str] = None # background image
    # Allow arbitrary extra data
    model_config = ConfigDict(extra='allow')

class MediaEntry(BaseMediaEntry):
    """Represents a single media entry."""
    pass

class PluginStream(BaseMediaEntry):
    """Represents a media entry from a plugin stream."""
    plugin_id: str
    stream_id: str

class Playlist(BaseModel):
    """Represents a playlist of media entries."""
    title: Optional[str] = None
    author: Optional[str] = None
    image: Optional[str] = None
    thumbnail: Optional[str] = None
    url: Optional[str] = None
    entries: List[MediaEntry] = Field(default_factory=list)
    # Allow arbitrary extra data
    model_config = ConfigDict(extra='allow')


# --- OVOS Common Playback Skill Message Models ---

class OvosCommonPlayQueryData(BaseModel):
    """Data for `ovos.common_play.query` message."""
    phrase: str = Field(..., description="The search phrase from the user utterance.")
    question_type: MediaType = Field(MediaType.GENERIC, description="The media type being queried.")
    # Allow other context from the original message if needed
    model_config = ConfigDict(extra='allow')

class OvosCommonPlayQueryMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_play.query` (request to search for media)."""
    message_type: str = "ovos.common_play.query"
    data: OvosCommonPlayQueryData


class OvosCommonPlayFeaturedTracksPlayData(BaseModel):
    """Data for `ovos.common_play.featured_tracks.play` message."""
    skill_id: str = Field(..., description="The ID of the skill to request featured tracks from.")
    # Allow other context from the original message if needed
    model_config = ConfigDict(extra='allow')

class OvosCommonPlayFeaturedTracksPlayMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_play.featured_tracks.play`."""
    message_type: str = "ovos.common_play.featured_tracks.play"
    data: OvosCommonPlayFeaturedTracksPlayData


class OvosCommonPlaySkillsGetMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_play.skills.get` (request for OCP skill info)."""
    message_type: str = "ovos.common_play.skills.get"
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class OvosCommonPlaySkillPlayData(BaseModel):
    """
    Data for `ovos.common_play.{skill_id}.play` message.
    This message is sent to a specific skill to initiate playback.
    """
    # The original message data (media, disambiguation, playlist) is passed
    media: Union[MediaEntry, PluginStream, Dict[str, Any]] = Field(..., description="The media entry to play.")
    disambiguation: List[Union[MediaEntry, PluginStream, Dict[str, Any]]] = Field(
        ..., description="List of media entries for disambiguation."
    )
    playlist: List[Union[MediaEntry, PluginStream, Dict[str, Any]]] = Field(
        ..., description="The playlist of media entries."
    )
    model_config = ConfigDict(extra='allow') # Allow other data from original message

class OvosCommonPlaySkillPlayMessage(OpenVoiceOSMessage):
    """
    Message for `ovos.common_play.{skill_id}.play`.
    The `message_type` will be dynamically set to the skill ID.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'ovos.common_play.my-skill-id.play'.")
    data: OvosCommonPlaySkillPlayData


class OvosCommonPlaySkillPauseData(BaseModel):
    """
    Data for `ovos.common_play.{skill_id}.pause` message.
    """
    model_config = ConfigDict(extra='allow') # No specific fields, but allow extra

class OvosCommonPlaySkillPauseMessage(OpenVoiceOSMessage):
    """
    Message for `ovos.common_play.{skill_id}.pause`.
    The `message_type` will be dynamically set to the skill ID.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'ovos.common_play.my-skill-id.pause'.")
    data: OvosCommonPlaySkillPauseData = Field(default_factory=dict, description="Empty data payload for pause command.")


class OvosCommonPlaySkillResumeData(BaseModel):
    """
    Data for `ovos.common_play.{skill_id}.resume` message.
    """
    model_config = ConfigDict(extra='allow') # No specific fields, but allow extra

class OvosCommonPlaySkillResumeMessage(OpenVoiceOSMessage):
    """
    Message for `ovos.common_play.{skill_id}.resume`.
    The `message_type` will be dynamically set to the skill ID.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'ovos.common_play.my-skill-id.resume'.")
    data: OvosCommonPlaySkillResumeData = Field(default_factory=dict, description="Empty data payload for resume command.")


class OvosCommonPlaySkillNextData(BaseModel):
    """
    Data for `ovos.common_play.{skill_id}.next` message.
    """
    model_config = ConfigDict(extra='allow') # No specific fields, but allow extra

class OvosCommonPlaySkillNextMessage(OpenVoiceOSMessage):
    """
    Message for `ovos.common_play.{skill_id}.next`.
    The `message_type` will be dynamically set to the skill ID.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'ovos.common_play.my-skill-id.next'.")
    data: OvosCommonPlaySkillNextData = Field(default_factory=dict, description="Empty data payload for next track command.")


class OvosCommonPlaySkillPreviousData(BaseModel):
    """
    Data for `ovos.common_play.{skill_id}.previous` message.
    """
    model_config = ConfigDict(extra='allow') # No specific fields, but allow extra

class OvosCommonPlaySkillPreviousMessage(OpenVoiceOSMessage):
    """
    Message for `ovos.common_play.{skill_id}.previous`.
    The `message_type` will be dynamically set to the skill ID.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'ovos.common_play.my-skill-id.previous'.")
    data: OvosCommonPlaySkillPreviousData = Field(default_factory=dict, description="Empty data payload for previous track command.")


class OvosCommonPlaySkillStopData(BaseModel):
    """
    Data for `ovos.common_play.{skill_id}.stop` message.
    """
    model_config = ConfigDict(extra='allow') # No specific fields, but allow extra

class OvosCommonPlaySkillStopMessage(OpenVoiceOSMessage):
    """
    Message for `ovos.common_play.{skill_id}.stop`.
    The `message_type` will be dynamically set to the skill ID.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'ovos.common_play.my-skill-id.stop'.")
    data: OvosCommonPlaySkillStopData = Field(default_factory=dict, description="Empty data payload for stop command.")


class OvosCommonPlaySearchStopMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_play.search.stop`."""
    message_type: str = "ovos.common_play.search.stop"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for search stop command.")


# Reusing MycroftStopMessage from skill_messages
# class MycroftStopMessage(OpenVoiceOSMessage):
#     """Message for `mycroft.stop`."""
#     message_type: str = "mycroft.stop"
#     data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for stop command.")


class OvosCommonPlayAnnounceData(BaseModel):
    """Data for `ovos.common_play.announce` message."""
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
    """Message for `ovos.common_play.announce`."""
    message_type: str = "ovos.common_play.announce"
    data: OvosCommonPlayAnnounceData


class OvosCommonPlayPlayData(BaseModel):
    """Data for `ovos.common_play.play` message."""
    media: Union[MediaEntry, PluginStream, Dict[str, Any]] = Field(..., description="The media entry to play.")
    disambiguation: List[Union[MediaEntry, PluginStream, Dict[str, Any]]] = Field(
        ..., description="List of media entries for disambiguation."
    )
    playlist: List[Union[MediaEntry, PluginStream, Dict[str, Any]]] = Field(
        ..., description="The playlist of media entries."
    )
    model_config = ConfigDict(extra='allow')

class OvosCommonPlayPlayMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_play.play` (request to OCP to play media)."""
    message_type: str = "ovos.common_play.play"
    data: OvosCommonPlayPlayData


class OvosCommonPlayPlayerStateData(BaseModel):
    """Data for `ovos.common_play.player.state` message."""
    state: PlayerState = Field(..., description="The current state of the OCP player.")

class OvosCommonPlayPlayerStateMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_play.player.state`."""
    message_type: str = "ovos.common_play.player.state"
    data: OvosCommonPlayPlayerStateData


class OvosCommonPlaySkillSearchStartData(BaseModel):
    """Data for `ovos.common_play.skill.search_start` message."""
    skill_id: str = Field(..., description="The ID of the skill starting a search.")
    skill_name: str = Field(..., description="The name of the skill starting the search.")
    thumbnail: str = Field(..., description="URL or path to the skill's icon/thumbnail.")
    model_config = ConfigDict(extra='allow')

class OvosCommonPlaySkillSearchStartMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_play.skill.search_start`."""
    message_type: str = "ovos.common_play.skill.search_start"
    data: OvosCommonPlaySkillSearchStartData


class OvosCommonPlayQueryResponseData(BaseModel):
    """Data for `ovos.common_play.query.response` message (from skill back to OCP)."""
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
    """Response message for `ovos.common_play.query`."""
    message_type: str = "ovos.common_play.query.response"
    data: OvosCommonPlayQueryResponseData


class OvosCommonPlaySkillSearchEndData(BaseModel):
    """Data for `ovos.common_play.skill.search_end` message."""
    skill_id: str = Field(..., description="The ID of the skill ending a search.")
    model_config = ConfigDict(extra='allow')

class OvosCommonPlaySkillSearchEndMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_play.skill.search_end`."""
    message_type: str = "ovos.common_play.skill.search_end"
    data: OvosCommonPlaySkillSearchEndData


class OvosCommonPlayRegisterKeywordData(BaseModel):
    """Data for `ovos.common_play.register_keyword` message."""
    skill_id: str = Field(..., description="The ID of the skill registering the keyword.")
    label: str = Field(..., description="The label for the keyword (e.g., 'movie_name').")
    media_type: MediaType = Field(..., description="The media type associated with the keyword.")
    samples: Optional[List[str]] = Field(None, description="List of keyword samples (if not using CSV).")
    csv: Optional[str] = Field(None, description="Path to a CSV file containing keywords (if many samples).")
    model_config = ConfigDict(extra='allow')

class OvosCommonPlayRegisterKeywordMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_play.register_keyword`."""
    message_type: str = "ovos.common_play.register_keyword"
    data: OvosCommonPlayRegisterKeywordData


class OvosCommonPlayDeregisterKeywordData(BaseModel):
    """Data for `ovos.common_play.deregister_keyword` message."""
    skill_id: str = Field(..., description="The ID of the skill deregistering the keyword.")
    label: str = Field(..., description="The label of the keyword to deregister.")
    media_type: MediaType = Field(..., description="The media type associated with the keyword.")
    model_config = ConfigDict(extra='allow')

class OvosCommonPlayDeregisterKeywordMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_play.deregister_keyword`."""
    message_type: str = "ovos.common_play.deregister_keyword"
    data: OvosCommonPlayDeregisterKeywordData


class OvosCommonPlaySkillsDetachData(BaseModel):
    """Data for `ovos.common_play.skills.detach` message."""
    skill_id: str = Field(..., description="The ID of the skill detaching from OCP.")
    model_config = ConfigDict(extra='allow')

class OvosCommonPlaySkillsDetachMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_play.skills.detach`."""
    message_type: str = "ovos.common_play.skills.detach"
    data: OvosCommonPlaySkillsDetachData


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Demonstrating OVOS Common Playback Skill Message Models ---")

    # Create a dummy session and context for demonstration
    dummy_session = Session(session_id="test-ocp-skill-session-123", lang="en-us")
    dummy_context = MessageContext(source="ocp_skill", session=dummy_session)

    # Example: OCP Query Request
    ocp_query_data = OvosCommonPlayQueryData(phrase="play some music", question_type=MediaType.MUSIC)
    ocp_query_message = OvosCommonPlayQueryMessage(data=ocp_query_data, context=dummy_context)
    print(f"\nOCP Query Message:\n{ocp_query_message.model_dump_json(indent=2)}")

    # Example: OCP Featured Tracks Play Request
    featured_play_data = OvosCommonPlayFeaturedTracksPlayData(skill_id="skill-my-music.mycroft")
    featured_play_message = OvosCommonPlayFeaturedTracksPlayMessage(data=featured_play_data, context=dummy_context)
    print(f"\nOCP Featured Tracks Play Message:\n{featured_play_message.model_dump_json(indent=2)}")

    # Example: OCP Skills Get Request
    skills_get_message = OvosCommonPlaySkillsGetMessage(context=dummy_context)
    print(f"\nOCP Skills Get Message:\n{skills_get_message.model_dump_json(indent=2)}")

    # Example: Dynamic OCP Skill Play Message
    media_entry_example = MediaEntry(uri="https://example.com/song.mp3", title="My Song", artist="My Artist")
    skill_play_data = OvosCommonPlaySkillPlayData(
        media=media_entry_example,
        disambiguation=[media_entry_example],
        playlist=[media_entry_example]
    )
    skill_play_message = OvosCommonPlaySkillPlayMessage(
        message_type="ovos.common_play.skill-music.mycroft.play",
        data=skill_play_data,
        context=dummy_context
    )
    print(f"\nDynamic OCP Skill Play Message:\n{skill_play_message.model_dump_json(indent=2)}")

    # Example: Dynamic OCP Skill Pause Message
    skill_pause_message = OvosCommonPlaySkillPauseMessage(
        message_type="ovos.common_play.skill-music.mycroft.pause",
        context=dummy_context
    )
    print(f"\nDynamic OCP Skill Pause Message:\n{skill_pause_message.model_dump_json(indent=2)}")

    # Example: Dynamic OCP Skill Resume Message
    skill_resume_message = OvosCommonPlaySkillResumeMessage(
        message_type="ovos.common_play.skill-music.mycroft.resume",
        context=dummy_context
    )
    print(f"\nDynamic OCP Skill Resume Message:\n{skill_resume_message.model_dump_json(indent=2)}")

    # Example: Dynamic OCP Skill Next Message
    skill_next_message = OvosCommonPlaySkillNextMessage(
        message_type="ovos.common_play.skill-music.mycroft.next",
        context=dummy_context
    )
    print(f"\nDynamic OCP Skill Next Message:\n{skill_next_message.model_dump_json(indent=2)}")

    # Example: Dynamic OCP Skill Previous Message
    skill_previous_message = OvosCommonPlaySkillPreviousMessage(
        message_type="ovos.common_play.skill-music.mycroft.previous",
        context=dummy_context
    )
    print(f"\nDynamic OCP Skill Previous Message:\n{skill_previous_message.model_dump_json(indent=2)}")

    # Example: Dynamic OCP Skill Stop Message
    skill_stop_message = OvosCommonPlaySkillStopMessage(
        message_type="ovos.common_play.skill-music.mycroft.stop",
        context=dummy_context
    )
    print(f"\nDynamic OCP Skill Stop Message:\n{skill_stop_message.model_dump_json(indent=2)}")

    # Example: OCP Search Stop Message
    search_stop_message = OvosCommonPlaySearchStopMessage(context=dummy_context)
    print(f"\nOCP Search Stop Message:\n{search_stop_message.model_dump_json(indent=2)}")

    # Example: OCP Announce Message
    announce_data = OvosCommonPlayAnnounceData(
        skill_id="skill-music.mycroft",
        skill_name="Music Skill",
        aliases=["music", "songs"],
        thumbnail="https://example.com/music_icon.png",
        media_type=[MediaType.MUSIC, MediaType.AUDIO],
        featured_tracks=True
    )
    announce_message = OvosCommonPlayAnnounceMessage(data=announce_data, context=dummy_context)
    print(f"\nOCP Announce Message:\n{announce_message.model_dump_json(indent=2)}")

    # Example: OCP Play Message
    play_data = OvosCommonPlayPlayData(
        media=media_entry_example,
        disambiguation=[media_entry_example],
        playlist=[media_entry_example]
    )
    play_message = OvosCommonPlayPlayMessage(data=play_data, context=dummy_context)
    print(f"\nOCP Play Message:\n{play_message.model_dump_json(indent=2)}")

    # Example: OCP Player State Message
    player_state_data = OvosCommonPlayPlayerStateData(state=PlayerState.PLAYING)
    player_state_message = OvosCommonPlayPlayerStateMessage(data=player_state_data, context=dummy_context)
    print(f"\nOCP Player State Message:\n{player_state_message.model_dump_json(indent=2)}")

    # Example: OCP Skill Search Start Message
    search_start_data = OvosCommonPlaySkillSearchStartData(
        skill_id="skill-music.mycroft",
        skill_name="Music Skill",
        thumbnail="https://example.com/music_icon.png"
    )
    search_start_message = OvosCommonPlaySkillSearchStartMessage(data=search_start_data, context=dummy_context)
    print(f"\nOCP Skill Search Start Message:\n{search_start_message.model_dump_json(indent=2)}")

    # Example: OCP Query Response Message
    query_response_data = OvosCommonPlayQueryResponseData(
        phrase="play some jazz",
        skill_id="skill-music.mycroft",
        skill_name="Music Skill",
        thumbnail="https://example.com/music_icon.png",
        results=[media_entry_example],
        searching=False
    )
    query_response_message = OvosCommonPlayQueryResponseMessage(data=query_response_data, context=dummy_context)
    print(f"\nOCP Query Response Message:\n{query_response_message.model_dump_json(indent=2)}")

    # Example: OCP Skill Search End Message
    search_end_data = OvosCommonPlaySkillSearchEndData(skill_id="skill-music.mycroft")
    search_end_message = OvosCommonPlaySkillSearchEndMessage(data=search_end_data, context=dummy_context)
    print(f"\nOCP Skill Search End Message:\n{search_end_message.model_dump_json(indent=2)}")

    # Example: OCP Register Keyword Message (samples)
    register_keyword_data_samples = OvosCommonPlayRegisterKeywordData(
        skill_id="skill-music.mycroft",
        label="artist_name",
        media_type=MediaType.MUSIC,
        samples=["Frank Sinatra", "Ella Fitzgerald"]
    )
    register_keyword_message_samples = OvosCommonPlayRegisterKeywordMessage(
        data=register_keyword_data_samples, context=dummy_context
    )
    print(f"\nOCP Register Keyword Message (Samples):\n{register_keyword_message_samples.model_dump_json(indent=2)}")

    # Example: OCP Register Keyword Message (CSV)
    register_keyword_data_csv = OvosCommonPlayRegisterKeywordData(
        skill_id="skill-movies.mycroft",
        label="movie_title",
        media_type=MediaType.VIDEO,
        csv="/tmp/ocp_movie_titles.csv"
    )
    register_keyword_message_csv = OvosCommonPlayRegisterKeywordMessage(
        data=register_keyword_data_csv, context=dummy_context
    )
    print(f"\nOCP Register Keyword Message (CSV):\n{register_keyword_message_csv.model_dump_json(indent=2)}")

    # Example: OCP Deregister Keyword Message
    deregister_keyword_data = OvosCommonPlayDeregisterKeywordData(
        skill_id="skill-music.mycroft",
        label="artist_name",
        media_type=MediaType.MUSIC
    )
    deregister_keyword_message = OvosCommonPlayDeregisterKeywordMessage(
        data=deregister_keyword_data, context=dummy_context
    )
    print(f"\nOCP Deregister Keyword Message:\n{deregister_keyword_message.model_dump_json(indent=2)}")

    # Example: OCP Skills Detach Message
    skills_detach_data = OvosCommonPlaySkillsDetachData(skill_id="skill-music.mycroft")
    skills_detach_message = OvosCommonPlaySkillsDetachMessage(data=skills_detach_data, context=dummy_context)
    print(f"\nOCP Skills Detach Message:\n{skills_detach_message.model_dump_json(indent=2)}")
