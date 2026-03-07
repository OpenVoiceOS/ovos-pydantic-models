# ovos-pydantic-models Documentation

Typed Pydantic v2 models for every message that flows over the OVOS MessageBus. This package is the authoritative, machine-readable specification of the OVOS bus protocol.

## Contents

| Document | Description |
|---|---|
| [message-base.md](message-base.md) | `OpenVoiceOSMessage`, `MessageContext`, `Session` |
| [listener.md](listener.md) | Recognizer loop, wake word, mic control, OPM queries |
| [audio.md](audio.md) | TTS speak, audio queue, audio service, OCP media states |
| [intent-pipeline.md](intent-pipeline.md) | Converse, fallback, stop, context management |
| [ocp.md](ocp.md) | OCP query protocol, media entries, enums |
| [skill-manager.md](skill-manager.md) | Skill lifecycle, settings, installer, session sync |

## Quick Start

```python
pip install ovos-pydantic-models
```

```python
from ovos_pydantic_models import SpeakMessage, SpeakData

msg = SpeakMessage(data=SpeakData(utterance="Hello world"))
print(msg.message_type)   # "speak"
print(msg.model_dump())   # {"message_type": "speak", "data": {...}, "context": {...}}
```

## How Messages Work

Every OVOS bus message follows this structure:

```json
{
  "type": "speak",
  "data": {"utterance": "Hello world", "expect_response": false},
  "context": {"source": "skill-weather.mycroft", "session": {...}}
}
```

In this package, `type` is modelled as `message_type` on all subclasses of `OpenVoiceOSMessage`. The `data` field is typed specifically per message class. The `context` field is always a `MessageContext` (which embeds an optional `Session`).

## Dynamic Message Types

Some messages have a `message_type` that is determined at runtime (e.g., `{skill_id}.converse.ping`). These classes use:

```python
message_type: str = Field(..., description="Dynamic message type, e.g., 'my-skill-id.converse.ping'.")
```

Meaning `message_type` is a **required field** you must supply at construction time:

```python
from ovos_pydantic_models.intents.converse import SkillConversePingMessage, SkillConversePingData

msg = SkillConversePingMessage(
    message_type="my-skill.converse.ping",
    data=SkillConversePingData(skill_id="my-skill", utterances=["hello"], lang="en-us"),
)
```

## Serialization

All models support Pydantic v2 roundtrip serialization:

```python
raw = msg.model_dump()          # → dict (for sending over the bus)
restored = MyMessage.model_validate(raw)  # → typed model (for receiving from the bus)
```
