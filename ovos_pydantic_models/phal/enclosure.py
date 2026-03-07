from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


# --- Eyes ---

class EnclosureEyesOnMessage(OpenVoiceOSMessage):
    """Turn the Mark 1 enclosure's eye LEDs fully on.

    Emitted by skills or the enclosure PHAL plugin to illuminate the circular
    eye rings on the Mark 1 hardware to their current color at full brightness.
    Used as a visual attention indicator or idle state. The eyes remain on
    until explicitly turned off via `enclosure.eyes.off` or reset via
    `enclosure.eyes.reset`.
    """
    message_type: str = "enclosure.eyes.on"
    data: Dict[str, Any] = Field(default_factory=dict)


class EnclosureEyesOffMessage(OpenVoiceOSMessage):
    """Turn the Mark 1 enclosure's eye LEDs off.

    Emitted by skills or the enclosure PHAL plugin to extinguish the eye ring
    LEDs on the Mark 1 hardware. Used for power saving or to indicate the
    device is no longer listening/processing. The LEDs can be re-enabled via
    `enclosure.eyes.on` or by setting a new color via `enclosure.eyes.color`.
    """
    message_type: str = "enclosure.eyes.off"
    data: Dict[str, Any] = Field(default_factory=dict)


class EnclosureEyesColorData(BaseModel):
    """RGB color payload for setting the Mark 1 eye ring LEDs."""
    r: int = Field(..., description="Red component (0-255).")
    g: int = Field(..., description="Green component (0-255).")
    b: int = Field(..., description="Blue component (0-255).")


class EnclosureEyesColorMessage(OpenVoiceOSMessage):
    """Set the Mark 1 enclosure's eye ring LEDs to a specific RGB color.

    Emitted by skills or the enclosure PHAL plugin to change the color of the
    circular eye LEDs on the Mark 1 hardware. Common uses include indicating
    the device state (e.g. blue while listening, green for success, red for
    errors). The color persists until changed or reset.
    """
    message_type: str = "enclosure.eyes.color"
    data: EnclosureEyesColorData


class EnclosureEyesBlinkData(BaseModel):
    """Payload for triggering a blink animation on one or both Mark 1 eyes."""
    side: str = Field(..., description="Which eye(s) to blink: 'left', 'right', or 'both'.")


class EnclosureEyesBlinkMessage(OpenVoiceOSMessage):
    """Trigger a blink animation on the Mark 1 enclosure's eye LEDs.

    Emitted by skills to add expressiveness to the Mark 1's eye display.
    The enclosure PHAL plugin animates the specified eye(s) briefly going
    dark and returning to their current state, simulating a blink. The `side`
    field controls whether the left eye, right eye, or both blink together.
    """
    message_type: str = "enclosure.eyes.blink"
    data: EnclosureEyesBlinkData


class EnclosureEyesSpinMessage(OpenVoiceOSMessage):
    """Start a continuous spinning animation on the Mark 1 enclosure's eye LEDs.

    Emitted by skills or system components to indicate that a long-running
    operation is in progress (e.g. during loading or connecting to the network).
    The enclosure PHAL plugin continuously rotates a lit segment around the eye
    ring until `enclosure.eyes.reset` or another eye command is received.
    For a time-limited spin use `enclosure.eyes.timedspin`.
    """
    message_type: str = "enclosure.eyes.spin"
    data: Dict[str, Any] = Field(default_factory=dict)


class EnclosureEyesTimedSpinData(BaseModel):
    """Payload for a duration-limited spin animation on the Mark 1 eye LEDs."""
    length: int = Field(..., description="Duration of spin animation in milliseconds.")


class EnclosureEyesTimedSpinMessage(OpenVoiceOSMessage):
    """Run a timed spinning animation on the Mark 1 enclosure's eye LEDs.

    Emitted by skills or the enclosure PHAL plugin to show activity for a
    known duration without requiring an explicit stop command. The enclosure
    PHAL plugin animates the eye ring for `length` milliseconds and then
    automatically stops. Useful when the expected duration of an operation
    is known in advance.
    """
    message_type: str = "enclosure.eyes.timedspin"
    data: EnclosureEyesTimedSpinData


