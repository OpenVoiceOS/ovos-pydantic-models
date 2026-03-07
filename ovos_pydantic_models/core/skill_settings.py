from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, List, Optional, Union
from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


class SkillSettingsChangeData(BaseModel):
    """Payload for requesting a change to a skill's settings."""
    skill_id: str = Field(..., description="The ID of the skill whose settings are changing.")
    settings: Dict[str, Any] = Field(default_factory=dict, description="The new settings data for the skill.")
    model_config = ConfigDict(extra='allow')


class SkillSettingsChangeMessage(OpenVoiceOSMessage):
    """Request a change to a skill's settings.

    Emitted by GUI settings panels or admin tools when the user modifies
    a skill's configuration values. `ovos-core` applies the change and
    persists it to the skill's `settings.json`, then broadcasts
    `skill.settings.updated` to confirm the change.
    """
    message_type: str = "skill.settings.change"
    data: SkillSettingsChangeData


class SkillSettingsUpdatedData(BaseModel):
    """Confirmation payload after a skill's settings have been saved."""
    skill_id: str = Field(..., description="The ID of the skill whose settings have been updated.")
    settings: Dict[str, Any] = Field(default_factory=dict, description="The updated settings data for the skill.")
    model_config = ConfigDict(extra='allow')


class SkillSettingsUpdatedMessage(OpenVoiceOSMessage):
    """Confirm that a skill's settings have been saved successfully.

    Emitted by `ovos-core` after processing a `skill.settings.change` request
    and persisting the new values to `settings.json`. The skill's
    `settings_change_callback` is also invoked automatically.
    """
    message_type: str = "skill.settings.updated"
    data: SkillSettingsUpdatedData


class OvosSkillsSettingsChangedData(BaseModel):
    """Payload identifying the skill whose settings file was updated on disk."""
    skill_id: str = Field(..., description="The ID of the skill whose settings.json file has changed.")


class OvosSkillsSettingsChangedMessage(OpenVoiceOSMessage):
    """Signal that a skill's settings file has been updated (e.g. by backend sync).

    Emitted by the settings watchdog or backend sync service when a skill's
    `settings.json` is written to disk by an external process (e.g. the OVOS
    backend). The skill automatically reloads its settings and calls its
    `settings_change_callback`. Distinct from `mycroft.skills.settings.changed`
    which is emitted by the skill manager on in-process changes.
    """
    message_type: str = "ovos.skills.settings_changed"
    data: OvosSkillsSettingsChangedData
