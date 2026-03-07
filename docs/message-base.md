# Message Base, Context, and Session

## OpenVoiceOSMessage

```
ovos_pydantic_models.message.OpenVoiceOSMessage
```

Base class for all bus messages. Every specific message type inherits from this.

| Field | Type | Required | Description |
|---|---|---|---|
| `message_type` | `str` | yes | The bus message type string (e.g. `"speak"`) |
| `data` | `dict` | no | Message payload. Subclasses replace this with a typed model. |
| `context` | `MessageContext` | no | Routing/session context. Defaults to empty context. |

```python
from ovos_pydantic_models.message import OpenVoiceOSMessage

# All concrete message classes work identically
msg = OpenVoiceOSMessage(message_type="my.custom.event")
raw = msg.model_dump()
restored = OpenVoiceOSMessage.model_validate(raw)
```

---

## MessageContext

```
ovos_pydantic_models.message.MessageContext
```

Routing context attached to every message. Allows extra fields (open model).

| Field | Type | Default | Description |
|---|---|---|---|
| `source` | `str \| None` | `None` | Origin of the message (e.g. `"skills"`, `"listener"`) |
| `destination` | `str \| list[str] \| None` | `None` | Target(s). `None` = broadcast to all. |
| `session` | `Session \| None` | `None` | Embedded session context |

Extra fields are allowed — the bus adds arbitrary keys like `skill_id`, `ident`, etc., which are preserved on deserialization.

---

## Session

```
ovos_pydantic_models.session.Session
```

Represents a user's conversational session. Carried in `MessageContext.session`.

| Field | Type | Default | Description |
|---|---|---|---|
| `session_id` | `str` | `"default"` | Unique session identifier |
| `expiration_seconds` | `int` | `-1` | TTL in seconds (-1 = no expiry) |
| `active_skills` | `list[tuple[str, float]]` | `[]` | Skills currently active with their last-activation timestamp |
| `utterance_states` | `dict[str, UtteranceState]` | `{}` | Per-skill utterance state (`INTENT` or `RESPONSE`) |
| `lang` | `str` | `"en-us"` | Session language |
| `context` | `IntentContextManager` | — | Conversational context frame stack |
| `site_id` | `str` | `"unknown"` | Physical location / device identifier |
| `pipeline` | `list[str]` | default pipeline | Ordered intent pipeline stages |
| `location_preferences` | `dict` | `{}` | User location preferences |
| `system_unit` | `str` | `"metric"` | `"metric"` or `"imperial"` |
| `time_format` | `str` | `"full"` | Time display format |
| `date_format` | `str` | `"DMY"` | Date display format |
| `is_speaking` | `bool` | `False` | Device is currently speaking |
| `is_recording` | `bool` | `False` | Device is currently recording |
| `blacklisted_intents` | `list[str]` | `[]` | Intents blocked for this session |
| `blacklisted_skills` | `list[str]` | `[]` | Skills blocked for this session |
| `touch_time` | `int` | `time.time()` | Timestamp of last interaction |

### UtteranceState

```python
from ovos_pydantic_models.session import UtteranceState

UtteranceState.INTENT    # "intent"   — skill expects a new intent
UtteranceState.RESPONSE  # "response" — skill is waiting for a get_response() answer
```

---

## IntentContextManager

```
ovos_pydantic_models.session.IntentContextManager
```

Manages the conversational context frame stack inside a session.

| Field | Type | Default | Description |
|---|---|---|---|
| `timeout` | `int` | `120` | Context frame TTL in seconds |
| `frame_stack` | `list[tuple[IntentContextManagerFrame, float]]` | `[]` | Stack of (frame, timestamp) pairs |
| `context_keywords` | `list[str]` | `[]` | Keywords that trigger context extraction |
| `context_max_frames` | `int` | `3` | Max frames to retain |
| `context_greedy` | `bool` | `False` | If `True`, all entities update context |

### IntentContextManagerFrame

| Field | Type | Default | Description |
|---|---|---|---|
| `entities` | `list[ContextEntity]` | `[]` | Entities in this frame |
| `metadata` | `dict` | `{}` | Arbitrary metadata |

### ContextEntity

| Field | Type | Default | Description |
|---|---|---|---|
| `data` | `str` | required | Entity tag (e.g. `"time"`) |
| `key` | `str` | required | Resolved value (e.g. `"10:00 AM"`) |
| `confidence` | `float` | `1.0` | Match confidence |
| `origin` | `str \| None` | `None` | Source skill/entity |

---

## Example

```python
from ovos_pydantic_models.session import Session, UtteranceState
from ovos_pydantic_models.message import MessageContext

session = Session(
    session_id="user-abc",
    lang="de-de",
    utterance_states={"skill-weather.mycroft": UtteranceState.RESPONSE},
)

ctx = MessageContext(source="skills", session=session)
raw = ctx.model_dump()
restored = MessageContext.model_validate(raw)
assert restored.session.lang == "de-de"
```
