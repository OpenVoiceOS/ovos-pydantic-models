from typing import Dict, Any, Optional

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


class SystemRebootMessage(OpenVoiceOSMessage):
    """Request the device to reboot.

    Emitted by skills handling 'reboot' voice commands or by the system
    PHAL plugin in response to update requirements. The system PHAL plugin
    performs a graceful shutdown of OVOS services before rebooting the OS.
    """
    message_type: str = "system.reboot"
    data: Dict[str, Any] = Field(default_factory=dict)


class SystemRebootStartMessage(OpenVoiceOSMessage):
    """Signal that the reboot sequence has begun.

    Emitted by the system PHAL plugin just before issuing the OS reboot
    command. Skills and GUI components can subscribe to show a 'rebooting...'
    message or play a farewell sound.
    """
    message_type: str = "system.reboot.start"
    data: Dict[str, Any] = Field(default_factory=dict)


class SystemShutdownMessage(OpenVoiceOSMessage):
    """Request the device to shut down.

    Emitted by skills handling 'shut down' or 'power off' voice commands.
    The system PHAL plugin performs a graceful shutdown of OVOS services
    before issuing the OS shutdown command.
    """
    message_type: str = "system.shutdown"
    data: Dict[str, Any] = Field(default_factory=dict)


class SystemShutdownStartMessage(OpenVoiceOSMessage):
    """Signal that the shutdown sequence has begun.

    Emitted by the system PHAL plugin just before issuing the OS shutdown
    command. Skills and GUI components can subscribe to show a 'shutting
    down...' message or play a farewell sound.
    """
    message_type: str = "system.shutdown.start"
    data: Dict[str, Any] = Field(default_factory=dict)


class SystemFactoryResetMessage(OpenVoiceOSMessage):
    """Request a full factory reset of the device.

    Emitted by admin tools or the factory reset skill after user
    confirmation. The system PHAL plugin broadcasts `system.factory.reset.ping`
    to all registered components so they can clean up their data before
    the reset proceeds.
    """
    message_type: str = "system.factory.reset"
    data: Dict[str, Any] = Field(default_factory=dict)


class SystemFactoryResetPingMessage(OpenVoiceOSMessage):
    """Poll all registered components before executing a factory reset.

    Emitted by the system PHAL plugin to give registered skills and plugins
    the opportunity to clean up their data. Components that registered via
    `system.factory.reset.register` receive their registered callback message.
    """
    message_type: str = "system.factory.reset.ping"
    data: Dict[str, Any] = Field(default_factory=dict)


class SystemFactoryResetRegisterData(BaseModel):
    """Payload for a component to register a factory-reset cleanup callback."""
    skill_id: str = Field(..., description="ID of the skill/plugin registering for factory reset notification.")
    callback_msg: str = Field(..., description="Message type to send to this skill during factory reset.")


class SystemFactoryResetRegisterMessage(OpenVoiceOSMessage):
    """Register a factory-reset cleanup callback for a skill or plugin.

    Emitted by skills during `initialize()` if they store persistent state
    that must be wiped on factory reset (e.g. user profiles, cached data).
    The system PHAL plugin calls the registered `callback_msg` when a factory
    reset is triggered, giving the skill time to clean up before the reset.
    """
    message_type: str = "system.factory.reset.register"
    data: SystemFactoryResetRegisterData


class SystemFactoryResetPhalMessage(OpenVoiceOSMessage):
    """Tell the PHAL system plugin to perform its portion of the factory reset.

    Emitted by the system PHAL plugin after all registered component callbacks
    have been called. The PHAL plugin wipes its own configuration, credentials,
    and cached state.
    """
    message_type: str = "system.factory.reset.phal"
    data: Dict[str, Any] = Field(default_factory=dict)


class SystemFactoryResetPhalCompleteMessage(OpenVoiceOSMessage):
    """Signal that the PHAL plugin has finished its factory reset cleanup.

    Emitted by the system PHAL plugin after clearing its data. The factory
    reset orchestrator can proceed to reboot the device once all
    `system.factory.reset.phal.complete` events have been received.
    """
    message_type: str = "system.factory.reset.phal.complete"
    data: Dict[str, Any] = Field(default_factory=dict)


class SystemSshEnableMessage(OpenVoiceOSMessage):
    """Request the system to enable SSH remote access.

    Emitted by skills handling 'enable SSH' voice commands or the settings
    GUI. The system PHAL plugin enables the SSH daemon and confirms via
    `system.ssh.enabled`.
    """
    message_type: str = "system.ssh.enable"
    data: Dict[str, Any] = Field(default_factory=dict)


class SystemSshEnabledMessage(OpenVoiceOSMessage):
    """Signal that SSH access has been enabled on the device.

    Emitted by the system PHAL plugin after the SSH daemon starts
    successfully. Skills and GUI components can update their settings
    display in response.
    """
    message_type: str = "system.ssh.enabled"
    data: Dict[str, Any] = Field(default_factory=dict)


class SystemSshDisableMessage(OpenVoiceOSMessage):
    """Request the system to disable SSH remote access.

    Emitted by skills handling 'disable SSH' voice commands or the settings
    GUI. The system PHAL plugin stops the SSH daemon and confirms via
    `system.ssh.disabled`.
    """
    message_type: str = "system.ssh.disable"
    data: Dict[str, Any] = Field(default_factory=dict)


