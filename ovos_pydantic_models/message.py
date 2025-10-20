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


# Example usage (optional, for demonstration)
if __name__ == "__main__":
    # Create a Session instance
    session_data = Session(session_id="12345", lang="en-us")
    print(f"Session Data: {session_data.model_dump_json(indent=2)}\n")

    # Create a MessageContext instance with extra data
    context_data = MessageContext(source="my_skill", destination="audio_output", session=session_data,
                                  custom_field="some_value", another_data={"key": "value"})
    print(f"Context Data with extra fields: {context_data.model_dump_json(indent=2)}\n")

    # Create an OpenVoiceOSMessage instance
    message_data = OpenVoiceOSMessage(
        message_type="speak",
        data={"utterance": "Hello, how can I help you?"},
        context=context_data
    )
    print(f"OpenVoiceOS Message: {message_data.model_dump_json(indent=2)}\n")

    # Example with minimal data
    minimal_message = OpenVoiceOSMessage(
        message_type="recognizer_loop:utterance",
        data={"utterances": ["test utterance"]}
    )
    print(f"Minimal OpenVoiceOS Message: {minimal_message.model_dump_json(indent=2)}")
