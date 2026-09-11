from typing import Dict, Any

from pydantic import Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


class OvosAlertsCancelAlarmMessage(OpenVoiceOSMessage):
    """Request the alerts skill to cancel a pending alarm.

    Carries alarm identification in ``data`` (e.g. ``alarm_name`` or index).
    """
    message_type: str = "ovos.alerts.cancel_alarm"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosAlertsDismissNotificationMessage(OpenVoiceOSMessage):
    """Dismiss a pending notification from the alerts skill.

    Used by GUI components to signal the user has acknowledged a notification.
    """
    message_type: str = "ovos.alerts.dismiss_notification"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosAlertsGetAlertsMessage(OpenVoiceOSMessage):
    """Request the current list of all active alerts (alarms, timers, reminders).

    Emitted by GUI widgets and bus tools to query the alerts skill state.
    """
    message_type: str = "ovos.alerts.get_alerts"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosAlertsSnoozeAlarmMessage(OpenVoiceOSMessage):
    """Snooze a currently firing alarm for a configured duration.

    Emitted by GUI buttons or voice commands when the user asks to snooze.
    """
    message_type: str = "ovos.alerts.snooze_alarm"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosGuiShowActiveAlarmsMessage(OpenVoiceOSMessage):
    """Instruct the GUI to display the active alarms list.

    Emitted by the alerts skill to bring the alarms screen to the foreground.
    """
    message_type: str = "ovos.gui.show.active.alarms"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosGuiShowActiveTimersMessage(OpenVoiceOSMessage):
    """Instruct the GUI to display the active timers list.

    Emitted by the alerts skill to bring the timers screen to the foreground.
    """
    message_type: str = "ovos.gui.show.active.timers"
    data: Dict[str, Any] = Field(default_factory=dict)
