from typing import Dict, Any, List, Optional, Tuple, Union
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, model_validator

# Assuming these are available from your ovos_pydantic_models library
from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session

# Enums for FallbackMode (from ovos_workshop.permissions)
class FallbackMode(str, Enum):
    """
    Defines how the fallback system handles skill fallbacks.
    """
    ACCEPT_ALL = "accept_all"
    BLACKLIST = "blacklist"
    WHITELIST = "whitelist"


# --- Fallback Service Message Models ---

class OvosSkillsFallbackRegisterData(BaseModel):
    """Data for `ovos.skills.fallback.register` message."""
    skill_id: str = Field(..., description="The ID of the skill registering a fallback handler.")
    priority: int = Field(101, description="The priority of the fallback handler (lower is higher priority).")

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
    """Data for `ovos.skills.fallback.ping` message."""
    range: Optional[Tuple[int, int]] = Field(
        None, description="A tuple (start, stop) defining the priority range for fallbacks to consider."
    )
    # These fields are usually forwarded from the original utterance message
    utterances: List[str] = Field(..., description="List of utterance strings to check against fallbacks.")
    lang: str = Field(..., description="4-letter ISO language code for the utterances.")
    model_config = ConfigDict(extra='allow') # Allow other data from original message

class OvosSkillsFallbackPingMessage(OpenVoiceOSMessage):
    """Message for `ovos.skills.fallback.ping`."""
    message_type: str = "ovos.skills.fallback.ping"
    data: OvosSkillsFallbackPingData


class OvosSkillsFallbackPongData(BaseModel):
    """Data for `ovos.skills.fallback.pong` message."""
    skill_id: str = Field(..., description="The ID of the skill responding to the ping.")
    can_handle: bool = Field(True, description="True if the skill can handle the current fallback request.")
    model_config = ConfigDict(extra='allow') # Allow other data from original ping message

class OvosSkillsFallbackPongMessage(OpenVoiceOSMessage):
    """Message for `ovos.skills.fallback.pong`."""
    message_type: str = "ovos.skills.fallback.pong"
    data: OvosSkillsFallbackPongData


class OvosSkillsFallbackRequestData(BaseModel):
    """
    Data for `ovos.skills.fallback.{skill_id}.request` message.
    This message is used to trigger a specific skill's fallback handler.
    """
    skill_id: str = Field(..., description="The ID of the skill whose fallback handler is being requested.")
    utterances: List[str] = Field(..., description="List of utterance strings to be handled by the fallback.")
    lang: str = Field(..., description="4-letter ISO language code for the utterances.")
    model_config = ConfigDict(extra='allow') # Allow other data from original message

class OvosSkillsFallbackRequestMessage(OpenVoiceOSMessage):
    """
    Message for `ovos.skills.fallback.{skill_id}.request`.
    The `message_type` will be dynamically set to the skill ID.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'ovos.skills.fallback.my-skill-id.request'.")
    data: OvosSkillsFallbackRequestData


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Demonstrating Fallback Service Message Models ---")

    # Create a dummy session and context for demonstration
    dummy_session = Session(session_id="test-fallback-session-789", lang="en-us")
    dummy_context = MessageContext(source="fallback_service", session=dummy_session)

    # Example: Register Fallback
    register_fallback_data = OvosSkillsFallbackRegisterData(skill_id="skill-weather.mycroft", priority=50)
    register_fallback_message = OvosSkillsFallbackRegisterMessage(data=register_fallback_data, context=dummy_context)
    print(f"\nRegister Fallback Message:\n{register_fallback_message.model_dump_json(indent=2)}")

    # Example: Deregister Fallback
    deregister_fallback_data = OvosSkillsFallbackDeregisterData(skill_id="skill-weather.mycroft")
    deregister_fallback_message = OvosSkillsFallbackDeregisterMessage(data=deregister_fallback_data, context=dummy_context)
    print(f"\nDeregister Fallback Message:\n{deregister_fallback_message.model_dump_json(indent=2)}")

    # Example: Fallback Ping
    ping_data = OvosSkillsFallbackPingData(
        range=(0, 100),
        utterances=["what is the weather like"],
        lang="en-us",
        original_message_id="some-uuid-1"
    )
    ping_message = OvosSkillsFallbackPingMessage(data=ping_data, context=dummy_context)
    print(f"\nFallback Ping Message:\n{ping_message.model_dump_json(indent=2)}")

    # Example: Fallback Pong
    pong_data = OvosSkillsFallbackPongData(skill_id="skill-weather.mycroft", can_handle=True)
    pong_message = OvosSkillsFallbackPongMessage(data=pong_data, context=dummy_context)
    print(f"\nFallback Pong Message:\n{pong_message.model_dump_json(indent=2)}")

    # Example: Dynamic Fallback Request
    dynamic_fallback_request_data = OvosSkillsFallbackRequestData(
        skill_id="skill-weather.mycroft",
        utterances=["what's the forecast"],
        lang="en-us",
        some_extra_field="value" # Example of extra data
    )
    dynamic_fallback_request_message = OvosSkillsFallbackRequestMessage(
        message_type="ovos.skills.fallback.skill-weather.mycroft.request",
        data=dynamic_fallback_request_data,
        context=dummy_context
    )
    print(f"\nDynamic Fallback Request Message:\n{dynamic_fallback_request_message.model_dump_json(indent=2)}")
