from enum import IntEnum
from typing import Dict, Any

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


# Enum for MediaState, as defined in the original code
class MediaState(IntEnum):
    """
    Represents the status of media playback.
    (Based on Qt's QMediaPlayer.MediaStatus enum)
    """
    UNKNOWN = 0
    NO_MEDIA = 1
    LOADING_MEDIA = 2
    LOADED_MEDIA = 3
    STALLED_MEDIA = 4
    BUFFERING_MEDIA = 5
    BUFFERED_MEDIA = 6
    END_OF_MEDIA = 7
    INVALID_MEDIA = 8


class OvosCommonPlayMediaStateData(BaseModel):
    """Data for `ovos.common_play.media.state` message."""
    state: MediaState = Field(..., description="The current media state.")


class OvosCommonPlayMediaStateMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_play.media.state`."""
    message_type: str = "ovos.common_play.media.state"
    data: OvosCommonPlayMediaStateData


class OvosCommonPlayCorkMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_play.cork`."""
    message_type: str = "ovos.common_play.cork"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for cork command.")


class OvosCommonPlayDuckMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_play.duck`."""
    message_type: str = "ovos.common_play.duck"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for duck command.")


class OvosCommonPlayUncorkMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_play.uncork`."""
    message_type: str = "ovos.common_play.uncork"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for uncork command.")


class OvosCommonPlayUnduckMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_play.unduck`."""
    message_type: str = "ovos.common_play.unduck"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for unduck command.")


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Demonstrating OCP Message Models ---")

    # Example: ovos.common_play.media.state
    media_state_data = OvosCommonPlayMediaStateData(state=MediaState.INVALID_MEDIA)
    media_state_message = OvosCommonPlayMediaStateMessage(data=media_state_data)
    print(f"\nMedia State Message (INVALID_MEDIA):\n{media_state_message.model_dump_json(indent=2)}")

    media_state_data_buffering = OvosCommonPlayMediaStateData(state=MediaState.BUFFERING_MEDIA)
    media_state_message_buffering = OvosCommonPlayMediaStateMessage(data=media_state_data_buffering)
    print(f"\nMedia State Message (BUFFERING_MEDIA):\n{media_state_message_buffering.model_dump_json(indent=2)}")

    # Create a dummy session and context for demonstration
    dummy_session = Session(session_id="test-session-123", lang="en-us")
    dummy_context = MessageContext(source="playback_thread", session=dummy_session)

    # Example: ovos.common_play.cork
    cork_message = OvosCommonPlayCorkMessage(context=dummy_context)
    print(f"\nCork Message:\n{cork_message.model_dump_json(indent=2)}")

    # Example: ovos.common_play.duck
    duck_message = OvosCommonPlayDuckMessage(context=dummy_context)
    print(f"\nDuck Message:\n{duck_message.model_dump_json(indent=2)}")

    # Example: ovos.common_play.uncork
    uncork_message = OvosCommonPlayUncorkMessage(context=dummy_context)
    print(f"\nUncork Message:\n{uncork_message.model_dump_json(indent=2)}")

    # Example: ovos.common_play.unduck
    unduck_message = OvosCommonPlayUnduckMessage(context=dummy_context)
    print(f"\nUnduck Message:\n{unduck_message.model_dump_json(indent=2)}")
