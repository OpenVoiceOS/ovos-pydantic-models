import pytest
from pydantic import ValidationError

from ovos_pydantic_models.audio.playback import (
    SpeakData, SpeakMessage,
    MycroftAudioQueueData, MycroftAudioQueueMessage,
    MycroftAudioPlaySoundData, MycroftAudioPlaySoundMessage,
)
from ovos_pydantic_models.audio.ocp import OcpMediaState, OvosCommonPlayMediaStateData, OvosCommonPlayMediaStateMessage
from ovos_pydantic_models.audio.audioservice import (
    AudioServicePlayData, AudioServicePlayMessage,
    AudioServiceSeekForwardData, AudioServiceSeekForwardMessage,
)
from ovos_pydantic_models.audio.opm import (
    OvosLanguagesTtsMessage, OvosLanguagesTtsReplyData, OvosLanguagesTtsResponseMessage,
)


class TestSpeakMessage:
    def test_instantiation(self):
        msg = SpeakMessage(data=SpeakData(utterance="hello world"))
        assert msg.message_type == "speak"
        assert msg.data.utterance == "hello world"
        assert msg.data.expect_response is False

    def test_with_expect_response(self):
        msg = SpeakMessage(data=SpeakData(utterance="what is your name?", expect_response=True))
        assert msg.data.expect_response is True

    def test_utterance_required(self):
        with pytest.raises(ValidationError):
            SpeakData()

    def test_roundtrip_serialization(self):
        msg = SpeakMessage(data=SpeakData(utterance="hello"))
        restored = SpeakMessage.model_validate(msg.model_dump())
        assert restored.data.utterance == "hello"


class TestAudioQueueMessage:
    def test_with_uri(self):
        data = MycroftAudioQueueData(uri="file:///tmp/audio.wav")
        msg = MycroftAudioQueueMessage(data=data)
        assert msg.message_type == "mycroft.audio.queue"
        assert msg.data.uri == "file:///tmp/audio.wav"

    def test_with_binary_data(self):
        data = MycroftAudioQueueData(binary_data="deadbeef", audio_ext="wav")
        assert data.binary_data == "deadbeef"

    def test_requires_uri_or_binary(self):
        with pytest.raises(ValidationError):
            MycroftAudioQueueData()  # neither uri nor binary_data

    def test_roundtrip_serialization(self):
        data = MycroftAudioQueueData(uri="file:///tmp/test.wav", listen=True)
        msg = MycroftAudioQueueMessage(data=data)
        restored = MycroftAudioQueueMessage.model_validate(msg.model_dump())
        assert restored.data.uri == data.uri
        assert restored.data.listen is True


class TestOcpMediaState:
    def test_values(self):
        assert OcpMediaState.UNKNOWN == 0
        assert OcpMediaState.BUFFERED_MEDIA == 6
        assert OcpMediaState.END_OF_MEDIA == 7

    def test_media_state_message(self):
        msg = OvosCommonPlayMediaStateMessage(
            data=OvosCommonPlayMediaStateData(state=OcpMediaState.BUFFERING_MEDIA)
        )
        assert msg.message_type == "ovos.common_play.media.state"
        assert msg.data.state == OcpMediaState.BUFFERING_MEDIA

    def test_roundtrip_serialization(self):
        msg = OvosCommonPlayMediaStateMessage(
            data=OvosCommonPlayMediaStateData(state=OcpMediaState.LOADED_MEDIA)
        )
        restored = OvosCommonPlayMediaStateMessage.model_validate(msg.model_dump())
        assert restored.data.state == OcpMediaState.LOADED_MEDIA


class TestAudioServiceMessages:
    def test_play_message(self):
        data = AudioServicePlayData(tracks=["file:///song.mp3", ("http://stream.url", "audio/mpeg")])
        msg = AudioServicePlayMessage(data=data)
        assert msg.message_type == "mycroft.audio.service.play"
        assert len(msg.data.tracks) == 2

    def test_seek_forward(self):
        data = AudioServiceSeekForwardData(seconds=10)
        msg = AudioServiceSeekForwardMessage(data=data)
        assert msg.data.seconds == 10

    def test_roundtrip_serialization(self):
        data = AudioServicePlayData(tracks=["file:///song.mp3"])
        msg = AudioServicePlayMessage(data=data)
        restored = AudioServicePlayMessage.model_validate(msg.model_dump())
        assert restored.data.tracks == msg.data.tracks


class TestTtsLanguageMessages:
    def test_request(self):
        msg = OvosLanguagesTtsMessage()
        assert msg.message_type == "ovos.languages.tts"

    def test_response(self):
        data = OvosLanguagesTtsReplyData(langs=["en-us", "es-es", "fr-fr"])
        msg = OvosLanguagesTtsResponseMessage(data=data)
        assert msg.message_type == "ovos.languages.tts.response"
        assert "en-us" in msg.data.langs

    def test_roundtrip_serialization(self):
        data = OvosLanguagesTtsReplyData(langs=["en-us"])
        msg = OvosLanguagesTtsResponseMessage(data=data)
        restored = OvosLanguagesTtsResponseMessage.model_validate(msg.model_dump())
        assert restored.data.langs == ["en-us"]
