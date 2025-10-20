from typing import Dict, Any, Optional

from pydantic import BaseModel, Field, ConfigDict

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


# --- Skill Manager Message Models ---


class MycroftSkillsIsReadyMessage(OpenVoiceOSMessage):
    """Message for `mycroft.skills.is_ready` (request for skills service readiness)."""
    message_type: str = "mycroft.skills.is_ready"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for readiness request.")


class MycroftSkillsIsReadyReplyData(BaseModel):
    """Data for `mycroft.skills.is_ready.response` message."""
    status: bool = Field(..., description="True if the skills service is ready, False otherwise.")


class MycroftSkillsIsReadyResponseMessage(OpenVoiceOSMessage):
    """Response message for `mycroft.skills.is_ready`."""
    message_type: str = "mycroft.skills.is_ready.response"
    data: MycroftSkillsIsReadyReplyData


class MycroftSkillsReadyMessage(OpenVoiceOSMessage):
    """Message for `mycroft.skills.ready`."""
    message_type: str = "mycroft.skills.ready"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for skills ready event.")

class MycroftSkillsActivateData(BaseModel):
    """Data for `mycroft.skills.activate` message."""
    skill_id: str = Field(..., description="The ID of the skill that is activating itself.")
    # Allow other context from the original message if needed
    model_config = ConfigDict(extra='allow')


class MycroftSkillsActivateMessage(OpenVoiceOSMessage):
    """Message for `mycroft.skills.activate`."""
    message_type: str = "mycroft.skills.activate"
    data: MycroftSkillsActivateData


class MycroftSkillsDeactivateData(BaseModel):
    """Data for `mycroft.skills.deactivate` message."""
    skill_id: str = Field(..., description="The ID of the skill that is deactivating itself.")
    # Allow other context from the original message if needed
    model_config = ConfigDict(extra='allow')


class MycroftSkillsDeactivateMessage(OpenVoiceOSMessage):
    """Message for `mycroft.skills.deactivate`."""
    message_type: str = "mycroft.skills.deactivate"
    data: MycroftSkillsDeactivateData

class SkillManagerListData(BaseModel, extra='allow'):
    """Data for `skillmanager.list` message (request for skill list)."""
    # This message has no specific data payload for the request, but it's good to define it for clarity.


class SkillManagerListMessage(OpenVoiceOSMessage):
    """Message for `skillmanager.list` (request for skill list)."""
    message_type: str = "skillmanager.list"
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MycroftSkillsListData(BaseModel, extra='allow'):
    """Data for `mycroft.skills.list` message (response to skill list request)."""
    # Keys are skill IDs, values are dictionaries with "active" and "id"
    # Example: {"skill-id-1": {"active": True, "id": "skill-id-1"}}
    # Allow arbitrary skill_id keys


class MycroftSkillsListMessage(OpenVoiceOSMessage):
    """Response message for `skillmanager.list` (emitted as `mycroft.skills.list`)."""
    message_type: str = "mycroft.skills.list"
    data: MycroftSkillsListData


class SkillManagerDeactivateData(BaseModel):
    """Data for `skillmanager.deactivate` message."""
    skill: str = Field(..., description="The ID of the skill to deactivate.")


class SkillManagerDeactivateMessage(OpenVoiceOSMessage):
    """Message for `skillmanager.deactivate`."""
    message_type: str = "skillmanager.deactivate"
    data: SkillManagerDeactivateData


class SkillManagerDeactivateResponseMessage(OpenVoiceOSMessage):
    """Response message for `skillmanager.deactivate`."""
    message_type: str = "skillmanager.deactivate.response"
    data: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Optional error data if deactivation failed."
    )


class SkillManagerKeepData(BaseModel):
    """Data for `skillmanager.keep` message."""
    skill: str = Field(..., description="The ID of the skill to keep active; all others will be deactivated.")


class SkillManagerKeepMessage(OpenVoiceOSMessage):
    """Message for `skillmanager.keep`."""
    message_type: str = "skillmanager.keep"
    data: SkillManagerKeepData


class SkillManagerKeepResponseMessage(OpenVoiceOSMessage):
    """Response message for `skillmanager.keep`."""
    message_type: str = "skillmanager.keep.response"
    data: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Optional error data if deactivation failed."
    )


class SkillManagerActivateData(BaseModel):
    """Data for `skillmanager.activate` message."""
    skill: str = Field(..., description="The ID of the skill to activate ('all' for all deactivated skills).")


class SkillManagerActivateMessage(OpenVoiceOSMessage):
    """Message for `skillmanager.activate`."""
    message_type: str = "skillmanager.activate"
    data: SkillManagerActivateData


class SkillManagerActivateResponseMessage(OpenVoiceOSMessage):
    """Response message for `skillmanager.activate`."""
    message_type: str = "skillmanager.activate.response"
    data: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Optional error data if activation failed."
    )


class MycroftSkillsErrorData(BaseModel):
    """Data for `mycroft.skills.error` message."""
    internet_loaded: bool = Field(..., description="True if internet-dependent skills were loaded.")
    network_loaded: bool = Field(..., description="True if network-dependent skills were loaded.")
    error: Optional[str] = Field(None, description="Optional error message.")


