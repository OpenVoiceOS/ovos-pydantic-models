from typing import Dict, Any, List

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


# --- OVOS Audio Service OPM Message Models ---

class OvosLanguagesTtsMessage(OpenVoiceOSMessage):
    """Query which languages the active TTS plugin supports.

    Emitted by GUI settings panels, language-switcher skills, or anything
    that needs to present a language selector. `ovos-audio` replies with
    `ovos.languages.tts.response` containing the list of BCP-47 codes.
    """
    message_type: str = "ovos.languages.tts"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosLanguagesTtsReplyData(BaseModel):
    """TTS language support list returned by `ovos-audio`."""
    langs: List[str] = Field(..., description="List of supported TTS languages (e.g., 'en-us', 'es-es').")


class OvosLanguagesTtsResponseMessage(OpenVoiceOSMessage):
    """Return the languages supported by the active TTS plugin.

    Emitted by `ovos-audio` in response to `ovos.languages.tts`.
    The list reflects only languages the currently loaded plugin can synthesize.
    """
    message_type: str = "ovos.languages.tts.response"
    data: OvosLanguagesTtsReplyData


class OpmTtsQueryMessage(OpenVoiceOSMessage):
    """Query the Plugin Manager for all installed TTS plugins and their capabilities.

    Emitted by settings GUIs and configuration tools that need to let the
    user select a TTS engine. `ovos-audio` (via OPM) replies with
    `opm.tts.query.response`.
    """
    message_type: str = "opm.tts.query"
    data: Dict[str, Any] = Field(default_factory=dict)


class OpmTtsQueryReplyData(BaseModel):
    """TTS plugin inventory returned by the Plugin Manager."""
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
    """Return the full TTS plugin inventory from the Plugin Manager.

    Emitted by `ovos-audio` in response to `opm.tts.query`. Includes all
    installed plugins, the languages each supports, their config schemas, and
    UI-ready option lists for settings panels.
    """
    message_type: str = "opm.tts.query.response"
    data: OpmTtsQueryReplyData


class OpmAudioQueryMessage(OpenVoiceOSMessage):
    """Query the Plugin Manager for all installed audio backend plugins.

    Emitted by settings GUIs that need to list available audio backends
    (VLC, MPV, simple, etc.). `ovos-audio` replies with
    `opm.audio.query.response`.
    """
    message_type: str = "opm.audio.query"
    data: Dict[str, Any] = Field(default_factory=dict)


class OpmAudioQueryReplyData(BaseModel):
    """Audio backend plugin inventory returned by the Plugin Manager."""
    plugins: List[str] = Field(..., description="List of installed audio backend plugin names.")
    configs: Dict[str, Any] = Field(..., description="Dictionary mapping backend name to its configuration.")
    options: Dict[str, Any] = Field(..., description="UI-friendly options for audio backends.")


class OpmAudioQueryResponseMessage(OpenVoiceOSMessage):
    """Return the full audio backend plugin inventory from the Plugin Manager.

    Emitted by `ovos-audio` in response to `opm.audio.query`. Includes the
    names of all installed backends and their configuration schemas.
    """
    message_type: str = "opm.audio.query.response"
    data: OpmAudioQueryReplyData


class OpmG2pQueryMessage(OpenVoiceOSMessage):
    """Query the Plugin Manager for all installed Grapheme-to-Phoneme plugins.

    G2P plugins convert text to phoneme strings for TTS engines that need
    phonetic input. Emitted by settings GUIs or TTS plugin configuration
    tools. `ovos-audio` replies with `opm.g2p.query.response`.
    """
    message_type: str = "opm.g2p.query"
    data: Dict[str, Any] = Field(default_factory=dict)


class OpmG2pQueryReplyData(BaseModel):
    """G2P plugin inventory returned by the Plugin Manager."""
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
    """Return the full G2P plugin inventory from the Plugin Manager.

    Emitted by `ovos-audio` in response to `opm.g2p.query`. Includes all
    installed G2P plugins, language support, config schemas, and UI options.
    """
    message_type: str = "opm.g2p.query.response"
    data: OpmG2pQueryReplyData
