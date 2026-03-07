from enum import Enum
from typing import Dict, Any, List, Optional, Union, Tuple

from pydantic import BaseModel, Field, ConfigDict

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


# --- Listener Service Message Models ---


class ListeningState(str, Enum):
    """Lifecycle state of the voice-activity / wake-word loop in `ovos-dinkum-listener`."""
    SLEEPING = "sleeping"             # Wake-word detection paused (sleep mode)
    WAITING_FOR_WAKEWORD = "waiting_for_wakeword"  # Idle; listening for wake word
    CONTINUOUS = "continuous"         # Always-on STT, no wake word required
    RECORDING = "recording"           # Actively recording user speech
    MUTED = "muted"                   # Microphone hardware-muted
    DISABLED = "disabled"             # Listener service disabled entirely


class RecognizerLoopB64TranscribeData(BaseModel):
    """Request payload for on-demand STT transcription of a base64 audio clip."""
    audio_b64: str = Field(..., description="Base64-encoded audio bytes to transcribe (WAV or raw PCM).")
    lang: Optional[str] = Field(None, description="BCP-47 language code for the audio, e.g. 'en-us'. Falls back to session/config default.")
    context: Optional[MessageContext] = Field(None, description="Message context to propagate into the response.")


class RecognizerLoopB64TranscribeMessage(OpenVoiceOSMessage):
    """Transcribe a base64-encoded audio clip via the STT plugin, without a microphone.

    Emitted by external integrations (REST API, satellite nodes) that have
    pre-recorded audio they need converted to text. The listener responds with
    `recognizer_loop:b64_transcribe.response`.
    """
    message_type: str = "recognizer_loop:b64_transcribe"
    data: RecognizerLoopB64TranscribeData


class RecognizerLoopB64TranscribeReplyData(BaseModel, extra='allow'):
    """STT transcription results returned for a `recognizer_loop:b64_transcribe` request."""
    transcriptions: List[Tuple[str, float]] = Field(
        ..., description="Ordered list of (transcript_text, confidence) pairs, best result first."
    )
    lang: str = Field(..., description="BCP-47 language code that was used for transcription.")


class RecognizerLoopB64TranscribeResponseMessage(OpenVoiceOSMessage):
    """Return STT transcription results for a `recognizer_loop:b64_transcribe` request.

    Emitted by `ovos-dinkum-listener` after the STT plugin processes the audio.
    """
    message_type: str = "recognizer_loop:b64_transcribe.response"
    data: RecognizerLoopB64TranscribeReplyData


class RecognizerLoopB64AudioData(BaseModel):
    """Request payload for injecting a base64 audio clip into the full listener pipeline."""
    audio_b64: str = Field(..., description="Base64-encoded audio bytes to process through the full STT + intent pipeline.")
    lang: Optional[str] = Field(None, description="BCP-47 language code for the audio.")
    context: Optional[MessageContext] = Field(None, description="Message context to attach to the resulting utterance message.")


class RecognizerLoopB64AudioMessage(OpenVoiceOSMessage):
    """Inject a base64 audio clip into the listener as if it were microphone input.

    Unlike `b64_transcribe`, this runs the full pipeline: STT → wake-word
    filtering → `recognizer_loop:utterance`. Useful for testing and satellites.
    """
    message_type: str = "recognizer_loop:b64_audio"
    data: RecognizerLoopB64AudioData


class RecognizerLoopB64AudioResponseMessage(OpenVoiceOSMessage):
    """Acknowledgement that a `recognizer_loop:b64_audio` clip was accepted for processing."""
    message_type: str = "recognizer_loop:b64_audio.response"
    data: Dict[str, Any] = Field(default_factory=dict)


class RecognizerLoopRecordStopMessage(OpenVoiceOSMessage):
    """Force the listener to stop the current recording pass immediately.

    Emitted by any component that needs to cancel speech capture; the listener
    abandons the current VAD window and returns to wake-word standby.
    """
    message_type: str = "recognizer_loop:record_stop"
    data: Dict[str, Any] = Field(default_factory=dict)


class RecognizerLoopStateSetData(BaseModel):
    """Request payload for changing the listener's operating state."""
    state: ListeningState = Field(..., description="The desired listener state to transition to.")


class RecognizerLoopStateSetMessage(OpenVoiceOSMessage):
    """Command the listener to change its operating state.

    Emitted by the intent service, skills, or PHAL plugins. For example,
    skills use this to enter sleep mode or continuous listening. The listener
    transitions to the requested `ListeningState` immediately.
    """
    message_type: str = "recognizer_loop:state.set"
    data: RecognizerLoopStateSetData


