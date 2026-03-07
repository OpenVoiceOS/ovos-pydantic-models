from typing import Dict, Any, List, Optional, Union

from pydantic import BaseModel, Field, ConfigDict

from ovos_pydantic_models.message import OpenVoiceOSMessage

# Re-export OCP types and messages used by game skills
from ovos_pydantic_models.skills.ocp import (  # noqa: F401
    MediaType,
    PlaybackType,
    PlayerState,
    MatchConfidence,
    LoopState,
    TrackState,
    MediaState,
    PlaybackMode,
    BaseMediaEntry,
    MediaEntry,
    PluginStream,
    Playlist,
    OvosCommonPlayPlayerStateData,
    OvosCommonPlayPlayerStateMessage,
    OvosCommonPlayAnnounceData,
    OvosCommonPlayAnnounceMessage,
    OvosCommonPlayQueryData,
    OvosCommonPlayQueryMessage,
    OvosCommonPlayQueryResponseData,
    OvosCommonPlayQueryResponseMessage,
    OvosCommonPlaySkillSearchStartData,
    OvosCommonPlaySkillSearchStartMessage,
    OvosCommonPlaySkillSearchEndData,
    OvosCommonPlaySkillSearchEndMessage,
    OvosCommonPlayFeaturedTracksPlayData,
    OvosCommonPlayFeaturedTracksPlayMessage,
    OvosCommonPlaySkillsGetMessage,
    OvosCommonPlaySkillsDetachData,
    OvosCommonPlaySkillsDetachMessage,
    OvosCommonPlaySearchStopMessage,
)
from ovos_pydantic_models.intents.converse import (  # noqa: F401
    IntentServiceSkillsActivateData,
    IntentServiceSkillsActivateMessage,
    IntentServiceSkillsDeactivateData,
    IntentServiceSkillsDeactivateMessage,
)
from ovos_pydantic_models.intents.core import (  # noqa: F401
    IntentServiceIntentGetData,
    IntentServiceIntentGetMessage,
    IntentServiceIntentReplyData,
    IntentServiceIntentReplyMessage,
    SkillActivateMessage,
    SkillDeactivateMessage,
)


# --- Game Skill Specific Message Models ---

class OvosCommonPlaySkillPlayData(BaseModel):
    """Payload for OCP to initiate playback of a game skill's content list.

    Distinct from `OvosCommonPlaySkillPlayData` in `ocp.py` which handles
    the per-skill `{skill_id}.play` dynamic messages. This variant is sent
    from OCP to the game skill via `ovos.common_play.skill.play` and carries
    the full playlist to hand off to the game engine.
    """
    skill_id: str = Field(..., description="The ID of the skill to play media from.")
    skill_name: str = Field(..., description="The name of the skill playing media.")
    thumbnail: str = Field(..., description="URL or path to the skill's icon/thumbnail.")
    playlist: List[Union[MediaEntry, PluginStream, Dict[str, Any]]] = Field(
        ..., description="The playlist of media entries to play."
    )
    model_config = ConfigDict(extra='allow')


class OvosCommonPlaySkillPlayMessage(OpenVoiceOSMessage):
    """Tell a game skill to begin playing its selected content playlist.

    Emitted by OCP (via the game framework) after a search wins and the game
    skill should take over rendering. The game skill initializes its engine
    and begins presenting the first entry in `playlist`.
    """
    message_type: str = "ovos.common_play.skill.play"
    data: OvosCommonPlaySkillPlayData


class SkillGameCommandData(BaseModel):
    """Payload carrying a user utterance to a running game skill's command handler."""
    utterances: List[str] = Field(..., description="List of utterance strings to pipe to the game.")
    lang: str = Field(..., description="4-letter ISO language code for the utterances.")
    model_config = ConfigDict(extra='allow')


class SkillGameCommandMessage(OpenVoiceOSMessage):
    """Pipe a user utterance directly to a game skill's `on_game_command()` handler.

    Dynamic message type: `{skill_id}.game_cmd`. Emitted by the intent
    service when a skill is in 'game mode' — utterances bypass the normal
    pipeline and are forwarded as raw text to the active game skill.
    The skill's `on_game_command()` method interprets them as game input.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'my-skill-id.game_cmd'.")
    data: SkillGameCommandData
