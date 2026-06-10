"""
Tests for SESSION-1 / SESSION-2 / BRIDGE-1 / AUDIO-IN-1 spec models.

Coverage:
  - SESSION-1 §3 field registry completeness on the Session model
  - SESSION-1 §3.2 language-field semantics (secondary_langs, output_lang,
    stt_lang, request_lang, detected_lang)
  - SESSION-1 §3.3 site_id
  - PIPELINE-1 §7.1 ActiveHandlerEntry within Session.active_handlers
  - CONVERSE-1 §2.2 ResponseMode within Session.response_mode
  - TRANSFORM-1 §5 transformer lists and §5.2 blacklists
  - PIPELINE-1 §5 blacklisted_pipelines
  - SESSION-2 §2.7 OvosSessionSyncMessage — data.session carries the snapshot
  - Round-trip serialization for all new models
  - Rejection tests for missing required fields
"""
import time

import pytest
from pydantic import ValidationError

from ovos_pydantic_models.session import (
    Session,
    ActiveHandlerEntry,
    ResponseMode,
    IntentContextManager,
    ContextEntity,
    UtteranceState,
)
from ovos_pydantic_models.core.session import (
    OvosSessionSyncData,
    OvosSessionSyncMessage,
    OvosSessionUpdateDefaultData,
    OvosSessionUpdateDefaultMessage,
)


# ---------------------------------------------------------------------------
# ActiveHandlerEntry
# ---------------------------------------------------------------------------

class TestActiveHandlerEntry:
    def test_required_skill_id(self):
        e = ActiveHandlerEntry(skill_id="ovos-skill-weather.openvoiceos")
        assert e.skill_id == "ovos-skill-weather.openvoiceos"
        assert isinstance(e.activated_at, float)

    def test_explicit_activated_at(self):
        ts = 1_700_000_000.0
        e = ActiveHandlerEntry(skill_id="skill-x", activated_at=ts)
        assert e.activated_at == ts

    def test_missing_skill_id_raises(self):
        with pytest.raises(ValidationError):
            ActiveHandlerEntry()

    def test_roundtrip(self):
        e = ActiveHandlerEntry(skill_id="skill-a", activated_at=1.0)
        restored = ActiveHandlerEntry.model_validate(e.model_dump())
        assert restored.skill_id == "skill-a"

    def test_extra_fields_allowed(self):
        # extra='allow' — additional spec-defined fields should survive round-trip
        e = ActiveHandlerEntry(skill_id="s", activated_at=0.0, converse_active=True)
        assert e.model_dump()["converse_active"] is True


# ---------------------------------------------------------------------------
# ResponseMode
# ---------------------------------------------------------------------------

class TestResponseMode:
    def test_valid(self):
        rm = ResponseMode(skill_id="skill-q", expires_at=time.time() + 30)
        assert rm.skill_id == "skill-q"
        assert rm.expires_at > 0

    def test_missing_fields_raise(self):
        with pytest.raises(ValidationError):
            ResponseMode(skill_id="s")  # expires_at missing
        with pytest.raises(ValidationError):
            ResponseMode(expires_at=0.0)  # skill_id missing

    def test_roundtrip(self):
        rm = ResponseMode(skill_id="s", expires_at=9999.0)
        restored = ResponseMode.model_validate(rm.model_dump())
        assert restored.expires_at == 9999.0


# ---------------------------------------------------------------------------
# Session — SESSION-1 §3 field registry
# ---------------------------------------------------------------------------

