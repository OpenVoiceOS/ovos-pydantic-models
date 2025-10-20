from enum import Enum
from typing import Dict, Any, List, Optional, Union, Tuple

from pydantic import BaseModel, Field, ConfigDict

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


# --- Listener Service Message Models ---


class ListeningState(str, Enum):
    """
    Represents the current state of the listener's voice loop.
    """
    SLEEPING = "sleeping"
    WAITING_FOR_WAKEWORD = "waiting_for_wakeword"
    CONTINUOUS = "continuous"
    RECORDING = "recording"
    MUTED = "muted"
    DISABLED = "disabled"


class RecognizerLoopB64TranscribeData(BaseModel):
    """Data for `recognizer_loop:b64_transcribe` message."""
    audio_b64: str = Field(..., description="Base64 encoded audio data to transcribe.")
    lang: Optional[str] = Field(None, description="Language of the audio for transcription.")
    context: Optional[MessageContext] = Field(None, description="Original message context.")


class RecognizerLoopB64TranscribeMessage(OpenVoiceOSMessage):
    """Message for `recognizer_loop:b64_transcribe`."""
    message_type: str = "recognizer_loop:b64_transcribe"
    data: RecognizerLoopB64TranscribeData


class RecognizerLoopB64TranscribeReplyData(BaseModel, extra='allow'):
    """Data for `recognizer_loop:b64_transcribe` response."""
    transcriptions: List[Tuple[str, float]] = Field(
        ..., description="List of (transcription, confidence) tuples."
    )
    lang: str = Field(..., description="Language of the transcription.")
    # Allow arbitrary extra data from STT context


class RecognizerLoopB64TranscribeResponseMessage(OpenVoiceOSMessage):
    """Response message for `recognizer_loop:b64_transcribe`."""
    message_type: str = "recognizer_loop:b64_transcribe.response"
    data: RecognizerLoopB64TranscribeReplyData


class RecognizerLoopB64AudioData(BaseModel):
    """Data for `recognizer_loop:b64_audio` message."""
    audio_b64: str = Field(..., description="Base64 encoded audio data for processing/playback.")
    lang: Optional[str] = Field(None, description="Language of the audio.")
    context: Optional[MessageContext] = Field(None, description="Original message context.")


class RecognizerLoopB64AudioMessage(OpenVoiceOSMessage):
    """Message for `recognizer_loop:b64_audio`."""
    message_type: str = "recognizer_loop:b64_audio"
    data: RecognizerLoopB64AudioData


class RecognizerLoopB64AudioResponseMessage(OpenVoiceOSMessage):
    """Response message for `recognizer_loop:b64_audio`."""
    message_type: str = "recognizer_loop:b64_audio.response"
    data: Dict[str, Any] = Field(default_factory=dict, description="Generic response data for b64 audio processing.")


class RecognizerLoopRecordStopMessage(OpenVoiceOSMessage):
    """Message for `recognizer_loop:record_stop`."""
    message_type: str = "recognizer_loop:record_stop"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for record stop command.")


class RecognizerLoopStateSetData(BaseModel):
    """Data for `recognizer_loop:state.set` message."""
    state: ListeningState = Field(..., description="The desired listening state.")


class RecognizerLoopStateSetMessage(OpenVoiceOSMessage):
    """Message for `recognizer_loop:state.set`."""
    message_type: str = "recognizer_loop:state.set"
    data: RecognizerLoopStateSetData


class RecognizerLoopStateGetMessage(OpenVoiceOSMessage):
    """Message for `recognizer_loop:state.get` (request for listener state)."""
    message_type: str = "recognizer_loop:state.get"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for state request.")


class RecognizerLoopStateGetReplyData(BaseModel):
    """Data for `recognizer_loop:state.get` response."""
    state: ListeningState = Field(..., description="Current listening state of the voice loop.")


class RecognizerLoopStateResponseMessage(OpenVoiceOSMessage):
    """Response message for `recognizer_loop:state.get`."""
    message_type: str = "recognizer_loop:state.get.response"
    data: RecognizerLoopStateGetReplyData


