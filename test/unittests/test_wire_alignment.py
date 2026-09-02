"""Models parse the payloads their producers actually put on the bus.

The session payloads below are `ovos_bus_client.session.Session.serialize()`
output; the registration payloads come from the `ovos_workshop.intents`
`emit_legacy_*` helpers; the common query pongs follow OVOS-COMMON-QUERY-1 §6.2
and the pre-spec shape `ovos-workshop` emits from its ping handler.
"""
import pytest
from pydantic import ValidationError

from ovos_pydantic_models.intents.adapt import RegisterVocabData, RegisterIntentData
from ovos_pydantic_models.intents.padatious import (
    PadatiousRegisterIntentData, PadatiousRegisterEntityData,
)
from ovos_pydantic_models.session import Session, ResponseMode, SessionHandler
from ovos_pydantic_models.skills.common_query import (
    OvosCommonQueryPongData, OvosCommonQueryPongLegacyData,
)

# a session carrying every OVOS-SESSION-1 §3 field a producer can set
SPEC_SESSION = {
    "session_id": "x",
    "lang": "en-US",
    "secondary_langs": ["pt-PT"],
    "output_lang": "en-US",
    "stt_lang": "en-US",
    "request_lang": "pt-PT",
    "detected_lang": "en-US",
    "site_id": "kitchen",
    "pipeline": ["ovos-stop-pipeline-plugin-high"],
    "blacklisted_skills": ["skill-ovos-stop.openvoiceos"],
    "blacklisted_intents": ["skill:Intent"],
    "blacklisted_pipelines": ["ovos-adapt-pipeline-plugin-low"],
    "intent_context": {"Location": {"value": "Lisbon"}},
    "active_handlers": [{"skill_id": "a.test", "activated_at": 1.0}],
    "converse_handlers": [{"skill_id": "b.test", "activated_at": 2.0}],
    "response_mode": {"skill_id": "c.test", "expires_at": 3.0},
    "fallback_handlers": ["skill-ovos-fallback-unknown.openvoiceos"],
    "persona_id": "assistant",
    "audio_transformers": ["at"],
    "utterance_transformers": ["ut"],
    "metadata_transformers": ["mt"],
    "intent_transformers": ["it"],
    "dialog_transformers": ["dt"],
    "tts_transformers": ["tt"],
    "blacklisted_audio_transformers": ["bat"],
    "blacklisted_utterance_transformers": ["but"],
    "blacklisted_metadata_transformers": ["bmt"],
    "blacklisted_intent_transformers": ["bit"],
    "blacklisted_dialog_transformers": ["bdt"],
    "blacklisted_tts_transformers": ["btt"],
    "location": {"city": {"name": "Lisbon"}},
}


class TestSessionCarrierFields:
    def test_every_spec_field_survives_the_roundtrip(self):
        dumped = Session.model_validate(SPEC_SESSION).model_dump()
        for key, value in SPEC_SESSION.items():
            assert key in dumped, f"{key} dropped by the model"
            assert dumped[key] == value, f"{key} not carried faithfully"

    def test_language_evidence_is_per_utterance(self):
        session = Session.model_validate(SPEC_SESSION)
        assert session.stt_lang == "en-US"
        assert session.request_lang == "pt-PT"
        assert session.detected_lang == "en-US"
        assert session.secondary_langs == ["pt-PT"]
        assert session.output_lang == "en-US"

    def test_handlers_are_typed_objects(self):
        session = Session.model_validate(SPEC_SESSION)
        assert session.active_handlers == [SessionHandler(skill_id="a.test", activated_at=1.0)]
        assert session.converse_handlers == [SessionHandler(skill_id="b.test", activated_at=2.0)]
        assert session.response_mode == ResponseMode(skill_id="c.test", expires_at=3.0)

    def test_handler_objects_require_both_keys(self):
        with pytest.raises(ValidationError):
            Session(active_handlers=[{"skill_id": "a.test"}])
        with pytest.raises(ValidationError):
            Session(response_mode={"skill_id": "c.test"})

    def test_absent_pipeline_is_not_invented(self):
        assert Session().pipeline is None
        assert "pipeline" not in Session().model_dump(exclude_none=True)

    def test_absent_carrier_fields_stay_absent(self):
        dumped = Session().model_dump(exclude_none=True)
        for field in ("persona_id", "intent_context", "response_mode",
                      "active_handlers", "converse_handlers", "fallback_handlers",
                      "blacklisted_pipelines", "tts_transformers",
                      "blacklisted_tts_transformers", "detected_lang"):
            assert field not in dumped

    def test_location_uses_the_wire_key(self):
        session = Session.model_validate({"location": {"city": {"name": "Lisbon"}}})
        assert session.location == {"city": {"name": "Lisbon"}}
        assert not hasattr(session, "location_preferences")


