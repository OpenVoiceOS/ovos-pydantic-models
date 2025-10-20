from typing import Dict, Any, List, Optional, Tuple, Union
from pydantic import BaseModel, Field, ConfigDict

# Assuming these are available from your ovos_pydantic_models library
from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session, UtteranceState

# Mock for AbortEvent if not directly importable
try:
    from ovos_workshop.decorators.killable import AbortEvent
except ImportError:
    print("Warning: ovos_workshop.decorators.killable.AbortEvent not found. Using mock class.")
    class AbortEvent(Exception):
        """Exception raised to abort an event handler."""
        pass


# --- Fallback Skill Message Models ---

class OvosSkillsFallbackRegisterData(BaseModel):
    """Data for `ovos.skills.fallback.register` message."""
    skill_id: str = Field(..., description="The ID of the skill registering a fallback handler.")
    priority: int = Field(..., description="The priority of the fallback handler (lower is higher priority).")

class OvosSkillsFallbackRegisterMessage(OpenVoiceOSMessage):
    """Message for `ovos.skills.fallback.register`."""
    message_type: str = "ovos.skills.fallback.register"
    data: OvosSkillsFallbackRegisterData


class OvosSkillsFallbackDeregisterData(BaseModel):
    """Data for `ovos.skills.fallback.deregister` message."""
    skill_id: str = Field(..., description="The ID of the skill deregistering its fallback handler.")

class OvosSkillsFallbackDeregisterMessage(OpenVoiceOSMessage):
    """Message for `ovos.skills.fallback.deregister`."""
    message_type: str = "ovos.skills.fallback.deregister"
    data: OvosSkillsFallbackDeregisterData


class OvosSkillsFallbackPingData(BaseModel):
    """
    Data for `ovos.skills.fallback.ping` message.
    This message is often forwarded from an original query, so it can contain extra fields.
    """
    # The `range` field might be present if forwarded from FallbackService
    range: Optional[Tuple[int, int]] = Field(
        None, description="A tuple (start, stop) defining the priority range for fallbacks to consider."
    )
    # The original utterance data might also be forwarded
    utterances: Optional[List[str]] = Field(None, description="List of utterance strings to check against fallbacks.")
    lang: Optional[str] = Field(None, description="4-letter ISO language code for the utterances.")
    model_config = ConfigDict(extra='allow')

class OvosSkillsFallbackPingMessage(OpenVoiceOSMessage):
    """Message for `ovos.skills.fallback.ping` (request for fallback skills to respond)."""
    message_type: str = "ovos.skills.fallback.ping"
    data: OvosSkillsFallbackPingData = Field(default_factory=dict, description="Data payload for fallback ping.")


class OvosSkillsFallbackPongData(BaseModel):
    """Data for `ovos.skills.fallback.pong` message."""
    skill_id: str = Field(..., description="The ID of the skill responding to the ping.")
    can_handle: bool = Field(..., description="True if the skill can handle the current fallback request, False otherwise.")
    model_config = ConfigDict(extra='allow') # Allow other context from the original message if needed

class OvosSkillsFallbackPongMessage(OpenVoiceOSMessage):
    """Message for `ovos.skills.fallback.pong` (response from fallback skills)."""
    message_type: str = "ovos.skills.fallback.pong"
    data: OvosSkillsFallbackPongData


class OvosSkillsFallbackRequestData(BaseModel):
    """
    Data for `ovos.skills.fallback.{skill_id}.request` message.
    This message is used to trigger a specific skill's fallback handler.
    It typically includes the original utterance details.
    """
    utterances: List[str] = Field(..., description="List of utterance strings to be handled by the fallback.")
    lang: str = Field(..., description="4-letter ISO language code for the utterances.")
    model_config = ConfigDict(extra='allow')

class OvosSkillsFallbackRequestMessage(OpenVoiceOSMessage):
    """
    Message for `ovos.skills.fallback.{skill_id}.request`.
    The `message_type` will be dynamically set to the skill ID.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'ovos.skills.fallback.my-skill-id.request'.")
    data: OvosSkillsFallbackRequestData


class OvosSkillsFallbackStartMessage(OpenVoiceOSMessage):
    """
    Message for `ovos.skills.fallback.{skill_id}.start`.
    Indicates that a fallback handler for a specific skill has started processing.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'ovos.skills.fallback.my-skill-id.start'.")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Empty data payload for fallback start.")


class OvosSkillsFallbackResponseData(BaseModel):
    """Data for `ovos.skills.fallback.{skill_id}.response` message."""
    result: bool = Field(..., description="True if the fallback handler successfully handled the utterance, False otherwise.")
    fallback_handler: Optional[str] = Field(None, description="The name of the fallback handler that was invoked.")
    model_config = ConfigDict(extra='allow')

class OvosSkillsFallbackResponseMessage(OpenVoiceOSMessage):
    """
    Message for `ovos.skills.fallback.{skill_id}.response`.
    Response from a specific skill's fallback handler.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'ovos.skills.fallback.my-skill-id.response'.")
    data: OvosSkillsFallbackResponseData


class OvosSkillsFallbackKilledData(BaseModel):
    """
    Data for `ovos.skills.fallback.{skill_id}.killed` message.
    """
    error: str = Field(..., description="Error message indicating why the fallback handler was killed (e.g., 'timed out').")
    model_config = ConfigDict(extra='allow')

class OvosSkillsFallbackKilledMessage(OpenVoiceOSMessage):
    """
    Message for `ovos.skills.fallback.{skill_id}.killed`.
    Indicates that a fallback handler for a specific skill was forcefully terminated.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'ovos.skills.fallback.my-skill-id.killed'.")
    data: OvosSkillsFallbackKilledData


