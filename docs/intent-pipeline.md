# Intent Pipeline Messages

Messages that flow through the intent service during utterance handling, converse, fallback, and stop.

## Utterance Lifecycle

| Message type | Class | Direction | Description |
|---|---|---|---|
| `ovos.utterance.handled` | `OvosUtteranceHandledMessage` | service → bus | Utterance successfully handled by a skill |
| `ovos.utterance.cancelled` | `OvosUtteranceCancelledMessage` | service → bus | Utterance processing cancelled |
| `complete_intent_failure` | `CompleteIntentFailureMessage` | service → bus | No intent matched after full pipeline |

### `complete_intent_failure`

```python
from ovos_pydantic_models.intents.core import CompleteIntentFailureData, CompleteIntentFailureMessage

msg = CompleteIntentFailureMessage(
    data=CompleteIntentFailureData(utterance="what is blorg?", lang="en-us")
)
```

**`CompleteIntentFailureData`**

| Field | Type | Required |
|---|---|---|
| `utterance` | `str` | yes |
| `lang` | `str` | yes |

---

## Conversational Context

```python
from ovos_pydantic_models.intents.core import (
    AddContextData, AddContextMessage,
    RemoveContextData, RemoveContextMessage,
    ClearContextMessage,
)
```

| Message type | Class | Key data fields |
|---|---|---|
| `add_context` | `AddContextMessage` | `context` (str), `word` (str\|None), `origin` (str\|None) |
| `remove_context` | `RemoveContextMessage` | `context` (str) |
| `clear_context` | `ClearContextMessage` | none |

---

## Intent Get

Query the intent service for what intent would match an utterance (without executing it).

```python
from ovos_pydantic_models.intents.core import (
    IntentServiceIntentGetData, IntentServiceIntentGetMessage,
    IntentServiceIntentReplyData, IntentServiceIntentReplyMessage,
)

request = IntentServiceIntentGetMessage(
    data=IntentServiceIntentGetData(utterance="what time is it", lang="en-us")
)
```

**`IntentServiceIntentReplyData`**

| Field | Type | Description |
|---|---|---|
| `utterance` | `str` | Original utterance |
| `intent` | `IntentServiceIntentReplyIntentData \| None` | Matched intent, or `None` |

**`IntentServiceIntentReplyIntentData`**

| Field | Type | Description |
|---|---|---|
| `intent_name` | `str` | Name of the matched intent |
| `intent_service` | `str` | Pipeline stage that matched (e.g. `"adapt_high"`) |
| `skill_id` | `str` | Owning skill |
| `handler` | `str` | Handler function name |

---

## Converse Protocol

The converse system lets skills intercept utterances mid-conversation before the full pipeline runs.

```python
from ovos_pydantic_models.intents.converse import (
    ConverseMode, ConverseActivationMode,
    IntentServiceSkillsActivateData, IntentServiceSkillsActivateMessage,
    IntentServiceSkillsActivatedData, IntentServiceSkillsActivatedMessage,
    IntentServiceSkillsDeactivateData, IntentServiceSkillsDeactivateMessage,
    IntentServiceSkillsDeactivatedData, IntentServiceSkillsDeactivatedMessage,
    IntentServiceActiveSkillsGetMessage,
    IntentServiceActiveSkillsReplyData, IntentServiceActiveSkillsReplyMessage,
    SkillConversePingData, SkillConversePingMessage,
    SkillConversePongData, SkillConversePongMessage,
    SkillConverseRequestData, SkillConverseRequestMessage,
    SkillConverseResponseData, SkillConverseResponseMessage,
    SkillConverseGetResponseEnableData, SkillConverseGetResponseEnableMessage,
    SkillConverseGetResponseDisableData, SkillConverseGetResponseDisableMessage,
    SkillConverseKilledData, SkillConverseKilledMessage,
    ConverseSkillData, ConverseSkillMessage,
    OvosSkillsConverseForceTimeoutData, OvosSkillsConverseForceTimeoutMessage,
)
```

### Enums

**`ConverseMode`** — which skills are allowed to participate in converse:

