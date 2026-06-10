import time
from enum import Enum
from typing import Dict, Any, Optional, List, Tuple

from pydantic import BaseModel, Field, ConfigDict, model_validator


class UtteranceState(str, Enum):
    """
    Represents the state of an utterance within a session.
    INTENT: The skill is expecting an intent.
    RESPONSE: The skill is expecting a response.
    """
    INTENT = "intent"
    RESPONSE = "response"


# ---------------------------------------------------------------------------
# SESSION-1 §3.4 — active_handlers entry shape
# ---------------------------------------------------------------------------

class ActiveHandlerEntry(BaseModel, extra='allow'):
    """One entry in ``session.active_handlers`` (OVOS-SESSION-1 §3.4 / OVOS-PIPELINE-1 §7.1).

    Records a skill or plugin that has been activated as a handler for the
    current utterance lifecycle and may still accept follow-up converse turns.
    The orchestrator pushes an entry on dispatch and pops it on
    ``ovos.utterance.handled`` or on an explicit stop/deactivation event.
    """
    skill_id: str = Field(..., description="Identifier of the activated skill or pipeline plugin.")
    activated_at: float = Field(
        default_factory=time.time,
        description="Unix timestamp (seconds) when the handler was activated."
    )


# ---------------------------------------------------------------------------
# SESSION-1 §3.x — response_mode shape (OVOS-CONVERSE-1 §2.2)
# ---------------------------------------------------------------------------

class ResponseMode(BaseModel):
    """Tracks an active ``get_response`` / converse response-mode window.

    Owned by OVOS-CONVERSE-1 §2.2; projected into ``session.response_mode``
    so the state survives orchestrator restart and multi-orchestrator deployments
    (OVOS-SESSION-2 §2.4).
    """
    skill_id: str = Field(..., description="Skill waiting for the user's follow-up response.")
    expires_at: float = Field(..., description="Unix timestamp after which the response window closes.")


class ContextEntity(BaseModel):
    """
    Represents an entity within the conversational context.
    """
    data: str = Field(..., description="The entity tag (e.g., 'time').")
    key: str = Field(..., description="The proper name of the entity (e.g., '10:00 AM').")
    confidence: float = Field(1.0, description="Confidence score for the entity.")
    origin: Optional[str] = Field(None, description="Origin of the entity, used for context depth calculation.")


class IntentContextManagerFrame(BaseModel, extra='allow'):
    """
    Manages entities and metadata for a single frame of conversation.
    """
    entities: List[ContextEntity] = Field(default_factory=list, description="List of entities belonging to this frame.")
    metadata: Dict[str, Any] = Field(default_factory=dict,
                                     description="Arbitrary metadata describing the context frame.")


