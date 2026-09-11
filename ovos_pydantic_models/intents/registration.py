"""OVOS-INTENT-4 registration wire.

The six broadcasts a skill uses to publish and retract its intents and
entities (§§5-8), the two enable/disable controls (§8.5), and the
orchestrator's introspection pull-queries (§10).

Every registration is keyed by the ``session_id`` the consumer reads from
``context.session.session_id`` (§11.1), never from the payload. On the query
topics ``session_id`` *is* a payload field, because there it is a filter
rather than a scope assertion.

Two divergences between the specification and ovos-core 3.2.0a1 are modelled
as the specification defines them. ``ovos.entity.register`` and
``ovos.entity.deregister`` (§7, §8.3) have no subscriber — the manifest binds
only the intent topics (ovos_core/intent_services/manifest.py:36-43). And no
producer emits any of these topics yet; ovos-workshop still registers
in-process (ovos_workshop/intents.py:162, 189, 357, 375).
"""
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


class IntentMethod(str, Enum):
    """How an intent was defined — the ``method`` axis of the registration key (INTENT-3 §2)."""
    KEYWORD = "keyword"     # keyword constraints over vocabularies (INTENT-4 §5)
    TEMPLATE = "template"   # example sentence templates (INTENT-4 §6)


class VocabularyDescriptor(BaseModel):
    """One vocabulary of a keyword intent (INTENT-4 §5.1).

    ``name`` is the key the captured phrase appears under in the match result;
    ``samples`` are slot-free OVOS-INTENT-1 templates.
    """
    name: str = Field(..., description="Vocabulary name — the key the captured phrase appears under in Match.slots.")
    samples: List[str] = Field(..., min_length=1, description="Slot-free OVOS-INTENT-1 templates. At least one entry.")
    model_config = ConfigDict(extra='allow')


class OvosIntentRegisterKeywordData(BaseModel):
    """Keyword intent definition — the constraints and their vocabularies in one payload (INTENT-4 §5.2).

    An absent list-valued role is equivalent to an empty list; a consumer must
    not reject a registration merely because a role was omitted.
    """
    skill_id: str = Field(..., description="Skill that owns the intent.")
    intent_name: str = Field(..., description="Intent name, unique within the skill. Must not be a name reserved by PIPELINE-1 §7.3.")
    lang: str = Field(..., description="BCP-47 language tag the definition is written in.")
    required: List[VocabularyDescriptor] = Field(default_factory=list, description="Every entry must occur in the utterance.")
    optional: List[VocabularyDescriptor] = Field(default_factory=list, description="Captured when present; absence does not prevent a match.")
    one_of: List[List[VocabularyDescriptor]] = Field(default_factory=list, description="Groups; at least one member of each group must occur.")
    excluded: List[VocabularyDescriptor] = Field(default_factory=list, description="If any occurs the intent must not match.")
    model_config = ConfigDict(extra='allow')


class OvosIntentRegisterKeywordMessage(OpenVoiceOSMessage):
    """Register a keyword intent — OVOS-INTENT-4 §5.

    Broadcast by a skill; every pipeline plugin that can serve keyword intents
    indexes it independently. Re-registering the same
    ``(session_id, skill_id, intent_name, lang, keyword)`` quintuple replaces
    the previous definition and preserves its enabled state (§8.1).
    """
    message_type: str = "ovos.intent.register.keyword"
    data: OvosIntentRegisterKeywordData


class OvosIntentRegisterTemplateData(BaseModel):
    """Template intent definition — example sentences with named slots (INTENT-4 §6.1)."""
    skill_id: str = Field(..., description="Skill that owns the intent.")
    intent_name: str = Field(..., description="Intent name, unique within the skill. Must not be a name reserved by PIPELINE-1 §7.3.")
    lang: str = Field(..., description="BCP-47 language tag the templates are written in.")
    samples: List[str] = Field(..., min_length=1, description="OVOS-INTENT-1 templates with named slots. The one list a producer must supply.")
    blacklist: List[str] = Field(default_factory=list, description="Slot-free phrases whose occurrence suppresses the match.")
    required_slots: List[str] = Field(default_factory=list, description="Slot names the engine must extract for the match to be valid.")
    model_config = ConfigDict(extra='allow')


