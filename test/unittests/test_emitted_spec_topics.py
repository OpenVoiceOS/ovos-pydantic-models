"""Spec topics that OVOS services put on the bus resolve to a model.

Each payload is copied from the code that emits it:
ovos.audio.output.started/ended from ovos_audio/playback.py (``forward`` of
the speak Message with no data), ovos.stop.pong from
ovos_workshop/skills/ovos.py ``_handle_stop_ack``, ovos.skill.loaded from
ovos_workshop/skill_launcher.py ``_communicate_load_status``, and the
ovos.skills.list query with the reply ovos_core/intent_services/manifest.py
``_on_skills_list`` sends back.
"""
import pytest
from pydantic import ValidationError

import ovos_pydantic_models
from ovos_pydantic_models.message import OpenVoiceOSMessage

SKILLS_LIST_RESPONSE = {
    "ok": True,
    "skills": [
        {"skill_id": "weather.skill", "session_id": "default",
         "capabilities": ["fallback", "common_query"], "intents": 2},
        {"skill_id": "chat.skill", "session_id": "satellite-1",
         "capabilities": [], "intents": 0},
    ],
}

EMITTED = [
    ("ovos.audio.output.started", {}),
    ("ovos.audio.output.ended", {}),
    ("ovos.stop.pong", {"skill_id": "timer.skill", "can_handle": True}),
    ("ovos.skill.loaded", {"skill_id": "weather.skill",
                           "capabilities": ["fallback", "converse"]}),
    ("ovos.skills.list", {"session_id": "satellite-1"}),
    ("ovos.skills.list.response", SKILLS_LIST_RESPONSE),
]


def models_for(topic):
    """Every exported message class whose default ``message_type`` is *topic*."""
    return [cls for cls in vars(ovos_pydantic_models).values()
            if isinstance(cls, type) and issubclass(cls, OpenVoiceOSMessage)
            and cls.model_fields["message_type"].default == topic]


@pytest.mark.parametrize("topic, payload", EMITTED)
def test_topic_resolves_to_one_model_that_parses_the_emitted_payload(topic, payload):
    model, = models_for(topic)
    msg = model.model_validate({"message_type": topic, "data": payload})
    assert msg.message_type == topic
    data = msg.data if isinstance(msg.data, dict) else msg.data.model_dump(exclude_unset=True)
    assert data == payload


def test_stop_pong_without_can_handle_is_rejected():
    # STOP-1: a missing can_handle must not be coerced to true
    model, = models_for("ovos.stop.pong")
    with pytest.raises(ValidationError):
        model(data={"skill_id": "timer.skill"})


def test_skill_loaded_without_skill_id_is_rejected():
    model, = models_for("ovos.skill.loaded")
    with pytest.raises(ValidationError):
        model(data={"capabilities": ["converse"]})


def test_skill_loaded_capabilities_default_to_empty():
    model, = models_for("ovos.skill.loaded")
    assert model(data={"skill_id": "a.skill"}).data.capabilities == []


def test_skills_list_session_filter_is_optional():
    model, = models_for("ovos.skills.list")
    assert model().data.session_id is None


def test_skills_list_response_entries_are_typed():
    model, = models_for("ovos.skills.list.response")
    first = model(data=SKILLS_LIST_RESPONSE).data.skills[0]
    assert first.skill_id == "weather.skill"
    assert first.intents == 2
    with pytest.raises(ValidationError):
        model(data={"ok": True, "skills": [{"skill_id": "a.skill"}]})
