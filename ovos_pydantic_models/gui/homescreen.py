from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session

# --- Homescreen Manager Message Models ---

class HomescreenManagerAddData(BaseModel):
    """Payload for registering a new homescreen with the homescreen manager."""
    id: str = Field(..., description="The unique ID of the homescreen to add.")
    model_config = ConfigDict(extra='allow')


class HomescreenManagerAddMessage(OpenVoiceOSMessage):
    """Register a new homescreen skill with the homescreen manager.

    Emitted by homescreen skills during `initialize()`. The homescreen
    manager stores the registration so the homescreen can be selected,
    activated, and displayed when the device is idle.
    """
    message_type: str = "homescreen.manager.add"
    data: HomescreenManagerAddData


class HomescreenManagerRemoveData(BaseModel):
    """Payload for deregistering a homescreen from the homescreen manager."""
    id: str = Field(..., description="The unique ID of the homescreen to remove.")


class HomescreenManagerRemoveMessage(OpenVoiceOSMessage):
    """Deregister a homescreen skill from the homescreen manager.

    Emitted by homescreen skills during `shutdown()`. The homescreen manager
    removes the entry from its registry; if it was the active homescreen,
    a fallback homescreen is selected.
    """
    message_type: str = "homescreen.manager.remove"
    data: HomescreenManagerRemoveData


class HomescreenManagerListMessage(OpenVoiceOSMessage):
    """Request the list of all registered homescreen skills.

    Emitted by settings GUIs or admin tools that present a homescreen
    selection menu. The homescreen manager replies with
    `homescreen.manager.list.response`.
    """
    message_type: str = "homescreen.manager.list"
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class HomescreenManagerListReplyData(BaseModel):
    """The list of all registered homescreens."""
    homescreens: List[Dict[str, Any]] = Field(
        ..., description="A list of dictionaries, each representing a homescreen with its 'id' and other properties."
    )


class HomescreenManagerListResponseMessage(OpenVoiceOSMessage):
    """Return the list of all registered homescreen skills.

    Emitted by the homescreen manager in response to `homescreen.manager.list`.
    Each entry includes the homescreen `id` and any additional metadata
    the homescreen skill registered.
    """
    message_type: str = "homescreen.manager.list.response"
    data: HomescreenManagerListReplyData


class HomescreenManagerGetActiveMessage(OpenVoiceOSMessage):
    """Query which homescreen is currently active.

    Emitted by settings GUIs or skills that need to know which homescreen
    is displayed when the device is idle. The homescreen manager replies
    with `homescreen.manager.get_active.response`.
    """
    message_type: str = "homescreen.manager.get_active"
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class HomescreenManagerGetActiveReplyData(BaseModel):
    """The currently active homescreen, if any."""
    homescreen: Optional[Dict[str, Any]] = Field(
        None, description="The active homescreen dictionary, or None if no homescreen is active/configured."
    )


class HomescreenManagerGetActiveResponseMessage(OpenVoiceOSMessage):
    """Return the currently active homescreen.

    Emitted by the homescreen manager in response to
    `homescreen.manager.get_active`. `homescreen` is None if no homescreen
    has been registered or if the manager is unconfigured.
    """
    message_type: str = "homescreen.manager.get_active.response"
    data: HomescreenManagerGetActiveReplyData


class HomescreenManagerSetActiveData(BaseModel):
    """Payload for switching the active homescreen."""
    id: str = Field(..., description="The ID of the homescreen to set as active.")


class HomescreenManagerSetActiveMessage(OpenVoiceOSMessage):
    """Switch the active homescreen to a specific registered skill.

    Emitted by settings GUIs or admin tools. The homescreen manager updates
    its active selection and saves the preference. The new homescreen is
    displayed the next time the device goes idle.
    """
    message_type: str = "homescreen.manager.set_active"
    data: HomescreenManagerSetActiveData


class HomescreenManagerDisableActiveMessage(OpenVoiceOSMessage):
    """Disable the currently active homescreen.

    Emitted by settings GUIs or the homescreen manager itself when the
    user disables the homescreen feature. The device will no longer show
    an idle screen after this.
    """
    message_type: str = "homescreen.manager.disable_active"
    data: Dict[str, Any] = Field(default_factory=dict)


