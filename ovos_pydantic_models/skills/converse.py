from typing import Dict, Any, List, Optional, Tuple, Union
from pydantic import BaseModel, Field, ConfigDict

# Assuming these are available from your ovos_pydantic_models library
from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session, UtteranceState

# Mock for AbortEvent and AbortQuestion if not directly importable
try:
    from ovos_workshop.decorators.killable import AbortEvent, AbortQuestion
except ImportError:
    print("Warning: ovos_workshop.decorators.killable.AbortEvent/AbortQuestion not found. Using mock classes.")
    class AbortEvent(Exception):
        """Exception raised to abort an event handler."""
        pass
    class AbortQuestion(Exception):
        """Exception raised to abort a get_response loop."""
        pass


# --- Conversational Skill Message Models ---

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


class SkillConversePingMessage(OpenVoiceOSMessage):
    """
    Message for `{skill_id}.converse.ping`.
    The `message_type` will be dynamically set to the skill ID followed by `.converse.ping`.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'my-skill-id.converse.ping'.")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Empty data payload for ping command.")


class SkillConverseRequestData(BaseModel):
    """
    Data for `{skill_id}.converse.request` message.
    """
    utterances: List[str] = Field(..., description="List of utterance strings to process.")
    lang: str = Field(..., description="4-letter ISO language code for the utterances.")
    model_config = ConfigDict(extra='allow') # Allow other data from original message

class SkillConverseRequestMessage(OpenVoiceOSMessage):
    """
    Message for `{skill_id}.converse.request`.
    The `message_type` will be dynamically set to the skill ID followed by `.converse.request`.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'my-skill-id.converse.request'.")
    data: SkillConverseRequestData


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
    data:  Optional[Dict[str, Any]] = Field(default_factory=dict, description="Empty data payload for deactivate command.")


class IntentServiceSkillsDeactivatedData(BaseModel):
    """Data for `intent.service.skills.deactivated` message."""
    skill_id: str = Field(..., description="The ID of the skill that was deactivated.")
    model_config = ConfigDict(extra='allow')

class IntentServiceSkillsDeactivatedMessage(OpenVoiceOSMessage):
    """Message for `intent.service.skills.deactivated`."""
    message_type: str = "intent.service.skills.deactivated"
    data: IntentServiceSkillsDeactivatedData


class IntentServiceSkillsActivatedData(BaseModel):
    """Data for `intent.service.skills.activated` message."""
    skill_id: str = Field(..., description="The ID of the skill that was activated.")
    model_config = ConfigDict(extra='allow')

class IntentServiceSkillsActivatedMessage(OpenVoiceOSMessage):
    """Message for `intent.service.skills.activated`."""
    message_type: str = "intent.service.skills.activated"
    data: IntentServiceSkillsActivatedData


class SkillConversePongData(BaseModel):
    """Data for `skill.converse.pong` message."""
    skill_id: str = Field(..., description="The ID of the skill responding to the ping.")
    can_handle: bool = Field(..., description="True if the skill can handle converse, False otherwise.")
    model_config = ConfigDict(extra='allow')

class SkillConversePongMessage(OpenVoiceOSMessage):
    """Message for `skill.converse.pong`."""
    message_type: str = "skill.converse.pong"
    data: SkillConversePongData


class SkillConverseResponseData(BaseModel):
    """Data for `skill.converse.response` message."""
    skill_id: str = Field(..., description="The ID of the skill responding to the converse request.")
    result: bool = Field(..., description="True if the skill handled the utterance, False otherwise.")
    error: Optional[str] = Field(None, description="Error message if an exception occurred during converse.")
    model_config = ConfigDict(extra='allow')

class SkillConverseResponseMessage(OpenVoiceOSMessage):
    """Message for `skill.converse.response`."""
    message_type: str = "skill.converse.response"
    data: SkillConverseResponseData


class OvosSkillsConverseForceTimeoutData(BaseModel):
    """Data for `ovos.skills.converse.force_timeout` message."""
    skill_id: str = Field(..., description="The ID of the skill whose converse session should be force-timed out.")
    model_config = ConfigDict(extra='allow')

class OvosSkillsConverseForceTimeoutMessage(OpenVoiceOSMessage):
    """Message for `ovos.skills.converse.force_timeout`."""
    message_type: str = "ovos.skills.converse.force_timeout"
    data: OvosSkillsConverseForceTimeoutData


class SkillConverseKilledData(BaseModel):
    """
    Data for `{skill_id}.converse.killed` message.
    """
    error: str = Field(..., description="Error message indicating why the converse session was killed (e.g., 'timed out').")
    model_config = ConfigDict(extra='allow')

