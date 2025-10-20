from typing import Dict, Any, List

from pydantic import BaseModel, Field

# Assuming these are available from your ovos_pydantic_models library
from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


# --- OVOS Audio Service OPM Message Models ---

class OvosLanguagesTtsMessage(OpenVoiceOSMessage):
    """Message for `ovos.languages.tts` (request for supported TTS languages)."""
    message_type: str = "ovos.languages.tts"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for language request.")


class OvosLanguagesTtsReplyData(BaseModel):
    """Data for `ovos.languages.tts` response."""
    langs: List[str] = Field(..., description="List of supported TTS languages (e.g., 'en-us', 'es-es').")


class OvosLanguagesTtsResponseMessage(OpenVoiceOSMessage):
    """Response message for `ovos.languages.tts`."""
    message_type: str = "ovos.languages.tts.response"
    data: OvosLanguagesTtsReplyData


class OpmTtsQueryMessage(OpenVoiceOSMessage):
    """Message for `opm.tts.query` (request for TTS plugin info)."""
    message_type: str = "opm.tts.query"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for query.")


class OpmTtsQueryReplyData(BaseModel):
    """Data for `opm.tts.query` response."""
    plugins: Dict[str, List[str]] = Field(
        ..., description="Dictionary mapping language to list of supported TTS plugin names."
    )
    langs: List[str] = Field(..., description="List of all languages with supported TTS plugins.")
    configs: Dict[str, Dict[str, Any]] = Field(
        ..., description="Dictionary mapping plugin name to its configuration options."
    )
    options: Dict[str, List[Dict[str, Any]]] = Field(
        ..., description="Dictionary mapping language to list of UI-friendly TTS options."
    )


class OpmTtsQueryResponseMessage(OpenVoiceOSMessage):
    """Response message for `opm.tts.query`."""
    message_type: str = "opm.tts.query.response"
    data: OpmTtsQueryReplyData


class OpmAudioQueryMessage(OpenVoiceOSMessage):
    """Message for `opm.audio.query` (request for audio backend plugin info)."""
    message_type: str = "opm.audio.query"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for query.")


class OpmAudioQueryReplyData(BaseModel):
    """Data for `opm.audio.query` response."""
    plugins: List[str] = Field(..., description="List of installed audio backend plugin names.")
    configs: Dict[str, Any] = Field(..., description="Dictionary mapping backend name to its configuration.")
    options: Dict[str, Any] = Field(..., description="UI-friendly options for audio backends.")


class OpmAudioQueryResponseMessage(OpenVoiceOSMessage):
    """Response message for `opm.audio.query`."""
    message_type: str = "opm.audio.query.response"
    data: OpmAudioQueryReplyData


class OpmG2pQueryMessage(OpenVoiceOSMessage):
    """Message for `opm.g2p.query` (request for G2P plugin info)."""
    message_type: str = "opm.g2p.query"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for query.")


class OpmG2pQueryReplyData(BaseModel):
    """Data for `opm.g2p.query` response."""
    plugins: Dict[str, List[str]] = Field(
        ..., description="Dictionary mapping language to list of supported G2P plugin names."
    )
    langs: List[str] = Field(..., description="List of all languages with supported G2P plugins.")
    configs: Dict[str, Dict[str, Any]] = Field(
        ..., description="Dictionary mapping plugin name to its configuration options."
    )
    options: Dict[str, List[Dict[str, Any]]] = Field(
        ..., description="Dictionary mapping language to list of UI-friendly G2P options."
    )


class OpmG2pQueryResponseMessage(OpenVoiceOSMessage):
    """Response message for `opm.g2p.query`."""
    message_type: str = "opm.g2p.query.response"
    data: OpmG2pQueryReplyData


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Demonstrating OVOS Audio Service Message Models ---")

    # Create a dummy session and context for demonstration
    dummy_session = Session(session_id="test-audio-session-456", lang="en-us")
    dummy_context = MessageContext(source="ovos_audio_service", session=dummy_session)

    # Example: Request TTS languages
    tts_langs_request = OvosLanguagesTtsMessage(context=dummy_context)
    print(f"\nTTS Languages Request:\n{tts_langs_request.model_dump_json(indent=2)}")

    # Example: TTS languages response
    tts_langs_reply_data = OvosLanguagesTtsReplyData(langs=["en-us", "es-es", "fr-fr"])
    tts_langs_response = OvosLanguagesTtsResponseMessage(data=tts_langs_reply_data, context=dummy_context)
    print(f"\nTTS Languages Response:\n{tts_langs_response.model_dump_json(indent=2)}")

    # Example: OPM TTS Query and Response
    opm_tts_query = OpmTtsQueryMessage(context=dummy_context)
    print(f"\nOPM TTS Query:\n{opm_tts_query.model_dump_json(indent=2)}")

    opm_tts_reply_data = OpmTtsQueryReplyData(
        plugins={"en-us": ["plugin-mimic3", "plugin-google"], "es-es": ["plugin-google"]},
        langs=["en-us", "es-es"],
        configs={"plugin-mimic3": {"voice": "default"}, "plugin-google": {"api_key": "..."}},
        options={"en-us": [{"engine": "plugin-mimic3", "lang": "en-us", "display_name": "Mimic3"}]}
    )
    opm_tts_response = OpmTtsQueryResponseMessage(data=opm_tts_reply_data, context=dummy_context)
    print(f"\nOPM TTS Query Response:\n{opm_tts_response.model_dump_json(indent=2)}")
