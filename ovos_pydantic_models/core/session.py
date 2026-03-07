from typing import Dict, Any, Optional

from pydantic import Field

from ovos_pydantic_models.message import OpenVoiceOSMessage
from ovos_pydantic_models.session import Session


class OvosSessionSyncMessage(OpenVoiceOSMessage):
    """Request a broadcast of the current default session state.

    Emitted by components that have just connected to the bus and need
    to initialize their local session cache. The intent service replies
    with `ovos.session.update_default` containing the full session.
    """
    message_type: str = "ovos.session.sync"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosSessionUpdateDefaultData(Session):
    """The complete updated default session, extending the Session model.

    Carries all session fields: `session_id`, `lang`, `active_skills`,
    `utterance_states`, pipeline config, and any custom context.
    """


class OvosSessionUpdateDefaultMessage(OpenVoiceOSMessage):
    """Broadcast an updated default session to all connected components.

    Emitted by the intent service whenever the default session changes
    (language switch, skill activation/deactivation, pipeline config update).
    All components that maintain a session cache should update it on receipt.
    """
    message_type: str = "ovos.session.update_default"
    data: OvosSessionUpdateDefaultData