class IntentContextManager(BaseModel):
    """
    Manages conversational context across multiple frames.
    """
    timeout: int = Field(120, description="Time-to-live (in seconds) for context frames.")
    frame_stack: List[Tuple[IntentContextManagerFrame, float]] = Field(
        default_factory=list,
        description="Stack of context frames, each paired with a timestamp of its creation/last update."
    )
    context_keywords: List[str] = Field(default_factory=list, description="Keywords used for context management.")
    context_max_frames: int = Field(3, description="Maximum number of context frames to retain.")
    context_greedy: bool = Field(False, description="If true, all entities update context; otherwise, only keywords.")

    # Custom validator to ensure frames are properly deserialized into Pydantic models
    # when the IntentContextManager is instantiated.
    @model_validator(mode='before')
    @classmethod
    def _validate_frame_stack(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        frame_stack = values.get('frame_stack')
        if frame_stack:
            validated_stack = []
            for frame_data, timestamp in frame_stack:
                # Ensure the frame data is parsed into an IntentContextManagerFrame model
                # This handles cases where frame_data might be a dict from serialization
                if isinstance(frame_data, dict):
                    validated_stack.append((IntentContextManagerFrame(**frame_data), timestamp))
                elif isinstance(frame_data, IntentContextManagerFrame):
                    validated_stack.append((frame_data, timestamp))
                else:
                    raise ValueError(f"Invalid frame data type in frame_stack: {type(frame_data)}")
            values['frame_stack'] = validated_stack
        return values


class Session(BaseModel):
    """Wire shape of the OVOS session carrier (OVOS-SESSION-1).

    This model mirrors the closed field registry defined in SESSION-1 §3.
    All fields are OPTIONAL on the wire; a consumer that does not recognise a
    field MUST treat it as absent (SESSION-1 §2.4). Fields owned by other
    specifications are documented with their owning spec reference.

    Implementation note: several fields here (``active_skills``,
    ``utterance_states``) pre-date the SESSION-1 spec and reflect the in-use
    runtime representation in ovos-core. They are retained for round-trip
    fidelity with existing bus traffic.
    """
    # SESSION-1 §3.1
    session_id: str = Field(
        default_factory=lambda: "default",
        description="Unique session identifier. The reserved value 'default' refers to the device-local session (SESSION-1 §3.1)."
    )

    # SESSION-1 §3.2 — language fields
    lang: str = Field(
        "en-us",
        description="Primary language for this session (BCP-47). Used by STT, intent parsing, and TTS. (SESSION-1 §3.2.1)"
    )
    secondary_langs: List[str] = Field(
        default_factory=list,
        description="Additional languages the session MAY fall back to when the primary language produces no result (SESSION-1 §3.2.2)."
    )
    output_lang: Optional[str] = Field(
        None,
        description="Language of text being spoken; influences TTS engine selection. Defaults to session.lang when absent (SESSION-1 §3.2.8)."
    )
    stt_lang: Optional[str] = Field(
        None,
        description="Language assumed by the STT engine for the current recording. Set by the audio input service (AUDIO-IN-1 §5.1)."
    )
    request_lang: Optional[str] = Field(
        None,
        description="Language hint from the capture mechanism (e.g. wake-word language selector). Input-side only (SESSION-1 §3.2.5)."
    )
    detected_lang: Optional[str] = Field(
        None,
        description="Language identified by an audio-transformer language-ID component. Highest priority for STT engine selection (SESSION-1 §3.2.6)."
    )

    # SESSION-1 §3.3
    site_id: str = Field(
        "unknown",
        description="Opaque group identifier for the physical location / device cluster (SESSION-1 §3.3)."
    )

    # OVOS-PIPELINE-1 §5 / SESSION-1 §3 registry
    pipeline: List[str] = Field(
        default_factory=lambda: [
            "stop_high", "converse", "padatious_high", "adapt_high",
            "fallback_high", "stop_medium", "padatious_medium",
            "adapt_medium", "adapt_low", "common_qa", "fallback_medium", "fallback_low"
        ],
        description="Ordered list of pipeline stage identifiers the orchestrator iterates during intent matching (PIPELINE-1 §5)."
    )

    # OVOS-PIPELINE-1 §7.1 — active handlers
    active_handlers: List[ActiveHandlerEntry] = Field(
        default_factory=list,
        description="Skills/plugins currently active as utterance handlers; popped on ovos.utterance.handled (PIPELINE-1 §7.1)."
    )

    # OVOS-CONVERSE-1 §2.2 — response-mode window
    response_mode: Optional[ResponseMode] = Field(
        None,
        description="Active get_response / converse window; None when no skill is waiting for a follow-up (CONVERSE-1 §2.2)."
    )

    # OVOS-TRANSFORM-1 §5 — transformer allow-lists (per-session overrides)
    audio_transformers: List[str] = Field(
        default_factory=list,
        description="Ordered list of audio-transformer plugin IDs active for this session (TRANSFORM-1 §5)."
    )
    utterance_transformers: List[str] = Field(
        default_factory=list,
        description="Ordered list of utterance-transformer plugin IDs active for this session (TRANSFORM-1 §5)."
    )
    metadata_transformers: List[str] = Field(
        default_factory=list,
        description="Ordered list of metadata-transformer plugin IDs active for this session (TRANSFORM-1 §5)."
    )
    intent_transformers: List[str] = Field(
        default_factory=list,
        description="Ordered list of intent-transformer plugin IDs active for this session (TRANSFORM-1 §5)."
    )
    dialog_transformers: List[str] = Field(
        default_factory=list,
        description="Ordered list of dialog-transformer plugin IDs active for this session (TRANSFORM-1 §5)."
    )
    tts_transformers: List[str] = Field(
        default_factory=list,
        description="Ordered list of TTS-transformer plugin IDs active for this session (TRANSFORM-1 §5)."
    )

    # OVOS-PIPELINE-1 §5 — blacklists
    blacklisted_skills: List[str] = Field(
        default_factory=list,
        description="Skill IDs excluded from the pipeline for this session (PIPELINE-1 §5). Typically injected at the bridge boundary (BRIDGE-1 §4.2)."
    )
    blacklisted_intents: List[str] = Field(
        default_factory=list,
        description="Intent names excluded from matching for this session (PIPELINE-1 §5)."
    )
    blacklisted_pipelines: List[str] = Field(
        default_factory=list,
        description="Pipeline stage identifiers excluded from the pipeline iteration for this session (PIPELINE-1 §5)."
    )

    # OVOS-TRANSFORM-1 §5.2 — transformer blacklists
    blacklisted_audio_transformers: List[str] = Field(
        default_factory=list,
        description="Audio-transformer plugins to skip for this session (TRANSFORM-1 §5.2)."
    )
    blacklisted_utterance_transformers: List[str] = Field(
        default_factory=list,
        description="Utterance-transformer plugins to skip for this session (TRANSFORM-1 §5.2)."
    )
    blacklisted_metadata_transformers: List[str] = Field(
        default_factory=list,
        description="Metadata-transformer plugins to skip for this session (TRANSFORM-1 §5.2)."
    )
    blacklisted_intent_transformers: List[str] = Field(
        default_factory=list,
        description="Intent-transformer plugins to skip for this session (TRANSFORM-1 §5.2)."
    )
    blacklisted_dialog_transformers: List[str] = Field(
        default_factory=list,
        description="Dialog-transformer plugins to skip for this session (TRANSFORM-1 §5.2)."
    )
    blacklisted_tts_transformers: List[str] = Field(
        default_factory=list,
        description="TTS-transformer plugins to skip for this session (TRANSFORM-1 §5.2)."
    )

    # Implementation fields — pre-spec, retained for round-trip fidelity
    expiration_seconds: int = Field(
        -1,
        description="Time-to-live for the session in seconds (-1 = no expiration). Implementation-level; not in SESSION-1 registry."
    )
    active_skills: List[Tuple[str, float]] = Field(
        default_factory=list,
        description="[Legacy] Active skills with last-activation timestamps. Superseded by active_handlers but retained for wire compatibility."
    )
    utterance_states: Dict[str, UtteranceState] = Field(
        default_factory=dict,
        description="[Legacy] Per-skill utterance states (INTENT | RESPONSE). Used by ovos-core to track get_response windows."
    )
    context: IntentContextManager = Field(
        default_factory=IntentContextManager,
        description="Intent context manager carrying cross-utterance entities (CONTEXT-1 §2 / SESSION-1 intent_context field)."
    )
    location_preferences: Dict[str, Any] = Field(
        default_factory=dict,
        description="User's location preferences (city, country, coordinates, timezone)."
    )
    system_unit: str = Field("metric", description="Preferred measurement system ('metric' or 'imperial').")
    time_format: str = Field("full", description="Preferred time format ('full', '12hour', or '24hour').")
    date_format: str = Field("DMY", description="Preferred date format ('DMY', 'MDY', or 'YMD').")
    is_speaking: bool = Field(False, description="True if the device is currently producing TTS audio.")
    is_recording: bool = Field(False, description="True if the listener is actively recording user speech.")
    touch_time: int = Field(
        default_factory=lambda: int(time.time()),
        description="Unix timestamp of the last interaction with this session."
    )

    # Custom validator to convert utterance_states strings to Enum on instantiation
    @model_validator(mode='before')
    @classmethod
    def _validate_utterance_states(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        utterance_states = values.get('utterance_states')
        if utterance_states:
            validated_states = {}
            for k, v in utterance_states.items():
                if isinstance(v, str):
                    validated_states[k] = UtteranceState(v)  # Convert string to Enum
                elif isinstance(v, UtteranceState):
                    validated_states[k] = v
                else:
                    raise ValueError(f"Invalid utterance state value type for key {k}: {type(v)}")
            values['utterance_states'] = validated_states
        return values


# Example usage removed — see tests/ for usage examples