class SkillConverseKilledMessage(OpenVoiceOSMessage):
    """
    Message for `{skill_id}.converse.killed`.
    The `message_type` will be dynamically set to the skill ID.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'my-skill-id.converse.killed'.")
    data: SkillConverseKilledData


class OvosUtteranceHandledMessage(OpenVoiceOSMessage):
    """
    Message for `ovos.utterance.handled`.
    (Already defined in intent_service_messages, playback_messages, and listener_messages, included here for completeness)
    """
    message_type: str = "ovos.utterance.handled"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for utterance handled event.")


class ConversationalIntentData(BaseModel):
    """
    Data for dynamic conversational intent messages (e.g., `my_skill_id.converse:my_intent_name`).
    """
    # Entities from the matched intent will be present here
    model_config = ConfigDict(extra='allow')

class ConversationalIntentMessage(OpenVoiceOSMessage):
    """
    Message for dynamic conversational intents.
    The `message_type` will be dynamically set, e.g., `f"{self.skill_id}.converse:{intent_file}"`.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'my-skill-id.converse:my_intent_name'.")
    data: ConversationalIntentData = Field(default_factory=dict, description="Entities from the matched intent.")


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Demonstrating Conversational Skill Message Models ---")

    # Create a dummy session and context for demonstration
    dummy_session = Session(session_id="test-conversational-session-789", lang="en-us")
    dummy_context = MessageContext(source="conversational_skill", session=dummy_session)

    # Example: Activate Skill Request (from skill itself)
    activate_skill_data = IntentServiceSkillsActivateData(skill_id="skill-chat.mycroft", timeout=5.0)
    activate_skill_message = IntentServiceSkillsActivateMessage(data=activate_skill_data, context=dummy_context)
    print(f"\nActivate Skill Request (from skill):\n{activate_skill_message.model_dump_json(indent=2)}")

    # Example: Deactivate Skill Request (from skill itself)
    deactivate_skill_data = IntentServiceSkillsDeactivateData(skill_id="skill-chat.mycroft")
    deactivate_skill_message = IntentServiceSkillsDeactivateMessage(data=deactivate_skill_data, context=dummy_context)
    print(f"\nDeactivate Skill Request (from skill):\n{deactivate_skill_message.model_dump_json(indent=2)}")

    # Example: Dynamic Skill Converse Ping
    ping_message = SkillConversePingMessage(
        message_type="skill-chat.mycroft.converse.ping",
        context=dummy_context
    )
    print(f"\nDynamic Skill Converse Ping Message:\n{ping_message.model_dump_json(indent=2)}")

    # Example: Dynamic Skill Converse Request
    converse_request_data = SkillConverseRequestData(
        utterances=["tell me a joke"],
        lang="en-us"
    )
    converse_request_message = SkillConverseRequestMessage(
        message_type="skill-chat.mycroft.converse.request",
        data=converse_request_data,
        context=dummy_context
    )
    print(f"\nDynamic Skill Converse Request Message:\n{converse_request_message.model_dump_json(indent=2)}")

    # Example: Dynamic Skill Activate Event (from intent service)
    skill_activate_event_message = SkillActivateMessage(
        message_type="skill-chat.mycroft.activate",
        context=dummy_context
    )
    print(f"\nDynamic Skill Activate Event:\n{skill_activate_event_message.model_dump_json(indent=2)}")

    # Example: Dynamic Skill Deactivate Event (from intent service)
    skill_deactivate_event_message = SkillDeactivateMessage(
        message_type="skill-chat.mycroft.deactivate",
        context=dummy_context
    )
    print(f"\nDynamic Skill Deactivate Event:\n{skill_deactivate_event_message.model_dump_json(indent=2)}")

    # Example: Intent Service Skills Deactivated
    intent_deactivated_data = IntentServiceSkillsDeactivatedData(skill_id="skill-chat.mycroft")
    intent_deactivated_message = IntentServiceSkillsDeactivatedMessage(data=intent_deactivated_data, context=dummy_context)
    print(f"\nIntent Service Skills Deactivated Message:\n{intent_deactivated_message.model_dump_json(indent=2)}")

    # Example: Intent Service Skills Activated
    intent_activated_data = IntentServiceSkillsActivatedData(skill_id="skill-chat.mycroft")
    intent_activated_message = IntentServiceSkillsActivatedMessage(data=intent_activated_data, context=dummy_context)
    print(f"\nIntent Service Skills Activated Message:\n{intent_activated_message.model_dump_json(indent=2)}")

    # Example: Skill Converse Pong
    pong_data = SkillConversePongData(skill_id="skill-chat.mycroft", can_handle=True)
    pong_message = SkillConversePongMessage(data=pong_data, context=dummy_context)
    print(f"\nSkill Converse Pong Message:\n{pong_message.model_dump_json(indent=2)}")

    # Example: Skill Converse Response (handled)
    converse_response_handled_data = SkillConverseResponseData(skill_id="skill-chat.mycroft", result=True)
    converse_response_handled_message = SkillConverseResponseMessage(
        data=converse_response_handled_data, context=dummy_context
    )
    print(f"\nSkill Converse Response (Handled):\n{converse_response_handled_message.model_dump_json(indent=2)}")

    # Example: Skill Converse Response (error)
    converse_response_error_data = SkillConverseResponseData(
        skill_id="skill-chat.mycroft", result=False, error="Some unexpected error."
    )
    converse_response_error_message = SkillConverseResponseMessage(
        data=converse_response_error_data, context=dummy_context
    )
    print(f"\nSkill Converse Response (Error):\n{converse_response_error_message.model_dump_json(indent=2)}")

    # Example: Ovos Skills Converse Force Timeout
    force_timeout_data = OvosSkillsConverseForceTimeoutData(skill_id="skill-chat.mycroft")
    force_timeout_message = OvosSkillsConverseForceTimeoutMessage(data=force_timeout_data, context=dummy_context)
    print(f"\nOvos Skills Converse Force Timeout Message:\n{force_timeout_message.model_dump_json(indent=2)}")

    # Example: Dynamic Skill Converse Killed
    killed_data = SkillConverseKilledData(error="timed out")
    killed_message = SkillConverseKilledMessage(
        message_type="skill-chat.mycroft.converse.killed",
        data=killed_data,
        context=dummy_context
    )
    print(f"\nDynamic Skill Converse Killed Message:\n{killed_message.model_dump_json(indent=2)}")

    # Example: Dynamic Conversational Intent (e.g., from a .intent file)
    conversational_intent_data = {"entity_name": "entity_value"}
    conversational_intent_message = ConversationalIntentMessage(
        message_type="skill-chat.mycroft.converse:tell_joke.intent",
        data=conversational_intent_data,
        context=dummy_context
    )
    print(f"\nDynamic Conversational Intent Message:\n{conversational_intent_message.model_dump_json(indent=2)}")
