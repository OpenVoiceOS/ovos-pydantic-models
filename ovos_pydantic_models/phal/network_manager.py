from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


class OvosPhalNmScanMessage(OpenVoiceOSMessage):
    """Request the PHAL network manager plugin to scan for nearby WiFi networks.

    Emitted by the WiFi setup GUI or skills handling 'show available networks'
    voice commands. The network manager plugin performs a scan and replies
    with `ovos.phal.nm.scan.complete`.
    """
    message_type: str = "ovos.phal.nm.scan"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalNmScanCompleteData(BaseModel):
    """WiFi network scan results from the PHAL network manager plugin."""
    networks: List[Dict[str, Any]] = Field(default_factory=list, description="List of discovered network dicts.")


class OvosPhalNmScanCompleteMessage(OpenVoiceOSMessage):
    """Return the list of nearby WiFi networks discovered during a scan.

    Emitted by the PHAL network manager plugin in response to
    `ovos.phal.nm.scan`. Each entry in `networks` contains at minimum
    `ssid`, `bssid`, `signal_strength`, and `secured` fields. The WiFi
    setup GUI renders this as a selectable network list.
    """
    message_type: str = "ovos.phal.nm.scan.complete"
    data: OvosPhalNmScanCompleteData


class OvosPhalNmConnectData(BaseModel):
    """Payload for connecting to a specific WiFi network."""
    bssid: str = Field(..., description="BSSID (network identifier) to connect to.")
    password: Optional[str] = Field(None, description="WiFi password; None for open networks.")


class OvosPhalNmConnectMessage(OpenVoiceOSMessage):
    """Request the PHAL network manager to connect to a specific WiFi network.

    Emitted by the WiFi setup GUI when the user selects a network and
    enters a password. The network manager plugin attempts the connection
    and replies with `ovos.phal.nm.connection.successful` or
    `ovos.phal.nm.connection.failure`.
    """
    message_type: str = "ovos.phal.nm.connect"
    data: OvosPhalNmConnectData


class OvosPhalNmConnectOpenNetworkData(BaseModel):
    """Payload for connecting to an open (passwordless) WiFi network."""
    bssid: str = Field(..., description="BSSID of the open network to connect to.")


class OvosPhalNmConnectOpenNetworkMessage(OpenVoiceOSMessage):
    """Request the PHAL network manager to connect to an open WiFi network.

    Emitted by the WiFi setup GUI when the user selects a network with no
    security. Functionally equivalent to `OvosPhalNmConnectMessage` with
    `password=None` but uses a separate message type for clarity.
    """
    message_type: str = "ovos.phal.nm.connect.open.network"
    data: OvosPhalNmConnectOpenNetworkData


class OvosPhalNmConnectionSuccessfulData(BaseModel):
    """Payload confirming a successful WiFi connection."""
    bssid: str = Field(..., description="BSSID of the successfully connected network.")


class OvosPhalNmConnectionSuccessfulMessage(OpenVoiceOSMessage):
    """Signal that the device successfully connected to a WiFi network.

    Emitted by the PHAL network manager plugin after a connection attempt
    succeeds. The WiFi setup GUI advances to the next onboarding step;
    the connectivity plugin emits `mycroft.network.connected` shortly after.
    """
    message_type: str = "ovos.phal.nm.connection.successful"
    data: OvosPhalNmConnectionSuccessfulData


class OvosPhalNmConnectionFailureData(BaseModel):
    """Payload describing a failed WiFi connection attempt."""
    bssid: str = Field(..., description="BSSID that failed to connect.")
    error: str = Field(..., description="Error description.")


class OvosPhalNmConnectionFailureMessage(OpenVoiceOSMessage):
    """Signal that a WiFi connection attempt failed.

    Emitted by the PHAL network manager plugin when the connection could
    not be established (wrong password, network disappeared, DHCP timeout).
    The WiFi setup GUI shows an error and allows the user to retry.
    """
    message_type: str = "ovos.phal.nm.connection.failure"
    data: OvosPhalNmConnectionFailureData


class OvosPhalNmDisconnectMessage(OpenVoiceOSMessage):
    """Request the PHAL network manager to disconnect from the current WiFi network.

    Emitted by the settings GUI or skills. The network manager plugin
    disassociates from the current AP; the connectivity plugin emits
    `mycroft.network.disconnected` shortly after.
    """
    message_type: str = "ovos.phal.nm.disconnect"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalNmDisconnectionSuccessfulMessage(OpenVoiceOSMessage):
    """Signal that the device successfully disconnected from its WiFi network.

    Emitted by the PHAL network manager plugin after a clean disconnect.
    The settings GUI updates its connected/disconnected state.
    """
    message_type: str = "ovos.phal.nm.disconnection.successful"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalNmDisconnectionFailureData(BaseModel):
    """Payload describing a failed disconnect attempt."""
    error: str = Field(..., description="Error description.")


