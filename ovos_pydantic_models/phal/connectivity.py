from typing import Dict, Any, Optional

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


class OvosPhalInternetCheckMessage(OpenVoiceOSMessage):
    """Query the PHAL connectivity plugin for the current network/internet status.

    Emitted by skills or core services that need to know whether internet
    and/or local network access is available before attempting network
    operations. The connectivity plugin replies with
    `ovos.PHAL.internet_check.response`.
    """
    message_type: str = "ovos.PHAL.internet_check"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalInternetCheckReplyData(BaseModel):
    """Network and internet connectivity status from the PHAL plugin."""
    internet_connected: Optional[bool] = Field(None, description="True if internet is connected.")
    network_connected: Optional[bool] = Field(None, description="True if network is connected (local or internet).")


class OvosPhalInternetCheckResponseMessage(OpenVoiceOSMessage):
    """Return the current network and internet connectivity status.

    Emitted by the PHAL connectivity plugin in response to
    `ovos.PHAL.internet_check`. `internet_connected` may be False while
    `network_connected` is True (e.g. captive portal, VPN-only network).
    """
    message_type: str = "ovos.PHAL.internet_check.response"
    data: OvosPhalInternetCheckReplyData


class MycroftNetworkDisconnectedMessage(OpenVoiceOSMessage):
    """Signal that the local network connection has been lost.

    Emitted by the PHAL connectivity plugin when the device loses its
    connection to the local network (Ethernet/WiFi disconnect). Skills
    that require LAN access should handle this gracefully.
    """
    message_type: str = "mycroft.network.disconnected"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftInternetDisconnectedMessage(OpenVoiceOSMessage):
    """Signal that internet access has been lost (but LAN may still be available).

    Emitted by the PHAL connectivity plugin when internet reachability
    tests fail. Network-dependent skills should degrade gracefully. This
    event is distinct from `mycroft.network.disconnected`.
    """
    message_type: str = "mycroft.internet.disconnected"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftNetworkConnectedMessage(OpenVoiceOSMessage):
    """Signal that the device has connected to a local network.

    Emitted by the PHAL connectivity plugin when a new network interface
    becomes active. This may not indicate internet access — wait for
    `mycroft.internet.connected` for confirmed internet reachability.
    """
    message_type: str = "mycroft.network.connected"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftInternetConnectedMessage(OpenVoiceOSMessage):
    """Signal that internet access has been restored.

    Emitted by the PHAL connectivity plugin after a successful internet
    reachability test. Skills that deferred operations due to
    `mycroft.internet.disconnected` can now retry.
    """
    message_type: str = "mycroft.internet.connected"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftInternetStateData(BaseModel):
    """Current internet reachability state."""
    connected: bool = Field(..., description="True if internet is reachable.")


class MycroftInternetStateMessage(OpenVoiceOSMessage):
    """Broadcast the current internet connectivity state.

    Emitted by the PHAL connectivity plugin on every state change.
    Unlike the dedicated connected/disconnected events, this carries
    the explicit boolean state — useful for initializing components
    that missed earlier events.
    """
    message_type: str = "mycroft.internet.state"
    data: MycroftInternetStateData


class MycroftInternetIsReadyMessage(OpenVoiceOSMessage):
    """Query whether internet connectivity is currently available.

    Emitted by services that need to check internet state synchronously
    without waiting for the next state-change event. The PHAL connectivity
    plugin responds with the current state.
    """
    message_type: str = "mycroft.internet.is_ready"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftNetworkStateData(BaseModel):
    """Current local network reachability state."""
    connected: bool = Field(..., description="True if local network is reachable.")


class MycroftNetworkStateMessage(OpenVoiceOSMessage):
    """Broadcast the current local network connectivity state.

    Emitted by the PHAL connectivity plugin on every local network state
    change. Carries the explicit boolean state for components that missed
    earlier connected/disconnected events.
    """
    message_type: str = "mycroft.network.state"
    data: MycroftNetworkStateData


class MycroftPairedMessage(OpenVoiceOSMessage):
    """Signal that the device has successfully paired with a backend service.

    Emitted by the PHAL pairing plugin after the OAuth/pairing flow
    completes successfully. Skills that require a backend account can
    proceed with API calls after receiving this event.
    """
    message_type: str = "mycroft.paired"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftNotPairedMessage(OpenVoiceOSMessage):
    """Signal that the device is not paired with any backend service.

    Emitted by the PHAL pairing plugin when pairing credentials are
    missing or expired. The pairing skill should launch its onboarding
    flow in response to this event.
    """
    message_type: str = "mycroft.not.paired"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftReadyCheckMessage(OpenVoiceOSMessage):
    """Query whether all OVOS core services have reported ready.

    Emitted by external tools or test harnesses that need to wait for
    the system to fully start before proceeding. The skill manager
    replies with `mycroft.ready` when all services are up.
    """
    message_type: str = "mycroft.ready.check"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPairingProcessCompletedMessage(OpenVoiceOSMessage):
    """Signal that the full OVOS pairing/onboarding process has completed.

    Emitted by the PHAL pairing plugin after all onboarding steps
    (network setup, backend pairing, etc.) are done. Skills and GUI
    components subscribe to show a welcome screen or enable backend features.
    """
    message_type: str = "ovos.pairing.process.completed"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPairingSetBackendData(BaseModel):
    """Payload for selecting the backend service to pair with."""
    backend: str = Field(..., description="Backend identifier to use (e.g. 'selene', 'local').")


class OvosPairingSetBackendMessage(OpenVoiceOSMessage):
    """Select which backend service to use for device pairing.

    Emitted during the onboarding flow when the user picks a backend
    (Selene, local backend, etc.). The PHAL pairing plugin configures
    itself and initiates the pairing handshake with the chosen service.
    """
    message_type: str = "ovos.pairing.set.backend"
    data: OvosPairingSetBackendData
