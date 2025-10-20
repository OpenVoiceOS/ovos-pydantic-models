from typing import Dict, Any

from pydantic import Field

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


class RecognizerLoopAudioOutputStartMessage(OpenVoiceOSMessage):
    """Message for `recognizer_loop:audio_output_start`."""
    message_type: str = "recognizer_loop:audio_output_start"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for audio output start event.")


class RecognizerLoopAudioOutputEndMessage(OpenVoiceOSMessage):
    """Message for `recognizer_loop:audio_output_end`."""
    message_type: str = "recognizer_loop:audio_output_end"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for audio output end event.")


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Demonstrating Listener Message Models ---")

    # Create a dummy session and context for demonstration
    dummy_session = Session(session_id="test-session-123", lang="en-us")
    dummy_context = MessageContext(source="playback_thread", session=dummy_session)
