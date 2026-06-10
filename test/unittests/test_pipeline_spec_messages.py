"""
Tests for the PIPELINE-1, STOP-1 spec messages, and PHAL tools bus surface.

Covers:
- ovos.utterance.handle (PIPELINE-1 §9.1)
- ovos.intent.matched (PIPELINE-1 §9.2)
- ovos.intent.unmatched (PIPELINE-1 §9.3)
- ovos.intent.handler.start / .complete / .error (PIPELINE-1 §8)
- ovos.utterance.speak (PIPELINE-1 §9.6)
- ovos.stop.ping / ovos.stop.pong / ovos.stop (STOP-1 §4-5)
- ovos.tools.* (ovos-PHAL-plugin-tools)
"""
import pytest
from pydantic import ValidationError

from ovos_pydantic_models.intents.core import (
    # PIPELINE-1 utterance lifecycle
    OvosUtteranceHandleData, OvosUtteranceHandleMessage,
    OvosIntentMatchedData, OvosIntentMatchedMessage,
    OvosIntentUnmatchedData, OvosIntentUnmatchedMessage,
    OvosIntentHandlerStartData, OvosIntentHandlerStartMessage,
    OvosIntentHandlerCompleteData, OvosIntentHandlerCompleteMessage,
    OvosIntentHandlerErrorData, OvosIntentHandlerErrorMessage,
    OvosUtteranceSpeakData, OvosUtteranceSpeakMessage,
    # STOP-1
    OvosStopPingMessage,
    OvosStopPongData, OvosStopPongMessage,
    OvosStopMessage,
)
from ovos_pydantic_models.phal.tools import (
    ToolEntry,
    OvosToolsListMessage, OvosToolsListResponseData, OvosToolsListResponseMessage,
    OvosToolsGetData, OvosToolsGetMessage,
    OvosToolsGetResponseData, OvosToolsGetResponseMessage,
    OvosToolsInvokeData, OvosToolsInvokeMessage,
    OvosToolsInvokeResponseData, OvosToolsInvokeResponseMessage,
    OvosToolsReloadMessage, OvosToolsReloadResponseData, OvosToolsReloadResponseMessage,
)


# ---------------------------------------------------------------------------
# PIPELINE-1 §9.1 — ovos.utterance.handle
# ---------------------------------------------------------------------------

class TestOvosUtteranceHandle:
    def test_basic(self):
        msg = OvosUtteranceHandleMessage(
            data=OvosUtteranceHandleData(utterances=["turn off the lights"], lang="en-US")
        )
        assert msg.message_type == "ovos.utterance.handle"
        assert msg.data.utterances == ["turn off the lights"]
        assert msg.data.lang == "en-US"

    def test_lang_optional(self):
        msg = OvosUtteranceHandleMessage(
            data=OvosUtteranceHandleData(utterances=["hello"])
        )
        assert msg.data.lang is None

    def test_utterances_required(self):
        with pytest.raises(ValidationError):
            OvosUtteranceHandleData(lang="en-US")

    def test_utterances_nonempty(self):
        with pytest.raises(ValidationError):
            OvosUtteranceHandleData(utterances=[])

    def test_roundtrip(self):
        msg = OvosUtteranceHandleMessage(
            data=OvosUtteranceHandleData(utterances=["play something"], lang="en-US")
        )
        restored = OvosUtteranceHandleMessage.model_validate(msg.model_dump())
        assert restored.data.utterances == ["play something"]
        assert restored.data.lang == "en-US"


# ---------------------------------------------------------------------------
# PIPELINE-1 §9.2 — ovos.intent.matched
# ---------------------------------------------------------------------------

