from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


# --- Vocabulary / Intent Registration ---

class RegisterVocabData(BaseModel):
    """Payload for registering a keyword or regex entity with Adapt."""
    entity_value: Optional[str] = Field(None, description="The natural-language keyword to register (e.g. 'weather').")
    entity_type: Optional[str] = Field(None, description="Tag/type name for this entity (e.g. 'WeatherKeyword').")
    alias_of: Optional[str] = Field(None, description="Another entity type this keyword is an alias of.")
    regex: Optional[str] = Field(None, description="Named-group regex to register as an entity (overrides entity_value/type).")
    lang: str = Field(..., description="BCP-47 language code for this vocabulary entry.")


class RegisterVocabMessage(OpenVoiceOSMessage):
    """Register a keyword or regex entity with the Adapt intent engine.

    **Legacy** — Adapt (keyword-based) is superseded by Padacioso / ML-based
    intent pipelines. Documented for reference; prefer registering intents via
    the newer pipeline plugin API.

    Emitted by `ovos-workshop` via `self.register_vocabulary()` during skill
    `initialize()`. The Adapt pipeline plugin receives this and adds the keyword
    or regex to its entity store for the given language. If `regex` is set all
    other fields are ignored and a named-group regex entity is registered instead
    of a keyword.
    """
    message_type: str = "register_vocab"
    data: RegisterVocabData


class RegisterIntentData(BaseModel):
    """Serialized Adapt IntentParser payload for registering a structured intent."""
    name: str = Field(..., description="Unique intent name (typically '{skill_id}:{IntentName}').")
    requires: List[Any] = Field(default_factory=list, description="List of (entity_type, attribute) tuples that must be present.")
    at_least_one: List[Any] = Field(default_factory=list, description="List of entity groups where at least one must match.")
    optional: List[Any] = Field(default_factory=list, description="List of (entity_type, attribute) tuples that are optional.")
    excludes: List[Any] = Field(default_factory=list, description="List of entity types that must NOT be present.")


class RegisterIntentMessage(OpenVoiceOSMessage):
    """Register a structured Adapt intent with the intent service.

    **Legacy** — Adapt (keyword-based) is superseded by Padacioso / ML-based
    intent pipelines. Documented for reference.

    Emitted by `ovos-workshop` via `@intent_handler` with an `IntentBuilder`
    during skill `initialize()`. The Adapt pipeline plugin deserializes the
    payload (via `open_intent_envelope`) and registers the intent parser in its
    engine for all configured languages. The `name` field doubles as the
    `match_type` returned in intent matches.
    """
    message_type: str = "register_intent"
    data: RegisterIntentData


# --- Intent / Skill Detach ---

class DetachIntentData(BaseModel):
    """Payload for removing a single intent from the Adapt engine."""
    intent_name: str = Field(..., description="Full intent name to remove (e.g. '{skill_id}:{IntentName}').")


class DetachIntentMessage(OpenVoiceOSMessage):
    """Remove a single named intent from the Adapt intent engine.

    Emitted by `ovos-workshop` when a skill removes a specific intent via
    `self.disable_intent()` or when the skill manager detaches individual
    intents during skill reload. Also handled by Padatious when its intents
    need to be removed.
    """
    message_type: str = "detach_intent"
    data: DetachIntentData


class DetachSkillData(BaseModel):
    """Payload for removing all intents registered by a specific skill."""
    skill_id: str = Field(..., description="ID of the skill whose intents should be removed.")


class DetachSkillMessage(OpenVoiceOSMessage):
    """Remove all intents and vocabulary for a skill from the Adapt engine.

    Emitted by the skill manager when a skill is unloaded, reloaded, or
    deactivated. The Adapt pipeline plugin drops all intent parsers and
    entity entries whose name starts with the given `skill_id`. Also handled
    by Padatious to remove all padatious intents for the skill.
    """
    message_type: str = "detach_skill"
    data: DetachSkillData


# --- Adapt Query / Introspection ---

