from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


# --- Intent / Entity Registration ---

class PadatiousRegisterIntentData(BaseModel):
    """Payload for registering a Padatious intent with its training utterances.

    The registering skill is identified by `context.skill_id`, not by a payload
    field.
    """
    name: str = Field(..., description="Fully-qualified intent name (e.g. '{skill_id}:{IntentName}').")
    file_name: Optional[str] = Field(None, description="Path to the .intent file containing training utterances.")
    samples: Optional[List[str]] = Field(None, description="Inline training utterances (used if file_name is absent or unreadable).")
    lang: str = Field(..., description="BCP-47 language code for this intent.")
    blacklisted_words: Optional[List[str]] = Field(None, description="Words that, if present, disqualify a match.")
    slot_blacklist: Optional[Dict[str, List[str]]] = Field(None, description="Per-slot values that disqualify a match.")
    requires_context: Optional[List[Any]] = Field(None, description="Context gates that must be satisfied for this intent to match.")
    excludes_context: Optional[List[Any]] = Field(None, description="Context gates that, if satisfied, block this intent.")


class PadatiousRegisterIntentMessage(OpenVoiceOSMessage):
    """Register an ML-based Padatious intent with its training utterances.

    **Legacy** — Padatious is superseded by Padacioso, which uses the same
    message protocol. Documented for reference; the message type is the same
    for both engines.

    Emitted by `ovos-workshop` via `@intent_file_handler` or
    `self.register_intent_file()` during skill `initialize()`. The Padatious
    (or Padacioso) pipeline plugin receives this, adds the training samples to
    its container for the given language, and schedules retraining via
    `mycroft.skills.train`. After training `mycroft.skills.trained` is emitted.

    Either `file_name` (path to a `.intent` file) or `samples` (inline list)
    must be provided.
    """
    message_type: str = "padatious:register_intent"
    data: PadatiousRegisterIntentData


class PadatiousRegisterEntityData(BaseModel):
    """Payload for registering a Padatious named entity with its training values.

    The registering skill is identified by `context.skill_id`, not by a payload
    field.
    """
    name: str = Field(..., description="Entity name (e.g. '{skill_id}:{EntityName}').")
    file_name: Optional[str] = Field(None, description="Path to the .entity file containing entity values.")
    samples: Optional[List[str]] = Field(None, description="Inline entity values (used if file_name is absent or unreadable).")
    lang: str = Field(..., description="BCP-47 language code for this entity.")
    blacklist: Optional[List[str]] = Field(None, description="Entity values that must never be matched.")


class PadatiousRegisterEntityMessage(OpenVoiceOSMessage):
    """Register a named entity type with its possible values for Padatious.

    **Legacy** — Padatious is superseded by Padacioso, which uses the same
    message protocol. Documented for reference.

    Emitted by `ovos-workshop` via `self.register_entity_file()` during skill
    `initialize()`. The pipeline plugin loads the entity values from `file_name`
    or `samples` and makes them available for slot-filling in intents of the
    same skill. Entity values appear as keys in the matched intent's data dict.
    """
    message_type: str = "padatious:register_entity"
    data: PadatiousRegisterEntityData


# --- Training lifecycle ---

class MycroftSkillsTrainMessage(OpenVoiceOSMessage):
    """Trigger Padatious (or Padacioso) to (re)train its intent models.

    Emitted by the skill manager (`mycroft.skills.trained` not yet received)
    after new intents or entities have been registered. The Padatious pipeline
    plugin trains its ML models for all languages. When training completes it
    emits `mycroft.skills.trained`.
    """
    message_type: str = "mycroft.skills.train"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftSkillsTrainedMessage(OpenVoiceOSMessage):
    """Signal that Padatious intent model training has completed.

    Emitted by the Padatious (or Padacioso) pipeline plugin after a training
    pass finishes. The skill manager and other components waiting for the
    pipeline to be ready use this to proceed. Components that emitted
    `mycroft.skills.train` unblock on receiving this message.
    """
    message_type: str = "mycroft.skills.trained"
    data: Dict[str, Any] = Field(default_factory=dict)


