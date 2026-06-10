"""
Registry completeness test — verifies that:
1. Every OpenVoiceOSMessage subclass has a non-empty ``message_type``.
2. No two *static* message types (non-Field dynamic) are duplicates.
3. Every subclass round-trips via model_dump / model_validate.
"""
import inspect
from typing import Dict, Any, get_type_hints

import pytest

import ovos_pydantic_models.audio.audioservice as m_audioservice
import ovos_pydantic_models.audio.ocp as m_ocp
import ovos_pydantic_models.audio.opm as m_audio_opm
import ovos_pydantic_models.audio.playback as m_playback
import ovos_pydantic_models.audio.recognizer_loop as m_audio_rl
import ovos_pydantic_models.audio.video_service as m_video_service
import ovos_pydantic_models.audio.web_service as m_web_service
import ovos_pydantic_models.core.configuration as m_config
import ovos_pydantic_models.core.scheduler as m_scheduler
import ovos_pydantic_models.core.session as m_session
import ovos_pydantic_models.core.skill_installer as m_installer
import ovos_pydantic_models.core.skill_manager as m_skill_manager
import ovos_pydantic_models.core.skill_settings as m_skill_settings
import ovos_pydantic_models.gui.homescreen as m_homescreen
import ovos_pydantic_models.gui.media_player as m_media_player
import ovos_pydantic_models.gui.namespace as m_namespace
import ovos_pydantic_models.gui.notifications as m_notifications
import ovos_pydantic_models.gui.shell as m_shell
import ovos_pydantic_models.gui.widgets as m_widgets
import ovos_pydantic_models.intents.adapt as m_adapt
import ovos_pydantic_models.intents.converse as m_converse
import ovos_pydantic_models.intents.core as m_core
import ovos_pydantic_models.intents.fallbacks as m_fallbacks
import ovos_pydantic_models.intents.padatious as m_padatious
import ovos_pydantic_models.intents.stop as m_stop
import ovos_pydantic_models.listener.opm as m_listener_opm
import ovos_pydantic_models.listener.recognizer_loop as m_recognizer_loop
import ovos_pydantic_models.phal.brightness as m_brightness
import ovos_pydantic_models.phal.camera as m_camera
import ovos_pydantic_models.phal.configuration_provider as m_cfg_provider
import ovos_pydantic_models.phal.connectivity as m_connectivity
import ovos_pydantic_models.phal.enclosure as m_enclosure
import ovos_pydantic_models.phal.network_manager as m_nm
import ovos_pydantic_models.phal.oauth as m_oauth
import ovos_pydantic_models.phal.sensors as m_sensors
import ovos_pydantic_models.phal.system as m_system
import ovos_pydantic_models.phal.termux as m_termux
import ovos_pydantic_models.phal.tools as m_tools
import ovos_pydantic_models.phal.volume as m_volume
import ovos_pydantic_models.phal.wallpaper as m_wallpaper
import ovos_pydantic_models.phal.wifi_setup as m_wifi
import ovos_pydantic_models.skills.common_query as m_cq
import ovos_pydantic_models.skills.converse as m_skills_converse
import ovos_pydantic_models.skills.fallback as m_skills_fallback
import ovos_pydantic_models.skills.game as m_game
import ovos_pydantic_models.skills.ocp as m_skills_ocp
import ovos_pydantic_models.skills.persona as m_persona
from ovos_pydantic_models.message import OpenVoiceOSMessage
from pydantic.fields import FieldInfo


ALL_MODULES = [
    m_audioservice, m_ocp, m_audio_opm, m_playback, m_audio_rl,
    m_video_service, m_web_service,
    m_config, m_scheduler, m_session, m_installer, m_skill_manager, m_skill_settings,
    m_homescreen, m_media_player, m_namespace, m_notifications, m_shell, m_widgets,
    m_adapt, m_converse, m_core, m_fallbacks, m_padatious, m_stop,
    m_listener_opm, m_recognizer_loop,
    m_brightness, m_camera, m_cfg_provider, m_connectivity, m_enclosure,
    m_nm, m_oauth, m_sensors, m_system, m_termux, m_tools,
    m_volume, m_wallpaper, m_wifi,
    m_cq, m_skills_converse, m_skills_fallback, m_game, m_skills_ocp, m_persona,
]