class TestSessionFieldRegistry:
    """Verify that every SESSION-1 §3 registered field is present on Session."""

    _SESSION1_FIELDS = [
        # §3.1
        "session_id",
        # §3.2
        "lang", "secondary_langs", "output_lang", "stt_lang",
        "request_lang", "detected_lang",
        # §3.3
        "site_id",
        # PIPELINE-1 §5
        "pipeline", "blacklisted_skills", "blacklisted_intents", "blacklisted_pipelines",
        # PIPELINE-1 §7.1
        "active_handlers",
        # CONVERSE-1 §2.2
        "response_mode",
        # TRANSFORM-1 §5
        "audio_transformers", "utterance_transformers", "metadata_transformers",
        "intent_transformers", "dialog_transformers", "tts_transformers",
        # TRANSFORM-1 §5.2
        "blacklisted_audio_transformers", "blacklisted_utterance_transformers",
        "blacklisted_metadata_transformers", "blacklisted_intent_transformers",
        "blacklisted_dialog_transformers", "blacklisted_tts_transformers",
    ]

    def test_all_spec_fields_present(self):
        s = Session()
        for field in self._SESSION1_FIELDS:
            assert hasattr(s, field), f"Session is missing SESSION-1 field '{field}'"

    def test_default_session_id(self):
        s = Session()
        assert s.session_id == "default"

    def test_custom_session_id(self):
        s = Session(session_id="sat-abc")
        assert s.session_id == "sat-abc"

    def test_default_lang(self):
        s = Session()
        assert s.lang == "en-us"

    def test_secondary_langs_default_empty(self):
        s = Session()
        assert s.secondary_langs == []

    def test_language_fields_nullable(self):
        s = Session()
        assert s.output_lang is None
        assert s.stt_lang is None
        assert s.request_lang is None
        assert s.detected_lang is None

    def test_language_fields_set(self):
        s = Session(
            lang="pt-pt",
            secondary_langs=["en-us", "es-es"],
            output_lang="pt-br",
            stt_lang="pt-pt",
            request_lang="en-us",
            detected_lang="pt-pt",
        )
        assert s.lang == "pt-pt"
        assert "en-us" in s.secondary_langs
        assert s.output_lang == "pt-br"
        assert s.stt_lang == "pt-pt"
        assert s.request_lang == "en-us"
        assert s.detected_lang == "pt-pt"

    def test_site_id_default(self):
        s = Session()
        assert s.site_id == "unknown"

    def test_site_id_set(self):
        s = Session(site_id="living-room")
        assert s.site_id == "living-room"

    def test_active_handlers_default_empty(self):
        s = Session()
        assert s.active_handlers == []

    def test_active_handlers_set(self):
        h = ActiveHandlerEntry(skill_id="ovos-skill-hello", activated_at=1.0)
        s = Session(active_handlers=[h])
        assert len(s.active_handlers) == 1
        assert s.active_handlers[0].skill_id == "ovos-skill-hello"

    def test_response_mode_default_none(self):
        s = Session()
        assert s.response_mode is None

    def test_response_mode_set(self):
        rm = ResponseMode(skill_id="ovos-skill-qa", expires_at=time.time() + 10)
        s = Session(response_mode=rm)
        assert s.response_mode is not None
        assert s.response_mode.skill_id == "ovos-skill-qa"

    def test_transformer_lists_default_empty(self):
        s = Session()
        for f in [
            "audio_transformers", "utterance_transformers", "metadata_transformers",
            "intent_transformers", "dialog_transformers", "tts_transformers",
        ]:
            assert getattr(s, f) == [], f"{f} should default to []"

    def test_transformer_lists_set(self):
        s = Session(
            audio_transformers=["ovos-audio-transformer-denoiser"],
            tts_transformers=["ovos-tts-transformer-style"],
        )
        assert s.audio_transformers == ["ovos-audio-transformer-denoiser"]
        assert s.tts_transformers == ["ovos-tts-transformer-style"]

    def test_transformer_blacklists_default_empty(self):
        s = Session()
        for f in [
            "blacklisted_audio_transformers", "blacklisted_utterance_transformers",
            "blacklisted_metadata_transformers", "blacklisted_intent_transformers",
            "blacklisted_dialog_transformers", "blacklisted_tts_transformers",
        ]:
            assert getattr(s, f) == [], f"{f} should default to []"

    def test_blacklisted_pipelines_default_empty(self):
        s = Session()
        assert s.blacklisted_pipelines == []

    def test_blacklisted_pipelines_set(self):
        s = Session(blacklisted_pipelines=["adapt_low", "fallback_low"])
        assert "adapt_low" in s.blacklisted_pipelines

    def test_bridge_injected_blacklists(self):
        """BRIDGE-1 §4.2: a bridge MAY inject blacklisted_skills at the boundary."""
        s = Session(
            session_id="remote-1",
            blacklisted_skills=["ovos-skill-parental-unsafe"],
            blacklisted_intents=["DangerousIntent"],
        )
        assert "ovos-skill-parental-unsafe" in s.blacklisted_skills
        assert "DangerousIntent" in s.blacklisted_intents


