from typing import Dict, Any, Optional

from pydantic import BaseModel, Field, ConfigDict

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


# --- Intent Service Message Models ---

class IntentServicePipelinesReloadMessage(OpenVoiceOSMessage):
    """Message for `intent.service.pipelines.reload` (request to reload intent parsing pipelines)."""
    message_type: str = "intent.service.pipelines.reload"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for reload request.")


class OvosUtteranceCancelledMessage(OpenVoiceOSMessage):
    """Message for `ovos.utterance.cancelled`."""
    message_type: str = "ovos.utterance.cancelled"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for utterance cancelled event.")


class OvosUtteranceHandledMessage(OpenVoiceOSMessage):
    """
    Message for `ovos.utterance.handled`.
    (Already defined in playback_messages and listener_messages, included here for completeness)
    """
    message_type: str = "ovos.utterance.handled"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for utterance handled event.")


class CompleteIntentFailureData(BaseModel, extra='allow'):
    """Data for `complete_intent_failure` message."""
    utterance: str = Field(..., description="The utterance that could not be handled by any intent.")
    lang: str = Field(..., description="The language of the utterance.")
    # Allow arbitrary extra data from the original message if needed


class CompleteIntentFailureMessage(OpenVoiceOSMessage):
    """Message for `complete_intent_failure`."""
    message_type: str = "complete_intent_failure"
    data: CompleteIntentFailureData


class AddContextData(BaseModel):
    """Data for `add_context` message."""
    context: str = Field(..., description="The context item to add (e.g., 'date').")
    word: Optional[str] = Field(None, description="An alias for the context item (e.g., 'today').")
    origin: Optional[str] = Field(None, description="Origin of the context, used for context depth calculation.")


class AddContextMessage(OpenVoiceOSMessage):
    """Message for `add_context`."""
    message_type: str = "add_context"
    data: AddContextData


class RemoveContextData(BaseModel):
    """Data for `remove_context` message."""
    context: str = Field(..., description="The context item to remove.")


class RemoveContextMessage(OpenVoiceOSMessage):
    """Message for `remove_context`."""
    message_type: str = "remove_context"
    data: RemoveContextData


class ClearContextMessage(OpenVoiceOSMessage):
    """Message for `clear_context`."""
    message_type: str = "clear_context"
    data: Dict[str, Any] = Field(default_factory=dict, description="Empty data payload for clear context command.")


class IntentServiceIntentGetData(BaseModel):
    """Data for `intent.service.intent.get` message."""
    utterance: str = Field(..., description="The utterance to get an intent for.")


class IntentServiceIntentGetMessage(OpenVoiceOSMessage):
    """Message for `intent.service.intent.get`."""
    message_type: str = "intent.service.intent.get"
    data: IntentServiceIntentGetData


class IntentServiceIntentReplyIntentData(BaseModel, extra='allow'):
    """Structure of the 'intent' dictionary within `IntentServiceIntentReplyData`."""
    intent_name: str = Field(..., description="The name of the matched intent.")
    intent_service: str = Field(..., description="The pipeline plugin that matched the intent (e.g., 'adapt_high').")
    skill_id: str = Field(..., description="The ID of the skill that owns the intent.")
    handler: str = Field(..., description="The name of the handler function that processed the intent.")
    # Allow arbitrary extra data from the match_data


class IntentServiceIntentReplyData(BaseModel):
    """Data for `intent.service.intent.reply` message."""
    intent: Optional[IntentServiceIntentReplyIntentData] = Field(
        None, description="Details of the matched intent, or None if no intent matched."
    )
    utterance: str = Field(..., description="The original utterance.")


class IntentServiceIntentReplyMessage(OpenVoiceOSMessage):
    """Message for `intent.service.intent.reply`."""
    message_type: str = "intent.service.intent.reply"
    data: IntentServiceIntentReplyData



class SkillActivateData(BaseModel, extra='allow'):
    """
    Data for skill activation messages (e.g., `{skill_id}.activate`).
    While the message_type is dynamic, the data payload is consistent.
    """
    # No specific fields defined in the current usage beyond the implicit skill_id
    # but could include activation context if needed.


