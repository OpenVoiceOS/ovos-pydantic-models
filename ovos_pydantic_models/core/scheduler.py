from typing import Dict, Any, Optional

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


class SchedulerScheduleEventData(BaseModel):
    """Payload for registering a future timed event."""
    event: str = Field(..., description="Message type to emit when the event fires.")
    time: float = Field(..., description="Unix timestamp when to fire the event.")
    repeat: Optional[float] = Field(None, description="If set, repeat every N seconds.")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Payload passed back to the skill handler.")


class SchedulerScheduleEventMessage(OpenVoiceOSMessage):
    """Register a future event with the OVOS event scheduler.

    Emitted by skills via `self.schedule_event()`. The scheduler service
    (running in `ovos-core`) fires a bus message with the given `event` as
    the message type at the specified Unix timestamp. If `repeat` is set
    the event fires repeatedly until cancelled. Message context is passed
    through unchanged and is not part of the payload.
    """
    message_type: str = "mycroft.scheduler.schedule_event"
    data: SchedulerScheduleEventData


class SchedulerRemoveEventData(BaseModel):
    """Payload for cancelling a scheduled event by name."""
    event: str = Field(..., description="Message type of the event to remove.")


class SchedulerRemoveEventMessage(OpenVoiceOSMessage):
    """Cancel a previously scheduled event.

    Emitted by skills via `self.cancel_scheduled_event()`. The scheduler
    removes the named event so it will no longer fire. Safe to call even
    if the event has already fired or never existed.
    """
    message_type: str = "mycroft.scheduler.remove_event"
    data: SchedulerRemoveEventData


class SchedulerUpdateEventData(BaseModel):
    """Payload for updating the data associated with a scheduled event."""
    event: str = Field(..., description="Message type of the event to update.")
    data: Dict[str, Any] = Field(default_factory=dict, description="New payload data for the event.")


class SchedulerUpdateEventMessage(OpenVoiceOSMessage):
    """Update the payload data for an existing scheduled event.

    Emitted by skills via `self.update_scheduled_event()`. Only the `data`
    dict is updated — the firing time is not changed. Useful for passing
    fresh context to a repeating event handler.
    """
    message_type: str = "mycroft.scheduler.update_event"
    data: SchedulerUpdateEventData


class SchedulerGetEventData(BaseModel):
    """Payload for querying a scheduled event by name."""
    name: str = Field(..., description="Name of the event to retrieve.")


class SchedulerGetEventMessage(OpenVoiceOSMessage):
    """Query details of a specific scheduled event.

    Emitted by skills or debug tools that need to inspect a pending event's
    firing time and payload. The scheduler replies with the event details.
    """
    message_type: str = "mycroft.scheduler.get_event"
    data: SchedulerGetEventData


class SchedulerListEventsMessage(OpenVoiceOSMessage):
    """Request a list of all pending scheduled events.

    Emitted by admin tools and debug utilities. The scheduler replies
    with all registered event names, firing times, and repeat intervals.
    """
    message_type: str = "mycroft.scheduler.list_events"
    data: Dict[str, Any] = Field(default_factory=dict)


class SchedulerUpdateEventLegacyMessage(OpenVoiceOSMessage):
    """Update a pending scheduled event (legacy bus-client path).

    Emitted by ``ovos_bus_client.apis.events.EventSchedulerInterface``
    via ``message.forward('mycroft.schedule.update_event', data)``.
    Note: the canonical spelling used by the scheduler service itself
    is ``mycroft.scheduler.update_event`` (see ``SchedulerUpdateEventMessage``);
    this legacy form is used by the bus-client API helper.
    """
    message_type: str = "mycroft.schedule.update_event"
    data: Dict[str, Any] = Field(default_factory=dict)
