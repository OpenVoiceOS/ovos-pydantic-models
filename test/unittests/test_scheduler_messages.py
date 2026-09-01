import pytest
from pydantic import ValidationError

from ovos_pydantic_models.core.scheduler import (
    SchedulerScheduleEventData, SchedulerScheduleEventMessage,
    SchedulerRemoveEventData, SchedulerRemoveEventMessage,
    SchedulerUpdateEventData, SchedulerUpdateEventMessage,
    SchedulerGetEventData, SchedulerGetEventMessage,
)


class TestSchedulerMessages:
    def test_schedule_event_wire_payload(self):
        # exact shape emitted by EventSchedulerInterface._schedule_event
        # and consumed by EventScheduler.handle_schedule_event
        payload = {
            "time": 1735689600.0,
            "event": "my_skill:my_reminder",
            "repeat": None,
            "data": {"text": "your reminder"},
        }
        data = SchedulerScheduleEventData(**payload)
        msg = SchedulerScheduleEventMessage(data=data)
        assert msg.message_type == "mycroft.scheduler.schedule_event"
        assert msg.data.event == "my_skill:my_reminder"
        assert msg.data.time == 1735689600.0
        assert msg.data.repeat is None
        assert msg.data.data == {"text": "your reminder"}

    def test_schedule_event_repeat_interval(self):
        data = SchedulerScheduleEventData(event="my_skill:tick", time=1.0, repeat=30.0)
        assert data.repeat == 30.0

    def test_schedule_event_rejects_old_field_names(self):
        with pytest.raises(ValidationError):
            SchedulerScheduleEventData(name="my_reminder", when=1.0)

    def test_remove_event_wire_payload(self):
        # exact shape emitted by EventSchedulerInterface.cancel_scheduled_event
        payload = {"event": "my_skill:my_reminder"}
        data = SchedulerRemoveEventData(**payload)
        msg = SchedulerRemoveEventMessage(data=data)
        assert msg.message_type == "mycroft.scheduler.remove_event"
        assert msg.data.event == "my_skill:my_reminder"

    def test_remove_event_rejects_old_field_name(self):
        with pytest.raises(ValidationError):
            SchedulerRemoveEventData(name="my_reminder")

    def test_update_event_wire_payload(self):
        # exact shape emitted by EventSchedulerInterface.update_scheduled_event
        payload = {"event": "my_skill:my_reminder", "data": {"text": "updated"}}
        data = SchedulerUpdateEventData(**payload)
        msg = SchedulerUpdateEventMessage(data=data)
        assert msg.message_type == "mycroft.scheduler.update_event"
        assert msg.data.event == "my_skill:my_reminder"
        assert msg.data.data == {"text": "updated"}

    def test_update_event_rejects_old_field_name(self):
        with pytest.raises(ValidationError):
            SchedulerUpdateEventData(name="my_reminder", data={})

    def test_get_event_wire_payload(self):
        # exact shape emitted by EventSchedulerInterface.get_scheduled_event_status
        payload = {"name": "my_skill:my_reminder"}
        data = SchedulerGetEventData(**payload)
        msg = SchedulerGetEventMessage(data=data)
        assert msg.message_type == "mycroft.scheduler.get_event"
        assert msg.data.name == "my_skill:my_reminder"
