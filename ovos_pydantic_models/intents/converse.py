from enum import Enum
from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field, ConfigDict

from ovos_pydantic_models.message import OpenVoiceOSMessage
from ovos_pydantic_models.session import Session


class IntentHandlerMatch(BaseModel):
    """Represents a successful intent match returned by a pipeline plugin."""
    match_type: str
    match_data: Dict[str, Any]
    skill_id: Optional[str] = None
    utterance: str
    confidence: float = 0.0
    updated_session: Optional[Session] = None
    model_config = ConfigDict(extra='allow')


class ConverseMode(str, Enum):
    """Controls which skills are allowed to participate in the converse pipeline."""
    ACCEPT_ALL = "accept_all"   # Any skill in the converse stack can handle utterances
    BLACKLIST = "blacklist"     # All except explicitly blacklisted skill IDs
    WHITELIST = "whitelist"     # Only explicitly whitelisted skill IDs


class ConverseActivationMode(str, Enum):
    """Controls which skills are permitted to add themselves to the converse stack."""
    ACCEPT_ALL = "accept_all"   # Any skill may activate itself
    PRIORITY = "priority"       # Activate only if no higher-priority skill is active
    BLACKLIST = "blacklist"     # All except blacklisted skill IDs
    WHITELIST = "whitelist"     # Only whitelisted skill IDs


# --- Converse Service Message Models ---

class IntentServiceSkillsActivateData(BaseModel):
    """Request payload for adding a skill to the converse priority stack."""
    skill_id: str = Field(..., description="Skill ID to add to the top of the converse stack.")
    timeout: Optional[float] = Field(
        None, description="How long (minutes) the skill stays active before auto-deactivation. -1 means indefinite."
    )
    model_config = ConfigDict(extra='allow')


class IntentServiceSkillsActivateMessage(OpenVoiceOSMessage):
    """Add a skill to the converse priority stack so it gets first refusal on utterances.

    Emitted by a skill (via `self.make_active()`) or the intent service after
    a skill handles an intent. The skill receives `{skill_id}.activate` once
    confirmed. Active skills' `converse()` method is called before any intent
    matching on subsequent utterances.
    """
    message_type: str = "intent.service.skills.activate"
    data: IntentServiceSkillsActivateData


class IntentServiceSkillsActivatedData(BaseModel):
    """Confirmation payload for a skill being added to the converse stack."""
    skill_id: str = Field(..., description="Skill ID that was successfully activated.")


class IntentServiceSkillsActivatedMessage(OpenVoiceOSMessage):
    """Confirm that a skill was successfully added to the converse stack.

    Emitted by the intent service in response to `intent.service.skills.activate`.
    The skill and any interested observers receive this event.
    """
    message_type: str = "intent.service.skills.activated"
    data: IntentServiceSkillsActivatedData


class IntentServiceActiveSkillsGetMessage(OpenVoiceOSMessage):
    """Query the ordered list of skills currently in the converse stack.

    Any component may request this; the intent service replies with
    `intent.service.active_skills.reply`. Useful for debugging and GUI displays.
    """
    message_type: str = "intent.service.active_skills.get"
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class IntentServiceActiveSkillsReplyData(BaseModel):
    """Ordered converse stack returned in reply to an active-skills query."""
    skills: List[str] = Field(..., description="Skill IDs in converse-priority order, highest priority first.")


class IntentServiceActiveSkillsReplyMessage(OpenVoiceOSMessage):
    """Return the ordered converse skill stack in reply to `intent.service.active_skills.get`.

    Emitted by the intent service.
    """
    message_type: str = "intent.service.active_skills.reply"
    data: IntentServiceActiveSkillsReplyData


class SkillConverseGetResponseEnableData(BaseModel):
    """Request payload for enabling get_response mode on a skill."""
    skill_id: str = Field(..., description="Skill ID that called `get_response()` and is now waiting for user input.")


