from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field, ConfigDict

from ovos_pydantic_models.message import OpenVoiceOSMessage


# --- Intent Service Message Models ---

class IntentServicePipelinesReloadMessage(OpenVoiceOSMessage):
    """Tell the intent service to reload all pipeline plugins from disk.

    Emitted after skills are installed, updated, or their intents change.
    Forces adapt, padatious, and other pipeline engines to retrain/reload.
    """
    message_type: str = "intent.service.pipelines.reload"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosUtteranceCancelledMessage(OpenVoiceOSMessage):
    """Signal that utterance processing was cancelled before completion.

    Emitted by the intent service when a new utterance interrupts an
    in-flight one, or when the user explicitly cancels (e.g. says 'cancel').
    """
    message_type: str = "ovos.utterance.cancelled"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosUtteranceHandledMessage(OpenVoiceOSMessage):
    """Signal that an utterance has been fully handled by the pipeline.

    Broadcast by the intent service at the end of every utterance lifecycle —
    whether a skill matched, fallback was used, or intent failed. Acts as the
    EOF marker for test capture sessions (ovoscope).

    Defined in PIPELINE-1 §9.5.
    """
    message_type: str = "ovos.utterance.handled"
    data: Dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# PIPELINE-1 §9 messages — utterance lifecycle entry/exit and handler trio
# ---------------------------------------------------------------------------

class OvosUtteranceHandleData(BaseModel):
    """Payload for the utterance-layer entry point.

    Defined in PIPELINE-1 §9.1.
    """
    utterances: List[str] = Field(
        ...,
        description="One or more candidate utterance strings; first element is primary.",
        min_length=1,
    )
    lang: Optional[str] = Field(
        None,
        description=(
            "BCP-47 language tag of the utterance. Present only when the producer "
            "authoritatively knows the content language; absent otherwise. "
            "Per PIPELINE-1 §9.1 the orchestrator MUST NOT synthesise a value."
        ),
    )


class OvosUtteranceHandleMessage(OpenVoiceOSMessage):
    """Feed an utterance into the OVOS intent pipeline.

    The utterance-layer entry point consumed by the orchestrator. Any producer
    (listener, chat bridge, CLI, test harness, satellite) emits here to start
    the utterance lifecycle.  The orchestrator iterates pipeline plugins and
    guarantees exactly one ``ovos.utterance.handled`` in response.

    Defined in PIPELINE-1 §9.1.

    Example::

        OvosUtteranceHandleMessage(
            data=OvosUtteranceHandleData(utterances=["turn off the lights"], lang="en-US")
        )
    """
    message_type: str = "ovos.utterance.handle"
    data: OvosUtteranceHandleData


class OvosIntentMatchedData(BaseModel):
    """Notification payload emitted after a pipeline plugin claims an utterance.

    Defined in PIPELINE-1 §9.2.
    """
    skill_id: str = Field(..., description="The handler's skill_id.")
    intent_name: str = Field(..., description="The matched intent name.")
    lang: str = Field(..., description="BCP-47 language tag the match was performed against.")
    utterance: str = Field(..., description="The primary utterance candidate that was matched.")
    slots: Optional[Dict[str, Any]] = Field(
        None,
        description="Named entity slots extracted by the pipeline plugin, keyed by slot name.",
    )
    pipeline_id: str = Field(..., description="pipeline_id of the plugin that produced the match.")
    model_config = ConfigDict(extra="allow")


class OvosIntentMatchedMessage(OpenVoiceOSMessage):
    """Notify observers that a pipeline plugin has claimed the current utterance.

    Broadcast (no ``destination``) by the orchestrator after a plugin's
    ``match()`` returns non-None, *before* the dispatch message goes out.
    This is a **notification**, not a dispatch — consumers MUST NOT treat
    receipt as permission to invoke a handler.

    Defined in PIPELINE-1 §9.2.
    """
    message_type: str = "ovos.intent.matched"
    data: OvosIntentMatchedData


class OvosIntentUnmatchedData(BaseModel):
    """Payload for the no-match notification emitted after all plugins declined.

    Both fields are optional — the topic name alone is normative.
    Defined in PIPELINE-1 §9.3.
    """
    utterances: Optional[List[str]] = Field(
        None,
        description=(
            "The candidate utterance list after the utterance-transformer chain. "
            "Included for observability; consumers MUST NOT re-submit without explicit user intent."
        ),
    )
    lang: Optional[str] = Field(
        None,
        description="BCP-47 tag from the entry-topic Message (§9.1), if present.",
    )


