from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


class OvosPhalWifiPluginAliveMessage(OpenVoiceOSMessage):
    """Signal that the OVOS WiFi setup PHAL plugin is running and ready.

    **Deprecated** — `ovos-PHAL-plugin-wifi-setup` is archived.
    These messages are documented for historical reference only.

    Emitted by the WiFi setup PHAL plugin on startup and periodically as a
    heartbeat. Components that depend on the WiFi setup flow (such as the
    onboarding GUI or the connectivity plugin) can subscribe to verify that
    the plugin is loaded before sending WiFi setup messages. Without this
    plugin, the `ovos.phal.wifi.plugin.*` message namespace is inert.
    """
    message_type: str = "ovos.phal.wifi.plugin.alive"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalWifiPluginRegisterClientData(BaseModel):
    """Payload for registering a client with the WiFi setup PHAL plugin."""
    client_id: str = Field(..., description="Unique client ID to register with the WiFi setup plugin.")


class OvosPhalWifiPluginRegisterClientMessage(OpenVoiceOSMessage):
    """Register a client with the OVOS WiFi setup PHAL plugin.

    Emitted by GUI pages or onboarding flow components that need to participate
    in the WiFi setup process. The WiFi setup plugin tracks registered clients
    and notifies them of setup state changes. Only the active client (set via
    `ovos.phal.wifi.plugin.set.active.client`) receives setup prompts and
    result notifications. Replies with `ovos.phal.wifi.plugin.client.registered`
    on success or `ovos.phal.wifi.plugin.client.registration.failure` on error.
    """
    message_type: str = "ovos.phal.wifi.plugin.register.client"
    data: OvosPhalWifiPluginRegisterClientData


class OvosPhalWifiPluginClientRegisteredData(BaseModel):
    """Confirmation that a client was successfully registered with the WiFi setup plugin."""
    client_id: str = Field(..., description="The client ID that was registered.")


class OvosPhalWifiPluginClientRegisteredMessage(OpenVoiceOSMessage):
    """Confirm that a client was successfully registered with the WiFi setup PHAL plugin.

    Emitted by the WiFi setup plugin in response to
    `ovos.phal.wifi.plugin.register.client`. The client should store its
    `client_id` and use it for all subsequent WiFi setup plugin interactions
    (set active, deregister, select, etc.).
    """
    message_type: str = "ovos.phal.wifi.plugin.client.registered"
    data: OvosPhalWifiPluginClientRegisteredData


class OvosPhalWifiPluginClientRegistrationFailureData(BaseModel):
    """Payload describing a failed client registration with the WiFi setup plugin."""
    client_id: str = Field(..., description="The client ID that failed to register.")
    error: str = Field(..., description="Error description.")


class OvosPhalWifiPluginClientRegistrationFailureMessage(OpenVoiceOSMessage):
    """Signal that a client failed to register with the WiFi setup PHAL plugin.

    Emitted by the WiFi setup plugin when `ovos.phal.wifi.plugin.register.client`
    cannot be processed — for example, if the `client_id` is already in use or
    the plugin is in an error state. The registering component should log the
    error and may retry registration.
    """
    message_type: str = "ovos.phal.wifi.plugin.client.registration.failure"
    data: OvosPhalWifiPluginClientRegistrationFailureData


class OvosPhalWifiPluginDeregisterClientData(BaseModel):
    """Payload for removing a client registration from the WiFi setup PHAL plugin."""
    client_id: str = Field(..., description="Client ID to deregister.")


class OvosPhalWifiPluginDeregisterClientMessage(OpenVoiceOSMessage):
    """Deregister a client from the OVOS WiFi setup PHAL plugin.

    Emitted by GUI pages or components when they are closed or no longer
    participating in the WiFi setup flow. The plugin removes the client from
    its registry and stops sending it setup notifications. If the deregistered
    client was the active client, the plugin reverts to having no active client
    until another is set. Replies with
    `ovos.phal.wifi.plugin.client.deregistered`.
    """
    message_type: str = "ovos.phal.wifi.plugin.deregister.client"
    data: OvosPhalWifiPluginDeregisterClientData