class OvosIntentRegisterTemplateMessage(OpenVoiceOSMessage):
    """Register a template intent — OVOS-INTENT-4 §6.

    Broadcast by a skill. Templates may declare different slot sets; the engine
    extracts only the slots of the template that best matched.
    """
    message_type: str = "ovos.intent.register.template"
    data: OvosIntentRegisterTemplateData


class OvosEntityRegisterData(BaseModel):
    """Entity value-set hint for a template-intent slot (INTENT-4 §7.1)."""
    skill_id: str = Field(..., description="Skill that owns the entity.")
    entity_name: str = Field(..., description="Entity name, unique within the skill. By convention the slot name a template references.")
    lang: str = Field(..., description="BCP-47 language tag of the values.")
    samples: List[str] = Field(..., min_length=1, description="Slot-free value-set entries.")
    model_config = ConfigDict(extra='allow')


class OvosEntityRegisterMessage(OpenVoiceOSMessage):
    """Register an entity value-set hint — OVOS-INTENT-4 §7.

    Broadcast by a skill. An entity is never a precondition for an intent that
    references the slot name: a slot with no entity still fills normally.
    """
    message_type: str = "ovos.entity.register"
    data: OvosEntityRegisterData


class OvosIntentDeregisterData(BaseModel):
    """Intent identity for deregistration, enable, and disable (INTENT-4 §8.2, §8.5).

    An omitted ``lang`` targets every language registered for the
    ``(skill_id, intent_name)`` pair. All methods under the triple are affected;
    there is no per-method operation.
    """
    skill_id: str = Field(..., description="Skill that owns the intent — the target of the operation, not necessarily the sender.")
    intent_name: str = Field(..., description="Intent to operate on.")
    lang: Optional[str] = Field(None, description="BCP-47 language tag. Omitted means every registered language.")
    model_config = ConfigDict(extra='allow')


class OvosIntentDeregisterMessage(OpenVoiceOSMessage):
    """Remove one intent — OVOS-INTENT-4 §8.2.

    Broadcast; every holder of a matching registration drops it. Deregistering
    something not registered is a no-op, which makes skill shutdown idempotent.
    """
    message_type: str = "ovos.intent.deregister"
    data: OvosIntentDeregisterData


class OvosIntentEnableMessage(OpenVoiceOSMessage):
    """Re-arm a disabled intent — OVOS-INTENT-4 §8.5.

    Shares the §8.2 payload. ``skill_id`` names the target, so an admin UI or
    conflict resolver may enable another skill's intent; the affected session is
    the one declared on the Message context, never a payload field.
    """
    message_type: str = "ovos.intent.enable"
    data: OvosIntentDeregisterData


class OvosIntentDisableMessage(OpenVoiceOSMessage):
    """Suppress an intent without removing its definition — OVOS-INTENT-4 §8.5.

    Shares the §8.2 payload. The orchestrator keeps the definition in the
    manifest and marks it disabled; plugins exclude it from match candidacy
    until it is enabled again.
    """
    message_type: str = "ovos.intent.disable"
    data: OvosIntentDeregisterData


class OvosEntityDeregisterData(BaseModel):
    """Entity identity for deregistration (INTENT-4 §8.3)."""
    skill_id: str = Field(..., description="Skill that owns the entity.")
    entity_name: str = Field(..., description="Entity to remove.")
    lang: Optional[str] = Field(None, description="BCP-47 language tag. Omitted means every registered language.")
    model_config = ConfigDict(extra='allow')


class OvosEntityDeregisterMessage(OpenVoiceOSMessage):
    """Remove one entity — OVOS-INTENT-4 §8.3."""
    message_type: str = "ovos.entity.deregister"
    data: OvosEntityDeregisterData


class OvosSkillDeregisterData(BaseModel):
    """Skill identity for a wholesale retraction (INTENT-4 §8.4)."""
    skill_id: str = Field(..., description="Skill whose every intent and entity is removed.")
    model_config = ConfigDict(extra='allow')


class OvosSkillDeregisterMessage(OpenVoiceOSMessage):
    """Remove everything a skill registered — OVOS-INTENT-4 §8.4.

    Emitted when a skill unloads, by the skill or by whatever unloads it, and
    by a bridge on behalf of a satellite that disconnects. The removal is scoped
    to the session on the Message context, so a satellite's deregistration
    leaves the default session's registrations alone.
    """
    message_type: str = "ovos.skill.deregister"
    data: OvosSkillDeregisterData


