"""The ratified INTENT-4, PIPELINE-1, CONVERSE-1 and FALLBACK-1 topics.

Handler-lifecycle and manifest payloads are captured off a bus driven by the
installed `ovos_core.intent_services` dispatcher and manifest, so the models are
validated against what a running orchestrator emits rather than a transcription
of the spec tables. The remaining payloads are shaped from the specification's
own field tables.
"""
import pytest
from ovos_bus_client.message import Message
from ovos_core.intent_services.dispatcher import IntentDispatcher
from ovos_core.intent_services.manifest import IntentManifest
from ovos_utils.fakebus import FakeBus
from pydantic import ValidationError

from ovos_pydantic_models.intents.converse import (
    ConverseErrorCode,
    OvosConversePingData, OvosConversePingMessage,
    OvosConversePongData, OvosConversePongMessage,
)
from ovos_pydantic_models.intents.fallbacks import (
    OvosFallbackPingData, OvosFallbackPingMessage,
    OvosFallbackPongData, OvosFallbackPongMessage,
)
from ovos_pydantic_models.intents.pipeline import (
    OvosUtteranceHandleMessage,
    OvosIntentMatchedMessage,
    OvosIntentUnmatchedMessage,
    OvosIntentHandlerStartMessage, OvosIntentHandlerCompleteMessage,
    OvosIntentHandlerErrorMessage,
)
from ovos_pydantic_models.intents.registration import (
    IntentMethod,
    OvosIntentRegisterKeywordMessage, OvosIntentRegisterTemplateMessage,
    OvosEntityRegisterMessage,
    OvosIntentDeregisterMessage, OvosEntityDeregisterMessage,
    OvosIntentEnableMessage, OvosIntentDisableMessage,
    OvosSkillDeregisterMessage,
    OvosIntentListMessage, OvosIntentListResponseMessage,
    OvosIntentDescribeMessage, OvosIntentDescribeResponseMessage,
)

# INTENT-4 §5.2
KEYWORD_REGISTRATION = {
    "skill_id": "lighting.skill",
    "intent_name": "set_brightness",
    "lang": "en-US",
    "required": [
        {"name": "set", "samples": ["set", "change", "adjust"]},
        {"name": "brightness", "samples": ["brightness", "light level"]},
    ],
    "optional": [],
    "one_of": [[
        {"name": "up", "samples": ["up", "higher", "brighter"]},
        {"name": "down", "samples": ["down", "lower", "dimmer"]},
    ]],
    "excluded": [{"name": "question", "samples": ["what is", "how"]}],
}

# INTENT-4 §6.1
TEMPLATE_REGISTRATION = {
    "skill_id": "music.skill",
    "intent_name": "play_music",
    "lang": "en-US",
    "samples": ["(play|put on) {query}", "i want to listen to {query}"],
    "blacklist": ["trailer", "music video"],
    "required_slots": ["query"],
}

# INTENT-4 §7.1
ENTITY_REGISTRATION = {
    "skill_id": "music.skill",
    "entity_name": "engine",
    "lang": "en-US",
    "samples": ["spotify", "youtube music", "the radio"],
}


def collect(bus, topic):
    """Record every payload emitted on *topic*."""
    seen = []
    bus.on(topic, lambda m: seen.append(m))
    return seen


