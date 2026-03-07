from typing import Dict, Any, Optional, List, Union

from pydantic import BaseModel, Field, ConfigDict

from ovos_pydantic_models.session import Session

# --- Base Message Models ---

MessageData = Dict[str, Any]
MessageSource = Optional[str]
MessageDestination = Optional[Union[str, List[str]]]


class MessageContext(BaseModel, extra='allow'):
    """Comprehensive context for a bus message."""
    source: MessageSource = Field(None, description="Origin of the message (e.g., 'skills', 'listener', 'audio').")
    destination: MessageDestination = Field(None,
                                            description="Intended recipient(s) of the message. None is considered a broadcast")
    session: Optional[Session] = Field(None, description="Session-specific context.")


class OpenVoiceOSMessage(BaseModel):
    """
    Base model for all OpenVoiceOS bus messages.
    All specific message types should inherit from or conform to this structure.
    """
    message_type: str = Field(..., description="The type of the message (e.g., 'speak', 'recognizer_loop:utterance').")
    data: MessageData = Field(default_factory=dict, description="The payload data of the message.")
    context: MessageContext = Field(default_factory=MessageContext,
                                    description="Contextual information about the message.")

