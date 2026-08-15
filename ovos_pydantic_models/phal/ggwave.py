from typing import Dict, Any

from pydantic import Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


class OvosGgwaveEnableMessage(OpenVoiceOSMessage):
    """Request the ggwave audio transformer plugin to enable data-over-sound encoding.

    Emitted by bus clients or skills that need to transmit data via the
    ggwave audio channel.
    """
    message_type: str = "ovos.ggwave.enable"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosGgwaveDisableMessage(OpenVoiceOSMessage):
    """Request the ggwave audio transformer plugin to disable data-over-sound encoding."""
    message_type: str = "ovos.ggwave.disable"
    data: Dict[str, Any] = Field(default_factory=dict)


class GgwaveEnabledMessage(OpenVoiceOSMessage):
    """Confirmation that the ggwave audio transformer has been enabled.

    Emitted by the ggwave PHAL plugin after successfully enabling.
    """
    message_type: str = "ovos.ggwave.enabled"
    data: Dict[str, Any] = Field(default_factory=dict)


class GgwaveDisabledMessage(OpenVoiceOSMessage):
    """Confirmation that the ggwave audio transformer has been disabled.

    Emitted by the ggwave PHAL plugin after successfully disabling.
    """
    message_type: str = "ovos.ggwave.disabled"
    data: Dict[str, Any] = Field(default_factory=dict)
