from typing import Dict, Any, Optional

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


# --- OVOS Shell / GUI Shell Companion Messages ---
# These messages are exchanged between the system PHAL plugin and the
# ovos-gui-plugin-shell-companion (OVOS Shell). They cover factory reset
# delegation and the GUI color theme system.


class OvosShellExecFactoryResetData(BaseModel):
    """Payload for delegating factory reset script execution to OVOS Shell."""
    script: str = Field(..., description="Absolute path to the factory reset shell script.")


class OvosShellExecFactoryResetMessage(OpenVoiceOSMessage):
    """Ask OVOS Shell to execute the factory reset script.

    Emitted by the system PHAL plugin when `use_external_factory_reset` is
    True (e.g. when `ovos-shell` is running). The shell handles running the
    script and emitting `system.factory.reset.complete` when done, rather
    than the PHAL plugin doing it directly.
    """
    message_type: str = "ovos.shell.exec.factory.reset"
    data: OvosShellExecFactoryResetData


class OvosShellGuiColorSchemeGenerateData(BaseModel):
    """Primary, secondary, and text colors for a new GUI color scheme."""
    primaryColor: str = Field(..., description="Primary/accent color as a CSS hex string (e.g. '#3daee9').")
    secondaryColor: str = Field(..., description="Secondary/background color as a CSS hex string.")
    textColor: str = Field(..., description="Foreground text color as a CSS hex string.")


class OvosShellGuiColorSchemeGenerateMessage(OpenVoiceOSMessage):
    """Request OVOS Shell to generate and save a new GUI color scheme.

    Emitted by settings GUIs or skill integrations when the user selects
    custom accent colors. The shell-companion color manager creates a KDE
    color scheme file and replies with `ovos.shell.gui.color.scheme.generated`.
    """
    message_type: str = "ovos.shell.gui.color.scheme.generate"
    data: OvosShellGuiColorSchemeGenerateData


class OvosShellGuiColorSchemeGeneratedData(BaseModel):
    """Location of the newly generated color scheme file."""
    theme_name: str = Field(..., description="Name of the generated color scheme (e.g. 'OvosTheme').")
    theme_path: str = Field(..., description="Directory path where the color scheme file was saved.")


class OvosShellGuiColorSchemeGeneratedMessage(OpenVoiceOSMessage):
    """Signal that a new GUI color scheme file has been created.

    Emitted by the shell-companion color manager after writing the KDE
    color scheme to disk. The GUI reloads the theme from `theme_path`.
    """
    message_type: str = "ovos.shell.gui.color.scheme.generated"
    data: OvosShellGuiColorSchemeGeneratedData


class OvosThemeGetMessage(OpenVoiceOSMessage):
    """Request the current OVOS GUI theme / color scheme.

    Emitted on shell-companion startup and by any component that needs the
    active theme data. The shell-companion color manager replies immediately
    via the bus with the current theme settings.
    """
    message_type: str = "ovos.theme.get"
    data: Dict[str, Any] = Field(default_factory=dict)


class SmartSpeakerExtendAboutData(BaseModel):
    """Additional items to display on the device 'About' settings page."""
    display_list: list = Field(
        ...,
        description="List of key-value items to append to the About page. "
                    "Each item is a dict with at least a 'label' and 'value' key."
    )


class SmartSpeakerExtendAboutMessage(OpenVoiceOSMessage):
    """Add extra entries to the OVOS Shell 'About' settings page.

    Emitted by PHAL plugins or skills that want to expose device-specific
    information (e.g. hardware version, IP address, serial number) in the
    GUI settings About page. The shell-companion appends each item in
    `display_list` to the page.
    """
    message_type: str = "smartspeaker.extension.extend.about"
    data: SmartSpeakerExtendAboutData
