from typing import Dict, Any, List

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


# --- Listener Service Message Models ---


class OvosLanguagesSttMessage(OpenVoiceOSMessage):
    """Message for `ovos.languages.stt` (request for supported STT languages)."""
    message_type: str = "ovos.languages.stt"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for language request.")


class OvosLanguagesSttReplyData(BaseModel):
    """Data for `ovos.languages.stt` response."""
    langs: List[str] = Field(..., description="List of supported STT languages (e.g., 'en-us', 'es-es').")


class OvosLanguagesSttResponseMessage(OpenVoiceOSMessage):
    """Response message for `ovos.languages.stt`."""
    message_type: str = "ovos.languages.stt.response"
    data: OvosLanguagesSttReplyData


class OpmSttQueryMessage(OpenVoiceOSMessage):
    """Message for `opm.stt.query` (request for STT plugin info)."""
    message_type: str = "opm.stt.query"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for query.")


class OpmSttQueryReplyData(BaseModel):
    """Data for `opm.stt.query` response."""
    plugins: Dict[str, List[str]] = Field(
        ..., description="Dictionary mapping language to list of supported STT plugin names."
    )
    langs: List[str] = Field(..., description="List of all languages with supported STT plugins.")
    configs: Dict[str, Dict[str, Any]] = Field(
        ..., description="Dictionary mapping plugin name to its configuration options."
    )
    options: Dict[str, List[Dict[str, Any]]] = Field(
        ..., description="Dictionary mapping language to list of UI-friendly STT options."
    )


class OpmSttQueryResponseMessage(OpenVoiceOSMessage):
    """Response message for `opm.stt.query`."""
    message_type: str = "opm.stt.query.response"
    data: OpmSttQueryReplyData


class OpmWwQueryMessage(OpenVoiceOSMessage):
    """Message for `opm.ww.query` (request for Wake Word plugin info)."""
    message_type: str = "opm.ww.query"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for query.")


class OpmWwQueryReplyData(BaseModel):
    """Data for `opm.ww.query` response."""
    plugins: Dict[str, List[str]] = Field(
        ..., description="Dictionary mapping language to list of supported Wake Word plugin names."
    )
    langs: List[str] = Field(..., description="List of all languages with supported Wake Word plugins.")
    configs: Dict[str, Dict[str, Any]] = Field(
        ..., description="Dictionary mapping plugin name to its configuration options."
    )
    options: Dict[str, List[Dict[str, Any]]] = Field(
        ..., description="Dictionary mapping language to list of UI-friendly Wake Word options."
    )


class OpmWwQueryResponseMessage(OpenVoiceOSMessage):
    """Response message for `opm.ww.query`."""
    message_type: str = "opm.ww.query.response"
    data: OpmWwQueryReplyData


class OpmVadQueryMessage(OpenVoiceOSMessage):
    """Message for `opm.vad.query` (request for VAD plugin info)."""
    message_type: str = "opm.vad.query"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for query.")


class OpmVadQueryReplyData(BaseModel):
    """Data for `opm.vad.query` response."""
    plugins: Dict[str, List[str]] = Field(
        ..., description="Dictionary mapping language to list of supported VAD plugin names."
    )
    langs: List[str] = Field(..., description="List of all languages with supported VAD plugins.")
    configs: Dict[str, Dict[str, Any]] = Field(
        ..., description="Dictionary mapping plugin name to its configuration options."
    )
    options: Dict[str, List[Dict[str, Any]]] = Field(
        ..., description="Dictionary mapping language to list of UI-friendly VAD options."
    )


class OpmVadQueryResponseMessage(OpenVoiceOSMessage):
    """Response message for `opm.vad.query`."""
    message_type: str = "opm.vad.query.response"
    data: OpmVadQueryReplyData


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Demonstrating Listener Service Message Models ---")

    # Create a dummy session and context for demonstration
    dummy_session = Session(session_id="test-listener-session-789", lang="en-us")
    dummy_context = MessageContext(source="ovos_listener_service", session=dummy_session)

    # Example: OPM STT Query and Response
    opm_stt_query = OpmSttQueryMessage(context=dummy_context)
    print(f"\nOPM STT Query:\n{opm_stt_query.model_dump_json(indent=2)}")

    opm_stt_reply_data = OpmSttQueryReplyData(
        plugins={"en-us": ["stt-mozilla", "stt-google"], "es-es": ["stt-google"]},
        langs=["en-us", "es-es"],
        configs={"stt-mozilla": {"model": "default"}, "stt-google": {"api_key": "..."}},
        options={"en-us": [{"engine": "stt-mozilla", "lang": "en-us", "display_name": "Mozilla STT"}]}
    )
    opm_stt_response = OpmSttQueryResponseMessage(data=opm_stt_reply_data, context=dummy_context)
    print(f"\nOPM STT Query Response:\n{opm_stt_response.model_dump_json(indent=2)}")
