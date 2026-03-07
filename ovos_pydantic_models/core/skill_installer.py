from enum import Enum
from typing import Dict, Any, List, Optional, Union

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


class InstallError(str, Enum):
    """Error codes for skill and package installation failures.

    Emitted in the `error` field of `*failed` messages so callers can
    distinguish configuration issues (pip disabled) from network problems
    (bad URL) or operational errors (pip subprocess failure).
    """
    DISABLED = "pip disabled in mycroft.conf"
    PIP_ERROR = "error in pip subprocess"
    BAD_URL = "skill url validation failed"
    NO_PKGS = "no packages to install"


# --- Installer Service Message Models ---

class OvosSkillsInstallData(BaseModel):
    """Payload for installing a skill from a remote URL."""
    url: str = Field(..., description="The URL of the skill to install (e.g., GitHub repository URL).")


class OvosSkillsInstallMessage(OpenVoiceOSMessage):
    """Request the installer service to install a skill from a URL.

    Emitted by admin GUIs, the `ovos-skill-installer` CLI, or the marketplace
    skill. The installer clones/downloads the skill, runs `pip install`, and
    then triggers a skill reload. Results in either `ovos.skills.install.complete`
    or `ovos.skills.install.failed`.
    """
    message_type: str = "ovos.skills.install"
    data: OvosSkillsInstallData


class OvosSkillsInstallFailedData(BaseModel):
    """Error payload for a failed skill installation."""
    error: InstallError = Field(..., description="The reason for the installation failure.")


class OvosSkillsInstallFailedMessage(OpenVoiceOSMessage):
    """Signal that a skill installation request failed.

    Emitted by the installer service when `ovos.skills.install` could not
    complete. The `error` field identifies whether the failure was due to
    a configuration issue, bad URL, or pip subprocess error.
    """
    message_type: str = "ovos.skills.install.failed"
    data: OvosSkillsInstallFailedData


class OvosSkillsInstallCompleteMessage(OpenVoiceOSMessage):
    """Signal that a skill installation completed successfully.

    Emitted by the installer service after the skill has been installed and
    the skill loader has been notified. The skill should be available within
    seconds of this event.
    """
    message_type: str = "ovos.skills.install.complete"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosSkillsUninstallData(BaseModel, extra='allow'):
    """Payload for uninstalling a skill by ID or package name."""
    skill_id: Optional[str] = Field(None, description="The ID of the skill to uninstall.")
    package_name: Optional[str] = Field(None, description="The Python package name of the skill to uninstall.")


class OvosSkillsUninstallMessage(OpenVoiceOSMessage):
    """Request the installer service to uninstall a skill.

    Emitted by admin GUIs or the marketplace skill. The installer shuts down
    the skill, runs `pip uninstall`, and removes its data directory. Results
    in `ovos.skills.uninstall.complete` or `ovos.skills.uninstall.failed`.
    """
    message_type: str = "ovos.skills.uninstall"
    data: OvosSkillsUninstallData


class OvosSkillsUninstallFailedData(BaseModel):
    """Error payload for a failed skill uninstallation."""
    error: Union[InstallError, str] = Field(..., description="The reason for the uninstallation failure.")


class OvosSkillsUninstallFailedMessage(OpenVoiceOSMessage):
    """Signal that a skill uninstallation request failed.

    Emitted by the installer service when `ovos.skills.uninstall` could not
    complete. The `error` field describes the reason for the failure.
    """
    message_type: str = "ovos.skills.uninstall.failed"
    data: OvosSkillsUninstallFailedData


class OvosSkillsUninstallCompleteMessage(OpenVoiceOSMessage):
    """Signal that a skill uninstallation completed successfully.

    Emitted by the installer service after the skill has been removed from
    disk and the skill loader has been notified.
    """
    message_type: str = "ovos.skills.uninstall.complete"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPipInstallData(BaseModel):
    """Payload for installing Python packages via pip."""
    packages: List[str] = Field(..., description="List of Python package names to install.")


class OvosPipInstallMessage(OpenVoiceOSMessage):
    """Request the installer service to install Python packages via pip.

    Emitted by skills or admin tools that need runtime Python dependencies
    that are not declared in their own `requirements.txt`. The installer
    runs `pip install` in the OVOS virtual environment. Results in
    `ovos.pip.install.complete` or `ovos.pip.install.failed`.
    """
    message_type: str = "ovos.pip.install"
    data: OvosPipInstallData


class OvosPipInstallFailedData(BaseModel):
    """Error payload for a failed pip install."""
    error: InstallError = Field(..., description="The reason for the pip installation failure.")


class OvosPipInstallFailedMessage(OpenVoiceOSMessage):
    """Signal that a pip install request failed.

    Emitted by the installer service when `ovos.pip.install` could not
    complete. Check `error` for the specific failure reason.
    """
    message_type: str = "ovos.pip.install.failed"
    data: OvosPipInstallFailedData


class OvosPipInstallCompleteMessage(OpenVoiceOSMessage):
    """Signal that pip package installation completed successfully.

    Emitted by the installer service after all requested packages have
    been installed in the OVOS virtual environment.
    """
    message_type: str = "ovos.pip.install.complete"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPipUninstallData(BaseModel):
    """Payload for uninstalling Python packages via pip."""
    packages: List[str] = Field(..., description="List of Python package names to uninstall.")


class OvosPipUninstallMessage(OpenVoiceOSMessage):
    """Request the installer service to uninstall Python packages via pip.

    Emitted by admin tools or the skill manager during cleanup. Results
    in `ovos.pip.uninstall.complete` or `ovos.pip.uninstall.failed`.
    """
    message_type: str = "ovos.pip.uninstall"
    data: OvosPipUninstallData


class OvosPipUninstallFailedData(BaseModel):
    """Error payload for a failed pip uninstall."""
    error: InstallError = Field(..., description="The reason for the pip uninstallation failure.")


class OvosPipUninstallFailedMessage(OpenVoiceOSMessage):
    """Signal that a pip uninstall request failed.

    Emitted by the installer service when `ovos.pip.uninstall` could not
    complete. Check `error` for the specific failure reason.
    """
    message_type: str = "ovos.pip.uninstall.failed"
    data: OvosPipUninstallFailedData


class OvosPipUninstallCompleteMessage(OpenVoiceOSMessage):
    """Signal that pip package uninstallation completed successfully.

    Emitted by the installer service after all requested packages have
    been removed from the OVOS virtual environment.
    """
    message_type: str = "ovos.pip.uninstall.complete"
    data: Dict[str, Any] = Field(default_factory=dict)
