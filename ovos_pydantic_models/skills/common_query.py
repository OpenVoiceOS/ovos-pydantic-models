from typing import Dict, Any, List, Optional, Tuple, Union
from enum import IntEnum
from pydantic import BaseModel, Field, ConfigDict

# Assuming these are available from your ovos_pydantic_models library
from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session

# Enums for CQSMatchLevel and CQSVisualMatchLevel
class CQSMatchLevel(IntEnum):
    """
    Represents the confidence level of a Common Query Skill match.
    """
    EXACT = 1       # Skill could find a specific answer for the question
    CATEGORY = 2    # Skill could find an answer from a category in the query
    GENERAL = 3     # The query could be processed as a general query

# Copy of CQSMatchLevel to use if the skill returns visual media
CQSVisualMatchLevel = IntEnum('CQSVisualMatchLevel',
                              [e.name for e in CQSMatchLevel])


# --- Common Query Skill Message Models ---

class QuestionQueryData(BaseModel):
    """Data for `question:query` message."""
    phrase: str = Field(..., description="The user's question phrase.")
    # Allow other context from the original message if needed
    model_config = ConfigDict(extra='allow')

class QuestionQueryMessage(OpenVoiceOSMessage):
    """Message for `question:query` (request to common query skills)."""
    message_type: str = "question:query"
    data: QuestionQueryData


class QuestionActionData(BaseModel):
    """Data for `question:action` message."""
    phrase: str = Field(..., description="The original user's question phrase.")
    skill_id: str = Field(..., description="The ID of the skill whose action is being requested.")
    callback_data: Optional[Dict[str, Any]] = Field(
        None, description="Optional data passed from CQS_match_query_phrase."
    )
    # Allow other context from the original message if needed
    model_config = ConfigDict(extra='allow')

class QuestionActionMessage(OpenVoiceOSMessage):
    """Message for `question:action` (triggering a skill's CQS_action)."""
    message_type: str = "question:action"
    data: QuestionActionData


class OvosCommonQueryPingMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_query.ping` (request for common query skills to announce themselves)."""
    message_type: str = "ovos.common_query.ping"
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class OvosCommonQueryPongData(BaseModel):
    """Data for `ovos.common_query.pong` message."""
    skill_id: str = Field(..., description="The ID of the skill responding to the ping.")
    is_classic_cq: bool = Field(True, description="Indicates if the skill is a classic CommonQuerySkill.")
    model_config = ConfigDict(extra='allow') # Allow other context from the original message if needed

class OvosCommonQueryPongMessage(OpenVoiceOSMessage):
    """Message for `ovos.common_query.pong` (response from common query skills)."""
    message_type: str = "ovos.common_query.pong"
    data: OvosCommonQueryPongData


class QuestionQueryResponseData(BaseModel):
    """Data for `question:query.response` message."""
    phrase: str = Field(..., description="The original user's question phrase.")
    skill_id: str = Field(..., description="The ID of the skill responding to the query.")
    searching: bool = Field(..., description="True if the skill is still searching, False if done.")
    answer: Optional[str] = Field(None, description="The speakable answer found by the skill.")
    handles_speech: Optional[bool] = Field(None, description="True if the skill handled speech itself.")
    callback_data: Optional[Dict[str, Any]] = Field(
        None, description="Optional data to be passed to CQS_action if this skill is selected."
    )
    conf: Optional[float] = Field(None, description="The calculated confidence level (0.0-1.0).")
    model_config = ConfigDict(extra='allow')

class QuestionQueryResponseMessage(OpenVoiceOSMessage):
    """Response message for `question:query`."""
    message_type: str = "question:query.response"
    data: QuestionQueryResponseData


# --- Example Usage ---
if __name__ == "__main__":
    print("--- Demonstrating Common Query Skill Message Models ---")

    # Create a dummy session and context for demonstration
    dummy_session = Session(session_id="test-cqs-session-456", lang="en-us")
    dummy_context = MessageContext(source="common_query_skill", session=dummy_session)

    # Example: Question Query Request
    question_query_data = QuestionQueryData(phrase="what is the capital of France?")
    question_query_message = QuestionQueryMessage(data=question_query_data, context=dummy_context)
    print(f"\nQuestion Query Request:\n{question_query_message.model_dump_json(indent=2)}")

    # Example: Question Query Response (Searching)
    query_response_searching_data = QuestionQueryResponseData(
        phrase="what is the capital of France?",
        skill_id="skill-geography.mycroft",
        searching=True
    )
    query_response_searching_message = QuestionQueryResponseMessage(
        data=query_response_searching_data, context=dummy_context
    )
    print(f"\nQuestion Query Response (Searching):\n{query_response_searching_message.model_dump_json(indent=2)}")

    # Example: Question Query Response (Answer Found)
    query_response_answer_data = QuestionQueryResponseData(
        phrase="what is the capital of France?",
        skill_id="skill-geography.mycroft",
        searching=False,
        answer="Paris is the capital of France.",
        handles_speech=False,
        callback_data={"city": "Paris", "country": "France"},
        conf=0.85
    )
    query_response_answer_message = QuestionQueryResponseMessage(
        data=query_response_answer_data, context=dummy_context
    )
    print(f"\nQuestion Query Response (Answer Found):\n{query_response_answer_message.model_dump_json(indent=2)}")

    # Example: Question Query Response (No Answer)
    query_response_no_answer_data = QuestionQueryResponseData(
        phrase="what is a blorg?",
        skill_id="skill-unknown-facts.mycroft",
        searching=False,
        answer=None,
        conf=0.0
    )
    query_response_no_answer_message = QuestionQueryResponseMessage(
        data=query_response_no_answer_data, context=dummy_context
    )
    print(f"\nQuestion Query Response (No Answer):\n{query_response_no_answer_message.model_dump_json(indent=2)}")

    # Example: Question Action Request
    question_action_data = QuestionActionData(
        phrase="what is the capital of France?",
        skill_id="skill-geography.mycroft",
        callback_data={"city": "Paris", "country": "France", "answer": "Paris is the capital of France."}
    )
    question_action_message = QuestionActionMessage(data=question_action_data, context=dummy_context)
    print(f"\nQuestion Action Request:\n{question_action_message.model_dump_json(indent=2)}")

    # Example: Common Query Ping
    cq_ping_message = OvosCommonQueryPingMessage(context=dummy_context)
    print(f"\nCommon Query Ping Message:\n{cq_ping_message.model_dump_json(indent=2)}")

    # Example: Common Query Pong
    cq_pong_data = OvosCommonQueryPongData(skill_id="skill-wikipedia.mycroft", is_classic_cq=True)
    cq_pong_message = OvosCommonQueryPongMessage(data=cq_pong_data, context=dummy_context)
    print(f"\nCommon Query Pong Message:\n{cq_pong_message.model_dump_json(indent=2)}")
