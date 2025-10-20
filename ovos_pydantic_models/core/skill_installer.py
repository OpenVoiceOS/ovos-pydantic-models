from enum import Enum
from typing import Dict, Any, List, Optional, Union

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


# Enum for InstallError, as defined in the original code
class InstallError(str, Enum):
    """
    Represents various errors that can occur during skill or package installation.
    """
    DISABLED = "pip disabled in mycroft.conf"
    PIP_ERROR = "error in pip subprocess"
    BAD_URL = "skill url validation failed"
    NO_PKGS = "no packages to install"


# --- Installer Service Message Models ---

class OvosSkillsInstallData(BaseModel):
    """Data for `ovos.skills.install` message."""
    url: str = Field(..., description="The URL of the skill to install (e.g., GitHub repository URL).")


class OvosSkillsInstallMessage(OpenVoiceOSMessage):
    """Message for `ovos.skills.install`."""
    message_type: str = "ovos.skills.install"
    data: OvosSkillsInstallData


class OvosSkillsInstallFailedData(BaseModel):
    """Data for `ovos.skills.install.failed` message."""
    error: InstallError = Field(..., description="The reason for the installation failure.")


class OvosSkillsInstallFailedMessage(OpenVoiceOSMessage):
    """Message for `ovos.skills.install.failed`."""
    message_type: str = "ovos.skills.install.failed"
    data: OvosSkillsInstallFailedData


class OvosSkillsInstallCompleteMessage(OpenVoiceOSMessage):
    """Message for `ovos.skills.install.complete`."""
    message_type: str = "ovos.skills.install.complete"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for successful installation.")


class OvosSkillsUninstallData(BaseModel, extra='allow'):
    """Data for `ovos.skills.uninstall` message."""
    # The code currently uses 'url' for install, but 'uninstall' would likely use skill_id or package name
    # Assuming 'skill_id' or 'package_name' based on common uninstall patterns.
    # The provided code has a TODO and uses generic "not implemented" error.
    skill_id: Optional[str] = Field(None, description="The ID of the skill to uninstall.")
    package_name: Optional[str] = Field(None, description="The Python package name of the skill to uninstall.")


class OvosSkillsUninstallMessage(OpenVoiceOSMessage):
    """Message for `ovos.skills.uninstall`."""
    message_type: str = "ovos.skills.uninstall"
    data: OvosSkillsUninstallData


class OvosSkillsUninstallFailedData(BaseModel):
    """Data for `ovos.skills.uninstall.failed` message."""
    error: Union[InstallError, str] = Field(..., description="The reason for the uninstallation failure.")


class OvosSkillsUninstallFailedMessage(OpenVoiceOSMessage):
    """Message for `ovos.skills.uninstall.failed`."""
    message_type: str = "ovos.skills.uninstall.failed"
    data: OvosSkillsUninstallFailedData


class OvosSkillsUninstallCompleteMessage(OpenVoiceOSMessage):
    """Message for `ovos.skills.uninstall.complete`."""
    message_type: str = "ovos.skills.uninstall.complete"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for successful uninstallation.")


class OvosPipInstallData(BaseModel):
    """Data for `ovos.pip.install` message."""
    packages: List[str] = Field(..., description="List of Python package names to install.")


class OvosPipInstallMessage(OpenVoiceOSMessage):
    """Message for `ovos.pip.install`."""
    message_type: str = "ovos.pip.install"
    data: OvosPipInstallData


class OvosPipInstallFailedData(BaseModel):
    """Data for `ovos.pip.install.failed` message."""
    error: InstallError = Field(..., description="The reason for the pip installation failure.")


class OvosPipInstallFailedMessage(OpenVoiceOSMessage):
    """Message for `ovos.pip.install.failed`."""
    message_type: str = "ovos.pip.install.failed"
    data: OvosPipInstallFailedData


class OvosPipInstallCompleteMessage(OpenVoiceOSMessage):
    """Message for `ovos.pip.install.complete`."""
    message_type: str = "ovos.pip.install.complete"
    data: Dict[str, Any] = Field(default_factory=dict,
                                 description="Empty data payload for successful pip installation.")


class OvosPipUninstallData(BaseModel):
    """Data for `ovos.pip.uninstall` message."""
    packages: List[str] = Field(..., description="List of Python package names to uninstall.")


