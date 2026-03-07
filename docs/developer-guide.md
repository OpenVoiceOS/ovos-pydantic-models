# Developer Guide — Using ovos-pydantic-models

`ovos-pydantic-models` provides typed Pydantic v2 models for every message that flows over the OVOS MessageBus. This guide explains when and how to use it in skills, plugins, and core components.

---

## Why use this library?

The raw OVOS MessageBus API uses `ovos_bus_client.message.Message` — essentially a dict wrapper with no type checking:

```python
# Untyped — any typo silently produces a wrong message
msg = Message("speak", {"utterence": "hello"})  # typo in key, no error
```

With pydantic models:

```python
from ovos_pydantic_models import SpeakMessage, SpeakData

# Validated at construction — typo raises ValidationError immediately
msg = SpeakMessage(data=SpeakData(utterance="hello"))
```

Benefits:
- **Catch errors early** — wrong field names and wrong types raise `ValidationError` at construction, not silently at runtime
- **IDE autocomplete** — field names and types are known
- **Self-documenting** — the model is the schema
- **Serialization roundtrip** — `model_dump()` / `model_validate()` for free
- **Test fixtures** — build expected messages with validation instead of plain dicts

---

## Installation

```bash
pip install ovos-pydantic-models
```

No OVOS runtime is required. This is a pure Pydantic v2 library.

---

## Basic usage

### Building a message

```python
from ovos_pydantic_models import SpeakMessage, SpeakData

msg = SpeakMessage(data=SpeakData(utterance="Hello, world!", expect_response=False))
print(msg.message_type)  # "speak"
print(msg.data.utterance)  # "Hello, world!"
```

### Serialization

```python
d = msg.model_dump()
# {"message_type": "speak", "data": {"utterance": "Hello, world!", ...}, "context": {...}}

restored = SpeakMessage.model_validate(d)
assert restored.data.utterance == "Hello, world!"
```

### Validation at construction

```python
from pydantic import ValidationError
from ovos_pydantic_models import RecognizerLoopUtteranceMessage, RecognizerLoopUtteranceData

try:
    # Missing required `utterances` field
    msg = RecognizerLoopUtteranceMessage(data=RecognizerLoopUtteranceData(lang="en-us"))
except ValidationError as e:
    print(e)  # "utterances: Field required"
```

---

## Bridge to ovos-bus-client

`ovos_bus_client.message.Message` and `OpenVoiceOSMessage` share the same three-field structure. Convert between them with two functions:

```python
from ovos_bus_client.message import Message
from ovos_pydantic_models.message import OpenVoiceOSMessage


def to_bus_message(pydantic_msg: OpenVoiceOSMessage) -> Message:
    d = pydantic_msg.model_dump()
    return Message(d["message_type"], d["data"], d["context"])


def from_bus_message(bus_msg: Message, model: type[OpenVoiceOSMessage]) -> OpenVoiceOSMessage:
    return model.model_validate({
        "message_type": bus_msg.msg_type,
        "data": bus_msg.data,
        "context": bus_msg.context,
    })
```

---

## Use in Skills

### Emitting typed messages

Use pydantic models to construct outgoing messages. Convert to bus format before emitting:

```python
from ovos_workshop.skills import OVOSSkill
from ovos_pydantic_models import SpeakMessage, SpeakData

class MySkill(OVOSSkill):
    def handle_hello(self, message):
        typed = SpeakMessage(data=SpeakData(utterance="Hello!"))
        self.bus.emit(to_bus_message(typed))
```

Or just use pydantic for validation and build the Message directly:

```python
# Validate first, then emit in the usual way
SpeakData(utterance="Hello!")  # raises if invalid
self.speak("Hello!")           # normal skill API
```

### Parsing received messages

When handling a bus event, parse into a typed model for safe field access:

```python
from ovos_pydantic_models import RecognizerLoopUtteranceMessage

def handle_utterance(self, message):
    typed = from_bus_message(message, RecognizerLoopUtteranceMessage)
    utterances = typed.data.utterances  # list[str], validated
    lang = typed.data.lang              # str, validated
```

### Scheduling typed events

```python
from ovos_pydantic_models.core.scheduler import SchedulerScheduleEventData
import time

# Validate the schedule payload before sending
payload = SchedulerScheduleEventData(
    name="my_reminder",
    when=time.time() + 60,
    data={"text": "your reminder"},
)
self.schedule_event(self._handle_reminder, 60, name="my_reminder")
```

---

## Use in PHAL Plugins

PHAL plugins send and receive bus messages for hardware control. Models document the contract:

```python
from ovos_pydantic_models.phal.brightness import (
    PhalBrightnessControlSetData,
    PhalBrightnessControlSetMessage,
    PhalBrightnessControlGetMessage,
    PhalBrightnessControlGetResponseData,
)

class BrightnessPlugin(PHALPlugin):
    def initialize(self):
        self.bus.on("phal.brightness.control.set", self.handle_set)

    def handle_set(self, message):
        typed = from_bus_message(message, PhalBrightnessControlSetMessage)
        self.set_brightness(typed.data.brightness)

    def report_brightness(self, level: int):
        response = PhalBrightnessControlGetResponseData(brightness=level)
        self.bus.emit(Message(
            "phal.brightness.control.get.response",
            response.model_dump(),
        ))
```