class EnclosureEyesNarrowMessage(OpenVoiceOSMessage):
    """Display a narrowed-eye expression on the Mark 1 enclosure.

    Emitted by skills to convey a skeptical or focused emotional expression
    on the Mark 1 hardware. The enclosure PHAL plugin adjusts the eye ring
    LEDs to simulate partially closed eyes, adding personality to skill
    interactions. Typically used in response to ambiguous or repeated inputs.
    """
    message_type: str = "enclosure.eyes.narrow"
    data: Dict[str, Any] = Field(default_factory=dict)


class EnclosureEyesLookData(BaseModel):
    """Payload for animating the Mark 1 eyes to look in a direction."""
    side: str = Field(..., description="Direction to look: 'left', 'right', 'up', 'down'.")


class EnclosureEyesLookMessage(OpenVoiceOSMessage):
    """Animate the Mark 1 enclosure's eye LEDs to look in a direction.

    Emitted by skills to add directional expression to the Mark 1 hardware.
    The enclosure PHAL plugin shifts the illuminated portion of the eye ring
    toward the specified direction, simulating the eyes glancing that way.
    Used to draw attention, express curiosity, or add personality to responses.
    """
    message_type: str = "enclosure.eyes.look"
    data: EnclosureEyesLookData


class EnclosureEyesLevelData(BaseModel):
    """Payload for setting the Mark 1 eye LED brightness level."""
    level: int = Field(..., description="Brightness level (0-30).")


class EnclosureEyesLevelMessage(OpenVoiceOSMessage):
    """Set the brightness level of the Mark 1 enclosure's eye LEDs.

    Emitted by skills or the enclosure PHAL plugin to adjust how brightly
    the eye ring LEDs are illuminated. `level` ranges from 0 (off) to 30
    (maximum brightness). Used by the auto-dim feature to reduce brightness
    in low-light environments, or by skills that want subtler visual feedback.
    """
    message_type: str = "enclosure.eyes.level"
    data: EnclosureEyesLevelData


class EnclosureEyesVolumeData(BaseModel):
    """Payload for visualizing volume level on the Mark 1 eye LEDs."""
    volume: int = Field(..., description="Volume level to visualize (0-11).")


class EnclosureEyesVolumeMessage(OpenVoiceOSMessage):
    """Visualize the current audio volume level on the Mark 1 enclosure's eye LEDs.

    Emitted by the volume skill or audio service when volume changes. The
    enclosure PHAL plugin fills a proportional arc of the eye ring to visually
    represent the volume level (0 = empty ring, 11 = full ring). This provides
    tactile volume feedback without a screen on the Mark 1 hardware.
    """
    message_type: str = "enclosure.eyes.volume"
    data: EnclosureEyesVolumeData


class EnclosureEyesFillData(BaseModel):
    """Payload for filling the Mark 1 eye ring LEDs to a percentage."""
    percentage: int = Field(..., description="Fill percentage (0-100).")


class EnclosureEyesFillMessage(OpenVoiceOSMessage):
    """Fill the Mark 1 enclosure's eye ring LEDs to a given percentage.

    Emitted by skills to use the eye ring as a generic progress indicator.
    The enclosure PHAL plugin illuminates a proportional arc of the ring —
    0% is completely dark, 100% is fully illuminated. Used for progress bars,
    countdown indicators, or any skill that wants to show degree of completion
    on the Mark 1 hardware.
    """
    message_type: str = "enclosure.eyes.fill"
    data: EnclosureEyesFillData


class EnclosureEyesResetMessage(OpenVoiceOSMessage):
    """Reset the Mark 1 enclosure's eye LEDs to their default idle state.

    Emitted by the enclosure PHAL plugin or skills after completing an
    animation or custom display. The plugin restores the eyes to the default
    color and animation used during idle mode (typically a slow breathing
    pattern or solid color). This is the standard cleanup call after any
    custom eye command.
    """
    message_type: str = "enclosure.eyes.reset"
    data: Dict[str, Any] = Field(default_factory=dict)


