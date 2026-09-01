import pytest
from pydantic import ValidationError

from ovos_pydantic_models.skills.ocp import (
    MediaType, PlaybackType, PlayerState, MatchConfidence, MediaState,
    MediaEntry, Playlist, PluginStream,
    OvosCommonPlayQueryData, OvosCommonPlayQueryMessage,
    OvosCommonPlayAnnounceData, OvosCommonPlayAnnounceMessage,
    OvosCommonPlayPlayerStateData, OvosCommonPlayPlayerStateMessage,
    OvosCommonPlayQueryResponseData, OvosCommonPlayQueryResponseMessage,
    OvosCommonPlaySkillsDetachData, OvosCommonPlaySkillsDetachMessage,
    OvosCommonPlayRegisterKeywordData, OvosCommonPlayRegisterKeywordMessage,
    OvosCommonPlayStatusResponseData, OvosCommonPlayStatusResponseMessage,
)
from ovos_pydantic_models.audio.ocp import OcpMediaState
from ovos_pydantic_models.skills.game import (
    SkillGameCommandData, SkillGameCommandMessage,
    OvosCommonPlaySkillPlayData, OvosCommonPlaySkillPlayMessage,
)
from ovos_pydantic_models.skills.common_query import (
    CQSMatchLevel,
    QuestionQueryData, QuestionQueryMessage,
    QuestionQueryResponseData, QuestionQueryResponseMessage,
)


class TestMediaEntry:
    def test_minimal(self):
        entry = MediaEntry(uri="https://example.com/song.mp3")
        assert entry.uri == "https://example.com/song.mp3"
        assert entry.media_type == MediaType.GENERIC
        assert entry.playback == PlaybackType.AUDIO

    def test_full_entry(self):
        entry = MediaEntry(
            uri="https://example.com/song.mp3",
            title="My Song",
            artist="My Artist",
            media_type=MediaType.MUSIC,
            match_confidence=MatchConfidence.HIGH,
        )
        assert entry.title == "My Song"
        assert entry.media_type == MediaType.MUSIC

    def test_game_specific_types(self):
        from ovos_pydantic_models.skills.ocp import MediaType as MT, PlaybackType as PT
        assert MT.GAME == "game"
        assert PT.SKILL == "skill"

    def test_roundtrip_serialization(self):
        entry = MediaEntry(uri="https://example.com/video.mp4", media_type=MediaType.VIDEO)
        restored = MediaEntry.model_validate(entry.model_dump())
        assert restored.uri == entry.uri
        assert restored.media_type == MediaType.VIDEO


class TestOcpQueryMessages:
    def test_query(self):
        data = OvosCommonPlayQueryData(phrase="play some jazz", question_type=MediaType.MUSIC)
        msg = OvosCommonPlayQueryMessage(data=data)
        assert msg.message_type == "ovos.common_play.query"
        assert msg.data.question_type == MediaType.MUSIC

    def test_query_response(self):
        entry = MediaEntry(uri="https://example.com/jazz.mp3", title="Jazz Tune")
        data = OvosCommonPlayQueryResponseData(
            phrase="play some jazz",
            skill_id="skill-music.mycroft",
            skill_name="Music",
            thumbnail="icon.png",
            results=[entry],
            searching=False
        )
        msg = OvosCommonPlayQueryResponseMessage(data=data)
        assert msg.message_type == "ovos.common_play.query.response"
        assert len(msg.data.results) == 1

    def test_player_state(self):
        data = OvosCommonPlayPlayerStateData(state=PlayerState.PLAYING)
        msg = OvosCommonPlayPlayerStateMessage(data=data)
        assert msg.data.state == PlayerState.PLAYING


