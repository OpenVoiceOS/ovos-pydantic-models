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


class OvosAudioOutputStartedMessage(OpenVoiceOSMessage):
    """Signal that an audio output playback session has started — OVOS-AUDIO-1 §5.1.

    Emitted by `ovos-audio` when playback goes from idle to active, derived by
    `forward` from the speak Message so it keeps that Message's context. The
    spec name of `recognizer_loop:audio_output_start`.
    """
    message_type: str = "ovos.audio.output.started"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for audio output start event.")


class OvosAudioOutputEndedMessage(OpenVoiceOSMessage):
    """Signal that an audio output playback session has ended — OVOS-AUDIO-1 §5.2.

    Emitted by `ovos-audio` when the queue is empty and the last item has
    finished, derived by `forward` from the speak Message. The spec name of
    `recognizer_loop:audio_output_end`.
    """
    message_type: str = "ovos.audio.output.ended"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for audio output end event.")
