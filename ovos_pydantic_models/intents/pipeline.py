"""OVOS-PIPELINE-1 utterance lifecycle.

The entry topic every producer feeds an utterance into (§9.1), the match and
no-match notifications the orchestrator broadcasts (§9.2, §9.3), and the
handler-lifecycle trio that brackets every dispatch (§8).

Messages of a lifecycle share ``context.utterance_id`` (§9.1.1); it is an
envelope key preserved by the MSG-1 derivations, so it appears in
``MessageContext``, not in any payload here.

``ovos.intent.matched`` requires ``pipeline_id`` (§9.2). ovos-core 3.2.0a1
emits ``reply.context.get("pipeline_id")`` verbatim
(ovos_core/intent_services/service.py:634), so a match from a plugin that
declared no ``pipeline_id`` reaches the wire with the field null.
"""
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


class OvosUtteranceHandleData(BaseModel):
    """An utterance offered to the assistant (PIPELINE-1 §9.1).

    ``lang`` is present only when the producer authoritatively knows the
    content language — a chat client that saw the text typed, or an audio
    service reporting the language its decoder ran in. A producer that does not
    know must omit it rather than guess; the orchestrator then resolves the
    language once from the session's evidence fields and passes the result to
    every plugin.
    """
    utterances: List[str] = Field(..., description="Candidate transcriptions or texts, best first.")
    lang: Optional[str] = Field(None, description="BCP-47 tag of the content, when the producer authoritatively knows it.")
    model_config = ConfigDict(extra='allow')


class OvosUtteranceHandleMessage(OpenVoiceOSMessage):
    """Feed an utterance into the assistant — OVOS-PIPELINE-1 §9.1.

    The only entry topic the specification recognizes. Any producer emits it —
    a listener, a chat bridge, a CLI, a test harness, a remote peer — and
    receipt opens an utterance lifecycle that ends with exactly one
    ``ovos.utterance.handled``.
    """
    message_type: str = "ovos.utterance.handle"
    data: OvosUtteranceHandleData


class OvosIntentMatchedData(BaseModel):
    """The winning match, as the orchestrator announces it (PIPELINE-1 §9.2)."""
    skill_id: str = Field(..., description="Handler the match is addressed to.")
    intent_name: str = Field(..., description="Matched intent name.")
    lang: str = Field(..., description="Content language of the match.")
    utterance: str = Field(..., description="Candidate string that won the match.")
    slots: Dict[str, str] = Field(..., description="Slot map extracted by the matching plugin. May be empty.")
    pipeline_id: str = Field(..., description="Plugin that produced the match.")
    model_config = ConfigDict(extra='allow')


class OvosIntentMatchedMessage(OpenVoiceOSMessage):
    """Announce that a plugin claimed the utterance — OVOS-PIPELINE-1 §9.2.

    Broadcast after ``match`` returns and before the dispatch goes out. This is
    a notification: receipt is not permission to run a handler, which happens
    only on the ``<skill_id>:<intent_name>`` dispatch topic.
    """
    message_type: str = "ovos.intent.matched"
    data: OvosIntentMatchedData


class OvosIntentUnmatchedData(BaseModel):
    """What the match round saw before giving up (PIPELINE-1 §9.3).

    Both fields are observability only — the topic name alone carries the
    normative meaning. ``lang`` is absent only when iteration never started.
    A consumer must not resubmit ``utterances`` without explicit user intent.
    """
    utterances: List[str] = Field(default_factory=list, description="Candidate list no plugin matched, after the utterance-transformer chain.")
    lang: Optional[str] = Field(None, description="Resolved BCP-47 tag the match round ran in.")
    model_config = ConfigDict(extra='allow')


class OvosIntentUnmatchedMessage(OpenVoiceOSMessage):
    """Announce that no plugin claimed the utterance — OVOS-PIPELINE-1 §9.3.

    The intent-layer failure signal, distinct from a handler-layer error: this
    means no plugin claimed, while ``ovos.intent.handler.error`` means a
    handler ran and raised. Immediately followed by ``ovos.utterance.handled``.
    """
    message_type: str = "ovos.intent.unmatched"
    data: OvosIntentUnmatchedData = Field(default_factory=OvosIntentUnmatchedData)


class IntentHandlerLifecycleData(BaseModel):
    """Which handler the lifecycle event is about (PIPELINE-1 §8.2).

    Implementations may add fields; consumers must not require them.
    """
    skill_id: str = Field(..., description="Skill of the dispatched handler.")
    intent_name: str = Field(..., description="Intent the handler was dispatched for.")
    model_config = ConfigDict(extra='allow')


class OvosIntentHandlerStartMessage(OpenVoiceOSMessage):
    """The orchestrator is about to invoke a handler — OVOS-PIPELINE-1 §8.1.

    Forwarded from the dispatch, so the context and its session are unchanged.
    Exactly one ``start`` per accepted dispatch, followed by exactly one of
    ``complete`` or ``error``.
    """
    message_type: str = "ovos.intent.handler.start"
    data: IntentHandlerLifecycleData


class OvosIntentHandlerCompleteMessage(OpenVoiceOSMessage):
    """A handler returned normally — OVOS-PIPELINE-1 §8.1."""
    message_type: str = "ovos.intent.handler.complete"
    data: IntentHandlerLifecycleData


class IntentHandlerErrorData(IntentHandlerLifecycleData):
    """A failed handler and the failure (PIPELINE-1 §8.2)."""
    exception: str = Field(..., description="Human-readable description of the failure, or of the timeout that ended the invocation.")


class OvosIntentHandlerErrorMessage(OpenVoiceOSMessage):
    """A handler raised, or exceeded the deployment's time bound — OVOS-PIPELINE-1 §8.1, §8.3.

    A deployment that bounds handler execution emits this with a timeout
    ``exception`` when the bound expires, then proceeds to the end-marker. The
    dispatch is never re-emitted for the same match.
    """
    message_type: str = "ovos.intent.handler.error"
    data: IntentHandlerErrorData