class TestOcpStatusResponse:
    def test_ovos_media_snapshot(self):
        # shape emitted by PlayerSnapshot.as_status_dict in ovos-media
        payload = {
            "playback_type": 2,
            "media_type": 2,
            "player_state": 1,
            "loop_state": 0,
            "media_state": 6,
            "shuffle": False,
            "playlist_position": 0,
            "playlist_size": 3,
            "title": "My Song",
            "artist": "My Artist",
            "image": "https://example.com/art.png",
        }
        data = OvosCommonPlayStatusResponseData(**payload)
        msg = OvosCommonPlayStatusResponseMessage(data=data)
        assert msg.message_type == "ovos.common_play.status.response"
        assert msg.data.playback_type == 2
        assert msg.data.media_type == 2
        assert msg.data.player_state == 1
        assert msg.data.loop_state == 0
        assert msg.data.media_state == OcpMediaState.BUFFERED_MEDIA
        assert isinstance(msg.data.media_state, OcpMediaState)
        assert msg.data.shuffle is False
        assert msg.data.playlist_position == 0
        assert msg.data.playlist_size == 3
        assert msg.data.title == "My Song"
        assert msg.data.artist == "My Artist"
        assert msg.data.image == "https://example.com/art.png"

    def test_all_optional(self):
        data = OvosCommonPlayStatusResponseData()
        assert data.player_state is None
        assert data.media_state is None

    def test_announce(self):
        data = OvosCommonPlayAnnounceData(
            skill_id="skill-music.mycroft",
            skill_name="Music",
            thumbnail="icon.png",
            media_type=MediaType.MUSIC,
        )
        msg = OvosCommonPlayAnnounceMessage(data=data)
        assert msg.message_type == "ovos.common_play.announce"

    def test_register_keyword(self):
        data = OvosCommonPlayRegisterKeywordData(
            skill_id="skill-music.mycroft",
            label="artist_name",
            media_type=MediaType.MUSIC,
            samples=["Frank Sinatra", "Miles Davis"],
        )
        msg = OvosCommonPlayRegisterKeywordMessage(data=data)
        assert msg.message_type == "ovos.common_play.register_keyword"
        assert len(msg.data.samples) == 2

    def test_roundtrip_serialization(self):
        data = OvosCommonPlayQueryData(phrase="play jazz")
        msg = OvosCommonPlayQueryMessage(data=data)
        restored = OvosCommonPlayQueryMessage.model_validate(msg.model_dump())
        assert restored.data.phrase == "play jazz"


class TestGameSkillMessages:
    def test_game_command(self):
        data = SkillGameCommandData(utterances=["go north", "attack dragon"], lang="en-us")
        msg = SkillGameCommandMessage(message_type="my-game-skill.game_cmd", data=data)
        assert "game_cmd" in msg.message_type
        assert msg.data.utterances[0] == "go north"

    def test_game_command_requires_message_type(self):
        with pytest.raises(ValidationError):
            SkillGameCommandMessage(data=SkillGameCommandData(utterances=["test"], lang="en-us"))

    def test_ocp_skill_play(self):
        entry = MediaEntry(uri="skill:my-game.mycroft", playback=PlaybackType.SKILL)
        data = OvosCommonPlaySkillPlayData(
            skill_id="my-game.mycroft",
            skill_name="My Game",
            thumbnail="icon.png",
            playlist=[entry],
        )
        msg = OvosCommonPlaySkillPlayMessage(data=data)
        assert msg.message_type == "ovos.common_play.skill.play"

    def test_roundtrip_serialization(self):
        data = SkillGameCommandData(utterances=["move left"], lang="en-us")
        msg = SkillGameCommandMessage(message_type="game.game_cmd", data=data)
        restored = SkillGameCommandMessage.model_validate(msg.model_dump())
        assert restored.data.utterances == ["move left"]


class TestCommonQueryMessages:
    def test_cqs_match_level(self):
        assert CQSMatchLevel.EXACT == 1
        assert CQSMatchLevel.GENERAL == 3

    def test_question_query(self):
        data = QuestionQueryData(phrase="what is the capital of France?")
        msg = QuestionQueryMessage(data=data)
        assert msg.message_type == "question:query"
        assert msg.data.phrase == "what is the capital of France?"

    def test_question_response_with_answer(self):
        data = QuestionQueryResponseData(
            phrase="what is the capital of France?",
            skill_id="skill-wiki.mycroft",
            searching=False,
            answer="Paris is the capital of France.",
            conf=0.9,
        )
        msg = QuestionQueryResponseMessage(data=data)
        assert msg.data.answer == "Paris is the capital of France."

    def test_question_response_searching(self):
        data = QuestionQueryResponseData(
            phrase="what is blorg?",
            skill_id="skill-wiki.mycroft",
            searching=True,
        )
        msg = QuestionQueryResponseMessage(data=data)
        assert msg.data.searching is True

    def test_roundtrip_serialization(self):
        data = QuestionQueryData(phrase="test question")
        msg = QuestionQueryMessage(data=data)
        restored = QuestionQueryMessage.model_validate(msg.model_dump())
        assert restored.data.phrase == "test question"
