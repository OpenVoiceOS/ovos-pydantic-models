from typing import Dict, Any, Optional

from pydantic import Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


class OvosDisplayScreenshotGetMessage(OpenVoiceOSMessage):
    """Request a screenshot of the current display.

    Emitted by the screenshot skill or bus tools. The skill responds with
    ``ovos.display.screenshot.get.response`` carrying the image data.
    """
    message_type: str = "ovos.display.screenshot.get"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosDisplayScreenshotGetResponseMessage(OpenVoiceOSMessage):
    """Reply carrying a display screenshot.

    Emitted by the screenshot skill in response to
    ``ovos.display.screenshot.get``. Carries ``screenshot`` (base64-encoded
    image) and ``mime_type``.
    """
    message_type: str = "ovos.display.screenshot.get.response"
    data: Dict[str, Any] = Field(default_factory=dict)