class EnclosureEyesSetPixelData(BaseModel):
    """Payload for setting an individual LED pixel on the Mark 1 eye ring."""
    idx: int = Field(..., description="Pixel index.")
    r: int = Field(..., description="Red component (0-255).")
    g: int = Field(..., description="Green component (0-255).")
    b: int = Field(..., description="Blue component (0-255).")


class EnclosureEyesSetPixelMessage(OpenVoiceOSMessage):
    """Set the color of a single LED pixel on the Mark 1 enclosure's eye ring.

    Emitted by skills or the enclosure PHAL plugin for fine-grained control
    over individual LEDs in the eye ring. `idx` is the zero-based index of the
    pixel in the ring. This allows skills to create custom animations or
    patterns not covered by the higher-level eye commands. Used by advanced
    skills that implement their own eye animations frame by frame.
    """
    message_type: str = "enclosure.eyes.setpixel"
    data: EnclosureEyesSetPixelData


# --- Mouth ---

class EnclosureMouthResetMessage(OpenVoiceOSMessage):
    """Clear the Mark 1 enclosure's mouth LED matrix and return it to idle state.

    Emitted by the enclosure PHAL plugin after finishing a mouth animation or
    display. The plugin clears all pixels on the mouth matrix and returns to
    the default idle face. This is the standard cleanup call after viseme
    animations, text display, or custom image rendering.
    """
    message_type: str = "enclosure.mouth.reset"
    data: Dict[str, Any] = Field(default_factory=dict)


class EnclosureMouthTalkMessage(OpenVoiceOSMessage):
    """Animate the Mark 1 enclosure's mouth to indicate speaking.

    Emitted by the TTS service or audio service when OVOS begins speaking a
    response. The enclosure PHAL plugin runs a talking animation on the mouth
    LED matrix to visually indicate that audio is being played. For synchronized
    lip animation, use `enclosure.mouth.viseme` or `enclosure.mouth.viseme_list`
    instead, which tie mouth shapes to specific phoneme timings.
    """
    message_type: str = "enclosure.mouth.talk"
    data: Dict[str, Any] = Field(default_factory=dict)


class EnclosureMouthThinkMessage(OpenVoiceOSMessage):
    """Animate the Mark 1 enclosure's mouth to indicate processing/thinking.

    Emitted by the intent service or skills while processing a request, to
    give the user visual feedback that OVOS is working on a response. The
    enclosure PHAL plugin displays a thinking animation on the mouth matrix
    (typically a side-scrolling or pulsing pattern). Cancelled automatically
    when a response begins.
    """
    message_type: str = "enclosure.mouth.think"
    data: Dict[str, Any] = Field(default_factory=dict)


class EnclosureMouthListenMessage(OpenVoiceOSMessage):
    """Animate the Mark 1 enclosure's mouth to indicate active listening.

    Emitted by the listener when the wake word is detected and OVOS is
    recording the user's utterance. The enclosure PHAL plugin displays a
    listening animation on the mouth matrix (typically a waveform or
    expanding/contracting pattern) to show the microphone is active.
    """
    message_type: str = "enclosure.mouth.listen"
    data: Dict[str, Any] = Field(default_factory=dict)


class EnclosureMouthSmileMessage(OpenVoiceOSMessage):
    """Display a smile expression on the Mark 1 enclosure's mouth LED matrix.

    Emitted by skills to convey a positive emotional response on the Mark 1
    hardware — for example, after successfully completing a task or in
    response to a thank-you from the user. The enclosure PHAL plugin renders
    a smile pattern on the mouth matrix.
    """
    message_type: str = "enclosure.mouth.smile"
    data: Dict[str, Any] = Field(default_factory=dict)


