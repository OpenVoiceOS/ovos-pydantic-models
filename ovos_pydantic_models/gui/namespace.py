from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


# Note: GUI page/namespace messages use `__from` as a data key — a Python
# dunder that Pydantic cannot model as a typed field. These messages use
# `Dict[str, Any]` for `data` with the expected keys documented in docstrings.


class GuiPageShowMessage(OpenVoiceOSMessage):
    """Push one or more QML pages into a GUI namespace and display them.

    Emitted by `ovos-workshop` when a skill calls `self.gui.show_page()`.
    The GUI service (ovos-gui) loads the QML files, injects the namespace's
    current property values, and renders the pages on screen.

    Expected data keys:
    - `__from` (str): namespace identifier (typically the skill ID)
    - `page` (list[str]): QML file names to show
    - `namespace` (str): GUI namespace owning the pages
    - `index` (int): which page to display first
    """
    message_type: str = "gui.page.show"
    data: Dict[str, Any] = Field(default_factory=dict)


class GuiPageDeleteMessage(OpenVoiceOSMessage):
    """Remove specific QML pages from a GUI namespace.

    Emitted by `ovos-workshop` when a skill calls `self.gui.remove_page()`.
    The named pages are removed from the namespace's page stack. If the
    deleted page was currently visible, the next page in the stack is shown.

    Expected data keys:
    - `__from` (str): namespace identifier
    - `page` (list[str]): QML file names to remove
    - `namespace` (str): GUI namespace owning the pages
    """
    message_type: str = "gui.page.delete"
    data: Dict[str, Any] = Field(default_factory=dict)


class GuiPageDeleteAllMessage(OpenVoiceOSMessage):
    """Remove all QML pages from a GUI namespace and hide the skill's GUI.

    Emitted by `ovos-workshop` when a skill calls `self.gui.release()` or
    when the skill's GUI session expires. The GUI service clears the
    namespace entirely and may display the homescreen if no other namespace
    has pages.

    Expected data keys:
    - `__from` (str): namespace identifier
    - `namespace` (str): GUI namespace to clear
    """
    message_type: str = "gui.page.delete.all"
    data: Dict[str, Any] = Field(default_factory=dict)


class GuiValueSetMessage(OpenVoiceOSMessage):
    """Set or update a property value in a GUI namespace.

    Emitted by `ovos-workshop` when a skill assigns to `self.gui['key'] = value`.
    The GUI service updates the property in the namespace's model; any QML
    property binding that references the key updates immediately via Qt's
    property system.

    Expected data keys:
    - `__from` (str): namespace identifier
    - `namespace` (str): GUI namespace owning the property
    - `key` (str): property name
    - `value` (Any): new property value
    """
    message_type: str = "gui.value.set"
    data: Dict[str, Any] = Field(default_factory=dict)


class GuiEventSendMessage(OpenVoiceOSMessage):
    """Send a named event to the QML layer of a GUI namespace.

    Emitted by `ovos-workshop` when a skill calls `self.gui.send_event()`.
    The GUI service delivers the event to the QML engine where it can
    trigger signal handlers, animations, or state transitions.

    Expected data keys:
    - `__from` (str): namespace identifier
    - `namespace` (str): target namespace
    - `event_name` (str): name of the QML event to fire
    - `params` (dict): parameters passed to the event handler
    """
    message_type: str = "gui.event.send"
    data: Dict[str, Any] = Field(default_factory=dict)


class GuiClearNamespaceMessage(OpenVoiceOSMessage):
    """Remove all pages and properties for a GUI namespace.

    Emitted by `ovos-workshop` when a skill's GUI session ends completely.
    Unlike `gui.page.delete.all`, this also clears all property values from
    the namespace model, ensuring a clean state for the next activation.

    Expected data keys:
    - `__from` (str): namespace identifier
    - `namespace` (str): namespace to clear entirely
    """
    message_type: str = "gui.clear.namespace"
    data: Dict[str, Any] = Field(default_factory=dict)


