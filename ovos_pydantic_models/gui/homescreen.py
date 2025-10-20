from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session

# --- Homescreen Manager Message Models ---

class HomescreenManagerAddData(BaseModel):
    """Data for `homescreen.manager.add` message."""
    id: str = Field(..., description="The unique ID of the homescreen to add.")
    # Allow other fields if homescreen data includes more properties
    model_config = ConfigDict(extra='allow')

class HomescreenManagerAddMessage(OpenVoiceOSMessage):
    """Message for `homescreen.manager.add`."""
    message_type: str = "homescreen.manager.add"
    data: HomescreenManagerAddData


class HomescreenManagerRemoveData(BaseModel):
    """Data for `homescreen.manager.remove` message."""
    id: str = Field(..., description="The unique ID of the homescreen to remove.")

class HomescreenManagerRemoveMessage(OpenVoiceOSMessage):
    """Message for `homescreen.manager.remove`."""
    message_type: str = "homescreen.manager.remove"
    data: HomescreenManagerRemoveData

class HomescreenManagerListMessage(OpenVoiceOSMessage):
    """Message for `homescreen.manager.list` (request for homescreen list)."""
    message_type: str = "homescreen.manager.list"
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)

class HomescreenManagerListReplyData(BaseModel):
    """Data for `homescreen.manager.list.response` message."""
    homescreens: List[Dict[str, Any]] = Field(
        ..., description="A list of dictionaries, each representing a homescreen with its 'id' and other properties."
    )

class HomescreenManagerListResponseMessage(OpenVoiceOSMessage):
    """Response message for `homescreen.manager.list`."""
    message_type: str = "homescreen.manager.list.response"
    data: HomescreenManagerListReplyData

class HomescreenManagerGetActiveMessage(OpenVoiceOSMessage):
    """Message for `homescreen.manager.get_active` (request for active homescreen)."""
    message_type: str = "homescreen.manager.get_active"
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)

class HomescreenManagerGetActiveReplyData(BaseModel):
    """Data for `homescreen.manager.get_active.response` message."""
    homescreen: Optional[Dict[str, Any]] = Field(
        None, description="The active homescreen dictionary, or None if no homescreen is active/configured."
    )

class HomescreenManagerGetActiveResponseMessage(OpenVoiceOSMessage):
    """Response message for `homescreen.manager.get_active`."""
    message_type: str = "homescreen.manager.get_active.response"
    data: HomescreenManagerGetActiveReplyData


class HomescreenManagerSetActiveData(BaseModel):
    """Data for `homescreen.manager.set_active` message."""
    id: str = Field(..., description="The ID of the homescreen to set as active.")

class HomescreenManagerSetActiveMessage(OpenVoiceOSMessage):
    """Message for `homescreen.manager.set_active`."""
    message_type: str = "homescreen.manager.set_active"
    data: HomescreenManagerSetActiveData


class HomescreenManagerDisableActiveMessage(OpenVoiceOSMessage):
    """Message for `homescreen.manager.disable_active`."""
    message_type: str = "homescreen.manager.disable_active"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for disable active homescreen command.")


class HomescreenManagerShowActiveMessage(OpenVoiceOSMessage):
    """Message for `homescreen.manager.show_active`."""
    message_type: str = "homescreen.manager.show_active"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for show active homescreen command.")


class HomescreenManagerReloadListMessage(OpenVoiceOSMessage):
    """Message for `homescreen.manager.reload.list`."""
    message_type: str = "homescreen.manager.reload.list"
    data: Dict[str, Any] = Field(default_factory=dict)


class HomescreenManagerActivateDisplayData(BaseModel):
    """Data for `homescreen.manager.activate.display` message."""
    homescreen_id: str = Field(..., description="The ID of the homescreen to activate for display.")

class HomescreenManagerActivateDisplayMessage(OpenVoiceOSMessage):
    """Message for `homescreen.manager.activate.display`."""
    message_type: str = "homescreen.manager.activate.display"
    data: HomescreenManagerActivateDisplayData

class HomescreenRegisterExamplesData(BaseModel):
    """Data for `homescreen.register.examples` message."""
    skill_id: str = Field(..., description="The ID of the skill registering examples.")
    utterances: List[str] = Field(..., description="A list of example utterances for the skill.")
    lang: str = Field(..., description="The language of the example utterances (BCP-47 code).")

