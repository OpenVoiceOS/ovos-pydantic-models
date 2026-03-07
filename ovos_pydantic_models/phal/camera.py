from typing import Dict, Any

from ovos_pydantic_models.message import OpenVoiceOSMessage
from pydantic import Field


class OvosPhalCameraPingMessage(OpenVoiceOSMessage):
    """Check whether the PHAL camera plugin is running and responsive.

    Emitted by skills or components that need to verify camera availability
    before attempting to open or capture. The camera PHAL plugin replies
    with `ovos.phal.camera.pong`.
    """
    message_type: str = "ovos.phal.camera.ping"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalCameraPongMessage(OpenVoiceOSMessage):
    """Signal that the PHAL camera plugin is alive and ready.

    Emitted by the camera PHAL plugin in response to `ovos.phal.camera.ping`.
    Skills receive this before proceeding with camera operations.
    """
    message_type: str = "ovos.phal.camera.pong"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalCameraOpenMessage(OpenVoiceOSMessage):
    """Activate the device camera and prepare it for capture.

    Emitted by skills that need camera input (e.g. QR code scanner, face
    recognition). The camera PHAL plugin initializes the camera hardware and
    streams the viewfinder to the GUI.
    """
    message_type: str = "ovos.phal.camera.open"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalCameraCloseMessage(OpenVoiceOSMessage):
    """Deactivate the device camera and release its hardware resources.

    Emitted by skills when they are done using the camera, or by the stop
    service. The camera PHAL plugin stops the preview stream and shuts down
    the camera hardware to save power.
    """
    message_type: str = "ovos.phal.camera.close"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalCameraGetMessage(OpenVoiceOSMessage):
    """Request a still image capture from the device camera.

    Emitted by skills that need a single frame (e.g. to encode a QR code
    or to feed an image classifier). The camera PHAL plugin captures a frame
    and returns it to the requesting skill.
    """
    message_type: str = "ovos.phal.camera.get"
    data: Dict[str, Any] = Field(default_factory=dict)