class OvosPipUninstallMessage(OpenVoiceOSMessage):
    """Message for `ovos.pip.uninstall`."""
    message_type: str = "ovos.pip.uninstall"
    data: OvosPipUninstallData


class OvosPipUninstallFailedData(BaseModel):
    """Data for `ovos.pip.uninstall.failed` message."""
    error: InstallError = Field(..., description="The reason for the pip uninstallation failure.")


class OvosPipUninstallFailedMessage(OpenVoiceOSMessage):
    """Message for `ovos.pip.uninstall.failed`."""
    message_type: str = "ovos.pip.uninstall.failed"
    data: OvosPipUninstallFailedData


class OvosPipUninstallCompleteMessage(OpenVoiceOSMessage):
    """Message for `ovos.pip.uninstall.complete`."""
    message_type: str = "ovos.pip.uninstall.complete"
    data: Dict[str, Any] = Field(default_factory=dict,
                                 description="Empty data payload for successful pip uninstallation.")


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Demonstrating Skills Installer Message Models ---")

    # Create a dummy session and context for demonstration
    dummy_session = Session(session_id="test-installer-session-123", lang="en-us")
    dummy_context = MessageContext(source="skills_installer", session=dummy_session)

    # Example: Install Skill Request
    install_skill_data = OvosSkillsInstallData(url="https://github.com/OpenVoiceOS/skill-hello-world")
    install_skill_message = OvosSkillsInstallMessage(data=install_skill_data, context=dummy_context)
    print(f"\nInstall Skill Message:\n{install_skill_message.model_dump_json(indent=2)}")

    # Example: Install Skill Failed
    install_failed_data = OvosSkillsInstallFailedData(error=InstallError.DISABLED)
    install_failed_message = OvosSkillsInstallFailedMessage(data=install_failed_data, context=dummy_context)
    print(f"\nInstall Skill Failed Message:\n{install_failed_message.model_dump_json(indent=2)}")

    # Example: Install Skill Complete
    install_complete_message = OvosSkillsInstallCompleteMessage(context=dummy_context)
    print(f"\nInstall Skill Complete Message:\n{install_complete_message.model_dump_json(indent=2)}")

    # Example: Uninstall Skill Request (using skill_id)
    uninstall_skill_data = OvosSkillsUninstallData(skill_id="skill-hello-world.openvoiceos")
    uninstall_skill_message = OvosSkillsUninstallMessage(data=uninstall_skill_data, context=dummy_context)
    print(f"\nUninstall Skill Message:\n{uninstall_skill_message.model_dump_json(indent=2)}")

    # Example: Uninstall Skill Failed
    uninstall_failed_data = OvosSkillsUninstallFailedData(error="not implemented")
    uninstall_failed_message = OvosSkillsUninstallFailedMessage(data=uninstall_failed_data, context=dummy_context)
    print(f"\nUninstall Skill Failed Message:\n{uninstall_failed_message.model_dump_json(indent=2)}")

    # Example: Pip Install Request
    pip_install_data = OvosPipInstallData(packages=["requests", "beautifulsoup4"])
    pip_install_message = OvosPipInstallMessage(data=pip_install_data, context=dummy_context)
    print(f"\nPip Install Message:\n{pip_install_message.model_dump_json(indent=2)}")

    # Example: Pip Install Complete
    pip_install_complete_message = OvosPipInstallCompleteMessage(context=dummy_context)
    print(f"\nPip Install Complete Message:\n{pip_install_complete_message.model_dump_json(indent=2)}")

    # Example: Pip Uninstall Request
    pip_uninstall_data = OvosPipUninstallData(packages=["requests"])
    pip_uninstall_message = OvosPipUninstallMessage(data=pip_uninstall_data, context=dummy_context)
    print(f"\nPip Uninstall Message:\n{pip_uninstall_message.model_dump_json(indent=2)}")

    # Example: Pip Uninstall Failed
    pip_uninstall_failed_data = OvosPipUninstallFailedData(error=InstallError.PIP_ERROR)
    pip_uninstall_failed_message = OvosPipUninstallFailedMessage(data=pip_uninstall_failed_data, context=dummy_context)
    print(f"\nPip Uninstall Failed Message:\n{pip_uninstall_failed_message.model_dump_json(indent=2)}")
