from enum import Enum
from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field, ConfigDict

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


class IntentHandlerMatch(BaseModel):
    match_type: str
    match_data: Dict[str, Any]
    skill_id: Optional[str] = None
    utterance: str
    confidence: float = 0.0
    updated_session: Optional[Session] = None
    model_config = ConfigDict(extra='allow')


# Enums for ConverseMode and ConverseActivationMode (from ovos_workshop.permissions)
class ConverseMode(str, Enum):
    """
    Defines how the converse system handles skill conversations.
    """
    ACCEPT_ALL = "accept_all"
    BLACKLIST = "blacklist"
    WHITELIST = "whitelist"


class ConverseActivationMode(str, Enum):
    """
    Defines the conditions under which a skill is allowed to activate itself
    (jump to the front of the active skills list).
    """
    ACCEPT_ALL = "accept_all"
    PRIORITY = "priority"
    BLACKLIST = "blacklist"
    WHITELIST = "whitelist"


# --- Converse Service Message Models ---


class IntentServiceSkillsActivateData(BaseModel):
    """Data for `intent.service.skills.activate` message."""
    skill_id: str = Field(..., description="The ID of the skill to activate.")


class IntentServiceSkillsActivateMessage(OpenVoiceOSMessage):
    """Message for `intent.service.skills.activate`."""
    message_type: str = "intent.service.skills.activate"
    data: IntentServiceSkillsActivateData

class IntentServiceSkillsActivatedMessage(OpenVoiceOSMessage):
    """Message for `intent.service.skills.activated`."""
    message_type: str = "intent.service.skills.activated"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for skills activated event.")


class IntentServiceActiveSkillsGetMessage(OpenVoiceOSMessage):
    """Message for `intent.service.active_skills.get`."""
    message_type: str = "intent.service.active_skills.get"
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class IntentServiceActiveSkillsReplyData(BaseModel):
    """Data for `intent.service.active_skills.reply` message."""
    skills: List[str] = Field(..., description="Ordered list of active skill IDs.")


class IntentServiceActiveSkillsReplyMessage(OpenVoiceOSMessage):
    """Message for `intent.service.active_skills.reply`."""
    message_type: str = "intent.service.active_skills.reply"
    data: IntentServiceActiveSkillsReplyData


class SkillConverseGetResponseEnableData(BaseModel):
    """Data for `skill.converse.get_response.enable` message."""
    skill_id: str = Field(..., description="The ID of the skill to enable get_response mode for.")


class SkillConverseGetResponseEnableMessage(OpenVoiceOSMessage):
    """Message for `skill.converse.get_response.enable`."""
    message_type: str = "skill.converse.get_response.enable"
    data: SkillConverseGetResponseEnableData


class SkillConverseGetResponseDisableData(BaseModel):
    """Data for `skill.converse.get_response.disable` message."""
    skill_id: str = Field(..., description="The ID of the skill to disable get_response mode for.")


class SkillConverseGetResponseDisableMessage(OpenVoiceOSMessage):
    """Message for `skill.converse.get_response.disable`."""
    message_type: str = "skill.converse.get_response.disable"
    data: SkillConverseGetResponseDisableData


class ConverseSkillData(BaseModel):
    """Data for `converse:skill` message."""
    skill_id: str = Field(..., description="The ID of the skill to converse with.")
    # The original message data (utterances, lang) is also passed
    utterances: List[str] = Field(..., description="List of utterance strings to process.")
    lang: str = Field(..., description="4-letter ISO language code for the utterances.")
    model_config = ConfigDict(extra='allow')  # Allow other data from original message


class ConverseSkillMessage(OpenVoiceOSMessage):
    """Message for `converse:skill`."""
    message_type: str = "converse:skill"
    data: ConverseSkillData


class SkillConverseRequestData(BaseModel):
    """
    Data for `{skill_id}.converse.request` message.
    This message is forwarded from `converse:skill`, so it includes the same data.
    """
    skill_id: str = Field(..., description="The ID of the skill targeted for converse request.")
    utterances: List[str] = Field(..., description="List of utterance strings to process.")
    lang: str = Field(..., description="4-letter ISO language code for the utterances.")
    model_config = ConfigDict(extra='allow')  # Allow other data from original message


class SkillConverseRequestMessage(OpenVoiceOSMessage):
    """
    Message for `{skill_id}.converse.request`.
    The `message_type` will be dynamically set to the skill ID followed by `.converse.request`.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'my-skill-id.converse.request'.")
    data: SkillConverseRequestData


class IntentServiceSkillsDeactivateData(BaseModel):
    """Data for `intent.service.skills.deactivate` message."""
    skill_id: str = Field(..., description="The ID of the skill to deactivate from the active skills list.")


class IntentServiceSkillsDeactivateMessage(OpenVoiceOSMessage):
    """Message for `intent.service.skills.deactivate`."""
    message_type: str = "intent.service.skills.deactivate"
    data: IntentServiceSkillsDeactivateData

class IntentServiceSkillsDeactivatedData(BaseModel):
    """Data for `intent.service.skills.deactivated` message."""
    skill_id: str = Field(..., description="The ID of the skill that was deactivated.")


class IntentServiceSkillsDeactivatedMessage(OpenVoiceOSMessage):
    """Message for `intent.service.skills.deactivated`."""
    message_type: str = "intent.service.skills.deactivated"
    data: IntentServiceSkillsDeactivatedData


class SkillConversePongData(BaseModel):
    """Data for `skill.converse.pong` message."""
    skill_id: str = Field(..., description="The ID of the skill responding to the ping.")
    can_handle: bool = Field(True, description="True if the skill can handle the current conversation.")
    model_config = ConfigDict(extra='allow')  # Allow other data from original ping message


class SkillConversePongMessage(OpenVoiceOSMessage):
    """Message for `skill.converse.pong`."""
    message_type: str = "skill.converse.pong"
    data: SkillConversePongData


class SkillConversePingData(BaseModel):
    """
    Data for `{skill_id}.converse.ping` message.
    This message is forwarded from the original utterance message.
    """
    skill_id: str = Field(..., description="The ID of the skill being pinged for converse capability.")
    utterances: List[str] = Field(..., description="List of utterance strings to check for converse capability.")
    lang: str = Field(..., description="4-letter ISO language code for the utterances.")
    model_config = ConfigDict(extra='allow')  # Allow other data from original message


class SkillConversePingMessage(OpenVoiceOSMessage):
    """
    Message for `{skill_id}.converse.ping`.
    The `message_type` will be dynamically set to the skill ID followed by `.converse.ping`.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'my-skill-id.converse.ping'.")
    data: SkillConversePingData