class OvosPhalWifiPluginClientDeregisteredData(BaseModel):
    """Confirmation that a client was successfully deregistered from the WiFi setup plugin."""
    client_id: str = Field(..., description="The client ID that was deregistered.")


class OvosPhalWifiPluginClientDeregisteredMessage(OpenVoiceOSMessage):
    """Confirm that a client was successfully deregistered from the WiFi setup PHAL plugin.

    Emitted by the WiFi setup plugin in response to
    `ovos.phal.wifi.plugin.deregister.client`. After receiving this, the
    client will no longer receive WiFi setup events or result notifications
    from the plugin.
    """
    message_type: str = "ovos.phal.wifi.plugin.client.deregistered"
    data: OvosPhalWifiPluginClientDeregisteredData


class OvosPhalWifiPluginSetActiveClientData(BaseModel):
    """Payload for designating a specific registered client as the active WiFi setup recipient."""
    client_id: str = Field(..., description="Client ID to make active.")


class OvosPhalWifiPluginSetActiveClientMessage(OpenVoiceOSMessage):
    """Designate a registered client as the active recipient of WiFi setup events.

    Emitted by the onboarding orchestrator or GUI shell when a specific
    client should receive WiFi setup prompts, scan results, and connection
    outcomes. Only one client can be active at a time. The WiFi setup plugin
    routes all setup result messages to the active client. This is used when
    multiple GUI components are registered but only one is currently visible
    and should handle the WiFi setup interaction.
    """
    message_type: str = "ovos.phal.wifi.plugin.set.active.client"
    data: OvosPhalWifiPluginSetActiveClientData


class OvosPhalWifiPluginRemoveActiveClientData(BaseModel):
    """Payload for removing a client from the active slot in the WiFi setup plugin."""
    client_id: str = Field(..., description="Client ID to remove from active slot.")


class OvosPhalWifiPluginRemoveActiveClientMessage(OpenVoiceOSMessage):
    """Remove a client from the active slot in the WiFi setup PHAL plugin.

    Emitted by the onboarding orchestrator or GUI shell when the currently
    active client is closing or being replaced. The WiFi setup plugin stops
    routing setup messages to this client. If setup is in progress, the plugin
    may pause until a new active client is designated.
    """
    message_type: str = "ovos.phal.wifi.plugin.remove.active.client"
    data: OvosPhalWifiPluginRemoveActiveClientData


class OvosPhalWifiPluginGetRegisteredClientsMessage(OpenVoiceOSMessage):
    """Query the WiFi setup PHAL plugin for all currently registered clients.

    Emitted by management tools or the onboarding orchestrator to enumerate
    which components have registered to participate in the WiFi setup flow.
    The plugin replies with `ovos.phal.wifi.plugin.registered.clients`
    containing the list of registered client IDs.
    """
    message_type: str = "ovos.phal.wifi.plugin.get.registered.clients"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalWifiPluginRegisteredClientsData(BaseModel):
    """List of client IDs currently registered with the WiFi setup PHAL plugin."""
    clients: List[str] = Field(default_factory=list, description="List of registered client IDs.")


class OvosPhalWifiPluginRegisteredClientsMessage(OpenVoiceOSMessage):
    """Return the list of clients registered with the WiFi setup PHAL plugin.

    Emitted by the WiFi setup plugin in response to
    `ovos.phal.wifi.plugin.get.registered.clients`. Provides the current list
    of registered client IDs so the orchestrator can determine which components
    are participating in the setup flow and which should be made active.
    """
    message_type: str = "ovos.phal.wifi.plugin.registered.clients"
    data: OvosPhalWifiPluginRegisteredClientsData


