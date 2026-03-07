from typing import Dict, Any, Optional

from pydantic import BaseModel, Field, ConfigDict

from ovos_pydantic_models.message import OpenVoiceOSMessage
from ovos_pydantic_models.intents.core import OvosUtteranceHandledMessage  # noqa: F401 — re-export


# --- Stop Service Message Models ---

class StopGlobalMessage(OpenVoiceOSMessage):
    """Tell every active skill to stop whatever it is doing immediately.

    Emitted by the intent service when the user says 'stop' (or equivalent)
    and no specific skill claims the stop. All active skills receive this and
    should halt ongoing actions (playback, timers, etc.).
    """
    message_type: str = "stop:global"
    data: Dict[str, Any] = Field(default_factory=dict)


class StopSkillData(BaseModel):
    """Payload for stopping a specific skill."""
    skill_id: str = Field(..., description="ID of the skill that should stop its current action.")


class StopSkillMessage(OpenVoiceOSMessage):
    """Tell a specific skill to stop its current action.

    Emitted by the intent service when a stop intent is resolved to a
    particular skill (e.g. 'stop the timer'). More targeted than
    `stop:global` — only the named skill is asked to stop.
    """
    message_type: str = "stop:skill"
    data: StopSkillData


class MycroftStopMessage(OpenVoiceOSMessage):
    """Legacy broadcast to all skills to stop active processing.

    Emitted when the user says 'stop' or 'cancel'. Older skills subscribe to
    this; newer skills use the `stop:global` / `{skill_id}.stop` ping-pong
    protocol. Both may be emitted for backward compatibility.
    """
    message_type: str = "mycroft.stop"
    data: Dict[str, Any] = Field(default_factory=dict)


class SkillStopPingData(BaseModel):
    """Poll payload asking a specific skill if it can handle the stop request."""
    skill_id: str = Field(..., description="ID of the skill being polled for stop capability.")
    model_config = ConfigDict(extra='allow')


class SkillStopPingMessage(OpenVoiceOSMessage):
    """Ask a specific skill whether it wants to handle the current stop event.

    Dynamic message type: `{skill_id}.stop.ping`. Emitted by the stop
    service to each active skill in priority order. The skill replies with
    `skill.stop.pong`. This avoids blindly calling stop on every skill.
    """
    message_type: str = Field(..., description="Dynamic: '{skill_id}.stop.ping'.")
    data: SkillStopPingData


class SkillStopPongData(BaseModel):
    """A skill's reply to a stop capability ping."""
    skill_id: str = Field(..., description="Skill ID responding to the ping.")
    can_handle: bool = Field(True, description="True if this skill has something active to stop right now.")
    model_config = ConfigDict(extra='allow')


class SkillStopPongMessage(OpenVoiceOSMessage):
    """A skill reports whether it has something to stop in response to a stop ping.

    Emitted by the skill in reply to `{skill_id}.stop.ping`. If `can_handle`
    is True the stop service sends a targeted `{skill_id}.stop` request.
    """
    message_type: str = "skill.stop.pong"
    data: SkillStopPongData


class SkillStopRequestMessage(OpenVoiceOSMessage):
    """Command a specific skill to stop its current action.

    Dynamic message type: `{skill_id}.stop`. Emitted after the skill confirms
    it can handle the stop via `skill.stop.pong`. The skill should halt
    playback, cancel timers, or any other ongoing work and reply with
    `{skill_id}.stop.response`.
    """
    message_type: str = Field(..., description="Dynamic: '{skill_id}.stop'.")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SkillStopResponseData(BaseModel):
    """Result of a targeted stop request to a skill."""
    result: bool = Field(..., description="True if the skill successfully stopped its active action.")
    error: Optional[str] = Field(None, description="Error description if the stop failed.")
    model_config = ConfigDict(extra='allow')


class SkillStopResponseMessage(OpenVoiceOSMessage):
    """Report whether a skill successfully stopped its current action.

    Dynamic message type: `{skill_id}.stop.response`. Emitted by the skill
    in reply to `{skill_id}.stop`. The stop service uses this to decide
    whether to try the next skill or declare stop handled.
    """
    message_type: str = Field(..., description="Dynamic: '{skill_id}.stop.response'.")
    data: SkillStopResponseData


class MycroftSkillsAbortQuestionData(BaseModel):
    """Payload for aborting a skill's pending get_response() question."""
    skill_id: str = Field(..., description="ID of the skill whose pending question should be cancelled.")


class MycroftSkillsAbortQuestionMessage(OpenVoiceOSMessage):
    """Cancel a skill's pending `get_response()` / `ask_yesno()` question.

    Emitted by the intent service when a stop event arrives while a skill
    is waiting for user input. The skill's `get_response()` call unblocks
    and returns None.
    """
    message_type: str = "mycroft.skills.abort_question"
    data: MycroftSkillsAbortQuestionData


class MycroftSkillsAbortExecutionData(BaseModel):
    """Payload for aborting a skill's currently running intent handler."""
    skill_id: str = Field(..., description="ID of the skill whose intent handler thread should be killed.")


class MycroftSkillsAbortExecutionMessage(OpenVoiceOSMessage):
    """Force-terminate a skill's running intent handler thread.

    Used by the `@killable_intent` decorator. Emitted when a stop arrives
    while a long-running handler is executing. The skill's handler thread
    receives a `AbortEvent` exception and must clean up.
    """
    message_type: str = "mycroft.skills.abort_execution"
    data: MycroftSkillsAbortExecutionData


class OvosSkillsConverseForceTimeoutData(BaseModel):
    """Payload for force-expiring a skill's converse session."""
    skill_id: str = Field(..., description="ID of the skill whose converse session should be terminated.")


class OvosSkillsConverseForceTimeoutMessage(OpenVoiceOSMessage):
    """Force-expire a skill's converse session immediately.

    Emitted by the stop service or intent service watchdog when a skill's
    converse() is stuck. Causes the skill to receive `{skill_id}.converse.killed`.
    """
    message_type: str = "ovos.skills.converse.force_timeout"
    data: OvosSkillsConverseForceTimeoutData


class MycroftAudioSpeechStopData(BaseModel):
    """Payload for stopping TTS speech from a specific skill."""
    skill_id: Optional[str] = Field(None, description="Skill ID whose speech should be stopped. None stops any ongoing speech.")
    model_config = ConfigDict(extra='allow')


class MycroftAudioSpeechStopMessage(OpenVoiceOSMessage):
    """Stop TTS speech playback, optionally scoped to a specific skill.

    Emitted by the stop protocol when a skill's speech should be cut short.
    If `skill_id` is None all current speech is stopped (equivalent to
    `mycroft.audio.speech.stop`).
    """
    message_type: str = "mycroft.audio.speech.stop"
    data: MycroftAudioSpeechStopData


class MycroftStopHandledData(BaseModel):
    """Acknowledgement that a stop request was handled by a specific component."""
    by: str = Field(..., description="Identifier of the component that handled the stop (e.g. 'audio:vlc', 'skill:timer').")


class MycroftStopHandledMessage(OpenVoiceOSMessage):
    """Confirm that a stop request was successfully handled.

    Emitted by whichever component (audio backend, skill, etc.) actually
    executed the stop. The stop service uses this to avoid redundant stops
    once one component has taken responsibility.
    """
    message_type: str = "mycroft.stop.handled"
    data: MycroftStopHandledData