class IntentServiceAdaptGetData(BaseModel):
    """Payload for querying the Adapt engine directly for a single utterance."""
    utterance: str = Field(..., description="Utterance to parse with Adapt.")
    lang: Optional[str] = Field(None, description="BCP-47 language code; defaults to system language.")


class IntentServiceAdaptGetMessage(OpenVoiceOSMessage):
    """Query the Adapt intent engine for the best match for a given utterance.

    Emitted by diagnostic tools or the intent service itself during debug
    sessions. The Adapt pipeline plugin runs its deterministic keyword-matching
    engine against the utterance and replies with `intent.service.adapt.reply`
    containing the matched intent data or `None` if no match was found.
    """
    message_type: str = "intent.service.adapt.get"
    data: IntentServiceAdaptGetData


class IntentServiceAdaptReplyData(BaseModel):
    """Adapt intent match result returned in response to an adapt.get query."""
    intent: Optional[Dict[str, Any]] = Field(None, description="Matched Adapt intent dict with 'intent_type', 'confidence', '__tags__', and extracted entities, or None if no match.")


class IntentServiceAdaptReplyMessage(OpenVoiceOSMessage):
    """Return the Adapt intent match result for a queried utterance.

    Emitted by the Adapt pipeline plugin in response to
    `intent.service.adapt.get`. `intent` is a dict containing `intent_type`,
    `confidence`, `__tags__`, and any extracted entity values, or `None` if
    Adapt did not match the utterance.
    """
    message_type: str = "intent.service.adapt.reply"
    data: IntentServiceAdaptReplyData


class IntentServiceAdaptManifestGetMessage(OpenVoiceOSMessage):
    """Request the list of all intents currently registered with Adapt.

    Emitted by diagnostic tools or the intent service to enumerate registered
    Adapt intent parsers. The plugin replies with
    `intent.service.adapt.manifest` containing the list of parser dicts.
    """
    message_type: str = "intent.service.adapt.manifest.get"
    data: Dict[str, Any] = Field(default_factory=dict)


class IntentServiceAdaptManifestData(BaseModel):
    """List of all Adapt intent parsers currently registered in the engine."""
    intents: List[Dict[str, Any]] = Field(default_factory=list, description="List of registered Adapt IntentParser dicts.")


class IntentServiceAdaptManifestMessage(OpenVoiceOSMessage):
    """Return the list of all registered Adapt intent parsers.

    Emitted by the Adapt pipeline plugin in response to
    `intent.service.adapt.manifest.get`. Each entry in `intents` is an
    IntentParser dict including `name`, `requires`, `optional`, and `excludes`.
    """
    message_type: str = "intent.service.adapt.manifest"
    data: IntentServiceAdaptManifestData


class IntentServiceAdaptVocabManifestGetMessage(OpenVoiceOSMessage):
    """Request the list of all vocabulary registered with Adapt.

    Emitted by diagnostic tools to inspect which keywords and regex patterns
    have been registered across all loaded skills. Replies with
    `intent.service.adapt.vocab.manifest`.
    """
    message_type: str = "intent.service.adapt.vocab.manifest.get"
    data: Dict[str, Any] = Field(default_factory=dict)


class IntentServiceAdaptVocabManifestData(BaseModel):
    """List of all vocabulary entries registered with the Adapt engine."""
    vocab: List[Dict[str, Any]] = Field(default_factory=list, description="List of registered vocabulary entry dicts (entity_value, entity_type, alias_of, regex, lang).")


class IntentServiceAdaptVocabManifestMessage(OpenVoiceOSMessage):
    """Return all vocabulary currently registered with the Adapt engine.

    Emitted by the Adapt pipeline plugin in response to
    `intent.service.adapt.vocab.manifest.get`. Each entry mirrors the payload
    of the original `register_vocab` call that added it.
    """
    message_type: str = "intent.service.adapt.vocab.manifest"
    data: IntentServiceAdaptVocabManifestData