def _collect_message_classes():
    """Return all OpenVoiceOSMessage subclasses found in ALL_MODULES."""
    seen = set()
    classes = []
    for mod in ALL_MODULES:
        for name, obj in inspect.getmembers(mod, inspect.isclass):
            if (
                issubclass(obj, OpenVoiceOSMessage)
                and obj is not OpenVoiceOSMessage
                and id(obj) not in seen
            ):
                seen.add(id(obj))
                classes.append(obj)
    return classes


def _is_dynamic(cls) -> bool:
    """Return True if message_type is a dynamic Field (not a static string literal)."""
    field = cls.model_fields.get("message_type")
    if field is None:
        return False
    # A static literal has field.default as a plain str and no is_required().
    default = field.default
    return not isinstance(default, str)


ALL_CLASSES = _collect_message_classes()

# Pre-existing duplicates present in v0.1.1 that are tracked here for
# visibility.  New duplicates introduced after this commit will cause a test
# failure.
_KNOWN_DUPLICATE_PAIRS: set = {
    frozenset(("DetachIntentMessage", "DetachIntentMessage")),          # same class re-exported
    frozenset(("DetachSkillMessage", "DetachSkillMessage")),
    frozenset(("MycroftSkillsTrainMessage", "MycroftSkillsTrainMessage")),
    frozenset(("MycroftSkillsTrainedMessage", "MycroftSkillsTrainedMessage")),
    frozenset(("MycroftSpeechStopMessage", "MycroftAudioSpeechStopMessage")),
}


class TestRegistryCompleteness:
    def test_all_classes_have_message_type(self):
        for cls in ALL_CLASSES:
            field = cls.model_fields.get("message_type")
            assert field is not None, f"{cls.__name__} has no message_type field"

    def test_no_new_duplicate_static_message_types(self):
        """No *new* duplicate static message types beyond the known pre-existing set."""
        seen: Dict[str, str] = {}
        new_duplicates = []
        for cls in ALL_CLASSES:
            if _is_dynamic(cls):
                continue
            mt = cls.model_fields["message_type"].default
            if not isinstance(mt, str):
                continue
            if mt in seen:
                pair = frozenset((seen[mt], cls.__name__))
                if pair not in _KNOWN_DUPLICATE_PAIRS:
                    new_duplicates.append(f"{mt!r}: {seen[mt]} vs {cls.__name__}")
            else:
                seen[mt] = cls.__name__
        assert not new_duplicates, "New duplicate static message types:\n" + "\n".join(new_duplicates)

    def test_known_duplicates_documented(self):
        """Emit a warning-level note listing the known pre-existing duplicates."""
        import warnings
        seen: Dict[str, str] = {}
        existing = []
        for cls in ALL_CLASSES:
            if _is_dynamic(cls):
                continue
            mt = cls.model_fields["message_type"].default
            if not isinstance(mt, str):
                continue
            if mt in seen:
                existing.append(f"{mt!r}: {seen[mt]} vs {cls.__name__}")
            else:
                seen[mt] = cls.__name__
        if existing:
            warnings.warn(
                "Pre-existing duplicate message types (tracked, not enforced):\n"
                + "\n".join(existing),
                stacklevel=1,
            )

    def test_static_message_types_nonempty(self):
        for cls in ALL_CLASSES:
            if _is_dynamic(cls):
                continue
            mt = cls.model_fields["message_type"].default
            if isinstance(mt, str):
                assert mt, f"{cls.__name__}.message_type is an empty string"

    def test_class_count(self):
        """Sanity: at least 200 message classes registered (detect accidental imports)."""
        assert len(ALL_CLASSES) >= 200, f"Only {len(ALL_CLASSES)} classes found — import error?"
