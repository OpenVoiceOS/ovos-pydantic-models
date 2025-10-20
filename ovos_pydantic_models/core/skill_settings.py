from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, List, Optional, Union
from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


class SkillSettingsChangeData(BaseModel):
    """Data for `skill.settings.change` message."""
    skill_id: str = Field(..., description="The ID of the skill whose settings are changing.")
    # The actual settings data is usually nested here, allowing arbitrary content
    settings: Dict[str, Any] = Field(default_factory=dict, description="The new settings data for the skill.")
    model_config = ConfigDict(extra='allow')

class SkillSettingsChangeMessage(OpenVoiceOSMessage):
    """Message for `skill.settings.change`."""
    message_type: str = "skill.settings.change"
    data: SkillSettingsChangeData

class SkillSettingsUpdatedData(BaseModel):
    """Data for `skill.settings.updated` message."""
    skill_id: str = Field(..., description="The ID of the skill whose settings have been updated.")
    # The actual settings data is usually nested here, allowing arbitrary content
    settings: Dict[str, Any] = Field(default_factory=dict, description="The updated settings data for the skill.")
    model_config = ConfigDict(extra='allow')

class SkillSettingsUpdatedMessage(OpenVoiceOSMessage):
    """Message for `skill.settings.updated`."""
    message_type: str = "skill.settings.updated"
    data: SkillSettingsUpdatedData

class OvosSkillsSettingsChangedData(BaseModel):
    """Data for `ovos.skills.settings_changed` message."""
    skill_id: str = Field(..., description="The ID of the skill whose settings.json file has changed.")


class OvosSkillsSettingsChangedMessage(OpenVoiceOSMessage):
    """Message for `ovos.skills.settings_changed`."""
    message_type: str = "ovos.skills.settings_changed"
    data: OvosSkillsSettingsChangedData


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Demonstrating Skill Manager Message Models ---")

    # Create a dummy session and context for demonstration
    dummy_session = Session(session_id="test-skill-manager-session-101", lang="en-us")
    dummy_context = MessageContext(source="skill_manager", session=dummy_session)

    # Example: Skill settings changed
    settings_changed_data = OvosSkillsSettingsChangedData(skill_id="my-test-skill")
    settings_changed_message = OvosSkillsSettingsChangedMessage(data=settings_changed_data, context=dummy_context)
    print(f"\nSettings Changed Message:\n{settings_changed_message.model_dump_json(indent=2)}")

 # Example: Skill Settings Change
    settings_change_data = SkillSettingsChangeData(
        skill_id="skill-my-settings.mycroft",
        settings={"volume": 0.7, "mute": False}
    )
    settings_change_message = SkillSettingsChangeMessage(data=settings_change_data, context=dummy_context)
    print(f"\nSkill Settings Change Message:\n{settings_change_message.model_dump_json(indent=2)}")

    # Example: Skill Settings Updated
    settings_updated_data = SkillSettingsUpdatedData(
        skill_id="skill-my-settings.mycroft",
        settings={"volume": 0.7, "mute": False, "last_updated": "2023-10-27"}
    )
    settings_updated_message = SkillSettingsUpdatedMessage(data=settings_updated_data, context=dummy_context)
    print(f"\nSkill Settings Updated Message:\n{settings_updated_message.model_dump_json(indent=2)}")
