from typing import Dict, Any, List, Optional, Tuple

from pydantic import BaseModel, Field, model_validator

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


# --- OVOS Audio / TTS Playback Message Models ---

class MycroftSpeechStopMessage(OpenVoiceOSMessage):
    """Interrupt and discard any TTS speech that is currently playing.

    Emitted by skills, the intent service, or the stop protocol; handled by
    the active TTS plugin via `ovos-audio`. Does not affect music/media playback.
    """
    message_type: str = "mycroft.audio.speech.stop"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftAudioSpeakStatusMessage(OpenVoiceOSMessage):
    """Ask whether the TTS system is currently speaking.

    Any component may emit this; `ovos-audio` replies with
    `mycroft.audio.is_speaking` containing the current speaking state.
    """
    message_type: str = "mycroft.audio.speak.status"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftAudioIsSpeakingData(BaseModel):
    """Reply payload for a `mycroft.audio.speak.status` query."""
    speaking: bool = Field(..., description="True if TTS is actively rendering audio right now.")


class MycroftAudioIsSpeakingMessage(OpenVoiceOSMessage):
    """Response to `mycroft.audio.speak.status` — reports live TTS state.

    Emitted by `ovos-audio` in reply to a speak-status query.
    """
    message_type: str = "mycroft.audio.is_speaking"
    data: MycroftAudioIsSpeakingData


VisemeList = List[Tuple[float, str]]


class MycroftAudioQueueData(BaseModel):
    """Payload for queuing a TTS audio clip for sequential playback."""
    uri: Optional[str] = Field(None, description="URI of the pre-rendered audio file (WAV, MP3, etc.).")
    filename: Optional[str] = Field(None, description="Deprecated — use `uri` instead.")
    binary_data: Optional[str] = Field(None, description="Hex-encoded raw audio bytes (alternative to uri).")
    audio_ext: Optional[str] = Field(None, description="File extension hinting the codec when binary_data is used, e.g. 'wav'.")
    viseme: Optional[VisemeList] = Field(
        None, description="Lip-sync data: list of (timestamp_seconds, viseme_code) pairs for animatronic mouth movement."
    )
    listen: bool = Field(False, description="If True, the listener activates immediately after this clip finishes — used for get_response() flows.")

    @model_validator(mode='after')
    def check_uri_or_binary_data(self):
        if not self.uri and not self.binary_data and not self.filename:
            raise ValueError("Either 'uri', 'filename', or 'binary_data' must be provided.")
        return self


class MycroftAudioQueueMessage(OpenVoiceOSMessage):
    """Queue a pre-rendered audio clip for TTS playback.

    Emitted by TTS plugins after synthesis; handled by `ovos-audio` which
    plays clips sequentially. Use `mycroft.audio.play_sound` for immediate
    (non-queued) playback.
    """
    message_type: str = "mycroft.audio.queue"
    data: MycroftAudioQueueData


class MycroftAudioPlaySoundData(BaseModel):
    """Payload for immediate (non-queued) sound playback."""
    uri: Optional[str] = Field(None, description="URI of the audio file to play immediately (interrupts any current speech).")
    binary_data: Optional[str] = Field(None, description="Hex-encoded raw audio bytes (alternative to uri).")
    audio_ext: Optional[str] = Field(None, description="File extension hinting the codec when binary_data is used.")
    force_unmute: bool = Field(False, description="If True, temporarily unmute the system even if muted before playing.")

    @model_validator(mode='after')
    def check_uri_or_binary_data(self):
        if not self.uri and not self.binary_data:
            raise ValueError("Either 'uri' or 'binary_data' must be provided.")
        return self


class MycroftAudioPlaySoundMessage(OpenVoiceOSMessage):
    """Play a sound file immediately, bypassing the TTS speech queue.

    Emitted by skills or core for UI sounds (error chimes, confirmations, etc.).
    Handled by `ovos-audio`. A response is sent when playback completes.
    """
    message_type: str = "mycroft.audio.play_sound"
    data: MycroftAudioPlaySoundData


class MycroftAudioPlaySoundResponseMessage(OpenVoiceOSMessage):
    """Acknowledge that a `mycroft.audio.play_sound` clip finished playing.

    Emitted by `ovos-audio` once the sound file playback completes.
    """
    message_type: str = "mycroft.audio.play_sound.response"
    data: Dict[str, Any] = Field(default_factory=dict)


class SpeakData(BaseModel):
    """Payload for a TTS speak request."""
    utterance: str = Field(..., description="The text to synthesize and speak aloud.")
    expect_response: bool = Field(False, description="If True, the listener activates after speaking — used for yes/no questions and get_response() calls.")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata forwarded from the skill, e.g. {'skill': skill_id, 'dialog': 'weather.say'}.")


class SpeakMessage(OpenVoiceOSMessage):
    """Request TTS to speak a text string aloud.

    The most common output message in OVOS. Emitted by skills via
    `self.speak()` or `self.speak_dialog()`; handled by `ovos-audio` which
    routes to the active TTS plugin. If `expect_response` is True the listener
    re-activates after the utterance — enabling conversational flows.
    """
    message_type: str = "speak"
    data: SpeakData


class SpeakB64AudioData(BaseModel):
    """Request payload for `speak:b64_audio` — synthesize to raw audio without playing it."""
    utterance: str = Field(..., description="The text to synthesize.")
    listen: bool = Field(False, description="Whether the listen flag should be set on the returned audio.")


class SpeakB64AudioMessage(OpenVoiceOSMessage):
    """Request TTS synthesis without playing it — returns raw audio as base64.

    Emitted by external integrations (e.g. OVOS-REST, satellite nodes) that
    need the audio bytes directly. The TTS plugin synthesizes the text and
    replies with `speak:b64_audio.response` containing the encoded audio.
    """
    message_type: str = "speak:b64_audio"
    data: SpeakB64AudioData


class SpeakB64AudioReplyData(BaseModel):
    """Synthesized audio returned in response to a `speak:b64_audio` request."""
    audio: str = Field(..., description="Base64-encoded audio bytes (format matches the TTS plugin output, typically WAV).")
    listen: bool = Field(..., description="Forwarded listen flag from the original request.")
    tts_id: str = Field(..., description="Identifier of the TTS plugin that performed the synthesis.")
    utterance: str = Field(..., description="The text that was synthesized (echo of the original request).")


class SpeakB64AudioResponseMessage(OpenVoiceOSMessage):
    """Return synthesized audio as base64 in response to `speak:b64_audio`.

    Emitted by the TTS plugin / `ovos-audio` when synthesis completes.
    The caller receives raw PCM/WAV bytes encoded as base64.
    """
    message_type: str = "speak:b64_audio.response"
    data: SpeakB64AudioReplyData


# --- Example Usage ---
