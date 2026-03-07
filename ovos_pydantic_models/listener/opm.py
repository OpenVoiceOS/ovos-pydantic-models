from typing import Dict, Any, List

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


# --- Listener Service OPM Message Models ---


class OvosLanguagesSttMessage(OpenVoiceOSMessage):
    """Query which languages the active STT plugin supports.

    Emitted by GUI settings panels, language-switcher skills, or anything
    that needs to present a language selector. `ovos-dinkum-listener` replies
    with `ovos.languages.stt.response` containing BCP-47 language codes.
    """
    message_type: str = "ovos.languages.stt"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosLanguagesSttReplyData(BaseModel):
    """STT language support list returned by the listener."""
    langs: List[str] = Field(..., description="List of supported STT languages (e.g., 'en-us', 'es-es').")


class OvosLanguagesSttResponseMessage(OpenVoiceOSMessage):
    """Return the languages supported by the active STT plugin.

    Emitted by `ovos-dinkum-listener` in response to `ovos.languages.stt`.
    The list reflects only languages the currently loaded STT plugin recognizes.
    """
    message_type: str = "ovos.languages.stt.response"
    data: OvosLanguagesSttReplyData


class OpmSttQueryMessage(OpenVoiceOSMessage):
    """Query the Plugin Manager for all installed STT plugins and their capabilities.

    Emitted by settings GUIs and configuration tools that need to present
    a list of available STT engines to the user. `ovos-dinkum-listener`
    (via OPM) replies with `opm.stt.query.response`.
    """
    message_type: str = "opm.stt.query"
    data: Dict[str, Any] = Field(default_factory=dict)


class OpmSttQueryReplyData(BaseModel):
    """STT plugin inventory returned by the Plugin Manager."""
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
    """Return the full STT plugin inventory from the Plugin Manager.

    Emitted by `ovos-dinkum-listener` in response to `opm.stt.query`. Includes
    all installed STT plugins, language support, config schemas, and UI option
    lists for settings panels.
    """
    message_type: str = "opm.stt.query.response"
    data: OpmSttQueryReplyData


class OpmWwQueryMessage(OpenVoiceOSMessage):
    """Query the Plugin Manager for all installed Wake Word plugins.

    Emitted by settings GUIs or configuration tools. `ovos-dinkum-listener`
    replies with `opm.ww.query.response` listing all installed wake word
    engines and their language support.
    """
    message_type: str = "opm.ww.query"
    data: Dict[str, Any] = Field(default_factory=dict)


class OpmWwQueryReplyData(BaseModel):
    """Wake Word plugin inventory returned by the Plugin Manager."""
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
    """Return the full Wake Word plugin inventory from the Plugin Manager.

    Emitted by `ovos-dinkum-listener` in response to `opm.ww.query`. Includes
    all installed wake word engines, language support, and configuration schemas.
    """
    message_type: str = "opm.ww.query.response"
    data: OpmWwQueryReplyData


class OpmVadQueryMessage(OpenVoiceOSMessage):
    """Query the Plugin Manager for all installed Voice Activity Detection plugins.

    Emitted by settings GUIs or configuration tools. `ovos-dinkum-listener`
    replies with `opm.vad.query.response` listing installed VAD engines.
    VAD plugins determine when the user starts and stops speaking.
    """
    message_type: str = "opm.vad.query"
    data: Dict[str, Any] = Field(default_factory=dict)


class OpmVadQueryReplyData(BaseModel):
    """VAD plugin inventory returned by the Plugin Manager."""
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
    """Return the full VAD plugin inventory from the Plugin Manager.

    Emitted by `ovos-dinkum-listener` in response to `opm.vad.query`. Includes
    all installed VAD plugins, language support, and configuration schemas.
    """
    message_type: str = "opm.vad.query.response"
    data: OpmVadQueryReplyData