class SkillConverseGetResponseEnableMessage(OpenVoiceOSMessage):
    """Tell the intent service that a skill is waiting for a direct user response.

    Emitted internally when a skill calls `self.get_response()`. The intent
    service routes the next utterance directly to this skill's converse handler
    rather than through the normal pipeline. Disables fallback temporarily.
    """
    message_type: str = "skill.converse.get_response.enable"
    data: SkillConverseGetResponseEnableData


class SkillConverseGetResponseDisableData(BaseModel):
    """Request payload for exiting get_response mode on a skill."""
    skill_id: str = Field(..., description="Skill ID that is done waiting for user input.")


class SkillConverseGetResponseDisableMessage(OpenVoiceOSMessage):
    """Tell the intent service that a skill's get_response() wait is over.

    Emitted after the skill receives the user's response or times out.
    Normal pipeline routing resumes for subsequent utterances.
    """
    message_type: str = "skill.converse.get_response.disable"
    data: SkillConverseGetResponseDisableData


class ConverseSkillData(BaseModel):
    """Payload for routing an utterance directly to a named skill's converse handler."""
    skill_id: str = Field(..., description="Target skill ID whose converse() method will be called.")
    utterances: List[str] = Field(..., description="Transcription candidates, best first.")
    lang: str = Field(..., description="BCP-47 language code of the utterances.")
    model_config = ConfigDict(extra='allow')


class ConverseSkillMessage(OpenVoiceOSMessage):
    """Route an utterance to a specific skill's converse() method, bypassing the normal pipeline.

    Emitted by the intent service when it has determined a particular skill
    should handle the utterance in its converse phase (e.g. get_response flows).
    """
    message_type: str = "converse:skill"
    data: ConverseSkillData


class SkillConverseRequestData(BaseModel):
    """Payload for asking a specific skill to process an utterance in converse mode."""
    skill_id: str = Field(..., description="Target skill ID.")
    utterances: List[str] = Field(..., description="Transcription candidates, best first.")
    lang: str = Field(..., description="BCP-47 language code.")
    model_config = ConfigDict(extra='allow')


class SkillConverseRequestMessage(OpenVoiceOSMessage):
    """Ask a specific skill to handle an utterance via its `converse()` method.

    Dynamic message type: `{skill_id}.converse.request`. Emitted by the intent
    service per-skill during the converse phase. The skill replies with
    `skill.converse.response` indicating whether it handled the utterance.
    """
    message_type: str = Field(..., description="Dynamic: '{skill_id}.converse.request'.")
    data: SkillConverseRequestData


class IntentServiceSkillsDeactivateData(BaseModel):
    """Request payload for removing a skill from the converse stack."""
    skill_id: str = Field(..., description="Skill ID to remove from the converse stack.")
    model_config = ConfigDict(extra='allow')


class IntentServiceSkillsDeactivateMessage(OpenVoiceOSMessage):
    """Remove a skill from the converse priority stack.

    Emitted by a skill via `self.cancel_active()`, by the intent service
    after a deactivation timeout, or by `intent.service.skills.deactivate`
    from external control. The skill receives `{skill_id}.deactivate` once done.
    """
    message_type: str = "intent.service.skills.deactivate"
    data: IntentServiceSkillsDeactivateData


class IntentServiceSkillsDeactivatedData(BaseModel):
    """Confirmation that a skill was removed from the converse stack."""
    skill_id: str = Field(..., description="Skill ID that was deactivated.")


class IntentServiceSkillsDeactivatedMessage(OpenVoiceOSMessage):
    """Confirm that a skill was successfully removed from the converse stack.

    Emitted by the intent service in response to a deactivate request.
    """
    message_type: str = "intent.service.skills.deactivated"
    data: IntentServiceSkillsDeactivatedData


class SkillConversePongData(BaseModel):
    """A skill's response to a converse capability ping."""
    skill_id: str = Field(..., description="Skill ID responding to the ping.")
    can_handle: bool = Field(True, description="True if this skill's converse() is willing to handle the current utterance.")
    model_config = ConfigDict(extra='allow')