class RecognizerLoopStateGetMessage(OpenVoiceOSMessage):
    """Query the listener's current operating state.

    Any component may send this; the listener replies with
    `recognizer_loop:state.get.response`.
    """
    message_type: str = "recognizer_loop:state.get"
    data: Dict[str, Any] = Field(default_factory=dict)


class RecognizerLoopStateGetReplyData(BaseModel):
    """Current listener state returned in reply to a state query."""
    state: ListeningState = Field(..., description="The listener's current operating state.")


class RecognizerLoopStateResponseMessage(OpenVoiceOSMessage):
    """Report the listener's current state in response to `recognizer_loop:state.get`.

    Emitted by `ovos-dinkum-listener`.
    """
    message_type: str = "recognizer_loop:state.get.response"
    data: RecognizerLoopStateGetReplyData


class RecognizerLoopRecordBeginMessage(OpenVoiceOSMessage):
    """Signal that the listener has started recording user speech.

    Broadcast by `ovos-dinkum-listener` when VAD detects speech onset after
    wake-word detection. Skills and GUI can react (e.g. show a listening indicator).
    """
    message_type: str = "recognizer_loop:record_begin"
    data: Dict[str, Any] = Field(default_factory=dict)


class RecognizerLoopRecordEndMessage(OpenVoiceOSMessage):
    """Signal that the listener has finished recording the user's utterance.

    Broadcast by `ovos-dinkum-listener` when VAD detects end-of-speech. STT
    processing begins after this event.
    """
    message_type: str = "recognizer_loop:record_end"
    data: Dict[str, Any] = Field(default_factory=dict)


class RecognizerLoopSpeechRecognitionUnknownMessage(OpenVoiceOSMessage):
    """Signal that STT failed to produce a transcription for the recorded audio.

    Emitted by `ovos-dinkum-listener` when the STT plugin returns an empty or
    unintelligible result. This typically triggers a "I didn't catch that" response.
    """
    message_type: str = "recognizer_loop:speech.recognition.unknown"
    data: Dict[str, Any] = Field(default_factory=dict)


class RecognizerLoopWakeWordData(BaseModel):
    """Shared payload for all hotword/wake-word detection events."""
    key_phrase: str = Field(..., description="The text of the detected wake/hot/stop word, e.g. 'hey mycroft'.")
    utterance: Optional[str] = Field(
        None, description="Full transcription of the detected segment if the WW engine also provides STT."
    )
    sound: Optional[Union[str, List[str]]] = Field(
        None, description="Sound file path(s) to play on detection (e.g. a ding sound)."
    )
    listen: Optional[bool] = Field(
        None, description="If True, the listener should activate STT after this hotword."
    )
    event: Optional[str] = Field(
        None, description="Custom bus event to emit instead of the standard wakeword event."
    )
    filename: Optional[str] = Field(
        None, description="File URI where the captured hotword audio was saved, if recording is enabled."
    )
    engine: str = Field(..., description="MD5 hash of the hotword plugin module used for detection.")
    time: str = Field(..., description="Unix timestamp (milliseconds) when the hotword was detected.")
    sessionId: str = Field(..., description="Session ID associated with this detection event.")
    accountId: str = Field(..., description="Account ID, typically 'Anon' for local deployments.")
    model: str = Field(..., description="Hash or path of the hotword model file that triggered the detection.")


class RecognizerLoopWakeWordMessage(OpenVoiceOSMessage):
    """Signal that the primary wake word was detected.

    Emitted by `ovos-dinkum-listener` when the configured wake-word model
    fires. Triggers the STT recording phase. Subscribers include the GUI
    (listening indicator) and skills that track wake-word events.
    """
    message_type: str = "recognizer_loop:wakeword"
    data: RecognizerLoopWakeWordData


class RecognizerLoopHotwordMessage(OpenVoiceOSMessage):
    """Signal that any hotword (not necessarily the primary wake word) was detected.

    A broader variant of `recognizer_loop:wakeword` — covers all hotword
    types including secondary wake words and custom hotwords. Used for
    telemetry and multi-trigger scenarios.
    """
    message_type: str = "recognizer_loop:hotword"
    data: RecognizerLoopWakeWordData


class RecognizerLoopStopwordMessage(OpenVoiceOSMessage):
    """Signal that a stop word was detected, interrupting the current listen cycle.

    Emitted by `ovos-dinkum-listener` when a word configured as a stop
    trigger fires (e.g. 'stop', 'cancel'). The listener aborts recording.
    """
    message_type: str = "recognizer_loop:stopword"
    data: RecognizerLoopWakeWordData


class RecognizerLoopWakeupWordMessage(OpenVoiceOSMessage):
    """Signal that a wake-up word was detected while in sleep mode.

    Emitted when the device is sleeping and a configured wake-up phrase
    brings it back to active listening. Different from the primary wake word.
    """
    message_type: str = "recognizer_loop:wakeupword"
    data: RecognizerLoopWakeWordData


