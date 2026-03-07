# Audio Messages

Messages produced and consumed by `ovos-audio` (the TTS and audio playback service).

## TTS — Speak

### `speak`

The primary TTS request. Emitted by skills, handled by the audio service.

```python
from ovos_pydantic_models.audio.playback import SpeakData, SpeakMessage

msg = SpeakMessage(data=SpeakData(utterance="Hello, world!", lang="en-us"))
```

**`SpeakData`**

| Field | Type | Default | Description |
|---|---|---|---|
| `utterance` | `str` | required | Text to synthesize and speak |
| `expect_response` | `bool` | `False` | If `True`, listener activates after speech completes |
| `meta` | `dict` | `{}` | Optional metadata (e.g. `{"skill": "skill_id"}`) |

### `speak:b64_audio`

Request for base64 audio without playing it (useful for remote TTS).

**`SpeakB64AudioData`**

| Field | Type | Default | Description |
|---|---|---|---|
| `utterance` | `str` | required | Text to synthesize |
| `listen` | `bool` | `False` | Whether listener should activate after |

### `speak:b64_audio.response`

**`SpeakB64AudioReplyData`**

| Field | Type | Required | Description |
|---|---|---|---|
| `audio` | `str` | yes | Base64-encoded audio |
| `listen` | `bool` | yes | From original request |
| `tts_id` | `str` | yes | TTS plugin ID that synthesized |
| `utterance` | `str` | yes | Original text |

---

## Audio Queue / Play

### `mycroft.audio.queue`

Queue a pre-synthesized audio chunk for playback.

```python
from ovos_pydantic_models.audio.playback import MycroftAudioQueueData, MycroftAudioQueueMessage

msg = MycroftAudioQueueMessage(
    data=MycroftAudioQueueData(uri="file:///tmp/tts_output.wav")
)
```

**`MycroftAudioQueueData`** — one of `uri`, `filename`, or `binary_data` is required.

| Field | Type | Default | Description |
|---|---|---|---|
| `uri` | `str \| None` | `None` | URI to audio file |
| `filename` | `str \| None` | `None` | Deprecated — use `uri` |
| `binary_data` | `str \| None` | `None` | Hex-encoded audio bytes |
| `audio_ext` | `str \| None` | `None` | Extension for binary data (e.g. `"wav"`) |
| `viseme` | `list[tuple[float, str]] \| None` | `None` | `(timestamp, viseme)` for mouth animation |
| `listen` | `bool` | `False` | Activate listener after playback |

### `mycroft.audio.play_sound`

Play a sound immediately (bypasses queue).

**`MycroftAudioPlaySoundData`** — one of `uri` or `binary_data` is required.

| Field | Type | Default | Description |
|---|---|---|---|
| `uri` | `str \| None` | `None` | URI to audio file |
| `binary_data` | `str \| None` | `None` | Hex-encoded audio bytes |
| `audio_ext` | `str \| None` | `None` | Extension for binary data |
| `force_unmute` | `bool` | `False` | Ensure volume is not muted |

---

## Audio Service Control

These messages control the legacy audio service backend (e.g. for music playback via `ovos-audio`).

```python
from ovos_pydantic_models.audio.audioservice import (
    AudioServicePlayData, AudioServicePlayMessage,
    AudioServicePauseMessage, AudioServiceResumeMessage,
    AudioServiceStopMessage,
)
```

| Message type | Class | Has data? |
|---|---|---|
| `mycroft.audio.service.play` | `AudioServicePlayMessage` | yes |
| `mycroft.audio.service.pause` | `AudioServicePauseMessage` | no |
| `mycroft.audio.service.resume` | `AudioServiceResumeMessage` | no |
| `mycroft.audio.service.stop` | `AudioServiceStopMessage` | no |
| `mycroft.audio.service.next` | `AudioServiceNextMessage` | no |
| `mycroft.audio.service.prev` | `AudioServicePrevMessage` | no |
| `mycroft.audio.service.seek_forward` | `AudioServiceSeekForwardMessage` | no |
| `mycroft.audio.service.seek_backward` | `AudioServiceSeekBackwardMessage` | no |
| `mycroft.audio.service.track_info` | `AudioServiceTrackInfoMessage` | no |

**`AudioServicePlayData`**

| Field | Type | Default | Description |
|---|---|---|---|
| `tracks` | `list` | `[]` | Track URIs or dict entries to play |
| `utterance` | `str` | `""` | Original utterance that triggered playback |
| `repeat` | `bool` | `False` | Loop playback |

---

## Speech Status

| Message type | Class | Description |
|---|---|---|
| `mycroft.audio.speech.stop` | `MycroftSpeechStopMessage` | Stop current TTS speech |
| `mycroft.audio.speak.status` | `MycroftAudioSpeakStatusMessage` | Request speaking status |
| `mycroft.audio.is_speaking` | `MycroftAudioIsSpeakingMessage` | Reply: `speaking: bool` |

---

## OCP Media States

`OcpMediaState` is an `IntEnum` matching Qt's `QMediaPlayer::MediaStatus` constants. Used by the OCP audio player.

```python
from ovos_pydantic_models.audio.ocp import OcpMediaState

OcpMediaState.UNKNOWN         # 0
OcpMediaState.NO_MEDIA        # 1
OcpMediaState.LOADING_MEDIA   # 2
OcpMediaState.LOADED_MEDIA    # 3
OcpMediaState.STALLED_MEDIA   # 4
OcpMediaState.BUFFERING_MEDIA # 5
OcpMediaState.BUFFERED_MEDIA  # 6
OcpMediaState.END_OF_MEDIA    # 7
OcpMediaState.INVALID_MEDIA   # 8
```

> Note: This is distinct from `skills/ocp.py::MediaState` (a str Enum for OCP player state: `PLAYING`, `PAUSED`, etc.). See [ocp.md](ocp.md).

---

## OPM (Plugin Manager) TTS Queries

```python
from ovos_pydantic_models.audio.opm import (
    OvosLanguagesTtsMessage, OvosLanguagesTtsReplyData, OvosLanguagesTtsResponseMessage,
)

request = OvosLanguagesTtsMessage()
reply = OvosLanguagesTtsResponseMessage(
    data=OvosLanguagesTtsReplyData(langs=["en-us", "de-de", "es-es"])
)
```

| Message type | Class |
|---|---|
| `ovos.languages.tts` | `OvosLanguagesTtsMessage` |
| `ovos.languages.tts.response` | `OvosLanguagesTtsResponseMessage` |