---

## Use in Audio/Video Plugins

Audio service plugins handle `mycroft.audio.service.*` and `ovos.audio.service.*` messages:

```python
from ovos_pydantic_models import AudioServicePlayMessage

def handle_play(self, message):
    typed = from_bus_message(message, AudioServicePlayMessage)
    tracks = typed.data.tracks      # List[str | tuple]
    repeat = typed.data.repeat      # bool
    utterance = typed.data.utterance  # Optional[str]
```

The `ovos.audio.service.*` namespace uses identical data structures:

```python
from ovos_pydantic_models import OvosAudioServicePlayMessage
# Same data schema as AudioServicePlayMessage, different message_type
```

---

## Use in STT/TTS Plugins

OPM query messages document the plugin query protocol:

```python
from ovos_pydantic_models import (
    OpmTtsQueryMessage, OpmTtsQueryReplyData, OpmTtsQueryResponseMessage,
    OpmSttQueryMessage, OpmSttQueryReplyData, OpmSttQueryResponseMessage,
)

def handle_tts_query(self, message):
    typed = from_bus_message(message, OpmTtsQueryMessage)
    # respond with capabilities
    reply_data = OpmTtsQueryReplyData(
        plugin_name="my-tts-plugin",
        langs=["en-us", "de-de"],
        voices=[{"name": "alice", "lang": "en-us"}],
    )
    self.bus.emit(Message(
        "ovos.plugin.tts.query.response",
        reply_data.model_dump(),
        message.context,
    ))
```

---

## Use in OCP Skills

OCP skills receive query messages and emit results:

```python
from ovos_pydantic_models import (
    OvosCommonPlayQueryMessage,
    OvosCommonPlayQueryResponseData, OvosCommonPlayQueryResponseMessage,
    MediaEntry, PlaybackType,
)

def handle_ocp_query(self, message):
    typed = from_bus_message(message, OvosCommonPlayQueryMessage)
    phrase = typed.data.phrase

    result = MediaEntry(
        uri="https://example.com/song.mp3",
        title="My Song",
        playback=PlaybackType.AUDIO,
    )

    response = OvosCommonPlayQueryResponseMessage(
        data=OvosCommonPlayQueryResponseData(
            phrase=phrase,
            skill_id=self.skill_id,
            skill_name=self.name,
            thumbnail=self.icon,
            results=[result],
            searching=False,
        )
    )
    self.bus.emit(to_bus_message(response))
```

---

## Use in Tests (ovoscope / pytest)

### Typed source messages

```python
from ovos_bus_client.session import Session
from ovos_pydantic_models import RecognizerLoopUtteranceMessage, RecognizerLoopUtteranceData

utterance = to_bus_message(
    RecognizerLoopUtteranceMessage(
        data=RecognizerLoopUtteranceData(utterances=["what time is it"], lang="en-us")
    )
)
session = Session("test-123")
utterance.context["session"] = session.serialize()
utterance.context["source"] = "A"
utterance.context["destination"] = "B"
```

### Typed expected messages

```python
from ovos_pydantic_models import SpeakMessage, SpeakData

expected_speak = to_bus_message(
    SpeakMessage(data=SpeakData(utterance="It is 3pm."))
)
```

### Typed assertions on received messages

```python
speak_msgs = [m for m in messages if m.msg_type == "speak"]
typed_speak = from_bus_message(speak_msgs[0], SpeakMessage)
assert "3pm" in typed_speak.data.utterance
assert typed_speak.data.expect_response is False
```

### Reusable helpers

```python
def assert_speak(msg, expected_text=None):
    typed = from_bus_message(msg, SpeakMessage)  # raises if not a valid speak
    if expected_text:
        assert typed.data.utterance == expected_text
    return typed

def make_utterance(text: str, lang="en-us", session=None):
    msg = to_bus_message(RecognizerLoopUtteranceMessage(
        data=RecognizerLoopUtteranceData(utterances=[text], lang=lang)
    ))
    if session:
        msg.context["session"] = session.serialize()
    return msg
```

---

## Configuration Messages

Use configuration models when writing PHAL plugins or components that patch config:

```python
from ovos_pydantic_models.core.configuration import ConfigurationPatchData, ConfigurationPatchMessage

patch = ConfigurationPatchMessage(
    data=ConfigurationPatchData(config={"lang": "de-de"})
)
self.bus.emit(to_bus_message(patch))
```

---

## When NOT to use pydantic models

- **Ephemeral fire-and-forget messages with no data** — just use `self.bus.emit(Message("my.event"))`. No benefit to wrapping a no-data message.
- **Skills using the OVOSSkill API directly** — `self.speak()`, `self.ask_yesno()`, etc. already produce the right messages. Use models only when you need lower-level control or test assertions.
- **Skill settings** — managed by `ovos-workshop` settings system; don't manually build settings messages.

---

## Message type index

See individual doc files for per-subsystem references:

| Subsystem | File |
|---|---|
| Base message / context / session | `docs/message-base.md` |
| Listener (STT, wake word, mic) | `docs/listener.md` |
| Audio / TTS | `docs/audio.md` |
| Intent pipeline (converse, fallback, stop) | `docs/intent-pipeline.md` |
| OCP (Common Play) | `docs/ocp.md` |
| Skill manager / installer | `docs/skill-manager.md` |
