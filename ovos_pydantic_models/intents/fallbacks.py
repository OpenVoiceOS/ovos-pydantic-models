from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

from ovos_pydantic_models.message import OpenVoiceOSMessage


class FallbackMode(str, Enum):
    """Controls which fallback skills are allowed to participate in the fallback pipeline."""
    ACCEPT_ALL = "accept_all"   # Every registered fallback skill may be tried
    BLACKLIST = "blacklist"     # All except explicitly blacklisted skill IDs
    WHITELIST = "whitelist"     # Only explicitly whitelisted skill IDs


# --- Fallback Service Message Models ---

class OvosSkillsFallbackRegisterData(BaseModel):
    """Registration payload for declaring a skill's fallback handler."""
    skill_id: str = Field(..., description="ID of the skill registering a fallback handler.")
    priority: int = Field(101, description="Fallback priority — lower numbers are tried first. Default 101 (low priority). Use values 1-100 for high-priority fallbacks.")


class OvosSkillsFallbackRegisterMessage(OpenVoiceOSMessage):
    """Register a skill as a fallback handler in the intent pipeline.

    Emitted by skills that extend `OVOSFallbackSkill` during initialization.
    The intent service adds the skill to its ordered fallback list. Fallback
    skills are tried (lowest priority number first) only after all normal
    pipeline stages have failed.
    """
    message_type: str = "ovos.skills.fallback.register"
    data: OvosSkillsFallbackRegisterData


class OvosSkillsFallbackDeregisterData(BaseModel):
    """Deregistration payload for removing a skill's fallback handler."""
    skill_id: str = Field(..., description="ID of the skill removing its fallback handler.")


class OvosSkillsFallbackDeregisterMessage(OpenVoiceOSMessage):
    """Remove a skill from the fallback handler list.

    Emitted when a fallback skill unloads or shuts down. The intent service
    removes the skill from the ordered fallback list immediately.
    """
    message_type: str = "ovos.skills.fallback.deregister"
    data: OvosSkillsFallbackDeregisterData


class OvosSkillsFallbackPingData(BaseModel):
    """Poll payload broadcast to all registered fallback skills."""
    range: Optional[Tuple[int, int]] = Field(
        None, description="(start, stop) priority range to limit which fallbacks are polled. None means all."
    )
    utterances: List[str] = Field(..., description="Transcription candidates the fallback should evaluate.")
    lang: str = Field(..., description="BCP-47 language code.")
    model_config = ConfigDict(extra='allow')


class OvosSkillsFallbackPingMessage(OpenVoiceOSMessage):
    """Broadcast to all fallback skills asking if any can handle the current utterance.

    Emitted by the intent service after all normal pipeline stages fail. Each
    fallback skill in the priority range evaluates the utterance and replies
    with `ovos.skills.fallback.pong`. The highest-confidence willing skill is
    then called via a targeted request message.
    """
    message_type: str = "ovos.skills.fallback.ping"
    data: OvosSkillsFallbackPingData


class OvosSkillsFallbackPongData(BaseModel):
    """A fallback skill's response to a capability ping."""
    skill_id: str = Field(..., description="Skill ID responding to the ping.")
    can_handle: bool = Field(True, description="True if this skill's fallback handler can attempt the utterance.")
    model_config = ConfigDict(extra='allow')


class OvosSkillsFallbackPongMessage(OpenVoiceOSMessage):
    """A fallback skill reports whether it can handle the current utterance.

    Emitted by each registered fallback skill in reply to
    `ovos.skills.fallback.ping`. The intent service collects pongs to pick
    the highest-priority willing handler.
    """
    message_type: str = "ovos.skills.fallback.pong"
    data: OvosSkillsFallbackPongData


class OvosSkillsFallbackRequestData(BaseModel):
    """Targeted fallback execution payload for a specific skill."""
    skill_id: str = Field(..., description="ID of the skill chosen to handle the fallback.")
    utterances: List[str] = Field(..., description="Transcription candidates to pass to the fallback handler.")
    lang: str = Field(..., description="BCP-47 language code.")
    model_config = ConfigDict(extra='allow')


class OvosSkillsFallbackRequestMessage(OpenVoiceOSMessage):
    """Ask a specific fallback skill to handle the current utterance.

    Dynamic message type: `ovos.skills.fallback.{skill_id}.request`. Emitted
    by the intent service after selecting the winning pong. The skill executes
    its fallback handler and replies with `...response`.
    """
    message_type: str = Field(..., description="Dynamic: 'ovos.skills.fallback.{skill_id}.request'.")
    data: OvosSkillsFallbackRequestData


# --- Skill-side fallback messages ---

