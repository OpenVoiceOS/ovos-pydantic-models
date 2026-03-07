from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


class OvosNotificationApiSetData(BaseModel):
    """Payload for adding a new persistent notification to the notification center."""
    notification: Dict[str, Any] = Field(..., description="Notification payload dict.")


class OvosNotificationApiSetMessage(OpenVoiceOSMessage):
    """Add a persistent notification to the OVOS notification center.

    Emitted by skills (e.g. timer skill, reminder skill) when they want
    to post a notification that persists in the homescreen's notification
    panel until dismissed. The notification manager stores it and updates
    the badge counter via `ovos.notification.update_counter`.
    """
    message_type: str = "ovos.notification.api.set"
    data: OvosNotificationApiSetData


class OvosNotificationApiSetControlledData(BaseModel):
    """Payload for adding a skill-controlled notification (non-dismissible by user)."""
    notification: Dict[str, Any] = Field(..., description="Controlled notification payload dict.")


class OvosNotificationApiSetControlledMessage(OpenVoiceOSMessage):
    """Add a skill-controlled notification that cannot be dismissed by the user.

    Emitted by skills that own a notification's lifecycle — for example,
    the timer skill keeps a 'timer running' badge that only disappears when
    the timer fires. The skill must explicitly remove it via
    `ovos.notification.api.remove.controlled`.
    """
    message_type: str = "ovos.notification.api.set.controlled"
    data: OvosNotificationApiSetControlledData


class OvosNotificationApiRemoveControlledData(BaseModel):
    """Payload for removing a specific skill-controlled notification."""
    notification: Dict[str, Any] = Field(..., description="Controlled notification to remove.")


class OvosNotificationApiRemoveControlledMessage(OpenVoiceOSMessage):
    """Remove a skill-controlled notification from the notification center.

    Emitted by the owning skill when the controlled notification is no
    longer relevant (e.g. timer expired, reminder acknowledged). The
    notification manager removes the entry and decrements the badge counter.
    """
    message_type: str = "ovos.notification.api.remove.controlled"
    data: OvosNotificationApiRemoveControlledData


class OvosNotificationApiRequestStorageModelMessage(OpenVoiceOSMessage):
    """Request the full list of stored notifications from the notification manager.

    Emitted by the notification panel GUI when it opens, to populate the
    list of pending notifications. The manager replies with
    `ovos.notification.update_storage_model`.
    """
    message_type: str = "ovos.notification.api.request.storage.model"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosNotificationApiStorageClearMessage(OpenVoiceOSMessage):
    """Clear all user-dismissible notifications from the notification center.

    Emitted by the 'clear all' button in the notification panel GUI, or
    by a voice command like 'clear notifications'. Skill-controlled
    notifications are not affected.
    """
    message_type: str = "ovos.notification.api.storage.clear"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosNotificationApiStorageClearItemData(BaseModel):
    """Payload for removing a single specific notification."""
    notification: Dict[str, Any] = Field(..., description="Specific notification to clear.")


class OvosNotificationApiStorageClearItemMessage(OpenVoiceOSMessage):
    """Remove a single specific notification from the notification center.

    Emitted when the user dismisses an individual notification in the panel
    GUI (e.g. swipe-to-dismiss). The notification manager removes only
    the matching entry and updates the badge counter.
    """
    message_type: str = "ovos.notification.api.storage.clear.item"
    data: OvosNotificationApiStorageClearItemData


class OvosNotificationApiPopClearMessage(OpenVoiceOSMessage):
    """Clear the currently displayed pop-up notification without deleting it.

    Emitted by the GUI notification overlay after the pop-up display
    timeout expires. The notification is dismissed from the overlay
    but remains in the persistent notification center.
    """
    message_type: str = "ovos.notification.api.pop.clear"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosNotificationApiPopClearDeleteMessage(OpenVoiceOSMessage):
    """Clear and permanently delete the currently displayed pop-up notification.

    Emitted when the user taps the dismiss button on a pop-up notification.
    The overlay is cleared and the notification is removed from storage.
    """
    message_type: str = "ovos.notification.api.pop.clear.delete"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosNotificationUpdateCounterData(BaseModel):
    """Updated notification badge count from the notification manager."""
    count: int = Field(..., description="Current total notification count.")


class OvosNotificationUpdateCounterMessage(OpenVoiceOSMessage):
    """Update the notification badge counter shown on the homescreen.

    Emitted by the notification manager whenever the total number of
    pending notifications changes (add, remove, clear). The homescreen
    updates its badge icon to reflect the new count.
    """
    message_type: str = "ovos.notification.update_counter"
    data: OvosNotificationUpdateCounterData


class OvosNotificationUpdateStorageModelData(BaseModel):
    """The full list of pending notifications from the notification manager."""
    model: List[Dict[str, Any]] = Field(default_factory=list, description="Full notification list.")


class OvosNotificationUpdateStorageModelMessage(OpenVoiceOSMessage):
    """Push the full notification list to the notification panel GUI.

    Emitted by the notification manager in response to
    `ovos.notification.api.request.storage.model` or after any mutation
    (add/remove). The panel GUI re-renders its list view with this data.
    """
    message_type: str = "ovos.notification.update_storage_model"
    data: OvosNotificationUpdateStorageModelData


class OvosNotificationControlledTypeShowData(BaseModel):
    """Payload for showing all controlled notifications of a given type."""
    type: str = Field(..., description="Controlled notification type to show.")


class OvosNotificationControlledTypeShowMessage(OpenVoiceOSMessage):
    """Show all skill-controlled notifications of a specific type.

    Emitted by the notification manager when a skill requests its
    controlled notifications to become visible in the panel. Useful for
    surfacing persistent status indicators (timers, alarms, reminders).
    """
    message_type: str = "ovos.notification.controlled.type.show"
    data: OvosNotificationControlledTypeShowData


class OvosNotificationControlledTypeRemoveData(BaseModel):
    """Payload for removing all controlled notifications of a given type."""
    type: str = Field(..., description="Controlled notification type to remove.")


class OvosNotificationControlledTypeRemoveMessage(OpenVoiceOSMessage):
    """Remove all skill-controlled notifications of a specific type.

    Emitted by a skill when all notifications of its type are no longer
    relevant (e.g. all timers have fired). The notification manager
    clears every entry matching the type.
    """
    message_type: str = "ovos.notification.controlled.type.remove"
    data: OvosNotificationControlledTypeRemoveData


class OvosNotificationShowData(BaseModel):
    """Payload for immediately displaying a pop-up notification."""
    notification: Dict[str, Any] = Field(..., description="Notification to display.")


class OvosNotificationShowMessage(OpenVoiceOSMessage):
    """Display a pop-up notification on screen immediately.

    Emitted by skills or PHAL plugins when a time-sensitive notification
    needs to be shown regardless of what is currently on screen (e.g. an
    incoming call, a timer completion alert). The GUI overlays the
    notification for a configurable duration before it auto-dismisses.
    """
    message_type: str = "ovos.notification.show"
    data: OvosNotificationShowData


class OvosNotificationDataMessage(OpenVoiceOSMessage):
    """Internal event carrying notification data for processing pipelines.

    Low-level event emitted by the notification manager during notification
    lifecycle processing. Not intended for direct skill use — prefer the
    higher-level `ovos.notification.api.*` messages instead.
    """
    message_type: str = "ovos.notification.notification_data"
    data: Dict[str, Any] = Field(default_factory=dict)