class OvosPhalWifiPluginUserActivatedMessage(OpenVoiceOSMessage):
    """Signal that the user has manually triggered the WiFi setup flow.

    Emitted by the WiFi setup PHAL plugin or the settings GUI when the user
    explicitly requests to configure WiFi — for example, by tapping a "Setup WiFi"
    button or issuing a 'connect to WiFi' voice command. The onboarding
    orchestrator and GUI shell subscribe to launch the WiFi setup interface
    and register an active client.
    """
    message_type: str = "ovos.phal.wifi.plugin.user.activated"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalWifiPluginSetupLaunchedMessage(OpenVoiceOSMessage):
    """Signal that the WiFi setup GUI has been successfully launched.

    Emitted by the WiFi setup PHAL plugin after the GUI setup page is opened
    and an active client is registered. Components that were waiting for setup
    to begin (e.g. network scan triggers) can proceed once they receive this.
    """
    message_type: str = "ovos.phal.wifi.plugin.setup.launched"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalWifiPluginSetupFailedData(BaseModel):
    """Payload describing a WiFi setup launch or connection failure."""
    error: str = Field(..., description="Error description.")


class OvosPhalWifiPluginSetupFailedMessage(OpenVoiceOSMessage):
    """Signal that the WiFi setup flow failed to complete.

    Emitted by the WiFi setup PHAL plugin when the setup GUI could not be
    launched, or when a critical error occurs during the WiFi configuration
    process (e.g. network manager unavailable, AP mode failed to start).
    The `error` field contains a human-readable description. The onboarding
    orchestrator may retry or offer the user the option to skip setup.
    """
    message_type: str = "ovos.phal.wifi.plugin.setup.failed"
    data: OvosPhalWifiPluginSetupFailedData


class OvosPhalWifiPluginStopSetupEventMessage(OpenVoiceOSMessage):
    """Request the WiFi setup PHAL plugin to cancel the active setup flow.

    Emitted by the onboarding orchestrator or the user dismissing the setup
    GUI. The WiFi setup plugin stops any in-progress scan or connection
    attempt, tears down the AP mode if active, and deregisters all active
    clients. Use `ovos.phal.wifi.plugin.skip.setup` instead if the user
    explicitly wants to proceed without WiFi.
    """
    message_type: str = "ovos.phal.wifi.plugin.stop.setup.event"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalWifiPluginSkipSetupMessage(OpenVoiceOSMessage):
    """Signal that the user has chosen to skip WiFi setup and run offline.

    Emitted by the onboarding GUI when the user taps "Skip" or "Use offline"
    during the WiFi setup flow. The WiFi setup PHAL plugin records that setup
    was skipped and emits `ovos.phal.wifi.plugin.fully.offline` to inform
    other components. Onboarding continues without network configuration.
    """
    message_type: str = "ovos.phal.wifi.plugin.skip.setup"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalWifiPluginFullyOfflineMessage(OpenVoiceOSMessage):
    """Signal that the device is configured to run fully offline.

    Emitted by the WiFi setup PHAL plugin after the user skips WiFi setup
    or after repeated failed connection attempts result in an offline fallback.
    Skills and services that require network access should fall back to
    offline-capable alternatives or gracefully disable their online features
    upon receiving this message.
    """
    message_type: str = "ovos.phal.wifi.plugin.fully.offline"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalWifiPluginStatusData(BaseModel):
    """Current status string from the WiFi setup PHAL plugin."""
    status: str = Field(..., description="Current WiFi setup status string.")


class OvosPhalWifiPluginStatusMessage(OpenVoiceOSMessage):
    """Report the current status of the WiFi setup PHAL plugin.

    Emitted by the WiFi setup plugin when its internal state changes —
    for example, transitioning from 'idle' to 'scanning', 'connecting',
    'connected', or 'failed'. The settings GUI and onboarding flow
    subscribe to keep their status display synchronized with the plugin's
    actual state machine.
    """
    message_type: str = "ovos.phal.wifi.plugin.status"
    data: OvosPhalWifiPluginStatusData


