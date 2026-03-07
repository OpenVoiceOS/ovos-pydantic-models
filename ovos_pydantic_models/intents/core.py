from typing import Dict, Any, Optional

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
    """
    message_type: str = "ovos.utterance.handled"
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