class MycroftSkillsErrorMessage(OpenVoiceOSMessage):
    """Message for `mycroft.skills.error`."""
    message_type: str = "mycroft.skills.error"
    data: MycroftSkillsErrorData


class MycroftSkillsInitializedMessage(OpenVoiceOSMessage):
    """Message for `mycroft.skills.initialized`."""
    message_type: str = "mycroft.skills.initialized"
    data: Dict[str, Any] = Field(default_factory=dict,
                                 description="Empty data payload for initialization complete event.")


class MycroftSkillsTrainMessage(OpenVoiceOSMessage):
    """Message for `mycroft.skills.train` (request for intent training)."""
    message_type: str = "mycroft.skills.train"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for training request.")


class MycroftSkillsTrainedData(BaseModel):
    """Data for `mycroft.skills.trained` message (response to training request)."""
    error: Optional[str] = Field(None, description="Error message if training failed.")


class MycroftSkillsTrainedMessage(OpenVoiceOSMessage):
    """Response message for `mycroft.skills.train` (emitted as `mycroft.skills.trained`)."""
    message_type: str = "mycroft.skills.trained"
    data: MycroftSkillsTrainedData


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Demonstrating Skill Manager Message Models ---")

    # Create a dummy session and context for demonstration
    dummy_session = Session(session_id="test-skill-manager-session-101", lang="en-us")
    dummy_context = MessageContext(source="skill_manager", session=dummy_session)

    # Example: Skill Manager List request
    skill_list_request = SkillManagerListMessage(context=dummy_context)
    print(f"\nSkill Manager List Request:\n{skill_list_request.model_dump_json(indent=2)}")

    # Example: Mycroft Skills List response
    skills_list_data = MycroftSkillsListData(
        **{"skill-a.mycroft": {"active": True, "id": "skill-a.mycroft"},
           "skill-b.mycroft": {"active": False, "id": "skill-b.mycroft"}}
    )
    skills_list_response = MycroftSkillsListMessage(data=skills_list_data, context=dummy_context)
    print(f"\nMycroft Skills List Response:\n{skills_list_response.model_dump_json(indent=2)}")

    # Example: Deactivate skill
    deactivate_data = SkillManagerDeactivateData(skill="skill-to-deactivate.mycroft")
    deactivate_message = SkillManagerDeactivateMessage(data=deactivate_data, context=dummy_context)
    print(f"\nDeactivate Skill Message:\n{deactivate_message.model_dump_json(indent=2)}")

    # Example: Mycroft Skills Error
    skills_error_data = MycroftSkillsErrorData(internet_loaded=False, network_loaded=True,
                                               error="Some skills failed to load due to missing internet.")
    skills_error_message = MycroftSkillsErrorMessage(data=skills_error_data, context=dummy_context)
    print(f"\nSkills Error Message:\n{skills_error_message.model_dump_json(indent=2)}")

    # Example: Mycroft Skills Train request and response
    skills_train_request = MycroftSkillsTrainMessage(context=dummy_context)
    print(f"\nSkills Train Request:\n{skills_train_request.model_dump_json(indent=2)}")

    skills_trained_data = MycroftSkillsTrainedData()  # No error
    skills_trained_response = MycroftSkillsTrainedMessage(data=skills_trained_data, context=dummy_context)
    print(f"\nSkills Trained Response:\n{skills_trained_response.model_dump_json(indent=2)}")
    # Example: Mycroft Skills Activate
    skills_activate_data = MycroftSkillsActivateData(skill_id="skill-activated.mycroft")
    skills_activate_message = MycroftSkillsActivateMessage(data=skills_activate_data, context=dummy_context)
    print(f"\nMycroft Skills Activate Message:\n{skills_activate_message.model_dump_json(indent=2)}")

    # Example: Mycroft Skills Deactivate
    skills_deactivate_data = MycroftSkillsDeactivateData(skill_id="skill-deactivated.mycroft")
    skills_deactivate_message = MycroftSkillsDeactivateMessage(data=skills_deactivate_data, context=dummy_context)
    print(f"\nMycroft Skills Deactivate Message:\n{skills_deactivate_message.model_dump_json(indent=2)}")

    # Example: Mycroft Skills Is Ready Request
    skills_is_ready_request = MycroftSkillsIsReadyMessage(context=dummy_context)
    print(f"\nMycroft Skills Is Ready Request:\n{skills_is_ready_request.model_dump_json(indent=2)}")

    # Example: Mycroft Skills Is Ready Response
    skills_is_ready_reply_data = MycroftSkillsIsReadyReplyData(status=True)
    skills_is_ready_response = MycroftSkillsIsReadyResponseMessage(data=skills_is_ready_reply_data,
                                                                   context=dummy_context)
    print(f"\nMycroft Skills Is Ready Response:\n{skills_is_ready_response.model_dump_json(indent=2)}")

    # Example: Mycroft Skills Ready
    skills_ready_message = MycroftSkillsReadyMessage(context=dummy_context)
    print(f"\nMycroft Skills Ready Message:\n{skills_ready_message.model_dump_json(indent=2)}")
