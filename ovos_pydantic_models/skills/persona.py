from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


# --- OVOS Persona Skill Messages ---
# The persona system allows OVOS to route utterances to LLM-backed "personas"
# (e.g. ChatGPT, local GGUF models) as a conversational fallback. Users can
# summon, query, list, and release personas by voice or via the bus.
# Implemented in ovos-persona.


class PersonaQueryData(BaseModel):
    """Payload to direct a query at a specific persona."""
    persona: Optional[str] = Field(
        None,
        description="Name of the persona to query. If omitted, the active persona is used."
    )


class PersonaQueryMessage(OpenVoiceOSMessage):
    """Send a query to the active (or named) persona.

    Emitted when OVOS routes an utterance to a persona for a conversational
    response. The persona skill looks up the named persona (or the currently
    active one), passes the utterance to the underlying solver, and speaks
    the result.
    """
    message_type: str = "persona:query"
    data: PersonaQueryData


class PersonaSummonData(BaseModel):
    """Payload to activate a named persona."""
    persona: str = Field(..., description="Name of the persona to activate.")


class PersonaSummonMessage(OpenVoiceOSMessage):
    """Activate a named persona, making it the active fallback handler.

    Emitted when the user says 'hey [persona name]' or when a skill explicitly
    switches the conversational context to a persona. While a persona is active,
    all unmatched utterances are routed to it.
    """
    message_type: str = "persona:summon"
    data: PersonaSummonData


class PersonaReleaseMessage(OpenVoiceOSMessage):
    """Deactivate the currently active persona.

    Emitted when the user says 'goodbye' or a deactivation phrase while a
    persona is active. Returns OVOS to normal intent pipeline handling for
    subsequent utterances.
    """
    message_type: str = "persona:release"
    data: Dict[str, Any] = Field(default_factory=dict)


class PersonaListMessage(OpenVoiceOSMessage):
    """Request the persona skill to list all available personas aloud.

    Emitted by voice commands like 'list personas' or 'what personas do you
    have?'. The persona skill speaks the names of all loaded personas.
    """
    message_type: str = "persona:list"
    data: Dict[str, Any] = Field(default_factory=dict)


class PersonaCheckMessage(OpenVoiceOSMessage):
    """Request the persona skill to report which persona is currently active.

    Emitted by voice commands like 'which persona are you using?'. If no
    persona is active the skill says so; otherwise it speaks the persona name.
    """
    message_type: str = "persona:check"
    data: Dict[str, Any] = Field(default_factory=dict)
