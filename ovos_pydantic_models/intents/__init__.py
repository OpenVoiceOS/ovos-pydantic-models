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


if __name__ == "__main__":
    # Create a dummy session and context for demonstration
    dummy_session = Session(session_id="test-skill-manager-session-101", lang="en-us")
    dummy_context = MessageContext(source="skill_manager", session=dummy_session)

    # Example: Intent Service Is Ready request and response
    intents_ready_request = MycroftIntentsIsReadyMessage(context=dummy_context)
    print(f"\nIntents Ready Request:\n{intents_ready_request.model_dump_json(indent=2)}")

    intents_ready_reply_data = MycroftIntentsIsReadyReplyData(status=True)
    intents_ready_response = MycroftIntentsIsReadyResponseMessage(data=intents_ready_reply_data, context=dummy_context)
    print(f"\nIntents Ready Response:\n{intents_ready_response.model_dump_json(indent=2)}")
