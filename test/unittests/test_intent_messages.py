import pytest
from pydantic import ValidationError

from ovos_pydantic_models.intents.core import (
    OvosUtteranceHandledMessage, OvosUtteranceCancelledMessage,
    CompleteIntentFailureData, CompleteIntentFailureMessage,
    AddContextData, AddContextMessage,
    RemoveContextData, RemoveContextMessage, ClearContextMessage,
    IntentServiceIntentGetData, IntentServiceIntentGetMessage,
    SkillActivateMessage, SkillActivateData,
    SkillDeactivateMessage,
)
from ovos_pydantic_models.intents.converse import (
    IntentServiceSkillsActivateData, IntentServiceSkillsActivateMessage,
    IntentServiceSkillsDeactivateData, IntentServiceSkillsDeactivateMessage,
    SkillConversePongData, SkillConversePongMessage,
    SkillConverseResponseData, SkillConverseResponseMessage,
    ConverseMode,
)
from ovos_pydantic_models.intents.fallbacks import (
    FallbackMode,
    OvosSkillsFallbackRegisterData, OvosSkillsFallbackRegisterMessage,
    OvosSkillsFallbackPingData, OvosSkillsFallbackPingMessage,
    OvosSkillsFallbackPongData, OvosSkillsFallbackPongMessage,
    OvosSkillsFallbackRequestData, OvosSkillsFallbackRequestMessage,
    OvosSkillsFallbackResponseData, OvosSkillsFallbackResponseMessage,
)
from ovos_pydantic_models.intents.stop import (
    StopGlobalMessage, StopSkillData, StopSkillMessage,
    MycroftStopMessage,
    MycroftSkillsAbortQuestionData, MycroftSkillsAbortQuestionMessage,
    MycroftSkillsAbortExecutionData, MycroftSkillsAbortExecutionMessage,
    OvosSkillsConverseForceTimeoutData, OvosSkillsConverseForceTimeoutMessage,
)


class TestCoreIntentMessages:
    def test_utterance_handled(self):
        msg = OvosUtteranceHandledMessage()
        assert msg.message_type == "ovos.utterance.handled"

    def test_utterance_cancelled(self):
        msg = OvosUtteranceCancelledMessage()
        assert msg.message_type == "ovos.utterance.cancelled"

    def test_complete_intent_failure(self):
        data = CompleteIntentFailureData(utterance="what is blorg?", lang="en-us")
        msg = CompleteIntentFailureMessage(data=data)
        assert msg.message_type == "complete_intent_failure"
        assert msg.data.utterance == "what is blorg?"

    def test_add_context(self):
        data = AddContextData(context="location", word="home", origin="skill-weather.mycroft")
        msg = AddContextMessage(data=data)
        assert msg.message_type == "add_context"

    def test_remove_context(self):
        data = RemoveContextData(context="location")
        msg = RemoveContextMessage(data=data)
        assert msg.message_type == "remove_context"

    def test_clear_context(self):
        msg = ClearContextMessage()
        assert msg.message_type == "clear_context"

    def test_intent_get_with_lang(self):
        data = IntentServiceIntentGetData(utterance="what time is it", lang="en-us")
        msg = IntentServiceIntentGetMessage(data=data)
        assert msg.data.lang == "en-us"

    def test_intent_get_lang_optional(self):
        data = IntentServiceIntentGetData(utterance="what time is it")
        assert data.lang is None

    def test_skill_activate_dynamic(self):
        msg = SkillActivateMessage(message_type="my-skill.activate", data=SkillActivateData())
        assert msg.message_type == "my-skill.activate"

    def test_skill_deactivate_dynamic(self):
        msg = SkillDeactivateMessage(message_type="my-skill.deactivate")
        assert msg.message_type == "my-skill.deactivate"

    def test_roundtrip_serialization(self):
        data = CompleteIntentFailureData(utterance="test", lang="en-us")
        msg = CompleteIntentFailureMessage(data=data)
        restored = CompleteIntentFailureMessage.model_validate(msg.model_dump())
        assert restored.data.utterance == "test"


