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
    pipeline: List[str] = Field(
        default_factory=lambda: [
            "stop_high", "converse", "padatious_high", "adapt_high",
            "fallback_high", "stop_medium", "padatious_medium",
            "adapt_medium", "adapt_low", "common_qa", "fallback_medium", "fallback_low"
        ],
        description="Ordered list of intent matching pipeline stages."
    )
    location_preferences: Dict[str, Any] = Field(default_factory=dict,
                                                 description="User's location preferences.")
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
