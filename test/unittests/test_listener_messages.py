import pytest
from pydantic import ValidationError

from ovos_pydantic_models.listener.recognizer_loop import (
    ListeningState,
    RecognizerLoopUtteranceData, RecognizerLoopUtteranceMessage,
    RecognizerLoopWakeWordData, RecognizerLoopWakeWordMessage,
    RecognizerLoopStateSetData, RecognizerLoopStateSetMessage,
    RecognizerLoopStateGetMessage, RecognizerLoopStateGetReplyData, RecognizerLoopStateResponseMessage,
    MycroftMicMuteMessage, MycroftMicListenMessage,
)
from ovos_pydantic_models.listener.opm import (
    OvosLanguagesSttMessage, OvosLanguagesSttReplyData, OvosLanguagesSttResponseMessage,
    OpmWwQueryMessage,
)


class TestListeningState:
    def test_values(self):
        assert ListeningState.SLEEPING == "sleeping"
        assert ListeningState.WAITING_FOR_WAKEWORD == "waiting_for_wakeword"
        assert ListeningState.RECORDING == "recording"


class TestRecognizerLoopUtteranceMessage:
    def test_instantiation(self):
        data = RecognizerLoopUtteranceData(utterances=["hello world"], lang="en-us")
        msg = RecognizerLoopUtteranceMessage(data=data)
        assert msg.message_type == "recognizer_loop:utterance"
        assert msg.data.utterances == ["hello world"]
        assert msg.data.lang == "en-us"

    def test_utterances_required(self):
        with pytest.raises(ValidationError):
            RecognizerLoopUtteranceData(lang="en-us")

    def test_optional_fields(self):
        data = RecognizerLoopUtteranceData(
            utterances=["test"], lang="en-us",
            filename="file:///tmp/audio.wav",
            transcriptions=[("test", 0.95)]
        )
        assert data.filename == "file:///tmp/audio.wav"
        assert data.transcriptions[0][1] == 0.95

    def test_roundtrip_serialization(self):
        data = RecognizerLoopUtteranceData(utterances=["play music"], lang="en-us")
        msg = RecognizerLoopUtteranceMessage(data=data)
        restored = RecognizerLoopUtteranceMessage.model_validate(msg.model_dump())
        assert restored.data.utterances == ["play music"]


class TestRecognizerLoopWakeWordMessage:
    def test_instantiation(self):
        data = RecognizerLoopWakeWordData(
            key_phrase="hey mycroft",
            engine="abc123",
            time="1234567890",
            sessionId="sess-1",
            accountId="Anon",
            model="model-hash"
        )
        msg = RecognizerLoopWakeWordMessage(data=data)
        assert msg.message_type == "recognizer_loop:wakeword"
        assert msg.data.key_phrase == "hey mycroft"

    def test_key_phrase_required(self):
        with pytest.raises(ValidationError):
            RecognizerLoopWakeWordData(engine="x", time="0", sessionId="s", accountId="a", model="m")

    def test_roundtrip_serialization(self):
        data = RecognizerLoopWakeWordData(
            key_phrase="hey computer", engine="e", time="0", sessionId="s", accountId="a", model="m"
        )
        msg = RecognizerLoopWakeWordMessage(data=data)
        restored = RecognizerLoopWakeWordMessage.model_validate(msg.model_dump())
        assert restored.data.key_phrase == "hey computer"


class TestListenerStateMessages:
    def test_state_set(self):
        data = RecognizerLoopStateSetData(state=ListeningState.RECORDING)
        msg = RecognizerLoopStateSetMessage(data=data)
        assert msg.message_type == "recognizer_loop:state.set"
        assert msg.data.state == ListeningState.RECORDING

    def test_state_get(self):
        msg = RecognizerLoopStateGetMessage()
        assert msg.message_type == "recognizer_loop:state.get"

    def test_state_response(self):
        data = RecognizerLoopStateGetReplyData(state=ListeningState.SLEEPING)
        msg = RecognizerLoopStateResponseMessage(data=data)
        assert msg.data.state == ListeningState.SLEEPING

    def test_roundtrip_serialization(self):
        data = RecognizerLoopStateSetData(state=ListeningState.MUTED)
        msg = RecognizerLoopStateSetMessage(data=data)
        restored = RecognizerLoopStateSetMessage.model_validate(msg.model_dump())
        assert restored.data.state == ListeningState.MUTED


class TestMicMessages:
    def test_mute(self):
        msg = MycroftMicMuteMessage()
        assert msg.message_type == "mycroft.mic.mute"

    def test_listen(self):
        msg = MycroftMicListenMessage()
        assert msg.message_type == "mycroft.mic.listen"


class TestOpmMessages:
    def test_stt_languages_request(self):
        msg = OvosLanguagesSttMessage()
        assert msg.message_type == "ovos.languages.stt"

    def test_stt_languages_response(self):
        data = OvosLanguagesSttReplyData(langs=["en-us", "de-de"])
        msg = OvosLanguagesSttResponseMessage(data=data)
        assert "de-de" in msg.data.langs

    def test_ww_query(self):
        msg = OpmWwQueryMessage()
        assert msg.message_type == "opm.ww.query"

    def test_roundtrip_serialization(self):
        data = OvosLanguagesSttReplyData(langs=["en-us"])
        msg = OvosLanguagesSttResponseMessage(data=data)
        restored = OvosLanguagesSttResponseMessage.model_validate(msg.model_dump())
        assert restored.data.langs == ["en-us"]