class TestConverseMessages:
    def test_converse_mode_values(self):
        assert ConverseMode.ACCEPT_ALL == "accept_all"

    def test_activate_with_timeout(self):
        data = IntentServiceSkillsActivateData(skill_id="skill-chat.mycroft", timeout=5.0)
        msg = IntentServiceSkillsActivateMessage(data=data)
        assert msg.message_type == "intent.service.skills.activate"
        assert msg.data.timeout == 5.0

    def test_activate_timeout_optional(self):
        data = IntentServiceSkillsActivateData(skill_id="skill-chat.mycroft")
        assert data.timeout is None

    def test_deactivate(self):
        data = IntentServiceSkillsDeactivateData(skill_id="skill-chat.mycroft")
        msg = IntentServiceSkillsDeactivateMessage(data=data)
        assert msg.message_type == "intent.service.skills.deactivate"

    def test_converse_pong(self):
        data = SkillConversePongData(skill_id="skill-music.mycroft", can_handle=True)
        msg = SkillConversePongMessage(data=data)
        assert msg.message_type == "skill.converse.pong"
        assert msg.data.can_handle is True

    def test_converse_response(self):
        data = SkillConverseResponseData(skill_id="skill-chat.mycroft", result=True)
        msg = SkillConverseResponseMessage(data=data)
        assert msg.message_type == "skill.converse.response"

    def test_roundtrip_serialization(self):
        data = IntentServiceSkillsActivateData(skill_id="skill-a.mycroft", timeout=10.0)
        msg = IntentServiceSkillsActivateMessage(data=data)
        restored = IntentServiceSkillsActivateMessage.model_validate(msg.model_dump())
        assert restored.data.skill_id == "skill-a.mycroft"
        assert restored.data.timeout == 10.0


class TestFallbackMessages:
    def test_fallback_mode_values(self):
        assert FallbackMode.BLACKLIST == "blacklist"

    def test_register(self):
        data = OvosSkillsFallbackRegisterData(skill_id="skill-fallback.mycroft", priority=50)
        msg = OvosSkillsFallbackRegisterMessage(data=data)
        assert msg.message_type == "ovos.skills.fallback.register"
        assert msg.data.priority == 50

    def test_register_default_priority(self):
        data = OvosSkillsFallbackRegisterData(skill_id="skill-fallback.mycroft")
        assert data.priority == 101

    def test_ping(self):
        data = OvosSkillsFallbackPingData(utterances=["test"], lang="en-us", range=(0, 100))
        msg = OvosSkillsFallbackPingMessage(data=data)
        assert msg.message_type == "ovos.skills.fallback.ping"
        assert msg.data.range == (0, 100)

    def test_pong(self):
        data = OvosSkillsFallbackPongData(skill_id="skill-fallback.mycroft", can_handle=False)
        msg = OvosSkillsFallbackPongMessage(data=data)
        assert msg.data.can_handle is False

    def test_dynamic_request(self):
        data = OvosSkillsFallbackRequestData(
            skill_id="skill-fallback.mycroft",
            utterances=["unknown question"],
            lang="en-us"
        )
        msg = OvosSkillsFallbackRequestMessage(
            message_type="ovos.skills.fallback.skill-fallback.mycroft.request",
            data=data
        )
        assert "fallback" in msg.message_type

    def test_response(self):
        data = OvosSkillsFallbackResponseData(result=True, fallback_handler="handle_unknown")
        msg = OvosSkillsFallbackResponseMessage(
            message_type="ovos.skills.fallback.skill-fallback.mycroft.response",
            data=data
        )
        assert msg.data.result is True

    def test_roundtrip_serialization(self):
        data = OvosSkillsFallbackRegisterData(skill_id="skill-a.mycroft", priority=75)
        msg = OvosSkillsFallbackRegisterMessage(data=data)
        restored = OvosSkillsFallbackRegisterMessage.model_validate(msg.model_dump())
        assert restored.data.priority == 75


class TestStopMessages:
    def test_global_stop(self):
        msg = StopGlobalMessage()
        assert msg.message_type == "stop:global"

    def test_skill_stop(self):
        data = StopSkillData(skill_id="skill-music.mycroft")
        msg = StopSkillMessage(data=data)
        assert msg.message_type == "stop:skill"

    def test_mycroft_stop(self):
        msg = MycroftStopMessage()
        assert msg.message_type == "mycroft.stop"

    def test_abort_question(self):
        data = MycroftSkillsAbortQuestionData(skill_id="skill-qa.mycroft")
        msg = MycroftSkillsAbortQuestionMessage(data=data)
        assert msg.message_type == "mycroft.skills.abort_question"

    def test_abort_execution(self):
        data = MycroftSkillsAbortExecutionData(skill_id="skill-qa.mycroft")
        msg = MycroftSkillsAbortExecutionMessage(data=data)
        assert msg.message_type == "mycroft.skills.abort_execution"

    def test_converse_force_timeout(self):
        data = OvosSkillsConverseForceTimeoutData(skill_id="skill-chat.mycroft")
        msg = OvosSkillsConverseForceTimeoutMessage(data=data)
        assert msg.message_type == "ovos.skills.converse.force_timeout"

    def test_roundtrip_serialization(self):
        data = StopSkillData(skill_id="skill-music.mycroft")
        msg = StopSkillMessage(data=data)
        restored = StopSkillMessage.model_validate(msg.model_dump())
        assert restored.data.skill_id == "skill-music.mycroft"
