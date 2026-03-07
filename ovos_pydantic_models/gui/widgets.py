from typing import Dict, Any, Optional

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


class OvosWidgetsDisplayData(BaseModel):
    """Payload for showing a widget of a given type on the homescreen."""
    type: str = Field(..., description="Widget type identifier.")
    data: Dict[str, Any] = Field(default_factory=dict, description="Widget-specific display data.")


class OvosWidgetsDisplayMessage(OpenVoiceOSMessage):
    """Show a widget on the homescreen widget bar.

    Emitted by skills that provide homescreen widgets (timer, alarm, media,
    weather, etc.). The homescreen renders the widget in the widget area
    using the type-specific QML component.
    """
    message_type: str = "ovos.widgets.display"
    data: OvosWidgetsDisplayData


class OvosWidgetsRemoveData(BaseModel):
    """Payload for removing a widget by type from the homescreen."""
    type: str = Field(..., description="Widget type identifier to remove.")


class OvosWidgetsRemoveMessage(OpenVoiceOSMessage):
    """Remove a widget from the homescreen widget bar.

    Emitted by skills when they no longer have content to display in their
    widget (e.g. all timers have fired, media stopped). The homescreen
    removes the corresponding widget component.
    """
    message_type: str = "ovos.widgets.remove"
    data: OvosWidgetsRemoveData


class OvosWidgetsUpdateData(BaseModel):
    """Payload for updating a widget's displayed data."""
    type: str = Field(..., description="Widget type identifier.")
    data: Dict[str, Any] = Field(default_factory=dict, description="Updated widget data.")


class OvosWidgetsUpdateMessage(OpenVoiceOSMessage):
    """Update the data displayed by an existing homescreen widget.

    Emitted by skills when their widget's content changes without the
    widget being added or removed (e.g. timer countdown tick, media
    track change). The homescreen re-renders only the changed values.
    """
    message_type: str = "ovos.widgets.update"
    data: OvosWidgetsUpdateData


class OvosWidgetsTimerDisplayData(BaseModel):
    """Payload for displaying a timer widget on the homescreen."""
    timer: Dict[str, Any] = Field(..., description="Timer data dict.")


class OvosWidgetsTimerDisplayMessage(OpenVoiceOSMessage):
    """Show a timer widget on the homescreen.

    Emitted by the timer skill when a new timer is set. The homescreen
    displays a countdown widget. Multiple timers may be shown simultaneously
    if the homescreen supports it.
    """
    message_type: str = "ovos.widgets.timer.display"
    data: OvosWidgetsTimerDisplayData


class OvosWidgetsTimerUpdateData(BaseModel):
    """Payload for updating an existing timer widget's countdown."""
    timer: Dict[str, Any] = Field(..., description="Updated timer data dict.")


class OvosWidgetsTimerUpdateMessage(OpenVoiceOSMessage):
    """Update the countdown shown in an existing timer homescreen widget.

    Emitted by the timer skill on each tick. The homescreen widget updates
    the displayed remaining time without re-rendering the full widget.
    """
    message_type: str = "ovos.widgets.timer.update"
    data: OvosWidgetsTimerUpdateData


class OvosWidgetsTimerRemoveData(BaseModel):
    """Payload for removing a specific timer widget by ID."""
    timer_id: str = Field(..., description="ID of the timer to remove.")


class OvosWidgetsTimerRemoveMessage(OpenVoiceOSMessage):
    """Remove a specific timer's widget from the homescreen.

    Emitted by the timer skill when a timer fires or is cancelled. The
    homescreen removes the matching countdown widget. If no timers remain,
    the timer widget area is hidden.
    """
    message_type: str = "ovos.widgets.timer.remove"
    data: OvosWidgetsTimerRemoveData


class OvosWidgetsAlarmDisplayData(BaseModel):
    """Payload for displaying an alarm widget on the homescreen."""
    alarm: Dict[str, Any] = Field(..., description="Alarm data dict.")


class OvosWidgetsAlarmDisplayMessage(OpenVoiceOSMessage):
    """Show an alarm widget on the homescreen.

    Emitted by the alarm skill when an alarm is set. The homescreen
    displays the alarm time and label as a persistent widget so the user
    can see upcoming alarms at a glance.
    """
    message_type: str = "ovos.widgets.alarm.display"
    data: OvosWidgetsAlarmDisplayData


class OvosWidgetsAlarmUpdateData(BaseModel):
    """Payload for updating an existing alarm widget's data."""
    alarm: Dict[str, Any] = Field(..., description="Updated alarm data dict.")


class OvosWidgetsAlarmUpdateMessage(OpenVoiceOSMessage):
    """Update the data shown in an existing alarm homescreen widget.

    Emitted by the alarm skill when an alarm is modified (time, label,
    enabled state). The homescreen widget re-renders with the new data.
    """
    message_type: str = "ovos.widgets.alarm.update"
    data: OvosWidgetsAlarmUpdateData


class OvosWidgetsAlarmRemoveData(BaseModel):
    """Payload for removing a specific alarm widget by ID."""
    alarm_id: str = Field(..., description="ID of the alarm to remove.")


class OvosWidgetsAlarmRemoveMessage(OpenVoiceOSMessage):
    """Remove a specific alarm's widget from the homescreen.

    Emitted by the alarm skill when an alarm fires, is cancelled, or
    is deleted. The homescreen removes the matching alarm widget.
    """
    message_type: str = "ovos.widgets.alarm.remove"
    data: OvosWidgetsAlarmRemoveData


class OvosWidgetsMediaDisplayData(BaseModel):
    """Payload for displaying a now-playing media widget on the homescreen."""
    media: Dict[str, Any] = Field(..., description="Media data dict (title, artist, image, etc.).")


class OvosWidgetsMediaDisplayMessage(OpenVoiceOSMessage):
    """Show a now-playing media widget on the homescreen.

    Emitted by OCP skills when media playback begins. The homescreen
    displays a compact player widget showing title, artist, and album art
    with basic transport controls (pause/next/previous).
    """
    message_type: str = "ovos.widgets.media.display"
    data: OvosWidgetsMediaDisplayData


class OvosWidgetsMediaUpdateData(BaseModel):
    """Payload for updating the now-playing media widget's metadata."""
    media: Dict[str, Any] = Field(..., description="Updated media data dict.")


class OvosWidgetsMediaUpdateMessage(OpenVoiceOSMessage):
    """Update the media widget when the playing track changes.

    Emitted by OCP skills on track change. The homescreen widget updates
    title, artist, and album art to reflect the new track.
    """
    message_type: str = "ovos.widgets.media.update"
    data: OvosWidgetsMediaUpdateData


class OvosWidgetsMediaRemoveMessage(OpenVoiceOSMessage):
    """Hide the now-playing media widget from the homescreen.

    Emitted by OCP skills when playback stops or is paused for an
    extended period. The homescreen removes the compact player widget.
    """
    message_type: str = "ovos.widgets.media.remove"
    data: Dict[str, Any] = Field(default_factory=dict)