class GuiNamespaceDisplayedData(BaseModel):
    """Payload identifying the skill namespace that is now on screen."""
    skill_id: str = Field(..., description="The skill whose namespace is now displayed.")


class GuiNamespaceDisplayedMessage(OpenVoiceOSMessage):
    """Signal that a skill's GUI namespace has become visible on screen.

    Emitted by the GUI service when a skill's pages gain focus and are
    rendered. Skills can subscribe to know when their GUI is actually
    visible (as opposed to merely having pages registered).
    """
    message_type: str = "gui.namespace.displayed"
    data: GuiNamespaceDisplayedData


class GuiNamespaceRemovedData(BaseModel):
    """Payload identifying the skill namespace that was removed."""
    skill_id: str = Field(..., description="The skill whose namespace was removed.")


class GuiNamespaceRemovedMessage(OpenVoiceOSMessage):
    """Signal that a skill's GUI namespace has been fully removed.

    Emitted by the GUI service after all pages and properties for a
    namespace have been cleared. The skill's GUI is no longer visible
    and the device may revert to the homescreen.
    """
    message_type: str = "gui.namespace.removed"
    data: GuiNamespaceRemovedData


class GuiPageGainedFocusData(BaseModel):
    """Payload identifying the GUI page that gained focus."""
    skill_id: str = Field(..., description="Skill ID of the page gaining focus.")
    page_index: int = Field(..., description="Index of the page that gained focus.")


class GuiPageGainedFocusMessage(OpenVoiceOSMessage):
    """Signal that a specific GUI page has gained focus (become frontmost).

    Emitted by the GUI service when the user swipes between pages or when
    a skill explicitly navigates to a page. Skills can use this to drive
    state changes that match the visible page.
    """
    message_type: str = "gui.page_gained_focus"
    data: GuiPageGainedFocusData


class GuiPageInteractionData(BaseModel):
    """Payload identifying the GUI page the user interacted with."""
    skill_id: str = Field(..., description="Skill ID of the page being interacted with.")
    page_index: int = Field(..., description="Index of the interacted page.")


class GuiPageInteractionMessage(OpenVoiceOSMessage):
    """Signal that the user has interacted with a GUI page (tap/swipe).

    Emitted by the GUI service when a touch or click event occurs on a
    rendered skill page. Skills can use this to reset inactivity timers
    or drive follow-up actions.
    """
    message_type: str = "gui.page_interaction"
    data: GuiPageInteractionData


class GuiStatusRequestMessage(OpenVoiceOSMessage):
    """Query the current status of the GUI service.

    Emitted by skills or the homescreen manager to check whether the GUI
    service is running and what namespace (if any) is currently displayed.
    """
    message_type: str = "gui.status.request"
    data: Dict[str, Any] = Field(default_factory=dict)


class MycroftGuiScreenCloseData(BaseModel):
    """Payload for requesting the GUI to close a skill's screen."""
    skill_id: str = Field(..., description="ID of the skill whose screen should be closed.")


class MycroftGuiScreenCloseMessage(OpenVoiceOSMessage):
    """Request the GUI service to close the active screen for a skill.

    Emitted by skills via `self.gui.release()` when they are done displaying
    content and want to return control to the previous page or homescreen.
    The GUI service removes the skill's namespace from the display stack and
    shows the next item in the queue, or returns to the homescreen if the
    queue is empty.
    """
    message_type: str = "mycroft.gui.screen.close"
    data: MycroftGuiScreenCloseData


class MycroftGuiConnectedData(BaseModel):
    """Payload sent by a GUI client when it opens a connection to the GUI service."""
    gui_id: str = Field(..., description="Unique identifier for the connecting GUI client instance.")


class MycroftGuiConnectedMessage(OpenVoiceOSMessage):
    """Signal that a GUI client has connected to the OVOS GUI service.

    Emitted by the GUI WebSocket client (e.g. Qt/Kirigami frontend) immediately
    after establishing its connection. The GUI service uses `gui_id` to track
    which client is connected and route namespace updates accordingly.
    """
    message_type: str = "mycroft.gui.connected"
    data: MycroftGuiConnectedData