class TestPadatiousRegistration:
    # ovos_workshop.intents emit_legacy_register_template
    REGISTER_INTENT = {
        "file_name": "/opt/skill/vocab/en-us/hello.intent",
        "samples": ["hello"],
        "name": "skill-test.openvoiceos:Hello",
        "lang": "en-US",
        "blacklisted_words": None,
        "slot_blacklist": {"name": ["bob"]},
        "requires_context": [],
        "excludes_context": [],
    }
    # ovos_workshop.intents emit_legacy_register_entity
    REGISTER_ENTITY = {
        "file_name": "/opt/skill/vocab/en-us/name.entity",
        "samples": ["bob"],
        "name": "skill-test.openvoiceos:Name",
        "lang": "en-US",
        "blacklist": ["nobody"],
    }

    def test_register_intent_accepts_the_emitted_payload(self):
        data = PadatiousRegisterIntentData.model_validate(self.REGISTER_INTENT)
        assert data.model_dump() == self.REGISTER_INTENT

    def test_register_entity_accepts_the_emitted_payload(self):
        data = PadatiousRegisterEntityData.model_validate(self.REGISTER_ENTITY)
        assert data.model_dump() == self.REGISTER_ENTITY

    def test_skill_id_is_not_a_payload_field(self):
        assert "skill_id" not in PadatiousRegisterIntentData.model_fields
        assert "skill_id" not in PadatiousRegisterEntityData.model_fields

    def test_intent_name_and_lang_are_still_required(self):
        with pytest.raises(ValidationError):
            PadatiousRegisterIntentData(lang="en-US")
        with pytest.raises(ValidationError):
            PadatiousRegisterEntityData(name="skill:Name")


class TestAdaptRegistration:
    # ovos_workshop.intents emit_legacy_register_vocab, called with lang=None
    REGISTER_VOCAB = {
        "entity_value": "weather",
        "entity_type": "WeatherKeyword",
        "lang": None,
        "start": "weather",
        "end": "WeatherKeyword",
    }

    def test_register_vocab_accepts_a_null_lang(self):
        data = RegisterVocabData.model_validate(self.REGISTER_VOCAB)
        assert data.lang is None
        assert data.entity_value == "weather"

    def test_register_intent_carries_the_context_gates(self):
        data = RegisterIntentData.model_validate({
            "name": "skill-test.openvoiceos:Hello",
            "requires": [["WeatherKeyword", "WeatherKeyword"]],
            "at_least_one": [],
            "optional": [],
            "excludes": [],
            "requires_context": [{"key": "Location"}],
            "excludes_context": [{"key": "Muted"}],
        })
        assert data.requires_context == [{"key": "Location"}]
        assert data.excludes_context == [{"key": "Muted"}]


class TestCommonQueryPong:
    def test_ratified_pong(self):
        payload = {"utterance": "what is the capital of France",
                   "skill_id": "wiki.test", "can_answer": True, "latency_ms": 800}
        data = OvosCommonQueryPongData.model_validate(payload)
        assert data.can_answer is True
        assert data.utterance == "what is the capital of France"
        assert data.latency_ms == 800

    def test_latency_is_optional(self):
        data = OvosCommonQueryPongData(utterance="q", skill_id="wiki.test", can_answer=False)
        assert data.latency_ms is None

    def test_pong_without_can_answer_is_rejected(self):
        with pytest.raises(ValidationError):
            OvosCommonQueryPongData(utterance="q", skill_id="wiki.test")

    def test_pong_without_utterance_is_rejected(self):
        with pytest.raises(ValidationError):
            OvosCommonQueryPongData(skill_id="wiki.test", can_answer=True)

    def test_legacy_announcement_has_its_own_model(self):
        # ovos_workshop.skills.ovos OVOSSkill.__handle_common_query_ping
        data = OvosCommonQueryPongLegacyData.model_validate(
            {"skill_id": "wiki.test", "is_classic_cq": False})
        assert data.is_classic_cq is False
        assert "can_answer" not in OvosCommonQueryPongLegacyData.model_fields