class OvosPhalWifiPluginClientSelectData(BaseModel):
    """Payload for a client to signal which WiFi connection entry was selected by the user."""
    client_id: str = Field(..., description="Client ID selected by the user.")


class OvosPhalWifiPluginClientSelectMessage(OpenVoiceOSMessage):
    """Signal that the user has selected a client/provider in the WiFi setup GUI.

    Emitted by the WiFi setup GUI when the device has multiple WiFi setup
    client options and the user selects one — for example, choosing between
    different network manager backends or previously saved network profiles.
    The WiFi setup PHAL plugin records the selection and proceeds with the
    chosen client's setup flow.
    """
    message_type: str = "ovos.phal.wifi.plugin.client.select"
    data: OvosPhalWifiPluginClientSelectData


class OvosPhalWifiPluginClientSelectPageRemovedMessage(OpenVoiceOSMessage):
    """Signal that the client selection page has been dismissed from the GUI.

    Emitted by the WiFi setup GUI after the client selection page is closed —
    either because the user made a selection or navigated away. The WiFi setup
    PHAL plugin uses this to know it can proceed past the client selection step
    in its setup state machine.
    """
    message_type: str = "ovos.phal.wifi.plugin.client.select.page.removed"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalWifiPluginClientSetupFailureData(BaseModel):
    """Payload describing a per-client setup failure in the WiFi setup plugin."""
    client_id: str = Field(..., description="The client ID whose setup failed.")
    error: str = Field(..., description="Error description.")


class OvosPhalWifiPluginClientSetupFailureMessage(OpenVoiceOSMessage):
    """Signal that the setup flow for a specific WiFi setup client failed.

    Emitted by the WiFi setup PHAL plugin when a registered client encounters
    an error during its portion of the setup flow — for example, if a client's
    connection handler raises an exception or times out. The GUI shows an error
    and allows the user to retry with the same client or select a different one.
    """
    message_type: str = "ovos.phal.wifi.plugin.client.setup.failure"
    data: OvosPhalWifiPluginClientSetupFailureData


class OvosWifiSetupCompletedMessage(OpenVoiceOSMessage):
    """Signal that the WiFi setup flow has completed successfully.

    Emitted by the WiFi setup PHAL plugin after the device successfully
    connects to a WiFi network through the setup GUI. The onboarding
    orchestrator receives this to advance to the next onboarding step.
    The connectivity plugin will subsequently emit `mycroft.network.connected`
    and `mycroft.internet.connected` once the connection is verified.
    """
    message_type: str = "ovos.wifi.setup.completed"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalWifiScanMessage(OpenVoiceOSMessage):
    """Request the WiFi setup PHAL plugin to scan for available networks.

    Emitted by the WiFi setup GUI when the user opens the network list page
    or taps a "Refresh" button. The plugin delegates to the network manager
    plugin (`ovos.phal.nm.scan`) and presents results to the active GUI client.
    This is a convenience wrapper within the WiFi setup plugin context,
    distinct from the lower-level `ovos.phal.nm.scan` message sent directly
    to the network manager.
    """
    message_type: str = "ovos.phal.wifi.scan"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalWifiInfoData(BaseModel):
    """Current WiFi connection status from the WiFi setup PHAL plugin."""
    ssid: str = Field(..., description="Current WiFi SSID.")
    connected: bool = Field(..., description="True if currently connected.")


class OvosPhalWifiInfoMessage(OpenVoiceOSMessage):
    """Report the current WiFi connection status from the WiFi setup PHAL plugin.

    Emitted by the WiFi setup plugin in response to a status query or when
    the connection state changes. Contains the current network SSID and a
    boolean indicating whether the device is actively connected. The settings
    GUI uses this to display the current network name and connection indicator.
    """
    message_type: str = "ovos.phal.wifi.info"
    data: OvosPhalWifiInfoData
