from typing import Any, Optional

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


class OvosPhalSensorData(BaseModel):
    """Payload carrying a continuous sensor reading from the PHAL sensors plugin."""
    sensor_id: str = Field(..., description="Unique sensor identifier.")
    value: Any = Field(..., description="Current sensor reading.")
    unit: Optional[str] = Field(None, description="Unit of measurement (e.g. 'celsius', 'lux'), or None.")


class OvosPhalSensorMessage(OpenVoiceOSMessage):
    """Report a continuous (analog/numeric) sensor reading from the PHAL sensors plugin.

    Emitted by the PHAL sensors plugin whenever a monitored sensor value changes
    or is polled (e.g. temperature, humidity, ambient light level, CO2 ppm).
    Skills or automation components subscribe to this message to react to
    environmental conditions — for example, a climate skill may adjust TTS
    responses based on room temperature readings.

    `sensor_id` uniquely identifies the hardware sensor within the PHAL plugin's
    configuration. `unit` is optional but should be included where meaningful to
    allow consumers to display or convert the value correctly.
    """
    message_type: str = "ovos.phal.sensor"
    data: OvosPhalSensorData


class OvosPhalBinarySensorData(BaseModel):
    """Payload carrying a binary (on/off) sensor state from the PHAL sensors plugin."""
    sensor_id: str = Field(..., description="Unique binary sensor identifier.")
    value: bool = Field(..., description="Current boolean state of the sensor.")


class OvosPhalBinarySensorMessage(OpenVoiceOSMessage):
    """Report a binary (boolean) sensor state change from the PHAL sensors plugin.

    Emitted by the PHAL sensors plugin when a binary input changes state —
    for example, a door contact sensor opening/closing, a motion detector
    triggering, or a physical button being pressed. Skills or automation
    components subscribe to this message to trigger actions on state transitions.

    `sensor_id` uniquely identifies the binary sensor within the PHAL plugin's
    configuration. `value=True` typically means the sensor is active/triggered
    (e.g. door open, motion detected, button pressed).
    """
    message_type: str = "ovos.phal.binary_sensor"
    data: OvosPhalBinarySensorData