class RecognizerLoopRecordBeginMessage(OpenVoiceOSMessage):
    """Message for `recognizer_loop:record_begin`."""
    message_type: str = "recognizer_loop:record_begin"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for record begin event.")


class RecognizerLoopRecordEndMessage(OpenVoiceOSMessage):
    """Message for `recognizer_loop:record_end`."""
    message_type: str = "recognizer_loop:record_end"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for record end event.")


class RecognizerLoopSpeechRecognitionUnknownMessage(OpenVoiceOSMessage):
    """Message for `recognizer_loop:speech.recognition.unknown`."""
    message_type: str = "recognizer_loop:speech.recognition.unknown"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for unknown speech event.")


class RecognizerLoopWakeWordData(BaseModel):
    """Data for `recognizer_loop:wakeword`, `hotword`, `stopword`, `wakeupword` messages."""
    key_phrase: str = Field(..., description="The detected key phrase.")
    utterance: Optional[str] = Field(
        None, description="The transcribed utterance if hotword includes transcription."
    )
    sound: Optional[Union[str, List[str]]] = Field(
        None, description="Path to a sound file (or list of paths) to play on detection."
    )
    listen: Optional[bool] = Field(
        None, description="True if the system should enter listening mode after detection."
    )
    event: Optional[str] = Field(
        None, description="Custom event type to emit instead of default hotword events."
    )
    filename: Optional[str] = Field(
        None, description="URI to the saved audio file of the detected hotword."
    )
    engine: str = Field(..., description="MD5 hash of the hotword engine module.")
    time: str = Field(..., description="Timestamp of the hotword detection (milliseconds since epoch).")
    sessionId: str = Field(..., description="Session ID associated with the detection.")
    accountId: str = Field(..., description="Account ID associated with the detection (e.g., 'Anon').")
    model: str = Field(..., description="Model hash or identifier used for detection.")


class RecognizerLoopWakeWordMessage(OpenVoiceOSMessage):
    """Message for `recognizer_loop:wakeword`."""
    message_type: str = "recognizer_loop:wakeword"
    data: RecognizerLoopWakeWordData


class RecognizerLoopHotwordMessage(OpenVoiceOSMessage):
    """Message for `recognizer_loop:hotword`."""
    message_type: str = "recognizer_loop:hotword"
    data: RecognizerLoopWakeWordData


class RecognizerLoopStopwordMessage(OpenVoiceOSMessage):
    """Message for `recognizer_loop:stopword`."""
    message_type: str = "recognizer_loop:stopword"
    data: RecognizerLoopWakeWordData


class RecognizerLoopWakeupWordMessage(OpenVoiceOSMessage):
    """Message for `recognizer_loop:wakeupword`."""
    message_type: str = "recognizer_loop:wakeupword"
    data: RecognizerLoopWakeWordData


class RecognizerLoopUtteranceData(BaseModel, extra='allow'):
    """Data for `recognizer_loop:utterance` message."""
    utterances: List[str] = Field(..., description="List of transcribed utterances.")
    lang: str = Field(..., description="Language of the utterance (e.g., 'en-us').")
    # Additional fields from _stt_audio callback
    filename: Optional[str] = Field(None, description="URI to the saved audio file of the utterance.")
    transcriptions: Optional[List[Tuple[str, float]]] = Field(
        None, description="List of (transcription, confidence) tuples."
    )
    transcription: Optional[str] = Field(
        None, description="Deprecated: Main transcription string."
    )
    recording_name: Optional[str] = Field(
        None, description="Name of the recording if saved (for _save_recording)."
    )


class RecognizerLoopUtteranceMessage(OpenVoiceOSMessage):
    """Message for `recognizer_loop:utterance`."""
    message_type: str = "recognizer_loop:utterance"
    data: RecognizerLoopUtteranceData


class RecognizerLoopSleepMessage(OpenVoiceOSMessage):
    """Message for `recognizer_loop:sleep`."""
    message_type: str = "recognizer_loop:sleep"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for sleep command.")


class RecognizerLoopWakeUpMessage(OpenVoiceOSMessage):
    """Message for `recognizer_loop:wake_up`."""
    message_type: str = "recognizer_loop:wake_up"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for wake up command.")


