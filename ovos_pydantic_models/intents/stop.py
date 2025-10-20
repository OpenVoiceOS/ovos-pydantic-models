from typing import Dict, Any, Optional

from pydantic import BaseModel, Field, ConfigDict

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


# --- Stop Service Message Models ---

class StopGlobalMessage(OpenVoiceOSMessage):
    """Message for `stop:global`."""
    message_type: str = "stop:global"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for global stop command.")


class StopSkillData(BaseModel):
    """Data for `stop:skill` message."""
    skill_id: str = Field(..., description="The ID of the skill to stop.")


class StopSkillMessage(OpenVoiceOSMessage):
    """Message for `stop:skill`."""
    message_type: str = "stop:skill"
    data: StopSkillData


class MycroftStopMessage(OpenVoiceOSMessage):
    """
    Message for `mycroft.stop`.
    (Already defined in ovos_audio_messages, included here for completeness)
    """
    message_type: str = "mycroft.stop"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for stop command.")


class OvosUtteranceHandledMessage(OpenVoiceOSMessage):
    """
    Message for `ovos.utterance.handled`.
    (Already defined in intent_service_messages and listener_messages, included here for completeness)
    """
    message_type: str = "ovos.utterance.handled"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for utterance handled event.")


class SkillStopPingData(BaseModel):
    """
    Data for `{skill_id}.stop.ping` message.
    """
    skill_id: str = Field(..., description="The ID of the skill being pinged for stop capability.")
    model_config = ConfigDict(extra='allow')  # Allow other data if forwarded from original message


class SkillStopPingMessage(OpenVoiceOSMessage):
    """
    Message for `{skill_id}.stop.ping`.
    The `message_type` will be dynamically set to the skill ID followed by `.stop.ping`.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'my-skill-id.stop.ping'.")
    data: SkillStopPingData


class SkillStopPongData(BaseModel):
    """Data for `skill.stop.pong` message."""
    skill_id: str = Field(..., description="The ID of the skill responding to the ping.")
    can_handle: bool = Field(True, description="True if the skill can handle the current stop request.")
    model_config = ConfigDict(extra='allow')  # Allow other data from original ping message


class SkillStopPongMessage(OpenVoiceOSMessage):
    """Message for `skill.stop.pong`."""
    message_type: str = "skill.stop.pong"
    data: SkillStopPongData


class SkillStopRequestMessage(OpenVoiceOSMessage):
    """
    Message for `{skill_id}.stop`.
    The `message_type` will be dynamically set to the skill ID followed by `.stop`.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'my-skill-id.stop'.")
    data: Optional[Dict[str, Any]] = Field(default_factory=dict,
                                       description="Data payload for skill stop request.")


class SkillStopResponseData(BaseModel):
    """
    Data for `{skill_id}.stop.response` message.
    """
    result: bool = Field(..., description="True if the skill successfully handled the stop request, False otherwise.")
    error: Optional[str] = Field(None, description="Error message if the stop request failed.")
    model_config = ConfigDict(extra='allow')  # Allow other data if forwarded from original message