class OvosPhalNmDisconnectionFailureMessage(OpenVoiceOSMessage):
    """Signal that the device failed to disconnect from its WiFi network.

    Emitted by the PHAL network manager plugin when a disconnect request
    could not be completed. The settings GUI shows an error.
    """
    message_type: str = "ovos.phal.nm.disconnection.failure"
    data: OvosPhalNmDisconnectionFailureData


class OvosPhalNmForgetData(BaseModel):
    """Payload for removing a saved WiFi network credential."""
    bssid: str = Field(..., description="BSSID to forget/remove from saved networks.")


class OvosPhalNmForgetMessage(OpenVoiceOSMessage):
    """Request the PHAL network manager to delete a saved WiFi network.

    Emitted by the settings GUI when the user removes a saved network. The
    network manager plugin deletes the stored credentials and replies with
    `ovos.phal.nm.forget.successful` or `ovos.phal.nm.forget.failure`.
    """
    message_type: str = "ovos.phal.nm.forget"
    data: OvosPhalNmForgetData


class OvosPhalNmForgetSuccessfulData(BaseModel):
    """Payload confirming that a saved network was deleted."""
    bssid: str = Field(..., description="BSSID that was forgotten.")


class OvosPhalNmForgetSuccessfulMessage(OpenVoiceOSMessage):
    """Signal that a saved WiFi network credential was successfully deleted.

    Emitted by the PHAL network manager plugin after removing the saved
    network. The settings GUI removes the entry from the saved networks list.
    """
    message_type: str = "ovos.phal.nm.forget.successful"
    data: OvosPhalNmForgetSuccessfulData


class OvosPhalNmForgetFailureData(BaseModel):
    """Payload describing a failure to delete a saved WiFi network."""
    bssid: str = Field(..., description="BSSID that failed to be forgotten.")
    error: str = Field(..., description="Error description.")


class OvosPhalNmForgetFailureMessage(OpenVoiceOSMessage):
    """Signal that the PHAL network manager failed to delete a saved WiFi network.

    Emitted when the underlying OS network manager returns an error for a
    forget request. The settings GUI shows an error message.
    """
    message_type: str = "ovos.phal.nm.forget.failure"
    data: OvosPhalNmForgetFailureData


class OvosPhalNmIsConnectedMessage(OpenVoiceOSMessage):
    """Signal that the device currently has an active network connection.

    Emitted by the PHAL network manager plugin in response to a
    `ovos.phal.nm.get.connected` query when a connection is active.
    """
    message_type: str = "ovos.phal.nm.is.connected"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalNmIsNotConnectedMessage(OpenVoiceOSMessage):
    """Signal that the device does not have an active network connection.

    Emitted by the PHAL network manager plugin in response to a
    `ovos.phal.nm.get.connected` query when no connection is active.
    """
    message_type: str = "ovos.phal.nm.is.not.connected"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalNmGetConnectedMessage(OpenVoiceOSMessage):
    """Query the PHAL network manager for the current connection state.

    Emitted by skills or components that need to check connectivity before
    performing network operations. The plugin replies with either
    `ovos.phal.nm.is.connected` or `ovos.phal.nm.is.not.connected`.
    """
    message_type: str = "ovos.phal.nm.get.connected"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalNmReconnectMessage(OpenVoiceOSMessage):
    """Request the PHAL network manager to reconnect to the last known network.

    Emitted after a temporary disconnection or resume from sleep. The
    network manager plugin attempts to re-establish the most recently
    active connection without requiring user interaction.
    """
    message_type: str = "ovos.phal.nm.reconnect"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalNmSetBackendData(BaseModel):
    """Payload for selecting which OS network management backend to use."""
    backend: str = Field(..., description="Network manager backend to use (e.g. 'NetworkManager', 'iwconfig').")


class OvosPhalNmSetBackendMessage(OpenVoiceOSMessage):
    """Configure which OS network management backend the PHAL plugin uses.

    Emitted during PHAL plugin configuration or system setup. Different
    Linux distributions use different network managers (NetworkManager,
    wpa_supplicant, iwconfig). This message selects the correct one for
    the target platform.
    """
    message_type: str = "ovos.phal.nm.set.backend"
    data: OvosPhalNmSetBackendData


class OvosPhalNmBackendNotSupportedMessage(OpenVoiceOSMessage):
    """Signal that the requested network management backend is not available.

    Emitted by the PHAL network manager plugin when the backend specified
    in `ovos.phal.nm.set.backend` is not installed or not supported on the
    current platform. The settings GUI should present fallback options.
    """
    message_type: str = "ovos.phal.nm.backend.not.supported"
    data: Dict[str, Any] = Field(default_factory=dict)