class MycroftAwokenMessage(OpenVoiceOSMessage):
    """Message for `mycroft.awoken`."""
    message_type: str = "mycroft.awoken"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for awoken event.")


class MycroftMicMuteMessage(OpenVoiceOSMessage):
    """Message for `mycroft.mic.mute`."""
    message_type: str = "mycroft.mic.mute"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for mic mute command.")


class MycroftMicUnmuteMessage(OpenVoiceOSMessage):
    """Message for `mycroft.mic.unmute`."""
    message_type: str = "mycroft.mic.unmute"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for mic unmute command.")


class MycroftMicMuteToggleMessage(OpenVoiceOSMessage):
    """Message for `mycroft.mic.mute.toggle`."""
    message_type: str = "mycroft.mic.mute.toggle"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for mic mute toggle command.")


class MycroftMicGetStatusMessage(OpenVoiceOSMessage):
    """Message for `mycroft.mic.get_status` (request for mic status)."""
    message_type: str = "mycroft.mic.get_status"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for status request.")


class MycroftMicGetStatusReplyData(BaseModel):
    """Data for `mycroft.mic.get_status` response."""
    status: str = Field(..., description="Current status of the microphone/listener (e.g., 'running', 'muted').")


class MycroftMicGetStatusResponseMessage(OpenVoiceOSMessage):
    """Response message for `mycroft.mic.get_status`."""
    message_type: str = "mycroft.mic.get_status.response"
    data: MycroftMicGetStatusReplyData


class MycroftMicListenMessage(OpenVoiceOSMessage):
    """Message for `mycroft.mic.listen`."""
    message_type: str = "mycroft.mic.listen"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for mic listen command.")


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Demonstrating Listener Message Models ---")

    # Create a dummy session and context for demonstration
    dummy_session = Session(session_id="test-session-123", lang="en-us")
    dummy_context = MessageContext(source="playback_thread", session=dummy_session)

    # Example: mycroft.mic.listen
    mic_listen_message = MycroftMicListenMessage(context=dummy_context)
    print(f"\nMic Listen Message:\n{mic_listen_message.model_dump_json(indent=2)}")

    # Example: Mycroft Awoken
    awoken_message = MycroftAwokenMessage(context=dummy_context)
    print(f"\nMycroft Awoken Message:\n{awoken_message.model_dump_json(indent=2)}")

    # Example: Recognizer Loop Wake Word
    ww_data = RecognizerLoopWakeWordData(
        key_phrase="hey mycroft",
        utterance="hey mycroft play some music",
        sound="file:///path/to/sound.wav",
        listen=True,
        engine="mock-ww-engine-hash",
        time="1678886400000",
        sessionId="test-listener-session-789",
        accountId="Anon",
        model="0"
    )
    ww_message = RecognizerLoopWakeWordMessage(data=ww_data, context=dummy_context)
    print(f"\nRecognizer Loop Wake Word Message:\n{ww_message.model_dump_json(indent=2)}")

    # Example: Recognizer Loop Utterance
    utt_data = RecognizerLoopUtteranceData(
        utterances=["play some music", "play music"],
        lang="en-us",
        filename="file:///tmp/utterance_audio.wav",
        transcriptions=[("play some music", 0.95), ("play music", 0.9)]
    )
    utt_message = RecognizerLoopUtteranceMessage(data=utt_data, context=dummy_context)
    print(f"\nRecognizer Loop Utterance Message:\n{utt_message.model_dump_json(indent=2)}")

    # Example: Mycroft Mic Mute
    mute_message = MycroftMicMuteMessage(context=dummy_context)
    print(f"\nMycroft Mic Mute Message:\n{mute_message.model_dump_json(indent=2)}")

    # Example: Recognizer Loop State Set
    state_set_data = RecognizerLoopStateSetData(state=ListeningState.RECORDING)
    state_set_message = RecognizerLoopStateSetMessage(data=state_set_data, context=dummy_context)
    print(f"\nRecognizer Loop State Set Message:\n{state_set_message.model_dump_json(indent=2)}")
