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
    """A skill's answer to the poll: whether it can answer this utterance."""
    utterance: str = Field(..., description="Echo of the ping's utterance.")
    skill_id: str = Field(..., description="The ID of the responding skill.")
    can_answer: bool = Field(..., description="Whether the skill claims it can answer.")
    latency_ms: Optional[float] = Field(None, description="Hint for how long a full answer is expected to take. Never a commitment.")
    model_config = ConfigDict(extra='allow')


class OvosCommonQueryPongMessage(OpenVoiceOSMessage):
    """A skill declares whether it can answer the polled utterance.

    Emitted by a Common Query skill in reply to `ovos.common_query.ping`. The
    pipeline plugin uses `can_answer` to narrow the skill set before running the
    expensive full-answer round, and `latency_ms` to size its collection window.
    The decision must be a fast local one — keyword or vocabulary matching, never
    blocking I/O.

    The contest is identified by `context.utterance_id`, carried onto the pong by
    ordinary `reply` derivation.
    """
    message_type: str = "ovos.common_query.pong"
    data: OvosCommonQueryPongData


class OvosCommonQueryPongLegacyData(BaseModel):
    """Pre-spec pong payload: a skill announcing itself rather than answering."""
    skill_id: str = Field(..., description="The ID of the skill responding to the ping.")
    is_classic_cq: bool = Field(True, description="Whether the skill is a classic CommonQuerySkill.")
    model_config = ConfigDict(extra='allow')


class OvosCommonQueryPongLegacyMessage(OpenVoiceOSMessage):
    """A skill announces its availability, without saying whether it can answer.

    The shape `ovos-workshop` emits from its `ovos.common_query.ping` handler.
    It predates the poll semantics and omits `can_answer`, so a plugin reading it
    learns only that the skill exists. Producers should send
    `OvosCommonQueryPongMessage` instead.
    """
    message_type: str = "ovos.common_query.pong"
    data: OvosCommonQueryPongLegacyData


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


class CommonQueryQuestionData(BaseModel):
    """Payload for a common-query pipeline question dispatch."""
    utterance: str = Field(..., description="The user's utterance to answer.")


class CommonQueryQuestionMessage(OpenVoiceOSMessage):
    """Dispatch a user utterance to all registered common-query skills.

    Emitted by the common-query pipeline plugin (`ovos-common-query-pipeline-plugin`)
    after classifying the utterance as a factual question. All skills that
    registered via `ovos.common_query.pong` receive this message and respond
    with `question:query.response`. The pipeline collects responses and selects
    the highest-confidence answer.
    """
    message_type: str = "common_query.question"
    data: CommonQueryQuestionData


class PlayQueryData(BaseModel):
    """Payload for a legacy Common Play System media query."""
    phrase: str = Field(..., description="Media search phrase from the user utterance.")


class PlayQueryMessage(OpenVoiceOSMessage):
    """Query all legacy CommonPlaySkills for a media match.

    **Legacy** — superseded by the OCP query protocol (`ovos.common_play.query`).
    Emitted by `ocp-pipeline-plugin` compatibility layer to support skills that
    still inherit from the Mycroft `CommonPlaySkill` base class. Skills respond
    with `play:query.response`.
    """
    message_type: str = "play:query"
    data: PlayQueryData


class PlayQueryResponseData(BaseModel):
    """Response from a legacy CommonPlaySkill to a play:query."""
    phrase: str = Field(..., description="Original search phrase.")
    skill_id: str = Field(..., description="ID of the responding skill.")
    conf: float = Field(..., ge=0.0, le=1.0, description="Match confidence (0.0–1.0).")
    callback_data: Dict[str, Any] = Field(default_factory=dict,
                                           description="Data the skill needs back at play:start time.")
    searching: bool = Field(False, description="True if the skill is still searching (intermediate response).")


class PlayQueryResponseMessage(OpenVoiceOSMessage):
    """Response from a legacy CommonPlaySkill to a play:query.

    **Legacy** — part of the Mycroft Common Play System, superseded by OCP.
    Emitted by skills inheriting from `CommonPlaySkill` in response to
    `play:query`. The OCP pipeline selects the highest-confidence response.
    """
    message_type: str = "play:query.response"
    data: PlayQueryResponseData


class QuestionQueryHandlingMessage(OpenVoiceOSMessage):
    """Register a handler for an in-flight common-query collection round.

    Emitted internally by the ``CollectionClientBus`` helper in
    ovos-bus-client when a skill announces it is handling a query. Carries
    ``query`` (collection ID), ``handler`` (skill ID), and ``timeout``.
    """
    message_type: str = "question:query.handling"
    data: Dict[str, Any] = Field(default_factory=dict)