class OvosSkillsFallbackForceTimeoutData(BaseModel):
    """Data for `ovos.skills.fallback.force_timeout` message."""
    skill_id: str = Field(..., description="The ID of the skill whose fallback handler should be force-timed out.")
    model_config = ConfigDict(extra='allow')

class OvosSkillsFallbackForceTimeoutMessage(OpenVoiceOSMessage):
    """Message for `ovos.skills.fallback.force_timeout`."""
    message_type: str = "ovos.skills.fallback.force_timeout"
    data: OvosSkillsFallbackForceTimeoutData


class OvosUtteranceHandledMessage(OpenVoiceOSMessage):
    """
    Message for `ovos.utterance.handled`.
    (Already defined in conversational_skill_messages, included here for completeness)
    """
    message_type: str = "ovos.utterance.handled"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for utterance handled event.")


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Demonstrating Fallback Skill Message Models ---")

    # Create a dummy session and context for demonstration
    dummy_session = Session(session_id="test-fallback-skill-session-123", lang="en-us")
    dummy_context = MessageContext(source="fallback_skill", session=dummy_session)

    # Example: Register Fallback
    register_data = OvosSkillsFallbackRegisterData(skill_id="skill-my-fallback.mycroft", priority=95)
    register_message = OvosSkillsFallbackRegisterMessage(data=register_data, context=dummy_context)
    print(f"\nRegister Fallback Message:\n{register_message.model_dump_json(indent=2)}")

    # Example: Deregister Fallback
    deregister_data = OvosSkillsFallbackDeregisterData(skill_id="skill-my-fallback.mycroft")
    deregister_message = OvosSkillsFallbackDeregisterMessage(data=deregister_data, context=dummy_context)
    print(f"\nDeregister Fallback Message:\n{deregister_message.model_dump_json(indent=2)}")

    # Example: Fallback Ping
    ping_data = OvosSkillsFallbackPingData(utterances=["what is the meaning of life"], lang="en-us", range=(90, 100))
    ping_message = OvosSkillsFallbackPingMessage(data=ping_data, context=dummy_context)
    print(f"\nFallback Ping Message:\n{ping_message.model_dump_json(indent=2)}")

    # Example: Fallback Pong
    pong_data = OvosSkillsFallbackPongData(skill_id="skill-my-fallback.mycroft", can_handle=True)
    pong_message = OvosSkillsFallbackPongMessage(data=pong_data, context=dummy_context)
    print(f"\nFallback Pong Message:\n{pong_message.model_dump_json(indent=2)}")

    # Example: Dynamic Fallback Request
    request_data = OvosSkillsFallbackRequestData(
        utterances=["tell me something random"],
        lang="en-us"
    )
    request_message = OvosSkillsFallbackRequestMessage(
        message_type="ovos.skills.fallback.skill-my-fallback.mycroft.request",
        data=request_data,
        context=dummy_context
    )
    print(f"\nDynamic Fallback Request Message:\n{request_message.model_dump_json(indent=2)}")

    # Example: Dynamic Fallback Start
    start_message = OvosSkillsFallbackStartMessage(
        message_type="ovos.skills.fallback.skill-my-fallback.mycroft.start",
        context=dummy_context
    )
    print(f"\nDynamic Fallback Start Message:\n{start_message.model_dump_json(indent=2)}")

    # Example: Dynamic Fallback Response
    response_data = OvosSkillsFallbackResponseData(result=True, fallback_handler="handle_random_fact")
    response_message = OvosSkillsFallbackResponseMessage(
        message_type="ovos.skills.fallback.skill-my-fallback.mycroft.response",
        data=response_data,
        context=dummy_context
    )
    print(f"\nDynamic Fallback Response Message:\n{response_message.model_dump_json(indent=2)}")

    # Example: Dynamic Fallback Killed
    killed_data = OvosSkillsFallbackKilledData(error="timed out")
    killed_message = OvosSkillsFallbackKilledMessage(
        message_type="ovos.skills.fallback.skill-my-fallback.mycroft.killed",
        data=killed_data,
        context=dummy_context
    )
    print(f"\nDynamic Fallback Killed Message:\n{killed_message.model_dump_json(indent=2)}")

    # Example: Fallback Force Timeout
    force_timeout_data = OvosSkillsFallbackForceTimeoutData(skill_id="skill-another-fallback.mycroft")
    force_timeout_message = OvosSkillsFallbackForceTimeoutMessage(data=force_timeout_data, context=dummy_context)
    print(f"\nFallback Force Timeout Message:\n{force_timeout_message.model_dump_json(indent=2)}")

    # Example: Ovos Utterance Handled (reused from conversational_skill_messages)
    utterance_handled_message = OvosUtteranceHandledMessage(context=dummy_context)
    print(f"\nOvos Utterance Handled Message:\n{utterance_handled_message.model_dump_json(indent=2)}")
