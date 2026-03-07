# ovos-pydantic-models Documentation

> **Beta** — Message models are semi-automatically generated and under active review. Some subsystems are deprecated but documented here for historical reference. Do not treat this as a stable API contract.

Typed Pydantic v2 models for every message that flows over the OVOS MessageBus. This package is the machine-readable specification of the OVOS bus protocol.

## Contents

| Document | Description |
|---|---|
| [message-base.md](message-base.md) | `OpenVoiceOSMessage`, `MessageContext`, `Session` |
| [listener.md](listener.md) | Recognizer loop, wake word, mic control, OPM queries |
| [audio.md](audio.md) | TTS speak, audio queue, legacy audio service, OPM queries |
| [ocp.md](ocp.md) | OCP/Common Play — query protocol, playback control, media data models, enums |
| [intent-pipeline.md](intent-pipeline.md) | Converse, fallback, stop, context management; Adapt and Padatious (legacy) |
| [skill-manager.md](skill-manager.md) | Skill lifecycle, settings, installer, session sync |
| [missing-messages.md](missing-messages.md) | Tracking doc: modeled vs still missing |

## Subsystem Status

| Badge | Meaning |
|---|---|
| ⚠ **deprecated** | Backing plugin/package archived on GitHub — documented for reference only |
| β **beta** | Actively developed, not yet officially released — messages may change |
| ↩ **legacy** | Functional but superseded by a better alternative |

### Deprecated
- `phal.configuration_provider` — ovos-PHAL-plugin-configuration-provider archived
- `phal.wifi_setup` — ovos-PHAL-plugin-wifi-setup archived
- `gui.homescreen`, `gui.widgets`, `gui.media_player`, `gui.notifications` — superseded by GUI rewrite

### Beta
- `gui.namespace` — GUI protocol is unstable during the ongoing rewrite
- `audio.video_service`, `audio.web_service` — ovos-media not yet officially launched

### Legacy
- `audio.audioservice` — being superseded by OCP (ovos-media) for media playback
- `intents.adapt` — superseded by Padacioso / ML-based pipeline plugins
- `intents.padatious` — superseded by Padacioso / ML-based pipeline plugins
- `intents.core` context messages (`add_context`, `remove_context`, `clear_context`) — Adapt-specific

## Quick Start

```bash
pip install ovos-pydantic-models
```

```python
from ovos_pydantic_models.audio.playback import SpeakMessage, SpeakData

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

`type` is modelled as `message_type` on all subclasses of `OpenVoiceOSMessage`. The `data` field is typed per message class. The `context` field is always a `MessageContext` (which embeds an optional `Session`).

## Dynamic Message Types

Some messages have a `message_type` determined at runtime (e.g., `{skill_id}.converse.ping`). These classes use:

```python
message_type: str = Field(..., description="Dynamic: '{skill_id}.converse.ping'.")
```

`message_type` is a **required field** you must supply at construction time:

```python
from ovos_pydantic_models.intents.converse import SkillConversePingMessage, SkillConversePingData

msg = SkillConversePingMessage(
    message_type="my-skill.converse.ping",
    data=SkillConversePingData(skill_id="my-skill", utterances=["hello"], lang="en-us"),
)
```

## Serialization

```python
raw = msg.model_dump()                       # → dict (send over bus)
restored = MyMessage.model_validate(raw)     # → typed model (receive from bus)
```

## Interactive Reference

`docs/index.html` is a searchable, filterable web UI with all 545+ message types organized by subsystem, with deprecated/beta/legacy badges.

```bash
python -m http.server 8080 --directory docs
# open http://localhost:8080
```
