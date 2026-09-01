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


class SessionHandler(BaseModel):
    """A skill holding an activation slot, with the time it was granted."""
    skill_id: str = Field(..., description="ID of the skill holding the slot.")
    activated_at: float = Field(..., description="Unix timestamp of the activation.")


class ResponseMode(BaseModel):
    """The single skill awaiting a raw utterance, and when its hold lapses."""
    skill_id: str = Field(..., description="ID of the skill awaiting the response.")
    expires_at: float = Field(..., description="Unix timestamp after which the hold is void.")


class Session(BaseModel):
    """
    Comprehensive model for an OpenVoiceOS conversational session.
    """
    session_id: str = Field(default_factory=lambda: "default",
                            description="Unique identifier for the session.")
    expiration_seconds: int = Field(-1, description="Time-to-live for the session in seconds (-1 for no expiration).")
    active_skills: List[Tuple[str, float]] = Field(
        default_factory=list,
        description="List of active skills in the session, each with its last activation timestamp (skill_id, timestamp)."
    )
    utterance_states: Dict[str, UtteranceState] = Field(
        default_factory=dict,
        description="Dictionary mapping skill IDs to their current utterance state (INTENT or RESPONSE)."
    )
    lang: str = Field("en-us", description="Language of the session (e.g., 'en-us').")
    context: IntentContextManager = Field(default_factory=IntentContextManager,
                                          description="Context manager for the session's conversational flow.")
    site_id: str = Field("unknown", description="Identifier for the physical location or device.")
    pipeline: Optional[List[str]] = Field(
        None,
        description="Ordered list of pipeline matcher references. Absent when the producer declared none."
    )
    location: Dict[str, Any] = Field(default_factory=dict,
                                     description="Location the session resolves place-dependent answers against.")
    system_unit: str = Field("metric", description="Preferred system of measurement ('metric' or 'imperial').")
    time_format: str = Field("full", description="Preferred time format ('full' or '12hour'/'24hour').")
    date_format: str = Field("DMY", description="Preferred date format ('DMY', 'MDY', 'YMD').")
    is_speaking: bool = Field(False, description="True if the device is currently speaking.")
    is_recording: bool = Field(False, description="True if the device is currently recording audio.")
    blacklisted_intents: List[str] = Field(default_factory=list,
                                           description="List of intent names that are blacklisted for this session.")
    blacklisted_skills: List[str] = Field(default_factory=list,
                                          description="List of skill IDs that are blacklisted for this session.")
    touch_time: int = Field(default_factory=lambda: int(time.time()),
                            description="Timestamp of the last interaction with the session.")
    secondary_langs: Optional[List[str]] = Field(None, description="Additional BCP-47 tags the session also understands.")
    output_lang: Optional[str] = Field(None, description="BCP-47 tag the response is rendered in.")
    stt_lang: Optional[str] = Field(None, description="BCP-47 tag the transcriber reported for the current utterance.")
    request_lang: Optional[str] = Field(None, description="BCP-47 tag the client requested for the current utterance.")
    detected_lang: Optional[str] = Field(None, description="BCP-47 tag a detector inferred for the current utterance.")
    intent_context: Optional[Dict[str, Any]] = Field(None, description="Conversational context entries keyed by context name.")
    active_handlers: Optional[List[SessionHandler]] = Field(None, description="Skills holding an activation slot, most recent first.")
    converse_handlers: Optional[List[SessionHandler]] = Field(None, description="Skills eligible for the converse poll.")
    response_mode: Optional[ResponseMode] = Field(None, description="The skill awaiting a raw utterance, if any.")
    fallback_handlers: Optional[List[str]] = Field(None, description="Skill IDs registered as fallback handlers.")
    persona_id: Optional[str] = Field(None, description="Persona the session routes conversational queries to.")
    blacklisted_pipelines: Optional[List[str]] = Field(None, description="Pipeline matcher references barred from this session.")
    audio_transformers: Optional[List[str]] = Field(None, description="Audio transformer plugins active in this session.")
    utterance_transformers: Optional[List[str]] = Field(None, description="Utterance transformer plugins active in this session.")
    metadata_transformers: Optional[List[str]] = Field(None, description="Metadata transformer plugins active in this session.")
    intent_transformers: Optional[List[str]] = Field(None, description="Intent transformer plugins active in this session.")
    dialog_transformers: Optional[List[str]] = Field(None, description="Dialog transformer plugins active in this session.")
    tts_transformers: Optional[List[str]] = Field(None, description="TTS transformer plugins active in this session.")
    blacklisted_audio_transformers: Optional[List[str]] = Field(None, description="Audio transformers barred from this session.")
    blacklisted_utterance_transformers: Optional[List[str]] = Field(None, description="Utterance transformers barred from this session.")
    blacklisted_metadata_transformers: Optional[List[str]] = Field(None, description="Metadata transformers barred from this session.")
    blacklisted_intent_transformers: Optional[List[str]] = Field(None, description="Intent transformers barred from this session.")
    blacklisted_dialog_transformers: Optional[List[str]] = Field(None, description="Dialog transformers barred from this session.")
    blacklisted_tts_transformers: Optional[List[str]] = Field(None, description="TTS transformers barred from this session.")

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
