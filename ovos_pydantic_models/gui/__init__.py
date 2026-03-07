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
