from typing import Dict, Any, Optional

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage
from ovos_pydantic_models.session import Session


# ---------------------------------------------------------------------------
# SESSION-2 §2.7 — out-of-utterance session sync
# ---------------------------------------------------------------------------

class OvosSessionSyncData(BaseModel):
    """Payload for an explicit out-of-utterance session snapshot broadcast.

    Per SESSION-2 §2.7 the updated session snapshot travels in ``Message.data``
    as ``data.session``, NOT in ``Message.context.session``. The context.session
    continues to identify the session for routing; the ``data.session`` field is
    the explicit sync content.

    A consumer MUST merge ``data.session`` using field-replacement semantics:
    present fields replace current values; absent fields leave current values
    unchanged.
    """
    session: Session = Field(..., description="The updated session snapshot to broadcast (SESSION-2 §2.7).")


class OvosSessionSyncMessage(OpenVoiceOSMessage):
    """Broadcast an explicit session update outside the utterance lifecycle.

    Per SESSION-2 §2.7, a component SHOULD use this topic when a session
    update cannot ride on a Message already being emitted in the normal flow.
    The payload (``data.session``) is merged into the working session snapshot
    of every consumer observing the matching ``session_id``.

    The orchestrator MUST merge ``data.session`` into its working snapshot and
    reflect the merged state in the subsequent ``.complete`` and
    ``ovos.utterance.handled`` terminal events for the same utterance.
    """
    message_type: str = "ovos.session.sync"
    data: OvosSessionSyncData


class OvosSessionUpdateDefaultData(Session):
    """The complete updated default session, extending the Session model.

    Carries all session fields: ``session_id``, ``lang``, ``active_skills``,
    ``utterance_states``, pipeline config, and any custom context.
    """


class OvosSessionUpdateDefaultMessage(OpenVoiceOSMessage):
    """Broadcast an updated default session to all connected components.

    Emitted by the intent service whenever the default session changes
    (language switch, skill activation/deactivation, pipeline config update).
    All components that maintain a session cache should update it on receipt.
    """
    message_type: str = "ovos.session.update_default"
    data: OvosSessionUpdateDefaultData