| Value | String |
|---|---|
| `ACCEPT_ALL` | `"accept_all"` |
| `BLACKLIST` | `"blacklist"` |
| `WHITELIST` | `"whitelist"` |

**`ConverseActivationMode`** — when a skill may self-activate:

| Value | String |
|---|---|
| `ACCEPT_ALL` | `"accept_all"` |
| `PRIORITY` | `"priority"` |
| `BLACKLIST` | `"blacklist"` |
| `WHITELIST` | `"whitelist"` |

### Activation / Deactivation

| Message type | Class | Key field |
|---|---|---|
| `intent.service.skills.activate` | `IntentServiceSkillsActivateMessage` | `skill_id`, `timeout` (minutes, optional) |
| `intent.service.skills.activated` | `IntentServiceSkillsActivatedMessage` | `skill_id` |
| `intent.service.skills.deactivate` | `IntentServiceSkillsDeactivateMessage` | `skill_id` |
| `intent.service.skills.deactivated` | `IntentServiceSkillsDeactivatedMessage` | `skill_id` |
| `intent.service.active_skills.get` | `IntentServiceActiveSkillsGetMessage` | — |
| `intent.service.active_skills.reply` | `IntentServiceActiveSkillsReplyMessage` | `skills: list[str]` |

### Ping / Pong (service side)

The intent service pings each active skill to see if it can handle the current utterance.

| Message type | Class | Key fields |
|---|---|---|
| `{skill_id}.converse.ping` | `SkillConversePingMessage` | `skill_id`, `utterances`, `lang` |
| `skill.converse.pong` | `SkillConversePongMessage` | `skill_id`, `can_handle: bool` |

### Request / Response (skill side)

After confirming capability, the service sends the utterance to the skill.

| Message type | Class | Key fields |
|---|---|---|
| `{skill_id}.converse.request` | `SkillConverseRequestMessage` | `skill_id`, `utterances`, `lang` |
| `skill.converse.response` | `SkillConverseResponseMessage` | `skill_id`, `result: bool`, `error \| None` |
| `{skill_id}.converse.killed` | `SkillConverseKilledMessage` | `error: str` |
| `converse:skill` | `ConverseSkillMessage` | `skill_id`, `utterances`, `lang` |

### get_response Mode

Skills in `get_response()` expect the next utterance to go directly to them.

| Message type | Class |
|---|---|
| `skill.converse.get_response.enable` | `SkillConverseGetResponseEnableMessage` |
| `skill.converse.get_response.disable` | `SkillConverseGetResponseDisableMessage` |

### Force Timeout

| Message type | Class |
|---|---|
| `ovos.skills.converse.force_timeout` | `OvosSkillsConverseForceTimeoutMessage` |

---

## Fallback Protocol

When no intent matches, the intent service runs fallback handlers in priority order.

```python
from ovos_pydantic_models.intents.fallbacks import (
    FallbackMode,
    OvosSkillsFallbackRegisterData, OvosSkillsFallbackRegisterMessage,
    OvosSkillsFallbackDeregisterData, OvosSkillsFallbackDeregisterMessage,
    OvosSkillsFallbackPingData, OvosSkillsFallbackPingMessage,
    OvosSkillsFallbackPongData, OvosSkillsFallbackPongMessage,
    OvosSkillsFallbackRequestData, OvosSkillsFallbackRequestMessage,
    OvosSkillsFallbackResponseData, OvosSkillsFallbackResponseMessage,
    OvosSkillsFallbackKilledData, OvosSkillsFallbackKilledMessage,
    OvosSkillsFallbackForceTimeoutData, OvosSkillsFallbackForceTimeoutMessage,
)
```

**`FallbackMode`**

| Value | String |
|---|---|
| `ACCEPT_ALL` | `"accept_all"` |
| `BLACKLIST` | `"blacklist"` |
| `WHITELIST` | `"whitelist"` |

### Registration

| Message type | Class | Key fields |
|---|---|---|
| `ovos.skills.fallback.register` | `OvosSkillsFallbackRegisterMessage` | `skill_id`, `priority` (default 101) |
| `ovos.skills.fallback.deregister` | `OvosSkillsFallbackDeregisterMessage` | `skill_id` |

### Ping / Pong