class SkillActivateMessage(OpenVoiceOSMessage):
    """
    Generic message for skill activation (e.g., `{skill_id}.activate`).
    The `message_type` will be dynamically set to the skill ID followed by `.activate`.
    """
    message_type: str = Field(..., description="Dynamic message type, e.g., 'my-skill-id.activate'.")
    data: SkillActivateData = Field(default_factory=SkillActivateData, description="Data payload for skill activation.")


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Demonstrating Intent Service Message Models ---")

    # Create a dummy session and context for demonstration
    dummy_session = Session(session_id="test-intent-session-123", lang="en-us")
    dummy_context = MessageContext(source="intent_service", session=dummy_session)

    # Example: Pipelines Reload Request
    pipelines_reload_message = IntentServicePipelinesReloadMessage(context=dummy_context)
    print(f"\nPipelines Reload Message:\n{pipelines_reload_message.model_dump_json(indent=2)}")

    # Example: Utterance Cancelled
    utterance_cancelled_message = OvosUtteranceCancelledMessage(context=dummy_context)
    print(f"\nUtterance Cancelled Message:\n{utterance_cancelled_message.model_dump_json(indent=2)}")

    # Example: Complete Intent Failure
    failure_data = CompleteIntentFailureData(utterance="this is an unhandled query", lang="en-us")
    complete_failure_message = CompleteIntentFailureMessage(data=failure_data, context=dummy_context)
    print(f"\nComplete Intent Failure Message:\n{complete_failure_message.model_dump_json(indent=2)}")

    # Example: Add Context
    add_context_data = AddContextData(context="location", word="home", origin="skill-weather.mycroft")
    add_context_message = AddContextMessage(data=add_context_data, context=dummy_context)
    print(f"\nAdd Context Message:\n{add_context_message.model_dump_json(indent=2)}")

    # Example: Remove Context
    remove_context_data = RemoveContextData(context="location")
    remove_context_message = RemoveContextMessage(data=remove_context_data, context=dummy_context)
    print(f"\nRemove Context Message:\n{remove_context_message.model_dump_json(indent=2)}")

    # Example: Clear Context
    clear_context_message = ClearContextMessage(context=dummy_context)
    print(f"\nClear Context Message:\n{clear_context_message.model_dump_json(indent=2)}")

    # Example: Get Intent Request
    get_intent_data = IntentServiceIntentGetData(utterance="what time is it")
    get_intent_message = IntentServiceIntentGetMessage(data=get_intent_data, context=dummy_context)
    print(f"\nGet Intent Request:\n{get_intent_message.model_dump_json(indent=2)}")

    # Example: Get Intent Reply (Success)
    intent_reply_intent_data = IntentServiceIntentReplyIntentData(
        intent_name="TimeIntent",
        intent_service="adapt_high",
        skill_id="skill-date-time.mycroft",
        handler="handle_time_intent",
        entities={"Time": "time"}  # Example of extra data
    )
    intent_reply_data = IntentServiceIntentReplyData(
        intent=intent_reply_intent_data,
        utterance="what time is it"
    )
    intent_reply_message = IntentServiceIntentReplyMessage(data=intent_reply_data, context=dummy_context)
    print(f"\nGet Intent Reply (Success):\n{intent_reply_message.model_dump_json(indent=2)}")

    # Example: Get Intent Reply (Failure)
    intent_reply_failure_data = IntentServiceIntentReplyData(
        intent=None,
        utterance="unrecognized query"
    )
    intent_reply_failure_message = IntentServiceIntentReplyMessage(data=intent_reply_failure_data,
                                                                   context=dummy_context)
    print(f"\nGet Intent Reply (Failure):\n{intent_reply_failure_message.model_dump_json(indent=2)}")

    # Example: Skills Deactivate
    skills_deactivate_data = IntentServiceSkillsDeactivateData(skill_id="skill-conversation.mycroft")
    skills_deactivate_message = IntentServiceSkillsDeactivateMessage(data=skills_deactivate_data, context=dummy_context)
    print(f"\nSkills Deactivate Message:\n{skills_deactivate_message.model_dump_json(indent=2)}")

    # Example: Dynamic Skill Activate Message
    # Note: In actual usage, message_type would be f"{skill_id}.activate"
    skill_activate_message = SkillActivateMessage(
        message_type="skill-weather.mycroft.activate",
        data=SkillActivateData(),  # Empty data payload
        context=dummy_context
    )
    print(f"\nDynamic Skill Activate Message:\n{skill_activate_message.model_dump_json(indent=2)}")
