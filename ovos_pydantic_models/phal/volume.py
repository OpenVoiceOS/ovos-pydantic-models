from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


# --- OVOS Audio Volume Message Models ---

class MycroftVolumeGetMessage(OpenVoiceOSMessage):
    """Message for `mycroft.volume.get`."""
    message_type: str = "mycroft.volume.get"
    data: Optional[Dict[str, Any]] = Field(default_factory=dict,
                                           description="Empty data payload for volume get request.")


class MycroftVolumeGetReplyData(BaseModel):
    """Data for `mycroft.volume.get` response."""
    percent: int = Field(..., description="Current volume percentage (0-100).")
    muted: bool = Field(..., description="True if the volume is currently muted, False otherwise.")


class MycroftVolumeGetResponseMessage(OpenVoiceOSMessage):
    """Response message for `mycroft.volume.get`."""
    message_type: str = "mycroft.volume.get.response"
    data: MycroftVolumeGetReplyData


class VolumeSetPercentData(BaseModel):
    """Data for `volume.set.percent` message."""
    percent: float = Field(..., ge=0.0, le=1.0, description="Volume percentage (0.0-1.0).")


class VolumeSetPercentMessage(OpenVoiceOSMessage):
    """Message for `volume.set.percent`."""
    message_type: str = "volume.set.percent"
    data: VolumeSetPercentData


class MycroftVolumeIncreaseDecreaseData(BaseModel):
    """Data for `mycroft.volume.increase` and `mycroft.volume.decrease` messages."""
    percent: float = Field(..., description="Percentage change in volume (e.g., 0.1 for 10%).")


class MycroftVolumeIncreaseMessage(OpenVoiceOSMessage):
    """Message for `mycroft.volume.increase`."""
    message_type: str = "mycroft.volume.increase"
    data: MycroftVolumeIncreaseDecreaseData


class MycroftVolumeDecreaseMessage(OpenVoiceOSMessage):
    """Message for `mycroft.volume.decrease`."""
    message_type: str = "mycroft.volume.decrease"
    data: MycroftVolumeIncreaseDecreaseData


class MycroftVolumeSetData(BaseModel):
    """Data for `mycroft.volume.set` message."""
    percent: Optional[int] = Field(None, ge=0, le=100, description="Volume percentage to set (0-100).")
    play_sound: bool = Field(False, description="Whether to play a sound when setting the volume.")
    # Other potential fields like 'volume' (deprecated) or 'direction' (up/down) could be added if needed.
    # For now, focusing on 'percent' as it's used directly.


class MycroftVolumeSetMessage(OpenVoiceOSMessage):
    """Message for `mycroft.volume.set`."""
    message_type: str = "mycroft.volume.set"
    data: MycroftVolumeSetData


class MycroftVolumeUnmuteMessage(OpenVoiceOSMessage):
    """Message for `mycroft.volume.unmute`."""
    message_type: str = "mycroft.volume.unmute"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for unmute command.")


class MycroftVolumeMuteMessage(OpenVoiceOSMessage):
    """Message for `mycroft.volume.mute`."""
    message_type: str = "mycroft.volume.mute"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for mute command.")


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Demonstrating OVOS Audio Service Message Models ---")

    # Create a dummy session and context for demonstration
    dummy_session = Session(session_id="test-audio-session-456", lang="en-us")
    dummy_context = MessageContext(source="ovos_audio_service", session=dummy_session)

    # Example: Mycroft Volume Get and Response
    volume_get_request = MycroftVolumeGetMessage(context=dummy_context)
    print(f"\nVolume Get Request:\n{volume_get_request.model_dump_json(indent=2)}")

    volume_get_reply_data = MycroftVolumeGetReplyData(percent=75, muted=False)
    volume_get_response = MycroftVolumeGetResponseMessage(data=volume_get_reply_data, context=dummy_context)
    print(f"\nVolume Get Response:\n{volume_get_response.model_dump_json(indent=2)}")

    # Example: Mycroft Volume Set
    volume_set_data = MycroftVolumeSetData(percent=50, play_sound=True)
    volume_set_message = MycroftVolumeSetMessage(data=volume_set_data, context=dummy_context)
    print(f"\nVolume Set Message:\n{volume_set_message.model_dump_json(indent=2)}")

    # Example: Volume Set Percent
    volume_set_percent_data = VolumeSetPercentData(percent=0.75)
    volume_set_percent_message = VolumeSetPercentMessage(data=volume_set_percent_data, context=dummy_context)
    print(f"\nVolume Set Percent Message:\n{volume_set_percent_message.model_dump_json(indent=2)}")

    # Example: Mycroft Volume Increase
    volume_increase_data = MycroftVolumeIncreaseDecreaseData(percent=0.1)
    volume_increase_message = MycroftVolumeIncreaseMessage(data=volume_increase_data, context=dummy_context)
    print(f"\nMycroft Volume Increase Message:\n{volume_increase_message.model_dump_json(indent=2)}")
