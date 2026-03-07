from typing import Dict, Any

from pydantic import BaseModel, Field, ConfigDict

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


class RuntimeRequirements(BaseModel):
    """
    Defines the runtime requirements for a skill, indicating its dependencies
    on network, internet, and GUI availability.
    """
    internet_before_load: bool = Field(True, description="True if internet is required before skill loading.")
    network_before_load: bool = Field(True, description="True if network is required before skill loading.")
    requires_internet: bool = Field(True, description="True if internet is required for skill runtime.")
    requires_network: bool = Field(True, description="True if network is required for skill runtime.")
    requires_gui: bool = Field(False, description="True if GUI is required for skill runtime.")
    no_internet_fallback: bool = Field(False, description="True if skill has a fallback for no internet.")
    no_network_fallback: bool = Field(False, description="True if skill has a fallback for no network.")
    no_gui_fallback: bool = Field(False, description="True if skill has a fallback for no GUI.")
    model_config = ConfigDict(extra='allow')


# --- OVOS Skill Message Models ---


class MycroftSkillsLoadedData(BaseModel):
    """Data for `mycroft.skills.loaded` message."""
    path: str = Field(..., description="The file path of the loaded skill.")
    id: str = Field(..., description="The ID of the loaded skill.")


class MycroftSkillsLoadedMessage(OpenVoiceOSMessage):
    """Message for `mycroft.skills.loaded`."""
    message_type: str = "mycroft.skills.loaded"
    data: MycroftSkillsLoadedData


class MycroftSkillsLoadingData(BaseModel):
    """Data for `mycroft.skills.loading` message."""
    path: str = Field(..., description="The file path of the skill being loaded.")
    id: str = Field(..., description="The ID of the skill being loaded.")


class MycroftSkillsLoadingMessage(OpenVoiceOSMessage):
    """Message for `mycroft.skills.loading`."""
    message_type: str = "mycroft.skills.loading"
    data: MycroftSkillsLoadingData


class MycroftSkillHandlerStartData(BaseModel):
    """Data for `mycroft.skill.handler.start` message."""
    handler: str = Field(..., description="The name of the handler function that started.")
    skill_id: str = Field(..., description="The ID of the skill whose handler started.")
    # Allow other context from the original message if needed
    model_config = ConfigDict(extra='allow')


class MycroftSkillHandlerStartMessage(OpenVoiceOSMessage):
    """Message for `mycroft.skill.handler.start`."""
    message_type: str = "mycroft.skill.handler.start"
    data: MycroftSkillHandlerStartData


class MycroftSkillHandlerCompleteData(BaseModel):
    """Data for `mycroft.skill.handler.complete` message."""
    handler: str = Field(..., description="The name of the handler function that completed.")
    skill_id: str = Field(..., description="The ID of the skill whose handler completed.")
    duration: float = Field(..., description="The execution duration of the handler in seconds.")
    # Allow other context from the original message if needed
    model_config = ConfigDict(extra='allow')


class MycroftSkillHandlerCompleteMessage(OpenVoiceOSMessage):
    """Message for `mycroft.skill.handler.complete`."""
    message_type: str = "mycroft.skill.handler.complete"
    data: MycroftSkillHandlerCompleteData


class MycroftSkillHandlerErrorData(BaseModel):
    """Data for `mycroft.skill.handler.error` message."""
    handler: str = Field(..., description="The name of the handler function that encountered an error.")
    skill_id: str = Field(..., description="The ID of the skill whose handler encountered an error.")
    traceback: str = Field(..., description="The traceback of the error.")
    # Allow other context from the original message if needed
    model_config = ConfigDict(extra='allow')


class MycroftSkillHandlerErrorMessage(OpenVoiceOSMessage):
    """Message for `mycroft.skill.handler.error`."""
    message_type: str = "mycroft.skill.handler.error"
    data: MycroftSkillHandlerErrorData



class MycroftSkillsIdleMessage(OpenVoiceOSMessage):
    """Message for `mycroft.skills.idle`."""
    message_type: str = "mycroft.skills.idle"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for skills idle event.")


class MycroftSkillsCheckActiveMessage(OpenVoiceOSMessage):
    """Message for `mycroft.skills.check_active` (request to check active skills)."""
    message_type: str = "mycroft.skills.check_active"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for check active request.")


class MycroftSkillsActiveData(BaseModel):
    """Data for `mycroft.skills.active` message."""
    skill_id: str = Field(..., description="The ID of the active skill.")
    # Allow other context if needed
    model_config = ConfigDict(extra='allow')


class MycroftSkillsActiveMessage(OpenVoiceOSMessage):
    """Message for `mycroft.skills.active`."""
    message_type: str = "mycroft.skills.active"
    data: MycroftSkillsActiveData


# --- Example Usage ---