# --- Padatious Query / Introspection ---

class IntentServicePadatiousGetData(BaseModel):
    """Payload for querying the Padatious engine directly for a single utterance."""
    utterance: str = Field(..., description="Utterance to parse with Padatious.")
    lang: Optional[str] = Field(None, description="BCP-47 language code; defaults to system language.")


class IntentServicePadatiousGetMessage(OpenVoiceOSMessage):
    """Query the Padatious intent engine for the best match for a given utterance.

    Emitted by diagnostic tools or the intent service itself during debug
    sessions. The Padatious pipeline plugin runs its ML model against the
    utterance and replies with `intent.service.padatious.reply` containing
    the matched intent data (name, confidence, matched entities) or `None`.
    """
    message_type: str = "intent.service.padatious.get"
    data: IntentServicePadatiousGetData


class IntentServicePadatiousReplyData(BaseModel):
    """Padatious intent match result returned in response to a padatious.get query."""
    intent: Optional[Dict[str, Any]] = Field(None, description="Matched Padatious intent dict with 'name', 'conf', and extracted entity 'matches', or None if no match.")


class IntentServicePadatiousReplyMessage(OpenVoiceOSMessage):
    """Return the Padatious intent match result for a queried utterance.

    Emitted by the Padatious pipeline plugin in response to
    `intent.service.padatious.get`. `intent` is a dict with `name`
    (e.g. `'{skill_id}:{IntentName}'`), `conf` (0.0–1.0), and `matches`
    (dict of entity name → extracted value), or `None` if no match.
    """
    message_type: str = "intent.service.padatious.reply"
    data: IntentServicePadatiousReplyData


class IntentServicePadatiousManifestGetMessage(OpenVoiceOSMessage):
    """Request the list of all intents currently registered with Padatious.

    Emitted by diagnostic tools or the intent service. The plugin replies with
    `intent.service.padatious.manifest` listing all registered intent names.
    """
    message_type: str = "intent.service.padatious.manifest.get"
    data: Dict[str, Any] = Field(default_factory=dict)


class IntentServicePadatiousManifestData(BaseModel):
    """List of all intent names currently registered with Padatious."""
    intents: List[str] = Field(default_factory=list, description="Registered Padatious intent names (e.g. '{skill_id}:{IntentName}').")


class IntentServicePadatiousManifestMessage(OpenVoiceOSMessage):
    """Return the list of all registered Padatious intent names.

    Emitted by the Padatious pipeline plugin in response to
    `intent.service.padatious.manifest.get`.
    """
    message_type: str = "intent.service.padatious.manifest"
    data: IntentServicePadatiousManifestData


class IntentServicePadatiousEntitiesManifestGetMessage(OpenVoiceOSMessage):
    """Request the list of all entities currently registered with Padatious.

    Emitted by diagnostic tools to inspect which entity types are available
    for slot-filling in padatious intents. Replies with
    `intent.service.padatious.entities.manifest`.
    """
    message_type: str = "intent.service.padatious.entities.manifest.get"
    data: Dict[str, Any] = Field(default_factory=dict)


class IntentServicePadatiousEntitiesManifestData(BaseModel):
    """List of all entity registration payloads currently held by Padatious."""
    entities: List[Dict[str, Any]] = Field(default_factory=list, description="List of registered entity dicts (name, lang, samples, etc.).")


class IntentServicePadatiousEntitiesManifestMessage(OpenVoiceOSMessage):
    """Return all entities currently registered with Padatious.

    Emitted by the Padatious pipeline plugin in response to
    `intent.service.padatious.entities.manifest.get`. Each entry mirrors the
    payload of the original `padatious:register_entity` call.
    """
    message_type: str = "intent.service.padatious.entities.manifest"
    data: IntentServicePadatiousEntitiesManifestData