class SkillStopResponseMessage(OpenVoiceOSMessage):
    """
    Message for `{skill_id}.stop.response`.
    The `message_type` will be dynamically set to the skill ID.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'my-skill-id.stop.response'.")
    data: SkillStopResponseData


class MycroftSkillsAbortQuestionData(BaseModel):
    """Data for `mycroft.skills.abort_question` message."""
    skill_id: str = Field(..., description="The ID of the skill whose question should be aborted.")


class MycroftSkillsAbortQuestionMessage(OpenVoiceOSMessage):
    """Message for `mycroft.skills.abort_question`."""
    message_type: str = "mycroft.skills.abort_question"
    data: MycroftSkillsAbortQuestionData


class OvosSkillsConverseForceTimeoutData(BaseModel):
    """Data for `ovos.skills.converse.force_timeout` message."""
    skill_id: str = Field(..., description="The ID of the skill whose converse session should be force-timed out.")


class OvosSkillsConverseForceTimeoutMessage(OpenVoiceOSMessage):
    """Message for `ovos.skills.converse.force_timeout`."""
    message_type: str = "ovos.skills.converse.force_timeout"
    data: OvosSkillsConverseForceTimeoutData


class MycroftAudioSpeechStopData(BaseModel):
    """Data for `mycroft.audio.speech.stop` message."""
    skill_id: Optional[str] = Field(None, description="The ID of the skill whose speech should be stopped.")
    model_config = ConfigDict(extra='allow')  # Allow other data if forwarded from original message


class MycroftAudioSpeechStopMessage(OpenVoiceOSMessage):
    """
    Message for `mycroft.audio.speech.stop`.
    (Already defined in ovos_audio_messages, included here for completeness)
    """
    message_type: str = "mycroft.audio.speech.stop"
    data: MycroftAudioSpeechStopData


class MycroftStopHandledData(BaseModel):
    """Data for `mycroft.stop.handled` message."""
    by: str = Field(..., description="Identifier of the component that handled the stop (e.g., 'audio:backend_name').")


class MycroftStopHandledMessage(OpenVoiceOSMessage):
    """Message for `mycroft.stop.handled`."""
    message_type: str = "mycroft.stop.handled"
    data: MycroftStopHandledData


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Demonstrating Stop Service Message Models ---")

    # Create a dummy session and context for demonstration
    dummy_session = Session(session_id="test-stop-session-123", lang="en-us")
    dummy_context = MessageContext(source="stop_service", session=dummy_session)

    # Example: Global Stop
    global_stop_message = StopGlobalMessage(context=dummy_context)
    print(f"\nGlobal Stop Message:\n{global_stop_message.model_dump_json(indent=2)}")

    # Example: Skill Stop
    stop_skill_data = StopSkillData(skill_id="skill-music.mycroft")
    stop_skill_message = StopSkillMessage(data=stop_skill_data, context=dummy_context)
    print(f"\nSkill Stop Message:\n{stop_skill_message.model_dump_json(indent=2)}")

    # Example: Dynamic Skill Stop Ping
    ping_data = SkillStopPingData(skill_id="skill-music.mycroft")
    ping_message = SkillStopPingMessage(
        message_type="skill-music.mycroft.stop.ping",
        data=ping_data,
        context=dummy_context
    )
    print(f"\nDynamic Skill Stop Ping Message:\n{ping_message.model_dump_json(indent=2)}")

    # Example: Skill Stop Pong
    pong_data = SkillStopPongData(skill_id="skill-music.mycroft", can_handle=True)
    pong_message = SkillStopPongMessage(data=pong_data, context=dummy_context)
    print(f"\nSkill Stop Pong Message:\n{pong_message.model_dump_json(indent=2)}")

    # Example: Dynamic Skill Stop Request
    stop_request_message = SkillStopRequestMessage(
        message_type="skill-music.mycroft.stop",
        data={},  # Empty data payload
        context=dummy_context
    )
    print(f"\nDynamic Skill Stop Request Message:\n{stop_request_message.model_dump_json(indent=2)}")

    # Example: Dynamic Skill Stop Response (Success)
    stop_response_data_success = SkillStopResponseData(result=True)
    stop_response_message_success = SkillStopResponseMessage(
        message_type="skill-music.mycroft.stop.response",
        data=stop_response_data_success,
        context=dummy_context
    )
    print(f"\nDynamic Skill Stop Response (Success):\n{stop_response_message_success.model_dump_json(indent=2)}")

    # Example: Dynamic Skill Stop Response (Error)
    stop_response_data_error = SkillStopResponseData(result=False, error="Skill is busy.")
    stop_response_message_error = SkillStopResponseMessage(
        message_type="skill-music.mycroft.stop.response",
        data=stop_response_data_error,
        context=dummy_context
    )
    print(f"\nDynamic Skill Stop Response (Error):\n{stop_response_message_error.model_dump_json(indent=2)}")

    # Example: Abort Question
    abort_question_data = MycroftSkillsAbortQuestionData(skill_id="skill-qa.mycroft")
    abort_question_message = MycroftSkillsAbortQuestionMessage(data=abort_question_data, context=dummy_context)
    print(f"\nAbort Question Message:\n{abort_question_message.model_dump_json(indent=2)}")

    # Example: Converse Force Timeout
    force_timeout_data = OvosSkillsConverseForceTimeoutData(skill_id="skill-chat.mycroft")
    force_timeout_message = OvosSkillsConverseForceTimeoutMessage(data=force_timeout_data, context=dummy_context)
    print(f"\nConverse Force Timeout Message:\n{force_timeout_message.model_dump_json(indent=2)}")

    # Example: Mycroft Audio Speech Stop
    speech_stop_data = MycroftAudioSpeechStopData(skill_id="skill-news.mycroft")
    speech_stop_message = MycroftAudioSpeechStopMessage(data=speech_stop_data, context=dummy_context)
    print(f"\nMycroft Audio Speech Stop Message:\n{speech_stop_message.model_dump_json(indent=2)}")

    # Example: mycroft.stop.handled
    stop_handled_msg_data = MycroftStopHandledData(by="audio:my_audio_backend")
    stop_handled_message = MycroftStopHandledMessage(data=stop_handled_msg_data)
    print(f"\nStop Handled Message:\n{stop_handled_message.model_dump_json(indent=2)}")