class TestIntentRegistrationWire:
    def test_keyword_registration_roundtrips(self):
        msg = OvosIntentRegisterKeywordMessage(data=KEYWORD_REGISTRATION)
        assert msg.message_type == "ovos.intent.register.keyword"
        assert [v.name for v in msg.data.required] == ["set", "brightness"]
        assert msg.data.one_of[0][1].samples == ["down", "lower", "dimmer"]
        assert msg.data.model_dump() == KEYWORD_REGISTRATION

    def test_keyword_registration_omitting_every_role_is_valid(self):
        # §5.2: an absent list-valued key is equivalent to an empty list
        data = OvosIntentRegisterKeywordMessage(
            data={"skill_id": "a.skill", "intent_name": "x", "lang": "en-US"}).data
        assert data.required == [] and data.one_of == []

    def test_keyword_registration_keeps_unknown_fields(self):
        # §5.3: companion specs ride on the registration payload
        msg = OvosIntentRegisterKeywordMessage(
            data={**KEYWORD_REGISTRATION, "requires_context": ["Location"]})
        assert msg.data.model_dump()["requires_context"] == ["Location"]

    def test_keyword_vocabulary_without_samples_is_rejected(self):
        with pytest.raises(ValidationError):
            OvosIntentRegisterKeywordMessage(data={
                **KEYWORD_REGISTRATION, "required": [{"name": "set", "samples": []}]})

    def test_template_registration_roundtrips(self):
        msg = OvosIntentRegisterTemplateMessage(data=TEMPLATE_REGISTRATION)
        assert msg.message_type == "ovos.intent.register.template"
        assert msg.data.required_slots == ["query"]
        assert msg.data.model_dump() == TEMPLATE_REGISTRATION

    def test_template_registration_without_samples_is_rejected(self):
        # §6.3: samples missing or empty is malformed
        with pytest.raises(ValidationError):
            OvosIntentRegisterTemplateMessage(data={
                k: v for k, v in TEMPLATE_REGISTRATION.items() if k != "samples"})

    def test_entity_registration_roundtrips(self):
        msg = OvosEntityRegisterMessage(data=ENTITY_REGISTRATION)
        assert msg.message_type == "ovos.entity.register"
        assert msg.data.model_dump() == ENTITY_REGISTRATION

    def test_entity_registration_with_empty_samples_is_rejected(self):
        with pytest.raises(ValidationError):
            OvosEntityRegisterMessage(data={**ENTITY_REGISTRATION, "samples": []})

    def test_deregistration_lang_is_optional(self):
        msg = OvosIntentDeregisterMessage(
            data={"skill_id": "music.skill", "intent_name": "play_music"})
        assert msg.message_type == "ovos.intent.deregister"
        assert msg.data.lang is None

    def test_deregistration_without_intent_name_is_rejected(self):
        with pytest.raises(ValidationError):
            OvosIntentDeregisterMessage(data={"skill_id": "music.skill"})

    def test_entity_deregistration_roundtrips(self):
        msg = OvosEntityDeregisterMessage(
            data={"skill_id": "music.skill", "entity_name": "engine", "lang": "en-US"})
        assert msg.message_type == "ovos.entity.deregister"
        assert msg.data.entity_name == "engine"

    def test_entity_deregistration_without_entity_name_is_rejected(self):
        with pytest.raises(ValidationError):
            OvosEntityDeregisterMessage(data={"skill_id": "music.skill", "lang": "en-US"})

    def test_enable_and_disable_share_the_deregister_payload(self):
        payload = {"skill_id": "music.skill", "intent_name": "play_music", "lang": "en-US"}
        assert OvosIntentEnableMessage(data=payload).message_type == "ovos.intent.enable"
        assert OvosIntentDisableMessage(data=payload).message_type == "ovos.intent.disable"
        assert OvosIntentDisableMessage(data=payload).data.model_dump() == payload

    def test_disable_without_a_target_intent_is_rejected(self):
        with pytest.raises(ValidationError):
            OvosIntentDisableMessage(data={"skill_id": "music.skill", "lang": "en-US"})

    def test_skill_deregistration_roundtrips(self):
        msg = OvosSkillDeregisterMessage(data={"skill_id": "music.skill"})
        assert msg.message_type == "ovos.skill.deregister"
        assert msg.data.skill_id == "music.skill"

    def test_skill_deregistration_without_skill_id_is_rejected(self):
        with pytest.raises(ValidationError):
            OvosSkillDeregisterMessage(data={})

    def test_list_filters_are_all_optional(self):
        assert OvosIntentListMessage().data.session_id is None