class EnclosureMouthVisemeData(BaseModel):
    """Payload for displaying a single phoneme mouth shape on the Mark 1."""
    code: str = Field(..., description="Viseme code character.")


class EnclosureMouthVisemeMessage(OpenVoiceOSMessage):
    """Display a single viseme (phoneme mouth shape) on the Mark 1 mouth matrix.

    Emitted by the TTS service for each phoneme during speech playback to
    synchronize the mouth LED display with the audio. The `code` is a single-
    character viseme code mapping to a predefined mouth shape rendered on the
    matrix. For batched playback with timing, use `enclosure.mouth.viseme_list`
    instead to pre-load the full sequence.
    """
    message_type: str = "enclosure.mouth.viseme"
    data: EnclosureMouthVisemeData


class EnclosureMouthVisemeListData(BaseModel):
    """Payload for a timed sequence of viseme mouth shapes for the Mark 1."""
    start: float = Field(..., description="Start time (unix timestamp) for the viseme sequence.")
    visemes: List[Any] = Field(..., description="List of (viseme_code, duration) tuples.")


class EnclosureMouthVisemeListMessage(OpenVoiceOSMessage):
    """Load and play a timed sequence of viseme mouth shapes on the Mark 1.

    Emitted by the TTS service before or at the start of speech playback.
    Provides the complete list of `(viseme_code, duration_ms)` tuples and a
    `start` timestamp so the enclosure PHAL plugin can advance through mouth
    shapes in sync with the audio without requiring one message per phoneme.
    This is more efficient than sending individual `enclosure.mouth.viseme`
    messages and produces smoother lip-sync animation.
    """
    message_type: str = "enclosure.mouth.viseme_list"
    data: EnclosureMouthVisemeListData


class EnclosureMouthDisplayData(BaseModel):
    """Payload for rendering a custom image on the Mark 1 mouth LED matrix."""
    img_code: str = Field(..., description="Encoded image string to display.")
    xOffset: int = Field(0, description="Horizontal offset.")
    yOffset: int = Field(0, description="Vertical offset.")
    clearPrev: bool = Field(True, description="Whether to clear previous display.")


class EnclosureMouthDisplayMessage(OpenVoiceOSMessage):
    """Render a custom encoded image on the Mark 1 enclosure's mouth LED matrix.

    Emitted by skills that want to display a custom bitmap on the Mark 1
    mouth display — for example, showing a weather icon, a game state, or
    a custom animation frame. `img_code` is a compact string encoding of the
    8×32 pixel matrix. `xOffset`/`yOffset` allow positioning, and `clearPrev`
    controls whether the previous image is erased before rendering.
    """
    message_type: str = "enclosure.mouth.display"
    data: EnclosureMouthDisplayData


class EnclosureMouthTextData(BaseModel):
    """Payload for scrolling text on the Mark 1 mouth LED matrix."""
    text: str = Field(..., description="Text to display on the mouth matrix.")


class EnclosureMouthTextMessage(OpenVoiceOSMessage):
    """Scroll text across the Mark 1 enclosure's mouth LED matrix.

    Emitted by skills to display a short text message on the Mark 1 mouth
    display — for example, showing the current time, a weather summary, or
    an error code. The enclosure PHAL plugin scrolls the text horizontally
    across the 8×32 LED matrix. Long strings are scrolled repeatedly; short
    strings may be shown static if they fit.
    """
    message_type: str = "enclosure.mouth.text"
    data: EnclosureMouthTextData


class EnclosureMouthEventsActivateMessage(OpenVoiceOSMessage):
    """Enable automatic mouth animations in response to OVOS system events.

    Emitted by the enclosure PHAL plugin during startup or when returning
    to normal operation. When mouth events are active, the plugin automatically
    plays the appropriate mouth animations (talk, think, listen, reset) in
    response to the OVOS system events like wake word detection, TTS start,
    and intent handling. Deactivated during custom skill animations to prevent
    the system from overriding them.
    """
    message_type: str = "enclosure.mouth.events.activate"
    data: Dict[str, Any] = Field(default_factory=dict)