class OvosIntentUnmatchedMessage(OpenVoiceOSMessage):
    """Signal that no pipeline plugin matched the utterance.

    Broadcast by the orchestrator when pipeline iteration completed with no
    plugin claiming the utterance.  Immediately followed by
    ``ovos.utterance.handled`` (§9.5).

    This is the **intent-layer failure** signal, distinct from a handler-layer
    error (``ovos.intent.handler.error``) which means a handler ran and raised.

    Defined in PIPELINE-1 §9.3.
    """
    message_type: str = "ovos.intent.unmatched"
    data: OvosIntentUnmatchedData = Field(default_factory=OvosIntentUnmatchedData)


class OvosIntentHandlerStartData(BaseModel):
    """Payload stamped by the orchestrator just before invoking the handler.

    Defined in PIPELINE-1 §8.
    """
    skill_id: str = Field(..., description="The skill_id of the handler being invoked.")
    intent_name: str = Field(..., description="The intent name the handler is registered for.")
    pipeline_id: Optional[str] = Field(None, description="pipeline_id of the matching plugin.")
    model_config = ConfigDict(extra="allow")


class OvosIntentHandlerStartMessage(OpenVoiceOSMessage):
    """Signal that the orchestrator is about to invoke an intent handler.

    First event of the handler-lifecycle trio. Emitted by the orchestrator
    immediately before calling the handler function.

    Defined in PIPELINE-1 §8.
    """
    message_type: str = "ovos.intent.handler.start"
    data: OvosIntentHandlerStartData


class OvosIntentHandlerCompleteData(BaseModel):
    """Payload stamped after a handler returns normally.

    Defined in PIPELINE-1 §8.
    """
    skill_id: str = Field(..., description="The skill_id whose handler completed.")
    intent_name: str = Field(..., description="The intent name that was handled.")
    model_config = ConfigDict(extra="allow")


class OvosIntentHandlerCompleteMessage(OpenVoiceOSMessage):
    """Signal that an intent handler returned normally.

    Second (success) event of the handler-lifecycle trio.  Emitted by the
    orchestrator immediately after the handler function returns.  Followed
    by ``ovos.utterance.handled``.

    Defined in PIPELINE-1 §8.
    """
    message_type: str = "ovos.intent.handler.complete"
    data: OvosIntentHandlerCompleteData


class OvosIntentHandlerErrorData(BaseModel):
    """Payload stamped after a handler raises an exception.

    Defined in PIPELINE-1 §8.
    """
    skill_id: str = Field(..., description="The skill_id whose handler raised.")
    intent_name: str = Field(..., description="The intent name that was being handled.")
    exception: str = Field(
        ...,
        description="String representation of the exception that was raised (e.g. 'ValueError: ...').",
    )
    model_config = ConfigDict(extra="allow")


class OvosIntentHandlerErrorMessage(OpenVoiceOSMessage):
    """Signal that an intent handler raised an exception.

    Second (error) event of the handler-lifecycle trio.  Emitted by the
    orchestrator when a handler raises.  The utterance lifecycle still
    terminates with ``ovos.utterance.handled`` afterwards.

    Defined in PIPELINE-1 §8.
    """
    message_type: str = "ovos.intent.handler.error"
    data: OvosIntentHandlerErrorData


class OvosUtteranceSpeakData(BaseModel):
    """Natural-language response payload emitted by a skill handler.

    Defined in PIPELINE-1 §9.6.
    """
    utterance: str = Field(
        ...,
        description="The natural-language response string to convey to the user.",
    )
    lang: Optional[str] = Field(
        None,
        description=(
            "BCP-47 tag of the response language.  When absent, the output stage "
            "resolves language from the session per SESSION-1 §3.2."
        ),
    )
    model_config = ConfigDict(extra="allow")