class TestOvosIntentMatched:
    def test_basic(self):
        data = OvosIntentMatchedData(
            skill_id="music.skill",
            intent_name="play_music",
            lang="en-US",
            utterance="play the beatles",
            pipeline_id="template-high",
        )
        msg = OvosIntentMatchedMessage(data=data)
        assert msg.message_type == "ovos.intent.matched"
        assert msg.data.skill_id == "music.skill"
        assert msg.data.pipeline_id == "template-high"

    def test_slots_optional(self):
        data = OvosIntentMatchedData(
            skill_id="s", intent_name="i", lang="en-US",
            utterance="test", pipeline_id="p",
        )
        assert data.slots is None

    def test_slots_populated(self):
        data = OvosIntentMatchedData(
            skill_id="s", intent_name="i", lang="en-US",
            utterance="test", pipeline_id="p",
            slots={"query": "the beatles"},
        )
        assert data.slots["query"] == "the beatles"

    def test_required_fields(self):
        with pytest.raises(ValidationError):
            OvosIntentMatchedData(skill_id="s", intent_name="i", lang="en-US", utterance="t")

    def test_roundtrip(self):
        data = OvosIntentMatchedData(
            skill_id="s", intent_name="i", lang="en-US",
            utterance="hello", pipeline_id="p",
        )
        msg = OvosIntentMatchedMessage(data=data)
        restored = OvosIntentMatchedMessage.model_validate(msg.model_dump())
        assert restored.data.skill_id == "s"


# ---------------------------------------------------------------------------
# PIPELINE-1 §9.3 — ovos.intent.unmatched
# ---------------------------------------------------------------------------

class TestOvosIntentUnmatched:
    def test_empty_payload(self):
        msg = OvosIntentUnmatchedMessage()
        assert msg.message_type == "ovos.intent.unmatched"
        assert msg.data.utterances is None
        assert msg.data.lang is None

    def test_with_payload(self):
        data = OvosIntentUnmatchedData(utterances=["turn off lights"], lang="en-US")
        msg = OvosIntentUnmatchedMessage(data=data)
        assert msg.data.utterances == ["turn off lights"]

    def test_roundtrip(self):
        msg = OvosIntentUnmatchedMessage(
            data=OvosIntentUnmatchedData(utterances=["x"], lang="de-DE")
        )
        restored = OvosIntentUnmatchedMessage.model_validate(msg.model_dump())
        assert restored.data.lang == "de-DE"


# ---------------------------------------------------------------------------
# PIPELINE-1 §8 — handler lifecycle trio
# ---------------------------------------------------------------------------

class TestHandlerLifecycle:
    def test_start(self):
        data = OvosIntentHandlerStartData(skill_id="timer.skill", intent_name="SetTimerIntent")
        msg = OvosIntentHandlerStartMessage(data=data)
        assert msg.message_type == "ovos.intent.handler.start"
        assert msg.data.skill_id == "timer.skill"

    def test_start_requires_skill_and_intent(self):
        with pytest.raises(ValidationError):
            OvosIntentHandlerStartData(skill_id="s")

    def test_complete(self):
        data = OvosIntentHandlerCompleteData(skill_id="timer.skill", intent_name="SetTimerIntent")
        msg = OvosIntentHandlerCompleteMessage(data=data)
        assert msg.message_type == "ovos.intent.handler.complete"

    def test_error(self):
        data = OvosIntentHandlerErrorData(
            skill_id="timer.skill", intent_name="SetTimerIntent",
            exception="ValueError: bad input",
        )
        msg = OvosIntentHandlerErrorMessage(data=data)
        assert msg.message_type == "ovos.intent.handler.error"
        assert "ValueError" in msg.data.exception

    def test_error_requires_exception(self):
        with pytest.raises(ValidationError):
            OvosIntentHandlerErrorData(skill_id="s", intent_name="i")

    def test_start_roundtrip(self):
        msg = OvosIntentHandlerStartMessage(
            data=OvosIntentHandlerStartData(skill_id="s", intent_name="i", pipeline_id="p")
        )
        r = OvosIntentHandlerStartMessage.model_validate(msg.model_dump())
        assert r.data.pipeline_id == "p"

    def test_complete_roundtrip(self):
        msg = OvosIntentHandlerCompleteMessage(
            data=OvosIntentHandlerCompleteData(skill_id="s", intent_name="i")
        )
        r = OvosIntentHandlerCompleteMessage.model_validate(msg.model_dump())
        assert r.data.skill_id == "s"

    def test_error_roundtrip(self):
        msg = OvosIntentHandlerErrorMessage(
            data=OvosIntentHandlerErrorData(skill_id="s", intent_name="i", exception="err")
        )
        r = OvosIntentHandlerErrorMessage.model_validate(msg.model_dump())
        assert r.data.exception == "err"


