from typing import Dict, Any, List, Optional, Tuple, Union
from enum import IntEnum
from pydantic import BaseModel, Field, ConfigDict

from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import Session


class CQSMatchLevel(IntEnum):
    """Confidence tier for a Common Query Skill answer.

    Skills return one of these levels from `CQS_match_query_phrase()` to
    indicate how well their answer addresses the question. The CQS framework
    selects the highest-confidence answer across all registered skills.
    """
    EXACT = 1       # Skill found a specific, direct answer to the question
    CATEGORY = 2    # Skill found a category-level answer (e.g. a Wikipedia article)
    GENERAL = 3     # Skill can attempt a general/fallback answer


# Copy of CQSMatchLevel for skills that return visual media alongside answers
CQSVisualMatchLevel = IntEnum('CQSVisualMatchLevel',
                              [e.name for e in CQSMatchLevel])


# --- Common Query Skill Message Models ---

class QuestionQueryData(BaseModel):
    """Payload for broadcasting a user question to all Common Query Skills."""
    phrase: str = Field(..., description="The user's question phrase.")
    model_config = ConfigDict(extra='allow')


class QuestionQueryMessage(OpenVoiceOSMessage):
    """Broadcast a user question to all registered Common Query Skills.

    Emitted by the CQS framework when a question is not matched by any
    explicit intent. All skills that extend `CommonQuerySkill` receive this
    and may reply with `question:query.response`. The framework collects
    all responses, picks the highest-confidence answer, and calls
    `question:action` on the winning skill.
    """
    message_type: str = "question:query"
    data: QuestionQueryData


class QuestionActionData(BaseModel):
    """Payload for instructing the winning CQS skill to speak its answer."""
    phrase: str = Field(..., description="The original user's question phrase.")
    skill_id: str = Field(..., description="The ID of the skill whose action is being requested.")
    callback_data: Optional[Dict[str, Any]] = Field(
        None, description="Optional data passed from CQS_match_query_phrase."
    )
    model_config = ConfigDict(extra='allow')


class QuestionActionMessage(OpenVoiceOSMessage):
    """Tell the winning Common Query Skill to speak its answer.

    Emitted by the CQS framework after evaluating all `question:query.response`
    replies and selecting the best match. The named skill's `CQS_action()`
    method is called, which typically calls `self.speak()` with the answer.
    """
    message_type: str = "question:action"
    data: QuestionActionData


class OvosCommonQueryPingMessage(OpenVoiceOSMessage):
    """Poll all registered Common Query Skills to announce themselves.

    Emitted by the CQS framework at startup or after skill reload to discover
    which skills are available. Each CQS skill replies with
    `ovos.common_query.pong`. Used to build the active CQS skill registry.
    """
    message_type: str = "ovos.common_query.ping"
    data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class OvosCommonQueryPongData(BaseModel):
    """A Common Query Skill's response to the discovery ping."""
    skill_id: str = Field(..., description="The ID of the skill responding to the ping.")
    is_classic_cq: bool = Field(True, description="Indicates if the skill is a classic CommonQuerySkill.")
    model_config = ConfigDict(extra='allow')


class OvosCommonQueryPongMessage(OpenVoiceOSMessage):
    """A Common Query Skill announces its availability.

    Emitted by CQS skills in reply to `ovos.common_query.ping`. The framework
    adds the skill to its registry so it receives future `question:query`
    broadcasts.
    """
    message_type: str = "ovos.common_query.pong"
    data: OvosCommonQueryPongData


class QuestionQueryResponseData(BaseModel):
    """A Common Query Skill's response to a question broadcast."""
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
    """A Common Query Skill reports its answer to a question broadcast.

    Emitted by each CQS skill in reply to `question:query`. Skills may emit
    this multiple times: first with `searching=True` to claim the question
    while still processing, then with `searching=False` and `answer` set
    when the result is ready. The framework selects the response with the
    highest `conf` score from skills that have finished searching.
    """
    message_type: str = "question:query.response"
    data: QuestionQueryResponseData