The service queries which fallback skills can handle the utterance within a priority range.

**`OvosSkillsFallbackPingData`**

| Field | Type | Default | Description |
|---|---|---|---|
| `utterances` | `list[str]` | required | Utterances to check |
| `lang` | `str` | required | Language |
| `range` | `tuple[int, int] \| None` | `None` | Priority range `(start, stop)` |

| Message type | Class |
|---|---|
| `ovos.skills.fallback.ping` | `OvosSkillsFallbackPingMessage` |
| `ovos.skills.fallback.pong` | `OvosSkillsFallbackPongMessage` (`skill_id`, `can_handle: bool`) |

### Request / Response (dynamic message types)

| Message type | Class | Key fields |
|---|---|---|
| `ovos.skills.fallback.{skill_id}.request` | `OvosSkillsFallbackRequestMessage` | `skill_id`, `utterances`, `lang` |
| `ovos.skills.fallback.{skill_id}.start` | `OvosSkillsFallbackStartMessage` | — |
| `ovos.skills.fallback.{skill_id}.response` | `OvosSkillsFallbackResponseMessage` | `result: bool`, `fallback_handler \| None` |
| `ovos.skills.fallback.{skill_id}.killed` | `OvosSkillsFallbackKilledMessage` | `error: str` |
| `ovos.skills.fallback.force_timeout` | `OvosSkillsFallbackForceTimeoutMessage` | `skill_id` |

---

## Stop Protocol

```python
from ovos_pydantic_models.intents.stop import (
    StopGlobalMessage, StopSkillData, StopSkillMessage,
    MycroftStopMessage, MycroftStopHandledData, MycroftStopHandledMessage,
    SkillStopPingData, SkillStopPingMessage,
    SkillStopPongData, SkillStopPongMessage,
    SkillStopRequestMessage, SkillStopResponseData, SkillStopResponseMessage,
    MycroftSkillsAbortQuestionData, MycroftSkillsAbortQuestionMessage,
    MycroftSkillsAbortExecutionData, MycroftSkillsAbortExecutionMessage,
    MycroftAudioSpeechStopData, MycroftAudioSpeechStopMessage,
    OvosSkillsConverseForceTimeoutData, OvosSkillsConverseForceTimeoutMessage,
)
```

| Message type | Class | Key fields |
|---|---|---|
| `stop:global` | `StopGlobalMessage` | — |
| `stop:skill` | `StopSkillMessage` | `skill_id` |
| `mycroft.stop` | `MycroftStopMessage` | — |
| `mycroft.stop.handled` | `MycroftStopHandledMessage` | `by: str` |
| `mycroft.audio.speech.stop` | `MycroftAudioSpeechStopMessage` | `skill_id \| None` |
| `{skill_id}.stop.ping` | `SkillStopPingMessage` | `skill_id` |
| `skill.stop.pong` | `SkillStopPongMessage` | `skill_id`, `can_handle: bool` |
| `{skill_id}.stop` | `SkillStopRequestMessage` | — |
| `{skill_id}.stop.response` | `SkillStopResponseMessage` | `result: bool`, `error \| None` |
| `mycroft.skills.abort_question` | `MycroftSkillsAbortQuestionMessage` | `skill_id` |
| `mycroft.skills.abort_execution` | `MycroftSkillsAbortExecutionMessage` | `skill_id` (used by `@killable_intent`) |

---

## Skill Activate / Deactivate (skill-side events)

These are dynamic message types emitted by skills to signal their own activation state.

```python
from ovos_pydantic_models.intents.core import (
    SkillActivateData, SkillActivateMessage,
    SkillDeactivateData, SkillDeactivateMessage,
)

activate_msg = SkillActivateMessage(
    message_type="my-skill.activate",
    data=SkillActivateData(),
)
deactivate_msg = SkillDeactivateMessage(message_type="my-skill.deactivate")
```

These are open models (`extra='allow'`) — skills may include arbitrary extra data.

---

## Pipeline Reload

```python
from ovos_pydantic_models.intents.core import IntentServicePipelinesReloadMessage

msg = IntentServicePipelinesReloadMessage()
# message_type = "intent.service.pipelines.reload"
```