# ---------------------------------------------------------------------------
# PIPELINE-1 §9.6 — ovos.utterance.speak
# ---------------------------------------------------------------------------

class TestOvosUtteranceSpeak:
    def test_basic(self):
        msg = OvosUtteranceSpeakMessage(
            data=OvosUtteranceSpeakData(utterance="It is sunny.", lang="en-US")
        )
        assert msg.message_type == "ovos.utterance.speak"
        assert msg.data.utterance == "It is sunny."

    def test_lang_optional(self):
        msg = OvosUtteranceSpeakMessage(
            data=OvosUtteranceSpeakData(utterance="Hallo.")
        )
        assert msg.data.lang is None

    def test_utterance_required(self):
        with pytest.raises(ValidationError):
            OvosUtteranceSpeakData(lang="en-US")

    def test_roundtrip(self):
        msg = OvosUtteranceSpeakMessage(
            data=OvosUtteranceSpeakData(utterance="Hello world", lang="en-US")
        )
        r = OvosUtteranceSpeakMessage.model_validate(msg.model_dump())
        assert r.data.utterance == "Hello world"


# ---------------------------------------------------------------------------
# STOP-1 §4-5 — ovos.stop.ping / pong / stop
# ---------------------------------------------------------------------------

class TestStopSpecMessages:
    def test_ping(self):
        msg = OvosStopPingMessage()
        assert msg.message_type == "ovos.stop.ping"

    def test_pong_can_handle_true(self):
        data = OvosStopPongData(can_handle=True, skill_id="timer.skill")
        msg = OvosStopPongMessage(data=data)
        assert msg.message_type == "ovos.stop.pong"
        assert msg.data.can_handle is True
        assert msg.data.skill_id == "timer.skill"

    def test_pong_can_handle_false(self):
        data = OvosStopPongData(can_handle=False)
        msg = OvosStopPongMessage(data=data)
        assert msg.data.can_handle is False
        assert msg.data.skill_id is None

    def test_pong_requires_can_handle(self):
        with pytest.raises(ValidationError):
            OvosStopPongData(skill_id="s")

    def test_stop_broadcast(self):
        msg = OvosStopMessage()
        assert msg.message_type == "ovos.stop"

    def test_pong_roundtrip(self):
        msg = OvosStopPongMessage(data=OvosStopPongData(can_handle=True, skill_id="s"))
        r = OvosStopPongMessage.model_validate(msg.model_dump())
        assert r.data.skill_id == "s"


# ---------------------------------------------------------------------------
# PHAL tools bus surface
# ---------------------------------------------------------------------------

MINIMAL_SCHEMA = {"type": "object", "properties": {}}

