from typing import Dict, Any, Optional

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


class SchedulerScheduleEventData(BaseModel):
    """Payload for registering a future timed event."""
    name: str = Field(..., description="Unique name for the scheduled event.")
    when: float = Field(..., description="Unix timestamp when to fire the event.")
    data: Dict[str, Any] = Field(default_factory=dict, description="Payload passed back to the skill handler.")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context to include when the event fires.")
    repeat_interval: Optional[float] = Field(None, description="If set, repeat every N seconds.")


class SchedulerScheduleEventMessage(OpenVoiceOSMessage):
    """Register a future event with the OVOS event scheduler.

    Emitted by skills via `self.schedule_event()`. The scheduler service
    (running in `ovos-core`) fires a bus message with the given `name` as
    the message type at the specified Unix timestamp. If `repeat_interval`
    is set the event fires repeatedly until cancelled.
    """
    message_type: str = "mycroft.scheduler.schedule_event"
    data: SchedulerScheduleEventData


class SchedulerRemoveEventData(BaseModel):
    """Payload for cancelling a scheduled event by name."""
    name: str = Field(..., description="Name of the event to remove.")


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
    name: str = Field(..., description="Name of the event to update.")
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