class TestSessionRoundTrip:
    def test_minimal_roundtrip(self):
        s = Session(session_id="abc", lang="de-de")
        restored = Session.model_validate(s.model_dump())
        assert restored.session_id == "abc"
        assert restored.lang == "de-de"

    def test_full_roundtrip(self):
        h = ActiveHandlerEntry(skill_id="skill-x", activated_at=1.0)
        rm = ResponseMode(skill_id="skill-x", expires_at=9999.0)
        s = Session(
            session_id="full-test",
            lang="fr-fr",
            secondary_langs=["en-us"],
            stt_lang="fr-fr",
            output_lang="fr-fr",
            request_lang="fr-fr",
            detected_lang="fr-fr",
            site_id="office",
            active_handlers=[h],
            response_mode=rm,
            audio_transformers=["t1"],
            utterance_transformers=["t2"],
            blacklisted_pipelines=["fallback_low"],
            blacklisted_skills=["bad-skill"],
            blacklisted_audio_transformers=["noisy-plugin"],
        )
        dump = s.model_dump()
        restored = Session.model_validate(dump)
        assert restored.lang == "fr-fr"
        assert restored.secondary_langs == ["en-us"]
        assert restored.stt_lang == "fr-fr"
        assert restored.site_id == "office"
        assert len(restored.active_handlers) == 1
        assert restored.active_handlers[0].skill_id == "skill-x"
        assert restored.response_mode.skill_id == "skill-x"
        assert "fallback_low" in restored.blacklisted_pipelines
        assert "noisy-plugin" in restored.blacklisted_audio_transformers

    def test_response_mode_none_roundtrip(self):
        s = Session(response_mode=None)
        restored = Session.model_validate(s.model_dump())
        assert restored.response_mode is None


# ---------------------------------------------------------------------------
# SESSION-2 §2.7 — OvosSessionSyncMessage
# ---------------------------------------------------------------------------

class TestOvosSessionSyncMessage:
    def test_data_session_required(self):
        """SESSION-2 §2.7: sync payload MUST carry data.session."""
        with pytest.raises(ValidationError):
            OvosSessionSyncMessage()  # data.session missing

    def test_valid(self):
        session = Session(session_id="sat-1", lang="es-es")
        msg = OvosSessionSyncMessage(data=OvosSessionSyncData(session=session))
        assert msg.message_type == "ovos.session.sync"
        assert msg.data.session.session_id == "sat-1"
        assert msg.data.session.lang == "es-es"

    def test_roundtrip(self):
        session = Session(session_id="client-abc", lang="zh-cn")
        msg = OvosSessionSyncMessage(data=OvosSessionSyncData(session=session))
        restored = OvosSessionSyncMessage.model_validate(msg.model_dump())
        assert restored.data.session.session_id == "client-abc"
        assert restored.data.session.lang == "zh-cn"

    def test_sync_with_transformer_fields(self):
        """Transformer fields survive a sync round-trip."""
        session = Session(
            session_id="s1",
            audio_transformers=["audio-t"],
            blacklisted_tts_transformers=["slow-tts"],
        )
        msg = OvosSessionSyncMessage(data=OvosSessionSyncData(session=session))
        restored = OvosSessionSyncMessage.model_validate(msg.model_dump())
        assert restored.data.session.audio_transformers == ["audio-t"]
        assert "slow-tts" in restored.data.session.blacklisted_tts_transformers

    def test_sync_rejection_with_invalid_session(self):
        """Session inside sync still validates."""
        with pytest.raises(ValidationError):
            OvosSessionSyncData(session={"session_id": 12345})  # session_id must be str


# ---------------------------------------------------------------------------
# OvosSessionUpdateDefaultMessage — SESSION-2 §5
# ---------------------------------------------------------------------------

class TestOvosSessionUpdateDefaultMessage:
    def test_valid(self):
        session = Session(session_id="default", lang="it-it")
        data = OvosSessionUpdateDefaultData(**session.model_dump())
        msg = OvosSessionUpdateDefaultMessage(data=data)
        assert msg.message_type == "ovos.session.update_default"
        assert msg.data.lang == "it-it"

    def test_roundtrip(self):
        session = Session(session_id="default", lang="nl-nl")
        data = OvosSessionUpdateDefaultData(**session.model_dump())
        msg = OvosSessionUpdateDefaultMessage(data=data)
        restored = OvosSessionUpdateDefaultMessage.model_validate(msg.model_dump())
        assert restored.data.lang == "nl-nl"

    def test_new_fields_survive(self):
        """SESSION-1 new fields survive through OvosSessionUpdateDefaultData."""
        session = Session(
            session_id="default",
            secondary_langs=["en-us"],
            blacklisted_pipelines=["fallback_low"],
        )
        data = OvosSessionUpdateDefaultData(**session.model_dump())
        assert data.secondary_langs == ["en-us"]
        assert "fallback_low" in data.blacklisted_pipelines
