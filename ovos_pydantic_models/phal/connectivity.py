from typing import Dict, Any, Optional

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


class OvosPhalInternetCheckMessage(OpenVoiceOSMessage):
    """Message for `ovos.PHAL.internet_check` (request for internet/network status)."""
    message_type: str = "ovos.PHAL.internet_check"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for status request.")


class OvosPhalInternetCheckReplyData(BaseModel):
    """Data for `ovos.PHAL.internet_check` response."""
    internet_connected: Optional[bool] = Field(None, description="True if internet is connected.")
    network_connected: Optional[bool] = Field(None, description="True if network is connected (local or internet).")


class OvosPhalInternetCheckResponseMessage(OpenVoiceOSMessage):
    """Response message for `ovos.PHAL.internet_check`."""
    message_type: str = "ovos.PHAL.internet_check.response"
    data: OvosPhalInternetCheckReplyData


class MycroftNetworkDisconnectedMessage(OpenVoiceOSMessage):
    """Message for `mycroft.network.disconnected`."""
    message_type: str = "mycroft.network.disconnected"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for network disconnected event.")


class MycroftInternetDisconnectedMessage(OpenVoiceOSMessage):
    """Message for `mycroft.internet.disconnected`."""
    message_type: str = "mycroft.internet.disconnected"
    data: Dict[str, Any] = Field(default_factory=dict,
                                 description="Empty data payload for internet disconnected event.")


class MycroftNetworkConnectedMessage(OpenVoiceOSMessage):
    """Message for `mycroft.network.connected`."""
    message_type: str = "mycroft.network.connected"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for network connected event.")


class MycroftInternetConnectedMessage(OpenVoiceOSMessage):
    """Message for `mycroft.internet.connected`."""
    message_type: str = "mycroft.internet.connected"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for internet connected event.")


# --- Example Usage ---
if __name__ == "__main__":
    # Create a dummy session and context for demonstration
    dummy_session = Session(session_id="test-skill-manager-session-101", lang="en-us")
    dummy_context = MessageContext(source="skill_manager", session=dummy_session)

    # Example: Network connected
    network_connected_message = MycroftNetworkConnectedMessage(context=dummy_context)
    print(f"\nNetwork Connected Message:\n{network_connected_message.model_dump_json(indent=2)}")
