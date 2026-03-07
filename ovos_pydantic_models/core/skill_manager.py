from typing import Dict, Any, Optional

from pydantic import BaseModel, Field, ConfigDict

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


# --- Skill Manager Message Models ---


class MycroftReadyMessage(OpenVoiceOSMessage):
    """Signal that all OVOS core services have finished starting up.

    Broadcast by `ovos-core` once every required service (skills, audio,
    listener, etc.) has reported ready. Skills and PHAL plugins subscribe to
    this event to defer initialization work until the full system is available.
    """
    message_type: str = "mycroft.ready"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftSkillsIsReadyMessage(OpenVoiceOSMessage):
    """Query whether the skills service has finished loading.

    Emitted by components that need to wait for skills to be available
    before proceeding (e.g. startup scripts, test harnesses). `ovos-core`
    replies with `mycroft.skills.is_ready.response`.
    """
    message_type: str = "mycroft.skills.is_ready"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftSkillsIsReadyReplyData(BaseModel):
    """Readiness status of the skills service."""
    status: bool = Field(..., description="True if the skills service is ready, False otherwise.")


class MycroftSkillsIsReadyResponseMessage(OpenVoiceOSMessage):
    """Return whether the skills service has finished loading.

    Emitted by `ovos-core` in response to `mycroft.skills.is_ready`.
    Once `status` is True, all configured skills have been loaded and trained.
    """
    message_type: str = "mycroft.skills.is_ready.response"
    data: MycroftSkillsIsReadyReplyData


class MycroftSkillsReadyMessage(OpenVoiceOSMessage):
    """Signal that all skills have been loaded and trained successfully.

    Broadcast by the skill manager once every skill's `initialize()` has
    completed and intent training is done. This is a one-time event; use
    `mycroft.skills.is_ready` for a query-response version.
    """
    message_type: str = "mycroft.skills.ready"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftSkillsActivateData(BaseModel):
    """Request payload for activating a specific skill."""
    skill_id: str = Field(..., description="The ID of the skill that is activating itself.")
    model_config = ConfigDict(extra='allow')


class MycroftSkillsActivateMessage(OpenVoiceOSMessage):
    """Tell the skill manager to mark a skill as active.

    Emitted by a skill via `self.make_active()`. The skill manager adds it
    to the converse stack so its `converse()` method receives first refusal
    on subsequent utterances.
    """
    message_type: str = "mycroft.skills.activate"
    data: MycroftSkillsActivateData


class MycroftSkillsDeactivateData(BaseModel):
    """Request payload for deactivating a specific skill."""
    skill_id: str = Field(..., description="The ID of the skill that is deactivating itself.")
    model_config = ConfigDict(extra='allow')


class MycroftSkillsDeactivateMessage(OpenVoiceOSMessage):
    """Tell the skill manager to remove a skill from the active converse stack.

    Emitted by a skill via `self.cancel_active()`. The skill will no longer
    receive converse callbacks until it activates itself again.
    """
    message_type: str = "mycroft.skills.deactivate"
    data: MycroftSkillsDeactivateData


class SkillManagerListData(BaseModel, extra='allow'):
    """Request payload for listing all loaded skills (empty by convention)."""


class SkillManagerListMessage(OpenVoiceOSMessage):
    """Request a list of all skills currently loaded in the skill manager.

    Emitted by GUI skill managers, admin tools, or debug utilities. The
    skill manager replies with `mycroft.skills.list`.
    """
    message_type: str = "skillmanager.list"
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MycroftSkillsListData(BaseModel, extra='allow'):
    """Skill inventory returned by the skill manager.

    Keys are skill IDs; values are dicts with `"active"` (bool) and `"id"` (str).
    Example: `{"timer.openvoiceos": {"active": True, "id": "timer.openvoiceos"}}`.
    Extra fields are allowed for forward compatibility.
    """


class MycroftSkillsListMessage(OpenVoiceOSMessage):
    """Return the list of all currently loaded skills.

    Emitted by `ovos-core` in response to `skillmanager.list`. Each skill
    entry contains at minimum `active` and `id` fields.
    """
    message_type: str = "mycroft.skills.list"
    data: MycroftSkillsListData


class SkillManagerDeactivateData(BaseModel):
    """Request payload for disabling a specific skill."""
    skill: str = Field(..., description="The ID of the skill to deactivate.")


class SkillManagerDeactivateMessage(OpenVoiceOSMessage):
    """Tell the skill manager to disable a specific skill.

    Emitted by admin tools, skill manager GUIs, or the blacklist mechanism.
    The skill's `shutdown()` is called and it is removed from the intent pipeline.
    The skill manager replies with `skillmanager.deactivate.response`.
    """
    message_type: str = "skillmanager.deactivate"
    data: SkillManagerDeactivateData


class SkillManagerDeactivateResponseMessage(OpenVoiceOSMessage):
    """Confirm or report failure for a skill deactivation request.

    Emitted by `ovos-core` in response to `skillmanager.deactivate`.
    An empty payload means success; populated data indicates an error.
    """
    message_type: str = "skillmanager.deactivate.response"
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SkillManagerKeepData(BaseModel):
    """Request payload for keeping one skill active while disabling all others."""
    skill: str = Field(..., description="The ID of the skill to keep active; all others will be deactivated.")


