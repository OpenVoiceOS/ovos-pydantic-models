import json
import pytest
from pydantic import ValidationError

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session, UtteranceState, IntentContextManager


class TestOpenVoiceOSMessage:
    def test_minimal_instantiation(self):
        msg = OpenVoiceOSMessage(message_type="test.message")
        assert msg.message_type == "test.message"
        assert msg.data == {}

    def test_message_with_data(self):
        msg = OpenVoiceOSMessage(message_type="speak", data={"utterance": "hello"})
        assert msg.data["utterance"] == "hello"

    def test_roundtrip_serialization(self):
        msg = OpenVoiceOSMessage(message_type="speak", data={"utterance": "hello"})
        restored = OpenVoiceOSMessage.model_validate(msg.model_dump())
        assert restored.message_type == msg.message_type
        assert restored.data == msg.data

    def test_message_type_required(self):
        with pytest.raises(ValidationError):
            OpenVoiceOSMessage()


class TestMessageContext:
    def test_empty_context(self):
        ctx = MessageContext()
        assert ctx.source is None
        assert ctx.destination is None
        assert ctx.session is None

    def test_context_with_source(self):
        ctx = MessageContext(source="skills")
        assert ctx.source == "skills"

    def test_context_allows_extra_fields(self):
        ctx = MessageContext(source="skills", custom_field="value")
        assert ctx.model_extra.get("custom_field") == "value"

    def test_context_with_session(self):
        session = Session(session_id="test-123", lang="en-us")
        ctx = MessageContext(source="skills", session=session)
        assert ctx.session.session_id == "test-123"

    def test_roundtrip_serialization(self):
        ctx = MessageContext(source="skills", destination="audio")
        restored = MessageContext.model_validate(ctx.model_dump())
        assert restored.source == ctx.source
        assert restored.destination == ctx.destination


class TestSession:
    def test_default_session(self):
        session = Session()
        assert session.session_id == "default"
        assert session.lang == "en-us"
        assert session.pipeline is None  # absent on the wire, not fabricated

    def test_custom_session(self):
        session = Session(session_id="my-session", lang="es-es", site_id="kitchen")
        assert session.session_id == "my-session"
        assert session.lang == "es-es"
        assert session.site_id == "kitchen"

    def test_roundtrip_serialization(self):
        session = Session(session_id="abc", lang="fr-fr")
        restored = Session.model_validate(session.model_dump())
        assert restored.session_id == session.session_id
        assert restored.lang == session.lang

    def test_utterance_states_enum(self):
        session = Session(utterance_states={"skill-a.mycroft": "intent"})
        assert session.utterance_states["skill-a.mycroft"] == UtteranceState.INTENT

    def test_utterance_state_invalid(self):
        with pytest.raises((ValidationError, ValueError)):
            Session(utterance_states={"skill-a.mycroft": "invalid_state"})


class TestIntentContextManager:
    def test_default_context_manager(self):
        ctx = IntentContextManager()
        assert ctx.timeout == 120
        assert ctx.frame_stack == []
        assert ctx.context_max_frames == 3

    def test_roundtrip_serialization(self):
        ctx = IntentContextManager(timeout=60, context_greedy=True)
        restored = IntentContextManager.model_validate(ctx.model_dump())
        assert restored.timeout == 60
        assert restored.context_greedy is True


class TestWireFormatAlias:
    """message.py:26 - the wire key for a message's type is "type" (MSG-1),
    not "message_type". A real ovos-bus-client Message must round-trip."""

    def test_bus_client_message_roundtrips_through_model(self):
        pytest.importorskip("ovos_bus_client")
        from ovos_bus_client.message import Message

        wire = json.loads(Message("ovos.utterance.handled", {"x": 1}).serialize())
        assert "type" in wire
        assert "message_type" not in wire

        msg = OpenVoiceOSMessage.model_validate(wire)
        assert msg.message_type == "ovos.utterance.handled"
        assert msg.data == {"x": 1}

        dumped = msg.model_dump(by_alias=True)
        assert dumped["type"] == "ovos.utterance.handled"
        assert "message_type" not in dumped

    def test_construct_by_field_name_still_works(self):
        msg = OpenVoiceOSMessage(message_type="speak")
        assert msg.message_type == "speak"
