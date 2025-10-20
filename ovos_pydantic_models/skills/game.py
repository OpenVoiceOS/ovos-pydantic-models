from enum import Enum
from typing import Dict, Any, List, Optional, Union

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
    GAME = "game"  # Added for game skills


class PlaybackType(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"
    WEBVIEW = "webview"
    SKILL = "skill"  # Added for game skills


class PlayerState(str, Enum):
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    LOADING = "loading"
    BUFFERING = "buffering"


class MatchConfidence(float, Enum):
    EXACT = 1.0
    VERY_HIGH = 0.9
    HIGH = 0.8
    AVERAGE = 0.5
    LOW = 0.3
    NO_MATCH = 0.0


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
    length: Optional[int] = None  # in milliseconds
    position: Optional[int] = None  # in milliseconds
    bg_image: Optional[str] = None  # background image
    skill_icon: Optional[str] = None  # skill icon for OCP GUI
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
    entries: List[Union[MediaEntry, PluginStream]] = Field(default_factory=list)
    playback: PlaybackType = PlaybackType.AUDIO  # Added for playlists
    media_type: MediaType = MediaType.GENERIC  # Added for playlists
    match_confidence: MatchConfidence = MatchConfidence.AVERAGE  # Added for playlists
    skill_icon: Optional[str] = None  # Added for playlists
    # Allow arbitrary extra data
    model_config = ConfigDict(extra='allow')


# --- OVOS Game Skill Message Models ---

class OvosCommonPlayPlayerStateData(BaseModel):
    """Data for `ovos.common_play.player.state` message."""
    state: PlayerState = Field(..., description="The current state of the OCP player.")


class OvosCommonPlayPlayerStateMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_play.player.state`."""
    message_type: str = "ovos.common_play.player.state"
    data: OvosCommonPlayPlayerStateData


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


class OvosCommonPlaySkillSearchEndData(BaseModel):
    """Data for `ovos.common_play.skill.search_end` message."""
    skill_id: str = Field(..., description="The ID of the skill ending a search.")
    model_config = ConfigDict(extra='allow')


class OvosCommonPlaySkillSearchEndMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_play.skill.search_end`."""
    message_type: str = "ovos.common_play.skill.search_end"
    data: OvosCommonPlaySkillSearchEndData


class OvosCommonPlaySkillPlayData(BaseModel):
    """
    Data for `ovos.common_play.skill.play` message.
    This message is sent to a specific skill to initiate playback.
    """
    skill_id: str = Field(..., description="The ID of the skill to play media from.")
    skill_name: str = Field(..., description="The name of the skill playing media.")
    thumbnail: str = Field(..., description="URL or path to the skill's icon/thumbnail.")
    playlist: List[Union[MediaEntry, PluginStream, Dict[str, Any]]] = Field(
        ..., description="The playlist of media entries to play."
    )
    model_config = ConfigDict(extra='allow')


class OvosCommonPlaySkillPlayMessage(OpenVoiceOSMessage):
    """
    Message for `ovos.common_play.skill.play`.
    """
    message_type: str = "ovos.common_play.skill.play"
    data: OvosCommonPlaySkillPlayData


class OvosCommonPlaySkillsDetachData(BaseModel):
    """Data for `ovos.common_play.skills.detach` message."""
    skill_id: str = Field(..., description="The ID of the skill detaching from OCP.")
    model_config = ConfigDict(extra='allow')


class OvosCommonPlaySkillsDetachMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_play.skills.detach`."""
    message_type: str = "ovos.common_play.skills.detach"
    data: OvosCommonPlaySkillsDetachData


class OvosCommonPlayQueryData(BaseModel):
    """Data for `ovos.common_play.query` message."""
    phrase: str = Field(..., description="The search phrase from the user utterance.")
    question_type: MediaType = Field(MediaType.GENERIC, description="The media type being queried.")
    model_config = ConfigDict(extra='allow')


class OvosCommonPlayQueryMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_play.query` (request to search for media)."""
    message_type: str = "ovos.common_play.query"
    data: OvosCommonPlayQueryData


class OvosCommonPlayFeaturedTracksPlayData(BaseModel):
    """Data for `ovos.common_play.featured_tracks.play` message."""
    skill_id: str = Field(..., description="The ID of the skill to request featured tracks from.")
    model_config = ConfigDict(extra='allow')


class OvosCommonPlayFeaturedTracksPlayMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_play.featured_tracks.play`."""
    message_type: str = "ovos.common_play.featured_tracks.play"
    data: OvosCommonPlayFeaturedTracksPlayData


class OvosCommonPlaySkillsGetData(BaseModel):
    """Data for `ovos.common_play.skills.get` message (request)."""
    model_config = ConfigDict(extra='allow')  # No specific fields, but allow extra


class OvosCommonPlaySkillsGetMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_play.skills.get` (request for OCP skill info)."""
    message_type: str = "ovos.common_play.skills.get"
    data: OvosCommonPlaySkillsGetData


class OvosCommonPlaySkillPlayRequestData(BaseModel):
    """
    Data for `ovos.common_play.{skill_id}.play` message (request to skill).
    """
    media: Union[MediaEntry, PluginStream, Dict[str, Any]] = Field(..., description="The media entry to play.")
    disambiguation: List[Union[MediaEntry, PluginStream, Dict[str, Any]]] = Field(
        ..., description="List of media entries for disambiguation."
    )
    playlist: List[Union[MediaEntry, PluginStream, Dict[str, Any]]] = Field(
        ..., description="The playlist of media entries."
    )
    model_config = ConfigDict(extra='allow')


class OvosCommonPlaySkillPlayRequestMessage(OpenVoiceOSMessage):
    """
    Message for `ovos.common_play.{skill_id}.play`.
    The `message_type` will be dynamically set to the skill ID.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'ovos.common_play.my-skill-id.play'.")
    data: OvosCommonPlaySkillPlayRequestData


class OvosCommonPlaySkillPauseRequestData(BaseModel):
    """
    Data for `ovos.common_play.{skill_id}.pause` message (request to skill).
    """
    model_config = ConfigDict(extra='allow')


class OvosCommonPlaySkillPauseRequestMessage(OpenVoiceOSMessage):
    """
    Message for `ovos.common_play.{skill_id}.pause`.
    The `message_type` will be dynamically set to the skill ID.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'ovos.common_play.my-skill-id.pause'.")
    data: OvosCommonPlaySkillPauseRequestData = Field(default_factory=dict,
                                                      description="Empty data payload for pause command.")


class OvosCommonPlaySkillResumeRequestData(BaseModel):
    """
    Data for `ovos.common_play.{skill_id}.resume` message (request to skill).
    """
    model_config = ConfigDict(extra='allow')


class OvosCommonPlaySkillResumeRequestMessage(OpenVoiceOSMessage):
    """
    Message for `ovos.common_play.{skill_id}.resume`.
    The `message_type` will be dynamically set to the skill ID.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'ovos.common_play.my-skill-id.resume'.")
    data: OvosCommonPlaySkillResumeRequestData = Field(default_factory=dict,
                                                       description="Empty data payload for resume command.")


class OvosCommonPlaySkillNextRequestData(BaseModel):
    """
    Data for `ovos.common_play.{skill_id}.next` message (request to skill).
    """
    model_config = ConfigDict(extra='allow')


class OvosCommonPlaySkillNextRequestMessage(OpenVoiceOSMessage):
    """
    Message for `ovos.common_play.{skill_id}.next`.
    The `message_type` will be dynamically set to the skill ID.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'ovos.common_play.my-skill-id.next'.")
    data: OvosCommonPlaySkillNextRequestData = Field(default_factory=dict,
                                                     description="Empty data payload for next track command.")


class OvosCommonPlaySkillPreviousRequestData(BaseModel):
    """
    Data for `ovos.common_play.{skill_id}.previous` message (request to skill).
    """
    model_config = ConfigDict(extra='allow')


class OvosCommonPlaySkillPreviousRequestMessage(OpenVoiceOSMessage):
    """
    Message for `ovos.common_play.{skill_id}.previous`.
    The `message_type` will be dynamically set to the skill ID.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'ovos.common_play.my-skill-id.previous'.")
    data: OvosCommonPlaySkillPreviousRequestData = Field(default_factory=dict,
                                                         description="Empty data payload for previous track command.")


class OvosCommonPlaySkillStopRequestData(BaseModel):
    """
    Data for `ovos.common_play.{skill_id}.stop` message (request to skill).
    """
    model_config = ConfigDict(extra='allow')


class OvosCommonPlaySkillStopRequestMessage(OpenVoiceOSMessage):
    """
    Message for `ovos.common_play.{skill_id}.stop`.
    The `message_type` will be dynamically set to the skill ID.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'ovos.common_play.my-skill-id.stop'.")
    data: OvosCommonPlaySkillStopRequestData = Field(default_factory=dict,
                                                     description="Empty data payload for stop command.")


class OvosCommonPlaySearchStopMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_play.search.stop`."""
    message_type: str = "ovos.common_play.search.stop"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for search stop command.")


class MycroftStopMessage(OpenVoiceOSMessage):
    """Message for `mycroft.stop`."""
    message_type: str = "mycroft.stop"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for stop command.")


class SkillGameCommandData(BaseModel):
    """
    Data for `{self.skill_id}.game_cmd` message.
    """
    utterances: List[str] = Field(..., description="List of utterance strings to pipe to the game.")
    lang: str = Field(..., description="4-letter ISO language code for the utterances.")
    model_config = ConfigDict(extra='allow')


class SkillGameCommandMessage(OpenVoiceOSMessage):
    """
    Message for `{self.skill_id}.game_cmd`.
    This message is used to pipe user input to the game's `on_game_command` handler.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'my-skill-id.game_cmd'.")
    data: SkillGameCommandData


class IntentServiceIntentGetData(BaseModel):
    """Data for `intent.service.intent.get` message."""
    utterance: str = Field(..., description="The utterance to get an intent for.")
    lang: str = Field(..., description="4-letter ISO language code for the utterance.")
    model_config = ConfigDict(extra='allow')


class IntentServiceIntentGetMessage(OpenVoiceOSMessage):
    """Message for `intent.service.intent.get` (request to get intent)."""
    message_type: str = "intent.service.intent.get"
    data: IntentServiceIntentGetData


class IntentServiceIntentReplyData(BaseModel):
    """Data for `intent.service.intent.reply` message."""
    intent: Optional[Dict[str, Any]] = Field(
        None, description="The matched intent dictionary, or None if no intent matched."
    )
    model_config = ConfigDict(extra='allow')


class IntentServiceIntentReplyMessage(OpenVoiceOSMessage):
    """Response message for `intent.service.intent.get`."""
    message_type: str = "intent.service.intent.reply"
    data: IntentServiceIntentReplyData


class IntentServiceSkillsActivateData(BaseModel):
    """Data for `intent.service.skills.activate` message."""
    skill_id: str = Field(..., description="The ID of the skill to activate.")
    timeout: Optional[float] = Field(
        None, description="Duration in minutes for the skill to remain active. -1 for infinite."
    )
    model_config = ConfigDict(extra='allow')


class IntentServiceSkillsActivateMessage(OpenVoiceOSMessage):
    """Message for `intent.service.skills.activate`."""
    message_type: str = "intent.service.skills.activate"
    data: IntentServiceSkillsActivateData


class IntentServiceSkillsDeactivateData(BaseModel):
    """Data for `intent.service.skills.deactivate` message."""
    skill_id: str = Field(..., description="The ID of the skill to deactivate.")
    model_config = ConfigDict(extra='allow')


class IntentServiceSkillsDeactivateMessage(OpenVoiceOSMessage):
    """Message for `intent.service.skills.deactivate`."""
    message_type: str = "intent.service.skills.deactivate"
    data: IntentServiceSkillsDeactivateData


class SkillActivateMessage(OpenVoiceOSMessage):
    """
    Message for `{skill_id}.activate`.
    The `message_type` will be dynamically set to the skill ID followed by `.activate`.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'my-skill-id.activate'.")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Empty data payload for activate command.")


class SkillDeactivateMessage(OpenVoiceOSMessage):
    """
    Message for `{skill_id}.deactivate`.
    The `message_type` will be dynamically set to the skill ID followed by `.deactivate`.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'my-skill-id.deactivate'.")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict,
                                           description="Empty data payload for deactivate command.")


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Demonstrating OVOS Game Skill Message Models ---")

    # Create a dummy session and context for demonstration
    dummy_session = Session(session_id="test-game-session-456", lang="en-us")
    dummy_context = MessageContext(source="game_skill", session=dummy_session)

    # Example: OCP Player State
    player_state_data = OvosCommonPlayPlayerStateData(state=PlayerState.PLAYING)
    player_state_message = OvosCommonPlayPlayerStateMessage(data=player_state_data, context=dummy_context)
    print(f"\nOCP Player State Message:\n{player_state_message.model_dump_json(indent=2)}")

    # Example: OCP Announce
    announce_data = OvosCommonPlayAnnounceData(
        skill_id="skill-my-game.mycroft",
        skill_name="My Game",
        aliases=["my game", "the game"],
        thumbnail="https://example.com/game_icon.png",
        media_type=[MediaType.GAME],
        featured_tracks=True
    )
    announce_message = OvosCommonPlayAnnounceMessage(data=announce_data, context=dummy_context)
    print(f"\nOCP Announce Message:\n{announce_message.model_dump_json(indent=2)}")

    # Example: OCP Query Response
    game_entry = MediaEntry(
        uri="skill:skill-my-game.mycroft",
        title="My Game",
        image="https://example.com/game_image.png",
        playback=PlaybackType.SKILL,
        media_type=MediaType.GAME,
        match_confidence=0.8,
        skill_id="skill-my-game.mycroft"
    )
    query_response_data = OvosCommonPlayQueryResponseData(
        phrase="play my game",
        skill_id="skill-my-game.mycroft",
        skill_name="My Game",
        thumbnail="https://example.com/game_icon.png",
        results=[game_entry],
        searching=False
    )
    query_response_message = OvosCommonPlayQueryResponseMessage(data=query_response_data, context=dummy_context)
    print(f"\nOCP Query Response Message:\n{query_response_message.model_dump_json(indent=2)}")

    # Example: OCP Skill Search Start
    search_start_data = OvosCommonPlaySkillSearchStartData(
        skill_id="skill-my-game.mycroft",
        skill_name="My Game",
        thumbnail="https://example.com/game_icon.png"
    )
    search_start_message = OvosCommonPlaySkillSearchStartMessage(data=search_start_data, context=dummy_context)
    print(f"\nOCP Skill Search Start Message:\n{search_start_message.model_dump_json(indent=2)}")

    # Example: OCP Skill Search End
    search_end_data = OvosCommonPlaySkillSearchEndData(skill_id="skill-my-game.mycroft")
    search_end_message = OvosCommonPlaySkillSearchEndMessage(data=search_end_data, context=dummy_context)
    print(f"\nOCP Skill Search End Message:\n{search_end_message.model_dump_json(indent=2)}")

    # Example: OCP Skill Play (from featured media)
    playlist_entry = MediaEntry(
        uri="skill:skill-my-game.mycroft",
        title="My Game",
        image="https://example.com/game_image.png",
        playback=PlaybackType.SKILL,
        media_type=MediaType.GAME,
        match_confidence=1.0,
        skill_id="skill-my-game.mycroft"
    )
    skill_play_data = OvosCommonPlaySkillPlayData(
        skill_id="skill-my-game.mycroft",
        skill_name="My Game",
        thumbnail="https://example.com/game_icon.png",
        playlist=[playlist_entry]
    )
    skill_play_message = OvosCommonPlaySkillPlayMessage(data=skill_play_data, context=dummy_context)
    print(f"\nOCP Skill Play Message:\n{skill_play_message.model_dump_json(indent=2)}")

    # Example: OCP Skills Detach
    skills_detach_data = OvosCommonPlaySkillsDetachData(skill_id="skill-my-game.mycroft")
    skills_detach_message = OvosCommonPlaySkillsDetachMessage(data=skills_detach_data, context=dummy_context)
    print(f"\nOCP Skills Detach Message:\n{skills_detach_message.model_dump_json(indent=2)}")

    # Example: Dynamic Skill Game Command
    game_cmd_data = SkillGameCommandData(utterances=["move left"], lang="en-us")
    game_cmd_message = SkillGameCommandMessage(
        message_type="skill-my-game.mycroft.game_cmd",
        data=game_cmd_data,
        context=dummy_context
    )
    print(f"\nDynamic Skill Game Command Message:\n{game_cmd_message.model_dump_json(indent=2)}")

    # Example: Intent Service Intent Get
    intent_get_data = IntentServiceIntentGetData(utterance="what time is it", lang="en-us")
    intent_get_message = IntentServiceIntentGetMessage(data=intent_get_data, context=dummy_context)
    print(f"\nIntent Service Intent Get Message:\n{intent_get_message.model_dump_json(indent=2)}")

    # Example: Intent Service Intent Reply
    intent_reply_data = IntentServiceIntentReplyData(
        intent={"intent_type": "skill-time.mycroft:TimeIntent", "confidence": 0.9}
    )
    intent_reply_message = IntentServiceIntentReplyMessage(data=intent_reply_data, context=dummy_context)
    print(f"\nIntent Service Intent Reply Message:\n{intent_reply_message.model_dump_json(indent=2)}")

    # Example: Intent Service Skills Activate
    activate_data = IntentServiceSkillsActivateData(skill_id="skill-my-game.mycroft", timeout=10.0)
    activate_message = IntentServiceSkillsActivateMessage(data=activate_data, context=dummy_context)
    print(f"\nIntent Service Skills Activate Message:\n{activate_message.model_dump_json(indent=2)}")

    # Example: Intent Service Skills Deactivate
    deactivate_data = IntentServiceSkillsDeactivateData(skill_id="skill-my-game.mycroft")
    deactivate_message = IntentServiceSkillsDeactivateMessage(data=deactivate_data, context=dummy_context)
    print(f"\nIntent Service Skills Deactivate Message:\n{deactivate_message.model_dump_json(indent=2)}")

    # Example: Dynamic Skill Activate Event
    skill_activate_event = SkillActivateMessage(
        message_type="skill-my-game.mycroft.activate",
        context=dummy_context
    )
    print(f"\nDynamic Skill Activate Event:\n{skill_activate_event.model_dump_json(indent=2)}")

    # Example: Dynamic Skill Deactivate Event
    skill_deactivate_event = SkillDeactivateMessage(
        message_type="skill-my-game.mycroft.deactivate",
        context=dummy_context
    )
    print(f"\nDynamic Skill Deactivate Event:\n{skill_deactivate_event.model_dump_json(indent=2)}")