class OvosUtteranceSpeakMessage(OpenVoiceOSMessage):
    """Deliver a natural-language response string from a handler to the output stage.

    The symmetric counterpart to ``ovos.utterance.handle`` — the natural-
    language *output* exit point.  A handler MUST derive each emission from
    the dispatch Message it received (PIPELINE-1 §9.6), propagating
    ``context.session`` and ``context.skill_id`` automatically.

    What the deployment does downstream (TTS, audio queue, chat display) is
    out of scope for this specification.

    Defined in PIPELINE-1 §9.6.

    Example::

        OvosUtteranceSpeakMessage(
            data=OvosUtteranceSpeakData(
                utterance="It is currently 22 degrees and sunny.",
                lang="en-US",
            )
        )
    """
    message_type: str = "ovos.utterance.speak"
    data: OvosUtteranceSpeakData


# ---------------------------------------------------------------------------
# STOP-1 §4-5 messages — spec-defined stop bus surface
# ---------------------------------------------------------------------------

class OvosStopPingMessage(OpenVoiceOSMessage):
    """Query all active handlers for stoppability.

    Broadcast by the stop plugin inside ``match()`` (STOP-1 §4.2).  Payload
    MAY be empty; session_id is carried via ``context.session``.  Handlers
    that can stop for the inbound session_id reply with ``ovos.stop.pong``.

    Defined in STOP-1 §4.2.
    """
    message_type: str = "ovos.stop.ping"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosStopPongData(BaseModel):
    """Stoppability response from a single handler.

    Defined in STOP-1 §4.2.
    """
    can_handle: bool = Field(
        ...,
        description=(
            "True if this handler can stop for the session_id in the originating ping's "
            "context.session.  False means the handler has nothing to stop."
        ),
    )
    skill_id: Optional[str] = Field(
        None,
        description="skill_id of the responding handler, for disambiguation when multiple handlers reply.",
    )
    model_config = ConfigDict(extra="allow")


class OvosStopPongMessage(OpenVoiceOSMessage):
    """Reply from a handler declaring whether it can stop for the current session.

    A handler MUST derive this message from the ping via ``reply()``
    (MSG-1 §5), i.e. ``message.reply('ovos.stop.pong', data)``, ensuring
    session propagation.

    Defined in STOP-1 §4.2.
    """
    message_type: str = "ovos.stop.pong"
    data: OvosStopPongData


class OvosStopMessage(OpenVoiceOSMessage):
    """Universal stop broadcast — all components must cease activity for this session.

    Broadcast by the stop plugin's global-stop handler (STOP-1 §5.3).
    Every component performing user-visible activity MUST subscribe and cease
    activity for the ``session_id`` carried in ``context.session``.

    ``ovos.stop`` is **not** a dispatch topic and does not fire the
    handler-lifecycle trio.  The namespace ``ovos.stop.*`` is reserved.

    Defined in STOP-1 §5.3.
    """
    message_type: str = "ovos.stop"
    data: Dict[str, Any] = Field(default_factory=dict)


class CompleteIntentFailureData(BaseModel, extra='allow'):
    """Context for a complete intent failure — no pipeline stage handled the utterance."""
    utterance: str = Field(..., description="The utterance that no skill or fallback was able to handle.")
    lang: str = Field(..., description="BCP-47 language code of the failed utterance.")


class CompleteIntentFailureMessage(OpenVoiceOSMessage):
    """Signal that the utterance was not handled by any pipeline stage.

    Emitted by the intent service after all pipeline plugins (adapt, padatious,
    converse, fallback) have declined. Typically triggers an error sound and
    'I don't understand' style response. The original utterance is included.
    """
    message_type: str = "complete_intent_failure"
    data: CompleteIntentFailureData


class AddContextData(BaseModel):
    """Payload for adding a named context item to the intent service's context stack."""
    context: str = Field(..., description="Context key to set (e.g. 'Location', 'Artist'). Used by adapt for context-aware intents.")
    word: Optional[str] = Field(None, description="Natural-language alias for this context (e.g. 'here', 'that song'). Expand what adapt can match.")
    origin: Optional[str] = Field(None, description="Skill ID that set this context — used to track context depth and expiry.")


class AddContextMessage(OpenVoiceOSMessage):
    """Push a context item onto the intent service's conversational context stack.

    **Legacy** — context management is Adapt-specific. Emitted by skills via
    `self.set_context()`. Context persists across utterances (up to the
    configured depth) allowing Adapt to resolve references like 'play that
    again' or 'how about there?'.
    """
    message_type: str = "add_context"
    data: AddContextData


