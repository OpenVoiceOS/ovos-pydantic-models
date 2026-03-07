from typing import Dict, Any

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


class MycroftIntentsIsReadyMessage(OpenVoiceOSMessage):
    """Message for `mycroft.intents.is_ready` (request for IntentService status)."""
    message_type: str = "mycroft.intents.is_ready"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for status request.")


class MycroftIntentsIsReadyReplyData(BaseModel):
    """Data for `mycroft.intents.is_ready` response."""
    status: bool = Field(..., description="True if IntentService is ready, False otherwise.")


class MycroftIntentsIsReadyResponseMessage(OpenVoiceOSMessage):
    """Response message for `mycroft.intents.is_ready`."""
    message_type: str = "mycroft.intents.is_ready.response"
    data: MycroftIntentsIsReadyReplyData