class HomescreenManagerShowActiveMessage(OpenVoiceOSMessage):
    """Tell the homescreen manager to display the active homescreen now.

    Emitted by the device shell or skill manager when the device becomes
    idle and no skill is presenting content. The homescreen manager
    instructs the active homescreen skill to render its UI.
    """
    message_type: str = "homescreen.manager.show_active"
    data: Dict[str, Any] = Field(default_factory=dict)


class HomescreenManagerReloadListMessage(OpenVoiceOSMessage):
    """Tell the homescreen manager to rebuild its homescreen registry.

    Emitted after skills are installed or reloaded. The manager re-collects
    registrations from all loaded homescreen skills.
    """
    message_type: str = "homescreen.manager.reload.list"
    data: Dict[str, Any] = Field(default_factory=dict)


class HomescreenManagerActivateDisplayData(BaseModel):
    """Payload for activating a specific homescreen for display."""
    homescreen_id: str = Field(..., description="The ID of the homescreen to activate for display.")


class HomescreenManagerActivateDisplayMessage(OpenVoiceOSMessage):
    """Activate a specific homescreen for display immediately.

    Emitted by the homescreen manager or shell when transitioning to idle.
    The named homescreen skill renders its QML pages in the GUI.
    """
    message_type: str = "homescreen.manager.activate.display"
    data: HomescreenManagerActivateDisplayData


class HomescreenRegisterExamplesData(BaseModel):
    """Payload for registering example utterances on the homescreen."""
    skill_id: str = Field(..., description="The ID of the skill registering examples.")
    utterances: List[str] = Field(..., description="A list of example utterances for the skill.")
    lang: str = Field(..., description="The language of the example utterances (BCP-47 code).")


class HomescreenRegisterExamplesMessage(OpenVoiceOSMessage):
    """Register example utterances for a skill to display on the homescreen.

    Emitted by skills during `initialize()`. Homescreens that show a
    'What can I say?' section use these utterances as prompts to help users
    discover skill capabilities.
    """
    message_type: str = "homescreen.register.examples"
    data: HomescreenRegisterExamplesData


class HomescreenManagerAppData(BaseModel):
    """Payload for registering a skill as a launcher app on the homescreen."""
    skill_id: str = Field(..., description="The ID of the skill/app to register on the homescreen.")
    name: str = Field(..., description="Display name of the app.")
    icon: Optional[str] = Field(None, description="URL or path to the app icon.")
    model_config = ConfigDict(extra='allow')


class HomescreenManagerAppMessage(OpenVoiceOSMessage):
    """Register a skill as a tappable app icon on the homescreen.

    Emitted by skills that support GUI touch/click activation
    (in addition to voice). The homescreen displays an icon; tapping it
    triggers the skill's main intent. Used by the OVOS app launcher.
    """
    message_type: str = "homescreen.manager.app"
    data: HomescreenManagerAppData


class HomescreenRegisterAppData(BaseModel):
    """Payload for registering a skill app via the alternative homescreen.register.app protocol."""
    skill_id: str = Field(..., description="Skill ID registering as an app.")
    name: str = Field(..., description="Display name of the app.")
    icon: Optional[str] = Field(None, description="URL or path to the app icon.")
    model_config = ConfigDict(extra='allow')


class HomescreenRegisterAppMessage(OpenVoiceOSMessage):
    """Register a skill as a homescreen app (alternative protocol).

    Functionally similar to `HomescreenManagerAppMessage` but uses the
    `homescreen.register.app` message type used by some homescreen skins.
    Emitted by skills during `initialize()`.
    """
    message_type: str = "homescreen.register.app"
    data: HomescreenRegisterAppData


class HomescreenWallpaperSetData(BaseModel):
    """Payload for changing the homescreen wallpaper."""
    wallpaper: str = Field(..., description="URL or path of the wallpaper image to set.")


