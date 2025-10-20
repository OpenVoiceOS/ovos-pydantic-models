from typing import Dict, Any

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


# --- Skill Manager Message Models ---

class MycroftGuiAvailableData(BaseModel):
    """Data for `mycroft.gui.available` message."""
    permanent: bool = Field(False, description="If True, indicates GUI requests skills to never unload.")


class MycroftGuiAvailableMessage(OpenVoiceOSMessage):
    """Message for `mycroft.gui.available`."""
    message_type: str = "mycroft.gui.available"
    data: MycroftGuiAvailableData


class MycroftGuiUnavailableMessage(OpenVoiceOSMessage):
    """Message for `mycroft.gui.unavailable`."""
    message_type: str = "mycroft.gui.unavailable"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for GUI unavailable event.")


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Demonstrating Skill Manager Message Models ---")

    # Create a dummy session and context for demonstration
    dummy_session = Session(session_id="test-skill-manager-session-101", lang="en-us")
    dummy_context = MessageContext(source="skill_manager", session=dummy_session)

    # Example: GUI available
    gui_available_data = MycroftGuiAvailableData(permanent=False)
    gui_available_message = MycroftGuiAvailableMessage(data=gui_available_data, context=dummy_context)
    print(f"\nGUI Available Message:\n{gui_available_message.model_dump_json(indent=2)}")