class TestIntentManifestQueries:
    """Query responses captured off the installed INTENT-4 §10 manifest."""

    @pytest.fixture
    def bus(self):
        bus = FakeBus()
        manifest = IntentManifest(bus)
        bus.emit(Message("ovos.intent.register.keyword", KEYWORD_REGISTRATION))
        bus.emit(Message("ovos.intent.register.template", TEMPLATE_REGISTRATION))
        yield bus
        manifest.shutdown()

    def test_list_response_roundtrips(self, bus):
        seen = collect(bus, "ovos.intent.list.response")
        bus.emit(Message("ovos.intent.list", {"skill_id": "music.skill"}))
        msg = OvosIntentListResponseMessage(data=seen[0].data)
        assert msg.data.ok is True
        entry, = msg.data.intents
        assert entry.intent_name == "play_music"
        assert entry.method is IntentMethod.TEMPLATE
        assert entry.enabled is True
        assert entry.session_id == "default"

    def test_list_response_with_a_bad_method_is_rejected(self, bus):
        with pytest.raises(ValidationError):
            OvosIntentListResponseMessage(data={"ok": True, "intents": [
                {"skill_id": "a", "intent_name": "b", "lang": "en-US",
                 "method": "regex", "enabled": True, "session_id": "default"}]})

    def test_describe_response_carries_the_definition_as_broadcast(self, bus):
        seen = collect(bus, "ovos.intent.describe.response")
        bus.emit(Message("ovos.intent.describe", {
            "skill_id": "lighting.skill", "intent_name": "set_brightness", "lang": "en-US"}))
        msg = OvosIntentDescribeResponseMessage(data=seen[0].data)
        assert msg.data.ok is True
        definition, = msg.data.definitions
        assert definition.method is IntentMethod.KEYWORD
        assert definition.definition == KEYWORD_REGISTRATION
        # the described payload is exactly what the §5 model accepts
        assert OvosIntentRegisterKeywordMessage(data=definition.definition).data.required

    def test_describe_response_reports_an_unknown_intent(self, bus):
        seen = collect(bus, "ovos.intent.describe.response")
        bus.emit(Message("ovos.intent.describe", {
            "skill_id": "nope.skill", "intent_name": "x", "lang": "en-US"}))
        msg = OvosIntentDescribeResponseMessage(data=seen[0].data)
        assert msg.data.ok is False
        assert msg.data.definitions == []
        assert "unknown intent" in msg.data.error

    def test_describe_request_requires_the_intent_triple(self):
        with pytest.raises(ValidationError):
            OvosIntentDescribeMessage(data={"skill_id": "music.skill", "lang": "en-US"})


class TestUtteranceLifecycle:
    def test_entry_topic_roundtrips(self):
        msg = OvosUtteranceHandleMessage(
            data={"utterances": ["turn off the lights"], "lang": "en-US"})
        assert msg.message_type == "ovos.utterance.handle"
        assert msg.data.utterances == ["turn off the lights"]

    def test_entry_topic_lang_is_optional(self):
        # §9.1: a producer that does not authoritatively know the language omits it
        assert OvosUtteranceHandleMessage(data={"utterances": ["hello"]}).data.lang is None

    def test_entry_topic_without_utterances_is_rejected(self):
        with pytest.raises(ValidationError):
            OvosUtteranceHandleMessage(data={"lang": "en-US"})

    def test_matched_roundtrips(self):
        payload = {"skill_id": "music.skill", "intent_name": "play_music",
                   "lang": "en-US", "utterance": "play the beatles",
                   "slots": {"query": "the beatles"}, "pipeline_id": "template-high"}
        msg = OvosIntentMatchedMessage(data=payload)
        assert msg.message_type == "ovos.intent.matched"
        assert msg.data.model_dump() == payload

    def test_matched_without_a_pipeline_id_is_rejected(self):
        # §9.2 requires the producing plugin's identity
        with pytest.raises(ValidationError):
            OvosIntentMatchedMessage(data={
                "skill_id": "music.skill", "intent_name": "play_music", "lang": "en-US",
                "utterance": "play the beatles", "slots": {}})

    def test_unmatched_roundtrips(self):
        msg = OvosIntentUnmatchedMessage(
            data={"utterances": ["turn off the lights"], "lang": "en-US"})
        assert msg.message_type == "ovos.intent.unmatched"
        assert msg.data.lang == "en-US"

    def test_unmatched_needs_no_fields_at_all(self):
        # §9.3: the topic name alone is normative
        assert OvosIntentUnmatchedMessage().data.utterances == []

    def test_unmatched_with_a_non_list_utterances_is_rejected(self):
        with pytest.raises(ValidationError):
            OvosIntentUnmatchedMessage(data={"utterances": "turn off the lights"})