class HomescreenRegisterExamplesMessage(OpenVoiceOSMessage):
    """Message for `homescreen.register.examples`."""
    message_type: str = "homescreen.register.examples"
    data: HomescreenRegisterExamplesData

# --- Example Usage ---
if __name__ == "__main__":
    print("--- Demonstrating Homescreen Manager Message Models ---")

    # Create a dummy session and context for demonstration
    dummy_session = Session(session_id="test-homescreen-session-101", lang="en-us")
    dummy_context = MessageContext(source="homescreen_manager", session=dummy_session)

    # Example: Add Homescreen
    add_data = HomescreenManagerAddData(id="my-custom-homescreen", name="My Custom Homescreen", author="Me")
    add_message = HomescreenManagerAddMessage(data=add_data, context=dummy_context)
    print(f"\nAdd Homescreen Message:\n{add_message.model_dump_json(indent=2)}")

    # Example: Remove Homescreen
    remove_data = HomescreenManagerRemoveData(id="old-homescreen")
    remove_message = HomescreenManagerRemoveMessage(data=remove_data, context=dummy_context)
    print(f"\nRemove Homescreen Message:\n{remove_message.model_dump_json(indent=2)}")

    # Example: List Homescreens Request
    list_request = HomescreenManagerListMessage(context=dummy_context)
    print(f"\nList Homescreens Request:\n{list_request.model_dump_json(indent=2)}")

    # Example: List Homescreens Response
    list_reply_data = HomescreenManagerListReplyData(
        homescreens=[
            {"id": "default-homescreen", "name": "Default", "active": True},
            {"id": "my-custom-homescreen", "name": "My Custom Homescreen", "active": False}
        ]
    )
    list_response = HomescreenManagerListResponseMessage(data=list_reply_data, context=dummy_context)
    print(f"\nList Homescreens Response:\n{list_response.model_dump_json(indent=2)}")

    # Example: Get Active Homescreen Request
    get_active_request = HomescreenManagerGetActiveMessage(context=dummy_context)
    print(f"\nGet Active Homescreen Request:\n{get_active_request.model_dump_json(indent=2)}")

    # Example: Get Active Homescreen Response
    get_active_reply_data = HomescreenManagerGetActiveReplyData(
        homescreen={"id": "default-homescreen", "name": "Default", "active": True}
    )
    get_active_response = HomescreenManagerGetActiveResponseMessage(data=get_active_reply_data, context=dummy_context)
    print(f"\nGet Active Homescreen Response:\n{get_active_response.model_dump_json(indent=2)}")

    # Example: Set Active Homescreen
    set_active_data = HomescreenManagerSetActiveData(id="my-custom-homescreen")
    set_active_message = HomescreenManagerSetActiveMessage(data=set_active_data, context=dummy_context)
    print(f"\nSet Active Homescreen Message:\n{set_active_message.model_dump_json(indent=2)}")

    # Example: Disable Active Homescreen
    disable_active_message = HomescreenManagerDisableActiveMessage(context=dummy_context)
    print(f"\nDisable Active Homescreen Message:\n{disable_active_message.model_dump_json(indent=2)}")

    # Example: Show Active Homescreen
    show_active_message = HomescreenManagerShowActiveMessage(context=dummy_context)
    print(f"\nShow Active Homescreen Message:\n{show_active_message.model_dump_json(indent=2)}")

    # Example: Reload Homescreen List
    reload_list_message = HomescreenManagerReloadListMessage(context=dummy_context)
    print(f"\nReload Homescreen List Message:\n{reload_list_message.model_dump_json(indent=2)}")

    # Example: Activate Display
    activate_display_data = HomescreenManagerActivateDisplayData(homescreen_id="my-custom-homescreen")
    activate_display_message = HomescreenManagerActivateDisplayMessage(data=activate_display_data, context=dummy_context)
    print(f"\nActivate Display Message:\n{activate_display_message.model_dump_json(indent=2)}")

   # Example: Homescreen Register Examples
    register_examples_data = HomescreenRegisterExamplesData(
        skill_id="skill-my-app.mycroft",
        utterances=["open my app", "start my application"],
        lang="en-us"
    )
    register_examples_message = HomescreenRegisterExamplesMessage(data=register_examples_data, context=dummy_context)
    print(f"\nHomescreen Register Examples Message:\n{register_examples_message.model_dump_json(indent=2)}")