class SkillConversePongMessage(OpenVoiceOSMessage):
    """A skill declares whether it can handle the current utterance in converse mode.

    Emitted by the skill in reply to `{skill_id}.converse.ping`. The intent
    service collects pongs to determine which active skill to route to.
    """
    message_type: str = "skill.converse.pong"
    data: SkillConversePongData


class SkillConversePingData(BaseModel):
    """Poll payload sent to a specific skill asking if it wants to handle the utterance."""
    skill_id: str = Field(..., description="Target skill being polled.")
    utterances: List[str] = Field(..., description="Transcription candidates the skill should evaluate.")
    lang: str = Field(..., description="BCP-47 language code.")
    model_config = ConfigDict(extra='allow')


class SkillConversePingMessage(OpenVoiceOSMessage):
    """Poll a skill to see if it wants to handle the current utterance in converse mode.

    Dynamic message type: `{skill_id}.converse.ping`. Sent by the intent service
    to each active skill in priority order. The skill replies with
    `skill.converse.pong`. This two-step ping/pong avoids invoking converse()
    on skills that won't handle the utterance.
    """
    message_type: str = Field(..., description="Dynamic: '{skill_id}.converse.ping'.")
    data: SkillConversePingData


class SkillConverseGetResponseMatchData(BaseModel):
    """Utterance data delivered to a skill that called get_response() and is now waiting."""
    utterances: List[str] = Field(..., description="The user's response utterances.")
    lang: str = Field(..., description="BCP-47 language code.")
    model_config = ConfigDict(extra='allow')


# --- Skill-side converse messages ---

class SkillConverseResponseData(BaseModel):
    """A skill's verdict on whether it handled the converse request."""
    skill_id: str = Field(..., description="Skill ID that was asked to handle the utterance.")
    result: bool = Field(..., description="True if the skill's converse() consumed the utterance; False to pass to the next stage.")
    error: Optional[str] = Field(None, description="Exception message if converse() raised an unhandled error.")
    model_config = ConfigDict(extra='allow')


class SkillConverseResponseMessage(OpenVoiceOSMessage):
    """A skill reports whether its converse() method handled the utterance.

    Emitted by the skill in reply to `{skill_id}.converse.request`. If
    `result` is False the intent service moves to the next active skill or
    falls through to the normal intent pipeline.
    """
    message_type: str = "skill.converse.response"
    data: SkillConverseResponseData


class SkillConverseKilledData(BaseModel):
    """Error payload emitted when a converse session is force-terminated."""
    error: str = Field(..., description="Reason the converse session was killed (e.g. timeout, exception).")
    model_config = ConfigDict(extra='allow')


class SkillConverseKilledMessage(OpenVoiceOSMessage):
    """Signal that a skill's converse() was force-terminated (timeout or error).

    Dynamic message type: `{skill_id}.converse.killed`. Emitted by the intent
    service to notify the skill its converse handling was aborted. The skill
    should clean up any pending get_response() state.
    """
    message_type: str = Field(..., description="Dynamic: '{skill_id}.converse.killed'.")
    data: SkillConverseKilledData


class ConversationalIntentData(BaseModel):
    """Entities extracted from a matched conversational intent."""
    model_config = ConfigDict(extra='allow')


class ConversationalIntentMessage(OpenVoiceOSMessage):
    """Dispatch a matched conversational intent to its handler.

    Dynamic message type: `{skill_id}.converse:{intent_name}`. Emitted by
    the intent service when padatious/adapt matches an intent that was
    registered specifically for the converse phase (via `@converse_handler`).
    """
    message_type: str = Field(..., description="Dynamic: '{skill_id}.converse:{intent_name}'.")
    data: ConversationalIntentData = Field(default_factory=ConversationalIntentData, description="Extracted intent entities.")