class SkillManagerKeepMessage(OpenVoiceOSMessage):
    """Deactivate all skills except the named one.

    Used for debugging and kiosk-mode deployments where only one skill
    should be operational. The skill manager shuts down all other loaded
    skills. Replies with `skillmanager.keep.response`.
    """
    message_type: str = "skillmanager.keep"
    data: SkillManagerKeepData


class SkillManagerKeepResponseMessage(OpenVoiceOSMessage):
    """Confirm or report failure for a skillmanager.keep request.

    Emitted by `ovos-core` in response to `skillmanager.keep`.
    An empty payload means success; populated data indicates an error.
    """
    message_type: str = "skillmanager.keep.response"
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SkillManagerActivateData(BaseModel):
    """Request payload for re-enabling a specific skill or all skills."""
    skill: str = Field(..., description="The ID of the skill to activate ('all' for all deactivated skills).")


class SkillManagerActivateMessage(OpenVoiceOSMessage):
    """Re-enable a previously deactivated skill (or all skills).

    Emitted by admin tools or skill manager GUIs. Pass `skill='all'` to
    re-enable every disabled skill simultaneously. The skill manager loads
    and initializes the skill. Replies with `skillmanager.activate.response`.
    """
    message_type: str = "skillmanager.activate"
    data: SkillManagerActivateData


class SkillManagerActivateResponseMessage(OpenVoiceOSMessage):
    """Confirm or report failure for a skill activation request.

    Emitted by `ovos-core` in response to `skillmanager.activate`.
    An empty payload means success; populated data indicates an error.
    """
    message_type: str = "skillmanager.activate.response"
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MycroftSkillsErrorData(BaseModel):
    """Payload describing a skill service startup error."""
    internet_loaded: bool = Field(..., description="True if internet-dependent skills were loaded.")
    network_loaded: bool = Field(..., description="True if network-dependent skills were loaded.")
    error: Optional[str] = Field(None, description="Optional error message.")


class MycroftSkillsErrorMessage(OpenVoiceOSMessage):
    """Signal that the skills service encountered an error during startup.

    Emitted by `ovos-core` when skill loading fails — for example when
    network-dependent skills could not be loaded due to no internet access.
    """
    message_type: str = "mycroft.skills.error"
    data: MycroftSkillsErrorData


class MycroftSkillsInitializedMessage(OpenVoiceOSMessage):
    """Signal that the skills service has finished its initialization phase.

    Emitted by `ovos-core` once the skill loader completes its first pass.
    Some skills may still be loading asynchronously; use `mycroft.skills.ready`
    for the fully-trained signal.
    """
    message_type: str = "mycroft.skills.initialized"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftSkillsTrainMessage(OpenVoiceOSMessage):
    """Request all pipeline plugins to re-train from current intent files.

    Emitted after skills are added or updated. Forces Padatious, Adapt,
    and other trainable pipeline plugins to rebuild their models. The skill
    manager replies with `mycroft.skills.trained`.
    """
    message_type: str = "mycroft.skills.train"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftSkillsTrainedData(BaseModel):
    """Result of an intent training pass."""
    error: Optional[str] = Field(None, description="Error message if training failed.")


class MycroftSkillsTrainedMessage(OpenVoiceOSMessage):
    """Signal that intent training has completed.

    Emitted by `ovos-core` after a `mycroft.skills.train` request. If
    `error` is set, training failed and the pipeline may be stale.
    """
    message_type: str = "mycroft.skills.trained"
    data: MycroftSkillsTrainedData


class MycroftSkillEnableIntentData(BaseModel):
    """Payload for re-enabling a previously disabled intent."""
    intent_name: str = Field(..., description="Intent name to enable.")


class MycroftSkillEnableIntentMessage(OpenVoiceOSMessage):
    """Re-enable a previously disabled intent in the pipeline.

    Emitted by skills via `self.enable_intent()`. The intent service
    re-registers the named intent so it can match utterances again.
    """
    message_type: str = "mycroft.skill.enable_intent"
    data: MycroftSkillEnableIntentData


class MycroftSkillDisableIntentData(BaseModel):
    """Payload for temporarily disabling an intent."""
    intent_name: str = Field(..., description="Intent name to disable.")


class MycroftSkillDisableIntentMessage(OpenVoiceOSMessage):
    """Temporarily disable an intent in the pipeline.

    Emitted by skills via `self.disable_intent()`. The named intent is
    removed from the active pipeline until re-enabled, allowing skills to
    implement mode-dependent intent sets.
    """
    message_type: str = "mycroft.skill.disable_intent"
    data: MycroftSkillDisableIntentData


class MycroftSkillSetCrossContextData(BaseModel):
    """Payload for setting a context item visible across all skills."""
    context: str = Field(..., description="Context key to set.")
    word: str = Field(..., description="Context value.")
    origin: str = Field(..., description="Skill ID that set the context.")


