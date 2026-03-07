from typing import Dict, Any

from pydantic import Field

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


class RecognizerLoopAudioOutputStartMessage(OpenVoiceOSMessage):
    """Signal that the audio output pipeline has begun playing a TTS or sound clip.

    Emitted just before audio playback starts. The listener pauses microphone
    capture while audio is playing to prevent echo feedback. Paired with
    `recognizer_loop:audio_output_end` which signals when playback has finished.
    """
    message_type: str = "recognizer_loop:audio_output_start"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for audio output start event.")


class RecognizerLoopAudioOutputEndMessage(OpenVoiceOSMessage):
    """Signal that the audio output pipeline has finished playing a TTS or sound clip.

    Emitted after audio playback completes. The listener resumes microphone
    capture after receiving this. If `expect_response` was set on the preceding
    speak request, the listener activates directly without requiring the wake
    word — enabling `get_response()` conversational flows. Paired with
    `recognizer_loop:audio_output_start`.
    """
    message_type: str = "recognizer_loop:audio_output_end"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for audio output end event.")