class RemoveContextData(BaseModel):
    """Payload for removing a specific context item."""
    context: str = Field(..., description="Context key to remove from the active context stack.")


class RemoveContextMessage(OpenVoiceOSMessage):
    """Remove a single named context item from the intent service's context stack.

    **Legacy** — context management is Adapt-specific. Emitted by skills via
    `self.remove_context()` when a contextual reference is no longer valid
    (e.g. after completing a task).
    """
    message_type: str = "remove_context"
    data: RemoveContextData


class ClearContextMessage(OpenVoiceOSMessage):
    """Clear all context items from the intent service's context stack.

    **Legacy** — context management is Adapt-specific. Emitted by skills or
    the core to reset conversational state entirely. After this, Adapt intents
    requiring context will no longer match until context is repopulated.
    """
    message_type: str = "clear_context"
    data: Dict[str, Any] = Field(default_factory=dict)


class IntentServiceIntentGetData(BaseModel):
    """Query payload for asking the intent service what intent an utterance would match."""
    utterance: str = Field(..., description="The utterance text to evaluate against all pipeline plugins.")
    lang: Optional[str] = Field(None, description="BCP-47 language code. Defaults to active session language.")


class IntentServiceIntentGetMessage(OpenVoiceOSMessage):
    """Ask the intent service what intent a given utterance would trigger, without executing it.

    Useful for introspection, testing, and GUI 'preview' features. The intent
    service responds with `intent.service.intent.reply`.
    """
    message_type: str = "intent.service.intent.get"
    data: IntentServiceIntentGetData


class IntentServiceIntentReplyIntentData(BaseModel, extra='allow'):
    """Details of the winning intent match returned by the intent service."""
    intent_name: str = Field(..., description="Name of the matched intent (e.g. 'WeatherIntent').")
    intent_service: str = Field(..., description="Pipeline plugin that matched this intent (e.g. 'adapt_high', 'padatious_high').")
    skill_id: str = Field(..., description="ID of the skill that owns the matched intent.")
    handler: str = Field(..., description="Python function name of the intent handler that would be called.")


class IntentServiceIntentReplyData(BaseModel):
    """Response payload for `intent.service.intent.get` — the matched (or absent) intent."""
    intent: Optional[IntentServiceIntentReplyIntentData] = Field(
        None, description="Matched intent details, or None if no pipeline stage matched the utterance."
    )
    utterance: str = Field(..., description="The original utterance that was evaluated.")


class IntentServiceIntentReplyMessage(OpenVoiceOSMessage):
    """Return the intent that would be triggered for a given utterance.

    Emitted by the intent service in response to `intent.service.intent.get`.
    The `intent` field is None if no pipeline stage matched.
    """
    message_type: str = "intent.service.intent.reply"
    data: IntentServiceIntentReplyData


class SkillActivateData(BaseModel, extra='allow'):
    """Payload for a per-skill activate event (dynamic message type `{skill_id}.activate`)."""


class SkillActivateMessage(OpenVoiceOSMessage):
    """Signal that a specific skill has been activated (added to the converse stack).

    Dynamic message type: `{skill_id}.activate`. Emitted by the intent
    service when a skill is placed in the converse priority list. The skill
    itself subscribes to this event to know it's now in foreground.
    """
    message_type: str = Field(..., description="Dynamic: '{skill_id}.activate'.")
    data: SkillActivateData = Field(default_factory=SkillActivateData)


class SkillDeactivateData(BaseModel, extra='allow'):
    """Payload for a per-skill deactivate event (dynamic message type `{skill_id}.deactivate`)."""


class SkillDeactivateMessage(OpenVoiceOSMessage):
    """Signal that a specific skill has been removed from the converse stack.

    Dynamic message type: `{skill_id}.deactivate`. Emitted by the intent
    service when a skill's converse timeout expires or it explicitly
    deactivates. The skill subscribes to clean up its conversational state.
    """
    message_type: str = Field(..., description="Dynamic: '{skill_id}.deactivate'.")
    data: SkillDeactivateData = Field(default_factory=SkillDeactivateData)