class MycroftSkillSetCrossContextMessage(OpenVoiceOSMessage):
    """Set a context item that is shared across all skills.

    Emitted by skills via `self.set_cross_skill_context()`. Unlike regular
    Adapt context which is local, cross-context is visible to all skills
    in the pipeline for the duration of the conversation.
    """
    message_type: str = "mycroft.skill.set_cross_context"
    data: MycroftSkillSetCrossContextData


class MycroftSkillRemoveCrossContextData(BaseModel):
    """Payload for removing a shared cross-skill context item."""
    context: str = Field(..., description="Context key to remove.")


class MycroftSkillRemoveCrossContextMessage(OpenVoiceOSMessage):
    """Remove a previously set cross-skill context item.

    Emitted by skills via `self.remove_cross_skill_context()`. The named
    context key is deleted from the shared context store immediately.
    """
    message_type: str = "mycroft.skill.remove_cross_context"
    data: MycroftSkillRemoveCrossContextData


class MycroftSkillHandlerStartData(BaseModel):
    """Payload emitted when a skill's intent handler begins executing."""
    name: str = Field(..., description="Name of the intent handler starting.")


class MycroftSkillHandlerStartMessage(OpenVoiceOSMessage):
    """Signal that a skill's intent handler has begun executing.

    Emitted by `ovos-workshop` at the start of every `@intent_handler`
    decorated function. Useful for performance monitoring, timeout watchdogs,
    and the `@killable_intent` decorator.
    """
    message_type: str = "mycroft.skill.handler.start"
    data: MycroftSkillHandlerStartData


class MycroftSkillHandlerCompleteData(BaseModel):
    """Payload emitted when a skill's intent handler finishes executing."""
    name: str = Field(..., description="Name of the intent handler that completed.")


class MycroftSkillHandlerCompleteMessage(OpenVoiceOSMessage):
    """Signal that a skill's intent handler has finished executing.

    Emitted by `ovos-workshop` at the end of every `@intent_handler`
    decorated function — whether it completed normally or raised an exception.
    Counterpart of `mycroft.skill.handler.start`.
    """
    message_type: str = "mycroft.skill.handler.complete"
    data: MycroftSkillHandlerCompleteData


class MycroftSkillsShutdownData(BaseModel):
    """Payload identifying the skill that was shut down."""
    id: str = Field(..., description="Skill plugin ID.")
    folder: str = Field(..., description="Skill folder path.")


class MycroftSkillsShutdownMessage(OpenVoiceOSMessage):
    """Signal that a skill has been shut down and unloaded.

    Emitted by the skill loader after a skill's `shutdown()` completes.
    The skill's intents have been detached and it is no longer active.
    """
    message_type: str = "mycroft.skills.shutdown"
    data: MycroftSkillsShutdownData


class MycroftSkillsLoadingFailureData(BaseModel):
    """Payload identifying the skill that failed to load."""
    id: str = Field(..., description="Skill plugin ID.")
    folder: str = Field(..., description="Skill folder path.")


class MycroftSkillsLoadingFailureMessage(OpenVoiceOSMessage):
    """Signal that a skill failed to load during startup.

    Emitted by the skill loader when a skill's `initialize()` raises an
    unhandled exception. The skill is not retried until the next restart.
    """
    message_type: str = "mycroft.skills.loading_failure"
    data: MycroftSkillsLoadingFailureData


class MycroftSkillsSettingsChangedData(BaseModel):
    """Payload identifying the skill whose settings file changed."""
    skill_id: str = Field(..., description="Skill ID whose settings changed.")


class MycroftSkillsSettingsChangedMessage(OpenVoiceOSMessage):
    """Signal that a skill's `settings.json` file has been updated on disk.

    Emitted by the settings watcher. The skill reloads its settings dict
    automatically; this broadcast allows other components to react.
    Distinct from `ovos.skills.settings_changed` which is emitted by the
    backend sync service.
    """
    message_type: str = "mycroft.skills.settings.changed"
    data: MycroftSkillsSettingsChangedData


class DetachSkillData(BaseModel):
    """Payload identifying the skill to unload from the intent service."""
    skill_id: str = Field(..., description="ID of the skill to detach/unload.")


class DetachSkillMessage(OpenVoiceOSMessage):
    """Tell the intent service to unload all data for a specific skill.

    Emitted by the skill manager when a skill is being removed. The intent
    service removes all intents, entities, and converse hooks associated
    with the skill. Usually followed by `detach_intent`.
    """
    message_type: str = "detach_skill"
    data: DetachSkillData


class DetachIntentData(BaseModel):
    """Payload identifying the skill whose intents should be removed."""
    skill_id: str = Field(..., description="Skill ID whose intents to remove.")


class DetachIntentMessage(OpenVoiceOSMessage):
    """Remove all registered intents for a specific skill from the pipeline.

    Emitted by the skill manager during skill reload or shutdown. The
    pipeline plugins (Adapt, Padatious, etc.) remove all intent patterns
    registered by the named skill.
    """
    message_type: str = "detach_intent"
    data: DetachIntentData
