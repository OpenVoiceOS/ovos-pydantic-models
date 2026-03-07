# Re-export all fallback protocol messages from the canonical location.
# Skills should import from here (or directly from ovos_pydantic_models).
from ovos_pydantic_models.intents.fallbacks import (  # noqa: F401
    FallbackMode,
    OvosSkillsFallbackRegisterData,
    OvosSkillsFallbackRegisterMessage,
    OvosSkillsFallbackDeregisterData,
    OvosSkillsFallbackDeregisterMessage,
    OvosSkillsFallbackPingData,
    OvosSkillsFallbackPingMessage,
    OvosSkillsFallbackPongData,
    OvosSkillsFallbackPongMessage,
    OvosSkillsFallbackRequestData,
    OvosSkillsFallbackRequestMessage,
    OvosSkillsFallbackStartMessage,
    OvosSkillsFallbackResponseData,
    OvosSkillsFallbackResponseMessage,
    OvosSkillsFallbackKilledData,
    OvosSkillsFallbackKilledMessage,
    OvosSkillsFallbackForceTimeoutData,
    OvosSkillsFallbackForceTimeoutMessage,
)
from ovos_pydantic_models.intents.core import OvosUtteranceHandledMessage  # noqa: F401
