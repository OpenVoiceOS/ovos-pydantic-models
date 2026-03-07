import pytest
from pydantic import ValidationError

from ovos_pydantic_models.core.skill_manager import (
    MycroftReadyMessage,
    MycroftSkillsIsReadyMessage, MycroftSkillsIsReadyReplyData, MycroftSkillsIsReadyResponseMessage,
    MycroftSkillsReadyMessage,
    SkillManagerListMessage, MycroftSkillsListData, MycroftSkillsListMessage,
    SkillManagerDeactivateData, SkillManagerDeactivateMessage,
    MycroftSkillsErrorData, MycroftSkillsErrorMessage,
)
from ovos_pydantic_models.core.session import (
    OvosSessionSyncMessage,
    OvosSessionUpdateDefaultData, OvosSessionUpdateDefaultMessage,
)
from ovos_pydantic_models.core.skill_settings import (
    SkillSettingsChangeData, SkillSettingsChangeMessage,
    OvosSkillsSettingsChangedData, OvosSkillsSettingsChangedMessage,
)
from ovos_pydantic_models.core.skill_installer import (
    InstallError,
    OvosSkillsInstallData, OvosSkillsInstallMessage,
    OvosSkillsInstallFailedData, OvosSkillsInstallFailedMessage,
    OvosPipInstallData, OvosPipInstallMessage,
)
from ovos_pydantic_models.session import Session


class TestSkillManagerMessages:
    def test_mycroft_ready(self):
        msg = MycroftReadyMessage()
        assert msg.message_type == "mycroft.ready"

    def test_skills_is_ready_request(self):
        msg = MycroftSkillsIsReadyMessage()
        assert msg.message_type == "mycroft.skills.is_ready"

    def test_skills_is_ready_response(self):
        data = MycroftSkillsIsReadyReplyData(status=True)
        msg = MycroftSkillsIsReadyResponseMessage(data=data)
        assert msg.message_type == "mycroft.skills.is_ready.response"
        assert msg.data.status is True

    def test_skills_ready(self):
        msg = MycroftSkillsReadyMessage()
        assert msg.message_type == "mycroft.skills.ready"

    def test_skillmanager_list(self):
        msg = SkillManagerListMessage()
        assert msg.message_type == "skillmanager.list"

    def test_skills_list_response(self):
        data = MycroftSkillsListData(
            **{"skill-a.mycroft": {"active": True, "id": "skill-a.mycroft"}}
        )
        msg = MycroftSkillsListMessage(data=data)
        assert msg.message_type == "mycroft.skills.list"

    def test_skillmanager_deactivate(self):
        data = SkillManagerDeactivateData(skill="skill-old.mycroft")
        msg = SkillManagerDeactivateMessage(data=data)
        assert msg.message_type == "skillmanager.deactivate"

    def test_skills_error(self):
        data = MycroftSkillsErrorData(
            internet_loaded=False,
            network_loaded=True,
            error="Some skills failed to load"
        )
        msg = MycroftSkillsErrorMessage(data=data)
        assert msg.message_type == "mycroft.skills.error"
        assert msg.data.internet_loaded is False

    def test_roundtrip_serialization(self):
        msg = MycroftSkillsIsReadyResponseMessage(data=MycroftSkillsIsReadyReplyData(status=True))
        restored = MycroftSkillsIsReadyResponseMessage.model_validate(msg.model_dump())
        assert restored.data.status is True


class TestSessionMessages:
    def test_session_sync(self):
        msg = OvosSessionSyncMessage()
        assert msg.message_type == "ovos.session.sync"

    def test_session_update_default(self):
        session = Session(session_id="default", lang="es-es")
        data = OvosSessionUpdateDefaultData(**session.model_dump())
        msg = OvosSessionUpdateDefaultMessage(data=data)
        assert msg.message_type == "ovos.session.update_default"
        assert msg.data.lang == "es-es"

    def test_roundtrip_serialization(self):
        session = Session(session_id="abc", lang="de-de")
        data = OvosSessionUpdateDefaultData(**session.model_dump())
        msg = OvosSessionUpdateDefaultMessage(data=data)
        restored = OvosSessionUpdateDefaultMessage.model_validate(msg.model_dump())
        assert restored.data.lang == "de-de"


class TestSkillSettingsMessages:
    def test_settings_change(self):
        data = SkillSettingsChangeData(
            skill_id="skill-weather.mycroft",
            settings={"location": "London"}
        )
        msg = SkillSettingsChangeMessage(data=data)
        assert msg.message_type == "skill.settings.change"
        assert msg.data.settings["location"] == "London"

    def test_settings_changed_event(self):
        data = OvosSkillsSettingsChangedData(skill_id="skill-weather.mycroft")
        msg = OvosSkillsSettingsChangedMessage(data=data)
        assert msg.message_type == "ovos.skills.settings_changed"

    def test_roundtrip_serialization(self):
        data = SkillSettingsChangeData(skill_id="skill-a.mycroft", settings={"key": "value"})
        msg = SkillSettingsChangeMessage(data=data)
        restored = SkillSettingsChangeMessage.model_validate(msg.model_dump())
        assert restored.data.settings["key"] == "value"


class TestInstallerMessages:
    def test_install_error_values(self):
        assert InstallError.PIP_ERROR == "error in pip subprocess"

    def test_install_skill(self):
        data = OvosSkillsInstallData(url="https://github.com/OpenVoiceOS/skill-hello-world")
        msg = OvosSkillsInstallMessage(data=data)
        assert msg.message_type == "ovos.skills.install"

    def test_install_failed(self):
        data = OvosSkillsInstallFailedData(error=InstallError.DISABLED)
        msg = OvosSkillsInstallFailedMessage(data=data)
        assert msg.message_type == "ovos.skills.install.failed"
        assert msg.data.error == InstallError.DISABLED

    def test_pip_install(self):
        data = OvosPipInstallData(packages=["requests", "beautifulsoup4"])
        msg = OvosPipInstallMessage(data=data)
        assert msg.message_type == "ovos.pip.install"
        assert len(msg.data.packages) == 2

    def test_roundtrip_serialization(self):
        data = OvosSkillsInstallData(url="https://example.com/skill")
        msg = OvosSkillsInstallMessage(data=data)
        restored = OvosSkillsInstallMessage.model_validate(msg.model_dump())
        assert restored.data.url == "https://example.com/skill"