class SkillConverseGetResponseMatchData(BaseModel):
    """
    Data for `{skill_id}.converse.get_response` match.
    This is the data payload for the IntentHandlerMatch object returned by `match`.
    """
    utterances: List[str] = Field(..., description="List of utterance strings that triggered the get_response.")
    lang: str = Field(..., description="4-letter ISO language code for the utterances.")
    model_config = ConfigDict(extra='allow')  # Allow other data from original message


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Demonstrating Converse Service Message Models ---")

    # Create a dummy session and context for demonstration
    dummy_session = Session(session_id="test-converse-session-456", lang="en-us")
    dummy_context = MessageContext(source="converse_service", session=dummy_session)

    # Example: Activate Skill Request
    activate_skill_data = IntentServiceSkillsActivateData(skill_id="skill-example.mycroft")
    activate_skill_message = IntentServiceSkillsActivateMessage(data=activate_skill_data, context=dummy_context)
    print(f"\nActivate Skill Message:\n{activate_skill_message.model_dump_json(indent=2)}")

    # Example: Get Active Skills Request
    get_active_skills_request = IntentServiceActiveSkillsGetMessage(context=dummy_context)
    print(f"\nGet Active Skills Request:\n{get_active_skills_request.model_dump_json(indent=2)}")

    # Example: Get Active Skills Reply
    get_active_skills_reply_data = IntentServiceActiveSkillsReplyData(skills=["skill-a.mycroft", "skill-b.mycroft"])
    get_active_skills_reply_message = IntentServiceActiveSkillsReplyMessage(data=get_active_skills_reply_data,
                                                                            context=dummy_context)
    print(f"\nGet Active Skills Reply:\n{get_active_skills_reply_message.model_dump_json(indent=2)}")

    # Example: Enable Get Response
    enable_get_response_data = SkillConverseGetResponseEnableData(skill_id="skill-my-dialog.mycroft")
    enable_get_response_message = SkillConverseGetResponseEnableMessage(data=enable_get_response_data,
                                                                        context=dummy_context)
    print(f"\nEnable Get Response Message:\n{enable_get_response_message.model_dump_json(indent=2)}")

    # Example: Converse Skill
    converse_skill_data = ConverseSkillData(skill_id="skill-music.mycroft", utterances=["play some jazz"], lang="en-us")
    converse_skill_message = ConverseSkillMessage(data=converse_skill_data, context=dummy_context)
    print(f"\nConverse Skill Message:\n{converse_skill_message.model_dump_json(indent=2)}")

    # Example: Dynamic Skill Converse Request (from converse:skill)
    dynamic_converse_request_data = SkillConverseRequestData(
        skill_id="skill-music.mycroft",
        utterances=["play some jazz"],
        lang="en-us",
        some_extra_field="value"  # Example of extra data
    )
    dynamic_converse_request_message = SkillConverseRequestMessage(
        message_type="skill-music.mycroft.converse.request",
        data=dynamic_converse_request_data,
        context=dummy_context
    )
    print(f"\nDynamic Skill Converse Request Message:\n{dynamic_converse_request_message.model_dump_json(indent=2)}")

    # Example: Deactivated Skill
    deactivated_skill_data = IntentServiceSkillsDeactivatedData(skill_id="skill-old-context.mycroft")
    deactivated_skill_message = IntentServiceSkillsDeactivatedMessage(data=deactivated_skill_data,
                                                                      context=dummy_context)
    print(f"\nDeactivated Skill Message:\n{deactivated_skill_message.model_dump_json(indent=2)}")

    # Example: Skill Converse Pong
    pong_data = SkillConversePongData(skill_id="skill-music.mycroft", can_handle=True)
    pong_message = SkillConversePongMessage(data=pong_data, context=dummy_context)
    print(f"\nSkill Converse Pong Message:\n{pong_message.model_dump_json(indent=2)}")

    # Example: Dynamic Skill Converse Ping
    dynamic_ping_data = SkillConversePingData(
        skill_id="skill-music.mycroft",
        utterances=["what's playing"],
        lang="en-us"
    )
    dynamic_ping_message = SkillConversePingMessage(
        message_type="skill-music.mycroft.converse.ping",
        data=dynamic_ping_data,
        context=dummy_context
    )
    print(f"\nDynamic Skill Converse Ping Message:\n{dynamic_ping_message.model_dump_json(indent=2)}")

    # Example: Skill Converse Get Response Match Data (used by IntentHandlerMatch)
    get_response_match_data_example = SkillConverseGetResponseMatchData(
        utterances=["yes"],
        lang="en-us",
        original_message_id="some-uuid"
    )
    print(
        f"\nSkill Converse Get Response Match Data (example for IntentHandlerMatch):\n{get_response_match_data_example.model_dump_json(indent=2)}")