class OvosIntentListData(BaseModel):
    """Optional filters for an intent listing (INTENT-4 §10.1).

    Omitting a filter widens the query. With ``session_id`` set the response
    carries the effective pool for that session — its own intents plus the
    default-session ones — rather than its raw index.
    """
    skill_id: Optional[str] = Field(None, description="Restrict to one skill.")
    lang: Optional[str] = Field(None, description="Restrict to one BCP-47 language tag.")
    session_id: Optional[str] = Field(None, description="Return the effective pool for this session. Omitted means every session.")
    model_config = ConfigDict(extra='allow')


class OvosIntentListMessage(OpenVoiceOSMessage):
    """Ask the orchestrator which intents are registered — OVOS-INTENT-4 §10.1.

    The manifest is the only accurate view of registration state: an observer
    must query it rather than reconstruct it from broadcasts it happened to hear.
    """
    message_type: str = "ovos.intent.list"
    data: OvosIntentListData = Field(default_factory=OvosIntentListData)


class IntentManifestEntry(BaseModel):
    """One registered intent as the manifest reports it (INTENT-4 §10.1)."""
    skill_id: str = Field(..., description="Skill that owns the intent.")
    intent_name: str = Field(..., description="Registered intent name.")
    lang: str = Field(..., description="BCP-47 language tag of this registration.")
    method: IntentMethod = Field(..., description="How the intent was defined. An intent registered both ways appears twice.")
    enabled: bool = Field(..., description="False while suppressed by ovos.intent.disable.")
    session_id: str = Field(..., description="Session the intent was registered under.")
    model_config = ConfigDict(extra='allow')


class OvosIntentListResponseData(BaseModel):
    """Manifest listing (INTENT-4 §10.1)."""
    ok: bool = Field(..., description="True when the query was served.")
    intents: List[IntentManifestEntry] = Field(default_factory=list, description="Matching registrations.")
    model_config = ConfigDict(extra='allow')


class OvosIntentListResponseMessage(OpenVoiceOSMessage):
    """Return the registered intents — OVOS-INTENT-4 §10.1."""
    message_type: str = "ovos.intent.list.response"
    data: OvosIntentListResponseData


class OvosIntentDescribeData(BaseModel):
    """Identity of the intent to describe, plus optional filters (INTENT-4 §10.2)."""
    skill_id: str = Field(..., description="Skill that owns the intent.")
    intent_name: str = Field(..., description="Intent to describe.")
    lang: str = Field(..., description="BCP-47 language tag.")
    method: Optional[IntentMethod] = Field(None, description="Restrict to one method. Omitted returns every registered method.")
    session_id: Optional[str] = Field(None, description="Restrict to one session. Omitted returns every session's definitions.")
    model_config = ConfigDict(extra='allow')


class OvosIntentDescribeMessage(OpenVoiceOSMessage):
    """Ask the orchestrator for one intent's full definition — OVOS-INTENT-4 §10.2."""
    message_type: str = "ovos.intent.describe"
    data: OvosIntentDescribeData


class IntentDefinitionEntry(BaseModel):
    """One stored definition, self-identifying by method and session (INTENT-4 §10.2).

    ``definition`` is the §5 or §6 registration payload as it was broadcast,
    unknown fields included. Consumers key on ``method`` and ``session_id``,
    never on array position.
    """
    method: IntentMethod = Field(..., description="How this definition was registered.")
    session_id: str = Field(..., description="Session this definition was registered under.")
    definition: Dict[str, Any] = Field(..., description="The registration payload as broadcast.")
    model_config = ConfigDict(extra='allow')


class OvosIntentDescribeResponseData(BaseModel):
    """Stored definitions of one intent, or the reason there are none (INTENT-4 §10.2)."""
    ok: bool = Field(..., description="False when the intent is unknown or the request was incomplete.")
    definitions: List[IntentDefinitionEntry] = Field(default_factory=list, description="One entry per registered (session_id, method) combination passing the filters.")
    error: Optional[str] = Field(None, description="Why the query could not be served.")
    model_config = ConfigDict(extra='allow')


class OvosIntentDescribeResponseMessage(OpenVoiceOSMessage):
    """Return one intent's stored definitions — OVOS-INTENT-4 §10.2."""
    message_type: str = "ovos.intent.describe.response"
    data: OvosIntentDescribeResponseData