SAMPLE_TOOL = ToolEntry(
    name="add",
    description="Add two integers.",
    argument_schema={"type": "object", "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}}},
    output_schema={"type": "object", "properties": {"result": {"type": "integer"}}},
    toolbox_id="math_tools",
)


class TestOvosToolsList:
    def test_request(self):
        msg = OvosToolsListMessage()
        assert msg.message_type == "ovos.tools.list"

    def test_response(self):
        data = OvosToolsListResponseData(tools=[SAMPLE_TOOL])
        msg = OvosToolsListResponseMessage(data=data)
        assert msg.message_type == "ovos.tools.list.response"
        assert len(msg.data.tools) == 1
        assert msg.data.tools[0].name == "add"

    def test_empty_tools_list(self):
        data = OvosToolsListResponseData(tools=[])
        msg = OvosToolsListResponseMessage(data=data)
        assert msg.data.tools == []

    def test_roundtrip(self):
        data = OvosToolsListResponseData(tools=[SAMPLE_TOOL])
        msg = OvosToolsListResponseMessage(data=data)
        r = OvosToolsListResponseMessage.model_validate(msg.model_dump())
        assert r.data.tools[0].toolbox_id == "math_tools"


class TestOvosToolsGet:
    def test_request(self):
        msg = OvosToolsGetMessage(data=OvosToolsGetData(name="add"))
        assert msg.message_type == "ovos.tools.get"
        assert msg.data.name == "add"

    def test_request_name_required(self):
        with pytest.raises(ValidationError):
            OvosToolsGetData()

    def test_response_success(self):
        data = OvosToolsGetResponseData(
            name="add",
            description="Add two integers.",
            argument_schema=MINIMAL_SCHEMA,
            output_schema=MINIMAL_SCHEMA,
            toolbox_id="math_tools",
        )
        msg = OvosToolsGetResponseMessage(data=data)
        assert msg.message_type == "ovos.tools.get.response"
        assert msg.data.error is None

    def test_response_error(self):
        data = OvosToolsGetResponseData(error="Unknown tool: 'nonexistent'")
        msg = OvosToolsGetResponseMessage(data=data)
        assert "nonexistent" in msg.data.error

    def test_roundtrip_success(self):
        data = OvosToolsGetResponseData(
            name="add", description="d",
            argument_schema=MINIMAL_SCHEMA, output_schema=MINIMAL_SCHEMA,
            toolbox_id="tb",
        )
        msg = OvosToolsGetResponseMessage(data=data)
        r = OvosToolsGetResponseMessage.model_validate(msg.model_dump())
        assert r.data.toolbox_id == "tb"


class TestOvosToolsInvoke:
    def test_request(self):
        msg = OvosToolsInvokeMessage(data=OvosToolsInvokeData(name="add", args={"a": 3, "b": 4}))
        assert msg.message_type == "ovos.tools.invoke"
        assert msg.data.args == {"a": 3, "b": 4}

    def test_request_name_required(self):
        with pytest.raises(ValidationError):
            OvosToolsInvokeData(args={"a": 1})

    def test_args_default_empty(self):
        msg = OvosToolsInvokeMessage(data=OvosToolsInvokeData(name="ping"))
        assert msg.data.args == {}

    def test_response_success(self):
        data = OvosToolsInvokeResponseData(name="add", result={"result": 7})
        msg = OvosToolsInvokeResponseMessage(data=data)
        assert msg.message_type == "ovos.tools.invoke.response"
        assert msg.data.result == {"result": 7}
        assert msg.data.error is None

    def test_response_error(self):
        data = OvosToolsInvokeResponseData(name="add", error="ValueError: bad input")
        msg = OvosToolsInvokeResponseMessage(data=data)
        assert "ValueError" in msg.data.error

    def test_response_name_required(self):
        with pytest.raises(ValidationError):
            OvosToolsInvokeResponseData(result={"x": 1})

    def test_roundtrip(self):
        data = OvosToolsInvokeResponseData(name="add", result={"result": 42})
        msg = OvosToolsInvokeResponseMessage(data=data)
        r = OvosToolsInvokeResponseMessage.model_validate(msg.model_dump())
        assert r.data.result["result"] == 42


class TestOvosToolsReload:
    def test_request(self):
        msg = OvosToolsReloadMessage()
        assert msg.message_type == "ovos.tools.reload"

    def test_response(self):
        data = OvosToolsReloadResponseData(loaded=["math_tools"], total_tools=3)
        msg = OvosToolsReloadResponseMessage(data=data)
        assert msg.message_type == "ovos.tools.reload.response"
        assert msg.data.total_tools == 3
        assert "math_tools" in msg.data.loaded

    def test_response_requires_loaded_and_total(self):
        with pytest.raises(ValidationError):
            OvosToolsReloadResponseData(loaded=["x"])  # missing total_tools

    def test_roundtrip(self):
        data = OvosToolsReloadResponseData(loaded=["tb1", "tb2"], total_tools=5)
        msg = OvosToolsReloadResponseMessage(data=data)
        r = OvosToolsReloadResponseMessage.model_validate(msg.model_dump())
        assert r.data.total_tools == 5