class SystemSshDisabledMessage(OpenVoiceOSMessage):
    """Signal that SSH access has been disabled on the device.

    Emitted by the system PHAL plugin after the SSH daemon stops. Skills
    and GUI components can update their settings display in response.
    """
    message_type: str = "system.ssh.disabled"
    data: Dict[str, Any] = Field(default_factory=dict)


class SystemSshStatusData(BaseModel):
    """Current SSH service state from the system PHAL plugin."""
    enabled: bool = Field(..., description="True if SSH is currently enabled.")


class SystemSshStatusMessage(OpenVoiceOSMessage):
    """Report the current SSH service state.

    Emitted by the system PHAL plugin in response to a status query, or
    proactively when the SSH state changes. GUI settings panels subscribe
    to keep their SSH toggle synchronized.
    """
    message_type: str = "system.ssh.status"
    data: SystemSshStatusData


class SystemMycroftServiceRestartMessage(OpenVoiceOSMessage):
    """Request a restart of the OVOS core service (not the OS).

    Emitted by skills, admin tools, or the updater after installing a new
    version. The system PHAL plugin gracefully stops and restarts only the
    OVOS systemd service without rebooting the hardware.
    """
    message_type: str = "system.mycroft.service.restart"
    data: Dict[str, Any] = Field(default_factory=dict)


class SystemMycroftServiceRestartStartMessage(OpenVoiceOSMessage):
    """Signal that the OVOS service restart has been initiated.

    Emitted by the system PHAL plugin just before stopping the OVOS service.
    Components can subscribe to perform cleanup before the process exits.
    """
    message_type: str = "system.mycroft.service.restart.start"
    data: Dict[str, Any] = Field(default_factory=dict)


class SystemClockSyncedMessage(OpenVoiceOSMessage):
    """Signal that the system clock has been synchronized (e.g. via NTP).

    Emitted by the system PHAL plugin after a successful time synchronization.
    Skills that schedule events or display the current time should refresh
    after receiving this event, as the clock may have jumped significantly.
    """
    message_type: str = "system.clock.synced"
    data: Dict[str, Any] = Field(default_factory=dict)


class SystemConfigureLanguageData(BaseModel):
    """Payload for requesting a system-level language change."""
    lang: str = Field(..., description="BCP-47 language code to configure.")


class SystemConfigureLanguageMessage(OpenVoiceOSMessage):
    """Request a system-level language configuration change.

    Emitted by the settings GUI or onboarding flow when the user selects
    a new language. The system PHAL plugin updates the OS locale, reconfigures
    TTS/STT defaults, and may trigger skill re-initialization. Replies with
    `system.configure.language.complete`.
    """
    message_type: str = "system.configure.language"
    data: SystemConfigureLanguageData


class SystemConfigureLanguageCompleteData(BaseModel):
    """Payload confirming which language was configured."""
    lang: str = Field(..., description="BCP-47 language code that was configured.")


class SystemConfigureLanguageCompleteMessage(OpenVoiceOSMessage):
    """Signal that the system language configuration change has completed.

    Emitted by the system PHAL plugin after all language-related changes
    (locale, TTS voice, STT model) have been applied. The GUI can dismiss
    the 'changing language...' overlay.
    """
    message_type: str = "system.configure.language.complete"
    data: SystemConfigureLanguageCompleteData


class SystemDisplayHomescreenMessage(OpenVoiceOSMessage):
    """Tell the system to display the homescreen.

    Emitted by the system PHAL plugin or shell during startup or after a
    factory reset to ensure the homescreen is visible. Also used by skills
    that want to return the UI to idle state without going through the
    homescreen manager.
    """
    message_type: str = "system.display.homescreen"
    data: Dict[str, Any] = Field(default_factory=dict)


class SystemWifiSetupMessage(OpenVoiceOSMessage):
    """Request the system to launch the WiFi setup / onboarding flow.

    Emitted during first-boot onboarding or when the user has no network
    connection. The WiFi setup PHAL plugin responds by activating its
    access-point mode and presenting the captive portal GUI.
    """
    message_type: str = "system.wifi.setup"
    data: Dict[str, Any] = Field(default_factory=dict)


class SystemFactoryResetStartMessage(OpenVoiceOSMessage):
    """Signal that a factory reset sequence has begun.

    Emitted by the system PHAL plugin immediately after receiving
    `system.factory.reset`, before any data is wiped. Components that
    need to perform cleanup or show a 'resetting…' UI can subscribe here.
    The data payload is forwarded from the original reset request and may
    contain flags such as `wipe_cache`, `wipe_data`, `wipe_configs`.
    """
    message_type: str = "system.factory.reset.start"
    data: Dict[str, Any] = Field(default_factory=dict)


class SystemFactoryResetCompleteMessage(OpenVoiceOSMessage):
    """Signal that the factory reset process has finished.

    Emitted by the system PHAL plugin after all data has been wiped and
    all registered component callbacks have completed. The device will
    typically reboot immediately after this event unless `reboot=False`
    was passed in the original reset request.
    """
    message_type: str = "system.factory.reset.complete"
    data: Dict[str, Any] = Field(default_factory=dict)