class EnclosureMouthEventsDeactivateMessage(OpenVoiceOSMessage):
    """Disable automatic mouth animations in response to OVOS system events.

    Emitted by skills that want to take full manual control of the Mark 1
    mouth display. While deactivated, the enclosure PHAL plugin will not
    automatically play talk/think/listen animations in response to system
    events — the skill is responsible for all mouth display updates and must
    call `enclosure.mouth.events.activate` and `enclosure.mouth.reset` when
    done to restore normal behavior.
    """
    message_type: str = "enclosure.mouth.events.deactivate"
    data: Dict[str, Any] = Field(default_factory=dict)


# --- System / Misc ---

class EnclosureResetMessage(OpenVoiceOSMessage):
    """Reset the entire Mark 1 enclosure hardware to its default idle state.

    Emitted by the enclosure PHAL plugin during startup, after a factory
    reset, or when recovering from an error state. Clears all LED animations
    on both eyes and mouth and returns the enclosure to its default idle
    appearance (eyes on in default color, mouth reset). Equivalent to
    calling `enclosure.eyes.reset` and `enclosure.mouth.reset` together.
    """
    message_type: str = "enclosure.reset"
    data: Dict[str, Any] = Field(default_factory=dict)


class EnclosureStartedMessage(OpenVoiceOSMessage):
    """Signal that the Mark 1 enclosure hardware has initialized and is ready.

    Emitted by the enclosure PHAL plugin after successfully establishing
    communication with the Mark 1 Arduino/hardware controller. Skills and
    system components can subscribe to this message to know when it is safe
    to send enclosure commands. Before this message is received, eye and
    mouth commands may be silently dropped.
    """
    message_type: str = "enclosure.started"
    data: Dict[str, Any] = Field(default_factory=dict)


class EnclosureNotifyNoInternetMessage(OpenVoiceOSMessage):
    """Tell the Mark 1 enclosure to display a no-internet indicator.

    Emitted by the connectivity PHAL plugin when the device loses internet
    access. The enclosure PHAL plugin shows a visual indicator (e.g. a sad
    face or specific LED pattern) to alert the user that the device is offline.
    Cleared when internet connectivity is restored.
    """
    message_type: str = "enclosure.notify.no_internet"
    data: Dict[str, Any] = Field(default_factory=dict)


class EnclosureSystemResetMessage(OpenVoiceOSMessage):
    """Command the Mark 1 enclosure's Arduino controller to perform a system reset.

    Emitted by the enclosure PHAL plugin when the hardware controller needs to
    be restarted — for example, after a firmware update or to recover from a
    communication error. This resets the Arduino microcontroller, not the host
    Linux OS; it causes a brief interruption of all enclosure LED animations.
    """
    message_type: str = "enclosure.system.reset"
    data: Dict[str, Any] = Field(default_factory=dict)


class EnclosureSystemMuteMessage(OpenVoiceOSMessage):
    """Mute the Mark 1 enclosure's hardware audio output.

    Emitted by the volume plugin or skill to mute the Mark 1's physical speaker
    at the hardware level via the enclosure controller. Hardware mute is distinct
    from software mute — it physically disables the audio amplifier output.
    Restored with `enclosure.system.unmute`.
    """
    message_type: str = "enclosure.system.mute"
    data: Dict[str, Any] = Field(default_factory=dict)


class EnclosureSystemUnmuteMessage(OpenVoiceOSMessage):
    """Unmute the Mark 1 enclosure's hardware audio output.

    Emitted by the volume plugin or skill to restore audio output on the
    Mark 1's speaker after a hardware mute. Re-enables the physical audio
    amplifier so TTS and media audio can be heard. Used after `enclosure.system.mute`
    or during initialization if the enclosure starts in a muted state.
    """
    message_type: str = "enclosure.system.unmute"
    data: Dict[str, Any] = Field(default_factory=dict)