class HomescreenWallpaperSetMessage(OpenVoiceOSMessage):
    """Change the homescreen wallpaper image.

    Emitted by wallpaper management skills or the wallpaper PHAL plugin.
    The homescreen skill updates its background image and persists the
    selection so it survives restarts.
    """
    message_type: str = "homescreen.wallpaper.set"
    data: HomescreenWallpaperSetData


class HomescreenMetadataGetMessage(OpenVoiceOSMessage):
    """Request metadata from the homescreen manager.

    Emitted by GUIs and admin tools that need to display homescreen
    configuration (active homescreen ID, registered apps, wallpaper path).
    """
    message_type: str = "homescreen.metadata.get"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftDeviceShowIdleMessage(OpenVoiceOSMessage):
    """Tell the device shell to show the idle / homescreen view.

    Emitted by the intent service after an utterance completes, by the
    skill manager when no skill is active, or by the GUI shell when it
    detects user inactivity. The homescreen manager responds by rendering
    the active homescreen.
    """
    message_type: str = "mycroft.device.show.idle"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftDeviceSettingsMessage(OpenVoiceOSMessage):
    """Open the device settings screen.

    Emitted by skills or PHAL plugins that need to direct the user to the
    settings UI (e.g. 'Open settings' voice command). The GUI shell
    navigates to the settings page.
    """
    message_type: str = "mycroft.device.settings"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftMark2RegisterIdleData(BaseModel):
    """Payload for registering a Mark 2 idle screen handler."""
    name: str = Field(..., description="Display name for the idle screen.")
    id: str = Field(..., description="Skill ID registering the idle screen.")


class MycroftMark2RegisterIdleMessage(OpenVoiceOSMessage):
    """Register a skill as an idle screen provider for the Mark 2 shell.

    Emitted by skills that provide idle screen content (clock, weather,
    photo frame) on the Mycroft Mark 2. The shell polls registered
    handlers in priority order when the device becomes idle.
    """
    message_type: str = "mycroft.mark2.register_idle"
    data: MycroftMark2RegisterIdleData


class MycroftMark2ResetIdleData(BaseModel):
    """Payload for deregistering a Mark 2 idle screen handler."""
    id: str = Field(..., description="Skill ID to stop showing as idle screen.")


class MycroftMark2ResetIdleMessage(OpenVoiceOSMessage):
    """Deregister a skill's idle screen from the Mark 2 shell.

    Emitted by skills during `shutdown()` or when they no longer want to
    provide an idle screen. The Mark 2 shell selects the next registered
    idle screen provider.
    """
    message_type: str = "mycroft.mark2.reset_idle"
    data: MycroftMark2ResetIdleData


class MycroftMark2CollectIdleMessage(OpenVoiceOSMessage):
    """Poll all registered idle screen skills to collect their registrations.

    Emitted by the Mark 2 shell during startup to discover which skills
    have registered idle screens. Each skill that has registered responds
    by emitting `mycroft.mark2.register_idle`.
    """
    message_type: str = "mycroft.mark2.collect_idle"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosHomescreenDisplayedMessage(OpenVoiceOSMessage):
    """Signal that the homescreen is now visible on screen.

    Emitted by the active homescreen skill after its QML pages are shown.
    Useful for analytics, test harnesses, and skills that need to know
    when the device has returned to idle.
    """
    message_type: str = "ovos.homescreen.displayed"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosHomescreenMainViewCurrentIndexSetData(BaseModel):
    """Payload for navigating the homescreen main view to a specific tab."""
    index: int = Field(..., description="Index to set in the homescreen main view.")


class OvosHomescreenMainViewCurrentIndexSetMessage(OpenVoiceOSMessage):
    """Navigate the homescreen main view to a specific tab or page index.

    Emitted by skills or the GUI shell to switch which panel is visible
    in a multi-tab homescreen (e.g. switching between clock, weather, and
    news panels). The homescreen skill animates to the requested index.
    """
    message_type: str = "ovos.homescreen.main_view.current_index.set"
    data: OvosHomescreenMainViewCurrentIndexSetData
