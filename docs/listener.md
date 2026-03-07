# Listener Messages

Messages produced and consumed by `ovos-dinkum-listener` (the wake word + STT service).

## ListeningState

```python
from ovos_pydantic_models.listener.recognizer_loop import ListeningState
```

| Value | String |
|---|---|
| `SLEEPING` | `"sleeping"` |
| `WAITING_FOR_WAKEWORD` | `"waiting_for_wakeword"` |
| `CONTINUOUS` | `"continuous"` |
| `RECORDING` | `"recording"` |
| `MUTED` | `"muted"` |
| `DISABLED` | `"disabled"` |

---

## Utterance

### `recognizer_loop:utterance`

Emitted when STT produces a transcription. This is the primary input to the intent pipeline.

```python
from ovos_pydantic_models.listener.recognizer_loop import (
    RecognizerLoopUtteranceData, RecognizerLoopUtteranceMessage,
)

data = RecognizerLoopUtteranceData(utterances=["play some jazz"], lang="en-us")
msg = RecognizerLoopUtteranceMessage(data=data)
```

**`RecognizerLoopUtteranceData`**

| Field | Type | Required | Description |
|---|---|---|---|
| `utterances` | `list[str]` | yes | Transcribed utterance candidates |
| `lang` | `str` | yes | Language code (e.g. `"en-us"`) |
| `filename` | `str \| None` | no | URI to saved audio file |
| `transcriptions` | `list[tuple[str, float]] \| None` | no | `(text, confidence)` pairs from STT |
| `transcription` | `str \| None` | no | Deprecated: single transcription string |
| `recording_name` | `str \| None` | no | Name of saved recording |

Extra fields are allowed (open model).

---

## Wake Word

### `recognizer_loop:wakeword` / `hotword` / `stopword` / `wakeupword`

All four variants use `RecognizerLoopWakeWordData`.

```python
from ovos_pydantic_models.listener.recognizer_loop import (
    RecognizerLoopWakeWordData,
    RecognizerLoopWakeWordMessage,
    RecognizerLoopHotwordMessage,
    RecognizerLoopStopwordMessage,
    RecognizerLoopWakeupWordMessage,
)
```

**`RecognizerLoopWakeWordData`**

| Field | Type | Required | Description |
|---|---|---|---|
| `key_phrase` | `str` | yes | Detected key phrase (e.g. `"hey mycroft"`) |
| `engine` | `str` | yes | MD5 hash of the hotword engine module |
| `time` | `str` | yes | Detection timestamp (ms since epoch) |
| `sessionId` | `str` | yes | Session ID |
| `accountId` | `str` | yes | Account ID (e.g. `"Anon"`) |
| `model` | `str` | yes | Model hash/identifier |
| `utterance` | `str \| None` | no | Transcription if hotword includes STT |
| `sound` | `str \| list[str] \| None` | no | Sound file(s) to play on detection |
| `listen` | `bool \| None` | no | Whether to enter listening mode |
| `event` | `str \| None` | no | Custom event type to emit |
| `filename` | `str \| None` | no | URI to saved hotword audio |

---

## Listener State

### `recognizer_loop:state.set`

```python
from ovos_pydantic_models.listener.recognizer_loop import (
    RecognizerLoopStateSetData, RecognizerLoopStateSetMessage,
)

msg = RecognizerLoopStateSetMessage(
    data=RecognizerLoopStateSetData(state=ListeningState.MUTED)
)
```

### `recognizer_loop:state.get` / `recognizer_loop:state.get.response`

```python
from ovos_pydantic_models.listener.recognizer_loop import (
    RecognizerLoopStateGetMessage,
    RecognizerLoopStateGetReplyData, RecognizerLoopStateResponseMessage,
)

request = RecognizerLoopStateGetMessage()
reply_data = RecognizerLoopStateGetReplyData(state=ListeningState.RECORDING)
reply = RecognizerLoopStateResponseMessage(data=reply_data)
```

### Other state events (no data)

| Message type | Class |
|---|---|
| `recognizer_loop:record_begin` | `RecognizerLoopRecordBeginMessage` |
| `recognizer_loop:record_end` | `RecognizerLoopRecordEndMessage` |
| `recognizer_loop:record_stop` | `RecognizerLoopRecordStopMessage` |
| `recognizer_loop:sleep` | `RecognizerLoopSleepMessage` |
| `recognizer_loop:wake_up` | `RecognizerLoopWakeUpMessage` |
| `recognizer_loop:speech.recognition.unknown` | `RecognizerLoopSpeechRecognitionUnknownMessage` |
| `mycroft.awoken` | `MycroftAwokenMessage` |

---

## Microphone Control

All mic control messages carry no data payload.

| Message type | Class |
|---|---|
| `mycroft.mic.mute` | `MycroftMicMuteMessage` |
| `mycroft.mic.unmute` | `MycroftMicUnmuteMessage` |
| `mycroft.mic.mute.toggle` | `MycroftMicMuteToggleMessage` |
| `mycroft.mic.listen` | `MycroftMicListenMessage` |
| `mycroft.mic.get_status` | `MycroftMicGetStatusMessage` |

### `mycroft.mic.get_status.response`

```python
from ovos_pydantic_models.listener.recognizer_loop import (
    MycroftMicGetStatusReplyData, MycroftMicGetStatusResponseMessage,
)

reply = MycroftMicGetStatusResponseMessage(
    data=MycroftMicGetStatusReplyData(status="running")
)
```

---

## Base64 Audio / Transcribe

For direct audio injection over the bus (e.g., remote STT).

| Message type | Class |
|---|---|
| `recognizer_loop:b64_transcribe` | `RecognizerLoopB64TranscribeMessage` |
| `recognizer_loop:b64_transcribe.response` | `RecognizerLoopB64TranscribeResponseMessage` |
| `recognizer_loop:b64_audio` | `RecognizerLoopB64AudioMessage` |
| `recognizer_loop:b64_audio.response` | `RecognizerLoopB64AudioResponseMessage` |

**`RecognizerLoopB64TranscribeData`**

| Field | Type | Required | Description |
|---|---|---|---|
| `audio_b64` | `str` | yes | Base64-encoded audio |
| `lang` | `str \| None` | no | Language for transcription |
| `context` | `MessageContext \| None` | no | Original message context |

**`RecognizerLoopB64TranscribeReplyData`**

| Field | Type | Required | Description |
|---|---|---|---|
| `transcriptions` | `list[tuple[str, float]]` | yes | `(text, confidence)` pairs |
| `lang` | `str` | yes | Language of transcription |

---

## OPM (Plugin Manager) Queries

Listener plugin capability queries.

```python
from ovos_pydantic_models.listener.opm import (
    OvosLanguagesSttMessage, OvosLanguagesSttReplyData, OvosLanguagesSttResponseMessage,
    OpmWwQueryMessage,
)
```

| Message type | Class | Description |
|---|---|---|
| `ovos.languages.stt` | `OvosLanguagesSttMessage` | Request supported STT languages |
| `ovos.languages.stt.response` | `OvosLanguagesSttResponseMessage` | Reply with `langs: list[str]` |
| `opm.ww.query` | `OpmWwQueryMessage` | Query available wake word plugins |
