from typing import Dict, Any, List, Optional, Tuple

from pydantic import BaseModel, Field, model_validator

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


# --- OVOS Audio Service Message Models ---

class MycroftSpeechStopMessage(OpenVoiceOSMessage):
    """Message for `mycroft.stop` and `mycroft.audio.speech.stop`."""
    message_type: str = "mycroft.audio.speech.stop"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for stop command.")


class MycroftAudioSpeakStatusMessage(OpenVoiceOSMessage):
    """Message for `mycroft.audio.speak.status` (request for speaking status)."""
    message_type: str = "mycroft.audio.speak.status"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for status request.")


class MycroftAudioIsSpeakingData(BaseModel):
    """Data for `mycroft.audio.is_speaking` message (reply to status request)."""
    speaking: bool = Field(..., description="True if the system is currently speaking, False otherwise.")


class MycroftAudioIsSpeakingMessage(OpenVoiceOSMessage):
    """Message for `mycroft.audio.is_speaking` (reply to status request)."""
    message_type: str = "mycroft.audio.is_speaking"
    data: MycroftAudioIsSpeakingData


VisemeList = List[Tuple[float, str]]


class MycroftAudioQueueData(BaseModel):
    """Data for `mycroft.audio.queue` message."""
    uri: Optional[str] = Field(None, description="URI of the audio file to queue.")
    filename: Optional[str] = Field(None, description="Deprecated: Use 'uri' instead. Filename of the audio to queue.")
    binary_data: Optional[str] = Field(None, description="Hex-encoded binary audio data to queue.")
    audio_ext: Optional[str] = Field(None, description="File extension for binary_data (e.g., 'wav', 'mp3').")
    viseme: Optional[VisemeList] = Field(
        None, description="List of (timestamp, viseme) tuples for mouth movements."
    )
    listen: bool = Field(False, description="True if a user response is expected after playback.")

    @model_validator(mode='after')
    def check_uri_or_binary_data(self):
        if not self.uri and not self.binary_data and not self.filename:
            raise ValueError("Either 'uri', 'filename', or 'binary_data' must be provided.")
        return self


class MycroftAudioQueueMessage(OpenVoiceOSMessage):
    """Message for `mycroft.audio.queue`."""
    message_type: str = "mycroft.audio.queue"
    data: MycroftAudioQueueData


class MycroftAudioPlaySoundData(BaseModel):
    """Data for `mycroft.audio.play_sound` message."""
    uri: Optional[str] = Field(None, description="URI of the audio file to play immediately.")
    binary_data: Optional[str] = Field(None, description="Hex-encoded binary audio data to play immediately.")
    audio_ext: Optional[str] = Field(None, description="File extension for binary_data (e.g., 'wav', 'mp3').")
    force_unmute: bool = Field(False, description="If True, ensures volume is not zero/muted before playing.")

    @model_validator(mode='after')
    def check_uri_or_binary_data(self):
        if not self.uri and not self.binary_data:
            raise ValueError("Either 'uri' or 'binary_data' must be provided.")
        return self


class MycroftAudioPlaySoundMessage(OpenVoiceOSMessage):
    """Message for `mycroft.audio.play_sound`."""
    message_type: str = "mycroft.audio.play_sound"
    data: MycroftAudioPlaySoundData


class MycroftAudioPlaySoundResponseMessage(OpenVoiceOSMessage):
    """Response message for `mycroft.audio.play_sound`."""
    message_type: str = "mycroft.audio.play_sound.response"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for play sound response.")


class SpeakData(BaseModel):
    """Data for `speak` message."""
    utterance: str = Field(..., description="The text to be spoken.")
    expect_response: bool = Field(False, description="True if a user response is expected after speaking.")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Optional metadata, e.g., {'skill': 'skill_id'}.")


class SpeakMessage(OpenVoiceOSMessage):
    """Message for `speak`."""
    message_type: str = "speak"
    data: SpeakData


class SpeakB64AudioData(BaseModel):
    """Data for `speak:b64_audio` message (request for base64 audio)."""
    utterance: str = Field(..., description="The text to be synthesized.")
    listen: bool = Field(False, description="True if a user response is expected after synthesis.")


class SpeakB64AudioMessage(OpenVoiceOSMessage):
    """Message for `speak:b64_audio` (request for base64 audio)."""
    message_type: str = "speak:b64_audio"
    data: SpeakB64AudioData


class SpeakB64AudioReplyData(BaseModel):
    """Data for `speak:b64_audio` response."""
    audio: str = Field(..., description="Base64 encoded audio data.")
    listen: bool = Field(..., description="True if a user response is expected after playback (from original request).")
    tts_id: str = Field(..., description="ID of the TTS plugin used for synthesis.")
    utterance: str = Field(..., description="The original utterance that was synthesized.")


class SpeakB64AudioResponseMessage(OpenVoiceOSMessage):
    """Response message for `speak:b64_audio`."""
    message_type: str = "speak:b64_audio.response"
    data: SpeakB64AudioReplyData


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Demonstrating OVOS Audio Service Message Models ---")

    # Create a dummy session and context for demonstration
    dummy_session = Session(session_id="test-audio-session-456", lang="en-us")
    dummy_context = MessageContext(source="ovos_audio_service", session=dummy_session)

    # Example: Speak message
    speak_data = SpeakData(utterance="Hello, this is a test.", expect_response=True)
    speak_message = SpeakMessage(data=speak_data, context=dummy_context)
    print(f"\nSpeak Message:\n{speak_message.model_dump_json(indent=2)}")

    # Example: Queue audio message with URI
    queue_audio_data_uri = MycroftAudioQueueData(uri="file:///tmp/test.wav", listen=False)
    queue_audio_message_uri = MycroftAudioQueueMessage(data=queue_audio_data_uri, context=dummy_context)
    print(f"\nQueue Audio Message (URI):\n{queue_audio_message_uri.model_dump_json(indent=2)}")

    # Example: Queue audio message with binary data
    # (Using a dummy hex string for demonstration)
    dummy_hex_audio = "4f564f5320417564696f2054657374"  # "OVOS Audio Test" in hex
    queue_audio_data_binary = MycroftAudioQueueData(binary_data=dummy_hex_audio, audio_ext="wav",
                                                    viseme=[(0.1, "A"), (0.5, "B")])
    queue_audio_message_binary = MycroftAudioQueueMessage(data=queue_audio_data_binary, context=dummy_context)
    print(f"\nQueue Audio Message (Binary):\n{queue_audio_message_binary.model_dump_json(indent=2)}")

    # Example: Play sound immediately
    play_sound_data = MycroftAudioPlaySoundData(uri="file:///opt/mycroft/sounds/ding.wav", force_unmute=True)
    play_sound_message = MycroftAudioPlaySoundMessage(data=play_sound_data, context=dummy_context)
    print(f"\nPlay Sound Message:\n{play_sound_message.model_dump_json(indent=2)}")