class OvosSkillsFallbackStartMessage(OpenVoiceOSMessage):
    """Signal that the fallback handler has begun executing in a skill.

    Dynamic message type: `ovos.skills.fallback.{skill_id}.start`. Emitted
    internally by the fallback skill before its handler runs — useful for
    logging and timing metrics.
    """
    message_type: str = Field(..., description="Dynamic: 'ovos.skills.fallback.{skill_id}.start'.")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class OvosSkillsFallbackResponseData(BaseModel):
    """Result payload from a fallback skill's handler execution."""
    result: bool = Field(..., description="True if the fallback handler successfully handled the utterance and consumed it.")
    fallback_handler: Optional[str] = Field(None, description="Python function name of the handler that was invoked.")
    model_config = ConfigDict(extra='allow')


class OvosSkillsFallbackResponseMessage(OpenVoiceOSMessage):
    """Report the result of a fallback handler execution back to the intent service.

    Dynamic message type: `ovos.skills.fallback.{skill_id}.response`. If
    `result` is False the intent service tries the next fallback in priority
    order. If all fallbacks return False, `complete_intent_failure` is emitted.
    """
    message_type: str = Field(..., description="Dynamic: 'ovos.skills.fallback.{skill_id}.response'.")
    data: OvosSkillsFallbackResponseData


class OvosSkillsFallbackKilledData(BaseModel):
    """Error payload emitted when a fallback handler is force-terminated."""
    error: str = Field(..., description="Reason the fallback was killed (e.g. timeout, unhandled exception).")
    model_config = ConfigDict(extra='allow')


class OvosSkillsFallbackKilledMessage(OpenVoiceOSMessage):
    """Signal that a fallback skill's handler was force-terminated.

    Dynamic message type: `ovos.skills.fallback.{skill_id}.killed`. Emitted
    by the intent service when a fallback times out or raises an exception.
    The skill should clean up any state from the aborted handler.
    """
    message_type: str = Field(..., description="Dynamic: 'ovos.skills.fallback.{skill_id}.killed'.")
    data: OvosSkillsFallbackKilledData


class OvosSkillsFallbackForceTimeoutData(BaseModel):
    """Request payload for forcibly timing out a hanging fallback handler."""
    skill_id: str = Field(..., description="ID of the skill whose fallback handler should be aborted.")
    model_config = ConfigDict(extra='allow')


class OvosSkillsFallbackForceTimeoutMessage(OpenVoiceOSMessage):
    """Force-terminate a fallback skill that is taking too long to respond.

    Emitted by the intent service watchdog when a fallback handler exceeds
    the configured timeout. Causes the skill to receive `...killed`.
    """
    message_type: str = "ovos.skills.fallback.force_timeout"
    data: OvosSkillsFallbackForceTimeoutData


# --- OVOS-FALLBACK-1 §6.1 willingness contest ---

class OvosFallbackPingData(BaseModel):
    """The round's question — the utterance every fallback skill evaluates (FALLBACK-1 §6.1)."""
    utterances: List[str] = Field(..., description="Candidate utterance list the skill should evaluate.")
    lang: str = Field(..., description="Resolved BCP-47 language tag.")
    model_config = ConfigDict(extra='allow')


class OvosFallbackPingMessage(OpenVoiceOSMessage):
    """Ask the whole fallback pool whether anyone will handle the utterance — OVOS-FALLBACK-1 §6.1.

    One broadcast per round, derived from the utterance Message by reply. Every
    registered fallback skill evaluates in parallel, so the round costs one
    collection window rather than a sum of per-skill waits. This is where a
    fallback skill does its real work — query a knowledge base, run a
    classifier, call a model — and the reply carries only the decision.

    ovos-core 3.2.0a1 and ovos-workshop 9.6.1a1 run this contest on
    ``ovos.skills.fallback.ping`` / ``.pong`` instead
    (ovos_core/intent_services/fallback_service.py:191,
    ovos_workshop/skills/fallback.py:106).
    """
    message_type: str = "ovos.fallback.ping"
    data: OvosFallbackPingData


class OvosFallbackPongData(BaseModel):
    """A fallback skill's answer to the round (FALLBACK-1 §6.1).

    ``utterance`` says *what* the skill judged; the envelope's
    ``utterance_id`` says *which round* the judgment belongs to.
    """
    skill_id: str = Field(..., description="Responding skill's identity.")
    can_handle: bool = Field(..., description="Whether the skill is willing to handle this utterance.")
    utterance: str = Field(..., description="Echo of the evaluated candidate — the first element of the ping's utterances.")
    model_config = ConfigDict(extra='allow')


class OvosFallbackPongMessage(OpenVoiceOSMessage):
    """A fallback skill claims or declines the utterance — OVOS-FALLBACK-1 §6.1.

    A skill should answer even when declining, so the window can close early
    instead of waiting out the ceiling. Silence at window close, a mismatched
    ``utterance_id``, or a missing or non-boolean ``can_handle`` all count as a
    decline.
    """
    message_type: str = "ovos.fallback.pong"
    data: OvosFallbackPongData