class RecognizerLoopUtteranceData(BaseModel, extra='allow'):
    """STT result payload delivered to the intent pipeline."""
    utterances: List[str] = Field(..., description="Ordered list of transcription candidates, best first. The intent service evaluates all of them.")
    lang: str = Field(..., description="BCP-47 language code of the utterance, e.g. 'en-us'.")
    filename: Optional[str] = Field(None, description="File URI of the saved audio recording, if audio logging is enabled.")
    transcriptions: Optional[List[Tuple[str, float]]] = Field(
        None, description="Full (transcript, confidence) pairs from the STT engine, if available."
    )
    transcription: Optional[str] = Field(
        None, description="Deprecated — use `utterances[0]` instead."
    )
    recording_name: Optional[str] = Field(
        None, description="Label for the recording file when audio saving is enabled."
    )


class RecognizerLoopUtteranceMessage(OpenVoiceOSMessage):
    """Deliver a speech-to-text result into the intent pipeline.

    The most important input message in OVOS. Emitted by
    `ovos-dinkum-listener` after a successful STT pass, or injected directly
    by tests and satellites. The intent service parses `utterances` through all
    configured pipeline plugins (adapt, padatious, converse, fallback) and
    dispatches to the matching skill.
    """
    message_type: str = "recognizer_loop:utterance"
    data: RecognizerLoopUtteranceData


class RecognizerLoopSleepMessage(OpenVoiceOSMessage):
    """Put the listener into sleep mode — stop responding to the primary wake word.

    Emitted by the sleep skill or directly by components that need to suppress
    wake-word activation (e.g. during audio playback). The listener will only
    respond to the configured wake-up word until woken.
    """
    message_type: str = "recognizer_loop:sleep"
    data: Dict[str, Any] = Field(default_factory=dict)


class RecognizerLoopWakeUpMessage(OpenVoiceOSMessage):
    """Wake the listener from sleep mode, resuming normal wake-word detection.

    Emitted by the sleep skill or any component after calling sleep. Mirrors
    `recognizer_loop:sleep`.
    """
    message_type: str = "recognizer_loop:wake_up"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftAwokenMessage(OpenVoiceOSMessage):
    """Broadcast that the device has woken from sleep mode.

    Emitted by `ovos-dinkum-listener` after successfully transitioning from
    sleep state to wake-word standby. Skills can react (e.g. play a chime,
    show a GUI indicator).
    """
    message_type: str = "mycroft.awoken"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftMicMuteMessage(OpenVoiceOSMessage):
    """Hardware-mute the microphone — no audio reaches the VAD or STT.

    Emitted by privacy-sensitive contexts (e.g. mute button press, PHAL plugin).
    The listener stops processing all audio until unmuted.
    """
    message_type: str = "mycroft.mic.mute"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftMicUnmuteMessage(OpenVoiceOSMessage):
    """Unmute the microphone after a `mycroft.mic.mute`.

    Emitted by the same contexts that issued the mute. Resumes full listener
    operation including wake-word detection.
    """
    message_type: str = "mycroft.mic.unmute"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftMicMuteToggleMessage(OpenVoiceOSMessage):
    """Toggle the microphone mute state (mute if active, unmute if muted).

    Convenient single-message alternative to separate mute/unmute commands,
    typically bound to a hardware button or GUI control.
    """
    message_type: str = "mycroft.mic.mute.toggle"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftMicGetStatusMessage(OpenVoiceOSMessage):
    """Query whether the microphone and listener are running or muted.

    Any component may send this; `ovos-dinkum-listener` responds with
    `mycroft.mic.get_status.response`.
    """
    message_type: str = "mycroft.mic.get_status"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftMicGetStatusReplyData(BaseModel):
    """Microphone status returned in reply to `mycroft.mic.get_status`."""
    status: str = Field(..., description="Current listener/mic state string, e.g. 'running', 'muted', 'sleeping'.")


class MycroftMicGetStatusResponseMessage(OpenVoiceOSMessage):
    """Report the microphone / listener status in response to `mycroft.mic.get_status`.

    Emitted by `ovos-dinkum-listener`.
    """
    message_type: str = "mycroft.mic.get_status.response"
    data: MycroftMicGetStatusReplyData


class MycroftMicListenMessage(OpenVoiceOSMessage):
    """Force the listener into active recording mode immediately, without a wake word.

    Emitted by skills (via `self.get_response()`) or external triggers that
    need to capture user speech on demand. Equivalent to manually pressing
    a listen button.
    """
    message_type: str = "mycroft.mic.listen"
    data: Dict[str, Any] = Field(default_factory=dict)


# --- Example Usage ---