class TestHandlerTrio:
    """Trio payloads captured off the installed PIPELINE-1 §8 dispatcher."""

    @pytest.fixture
    def bus(self):
        bus = FakeBus()
        dispatcher = IntentDispatcher(bus, timeout=None)
        yield bus, dispatcher
        dispatcher.shutdown()

    @staticmethod
    def dispatch(bus):
        bus.emit(Message("music.skill:play_music",
                         {"lang": "en-US", "utterance": "play the beatles", "slots": {}},
                         {"skill_id": "music.skill"}))

    def test_start_roundtrips(self, bus):
        bus, dispatcher = bus
        seen = collect(bus, "ovos.intent.handler.start")
        dispatcher.dispatch(Message("music.skill:play_music", {},
                                    {"skill_id": "music.skill"}))
        msg = OvosIntentHandlerStartMessage(data=seen[0].data)
        assert msg.message_type == "ovos.intent.handler.start"
        assert msg.data.skill_id == "music.skill"
        assert msg.data.intent_name == "play_music"

    def test_complete_roundtrips(self, bus):
        bus, dispatcher = bus
        seen = collect(bus, "ovos.intent.handler.complete")
        dispatcher.dispatch(Message("music.skill:play_music", {},
                                    {"skill_id": "music.skill"}))
        bus.emit(Message("mycroft.skill.handler.complete", {"intent_name": "play_music"},
                         {"skill_id": "music.skill"}))
        msg = OvosIntentHandlerCompleteMessage(data=seen[0].data)
        assert msg.message_type == "ovos.intent.handler.complete"
        assert msg.data.intent_name == "play_music"

    def test_error_carries_the_exception(self, bus):
        bus, dispatcher = bus
        seen = collect(bus, "ovos.intent.handler.error")
        dispatcher.dispatch(Message("music.skill:play_music", {},
                                    {"skill_id": "music.skill"}))
        bus.emit(Message("mycroft.skill.handler.error",
                         {"intent_name": "play_music",
                          "exception": "RuntimeError: Spotify is not configured"},
                         {"skill_id": "music.skill"}))
        msg = OvosIntentHandlerErrorMessage(data=seen[0].data)
        assert msg.data.exception == "RuntimeError: Spotify is not configured"

    def test_error_without_an_exception_is_rejected(self):
        # §8.2: `exception` is required on the error leg
        with pytest.raises(ValidationError):
            OvosIntentHandlerErrorMessage(data={
                "skill_id": "music.skill", "intent_name": "play_music"})

    def test_start_without_an_intent_name_is_rejected(self):
        with pytest.raises(ValidationError):
            OvosIntentHandlerStartMessage(data={"skill_id": "music.skill"})


class TestConversePoll:
    def test_ping_roundtrips(self):
        msg = OvosConversePingMessage(
            data={"utterances": ["the second one"], "lang": "en-US"})
        assert msg.message_type == "ovos.converse.ping"
        assert msg.data.utterances == ["the second one"]

    def test_ping_without_lang_is_rejected(self):
        with pytest.raises(ValidationError):
            OvosConversePingMessage(data={"utterances": ["the second one"]})

    def test_pong_roundtrips(self):
        msg = OvosConversePongMessage(
            data={"skill_id": "music.skill", "result": True})
        assert msg.message_type == "ovos.converse.pong"
        assert msg.data.result is True
        assert msg.data.error_code is None

    def test_pong_carries_a_structured_decline(self):
        msg = OvosConversePongMessage(data={
            "skill_id": "music.skill", "result": False, "error_code": "done"})
        assert msg.data.error_code is ConverseErrorCode.DONE

    def test_pong_with_an_unknown_error_code_is_rejected(self):
        with pytest.raises(ValidationError):
            OvosConversePongMessage(data={
                "skill_id": "music.skill", "result": False, "error_code": "bored"})

    def test_pong_without_a_verdict_is_rejected(self):
        with pytest.raises(ValidationError):
            OvosConversePongMessage(data={"skill_id": "music.skill"})

    def test_the_claim_boolean_is_named_result_not_can_handle(self):
        # §4.2: the boolean's name is normative only within its own protocol
        with pytest.raises(ValidationError):
            OvosConversePongData(skill_id="music.skill", can_handle=True)


class TestFallbackPoll:
    def test_ping_roundtrips(self):
        msg = OvosFallbackPingMessage(
            data={"utterances": ["what is the airspeed of a swallow"], "lang": "en-US"})
        assert msg.message_type == "ovos.fallback.ping"
        assert msg.data.lang == "en-US"

    def test_ping_without_utterances_is_rejected(self):
        with pytest.raises(ValidationError):
            OvosFallbackPingMessage(data={"lang": "en-US"})

    def test_pong_roundtrips(self):
        payload = {"skill_id": "skill-ovos-fallback-unknown.openvoiceos",
                   "can_handle": False,
                   "utterance": "what is the airspeed of a swallow"}
        msg = OvosFallbackPongMessage(data=payload)
        assert msg.message_type == "ovos.fallback.pong"
        assert msg.data.model_dump() == payload

    def test_pong_without_the_evaluated_utterance_is_rejected(self):
        # §6.1: `utterance` is REQUIRED — it says what the skill judged
        with pytest.raises(ValidationError):
            OvosFallbackPongMessage(data={
                "skill_id": "skill-ovos-fallback-unknown.openvoiceos", "can_handle": True})

    def test_pong_with_a_non_boolean_verdict_is_rejected(self):
        with pytest.raises(ValidationError):
            OvosFallbackPongMessage(data={
                "skill_id": "a.skill", "can_handle": "maybe", "utterance": "hi"})
