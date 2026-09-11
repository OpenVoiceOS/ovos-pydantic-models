# ovos-pydantic-models

Typed Pydantic v2 models for every message that flows over the [OVOS MessageBus](https://github.com/OpenVoiceOS/ovos-messagebus).

This package is the authoritative, machine-readable specification of the OVOS MessageBus protocol. Each message type is represented as a Pydantic model with validated fields, making it suitable for type-checking, serialization, documentation generation, and integration testing.

## Installation

```bash
pip install ovos-pydantic-models
```

## Usage

```python
from ovos_pydantic_models import SpeakMessage, SpeakData

# Create a typed message
msg = SpeakMessage(data=SpeakData(utterance="Hello, world!", lang="en-us"))
print(msg.message_type)   # "speak"
print(msg.model_dump())   # {"message_type": "speak", "data": {...}, "context": {...}}

# Roundtrip from dict (e.g. received over the bus)
raw = {"message_type": "speak", "data": {"utterance": "Hello"}, "context": {}}
restored = SpeakMessage.model_validate(raw)
print(restored.data.utterance)   # "Hello"
```

```python
from ovos_pydantic_models import RecognizerLoopUtteranceMessage, RecognizerLoopUtteranceData

msg = RecognizerLoopUtteranceMessage(
    data=RecognizerLoopUtteranceData(utterances=["play some jazz"], lang="en-us")
)
print(msg.message_type)   # "recognizer_loop:utterance"
```

## Message Index

Messages are organized by subsystem:

### Audio / TTS

| Message type | Class |
|---|---|
| `speak` | `SpeakMessage` |
| `mycroft.audio.service.play` | `AudioServicePlayMessage` |
| `mycroft.audio.service.pause` | `AudioServicePauseMessage` |
| `mycroft.audio.service.resume` | `AudioServiceResumeMessage` |

| Message type | Class |
|---|---|
| `mycroft.audio.service.stop` | `AudioServiceStopMessage` |
| `mycroft.audio.queue` | `MycroftAudioQueueMessage` |
| `ovos.languages.tts` | `OvosLanguagesTtsMessage` |
| `ovos.languages.tts.response` | `OvosLanguagesTtsResponseMessage` |

### Listener / STT

| Message type | Class |
|---|---|
| `recognizer_loop:utterance` | `RecognizerLoopUtteranceMessage` |
| `recognizer_loop:wakeword` | `RecognizerLoopWakeWordMessage` |
| `recognizer_loop:state.set` | `RecognizerLoopStateSetMessage` |
| `recognizer_loop:state.get` | `RecognizerLoopStateGetMessage` |

| Message type | Class |
|---|---|
| `recognizer_loop:state.get.response` | `RecognizerLoopStateResponseMessage` |
| `mycroft.mic.mute` | `MycroftMicMuteMessage` |
| `mycroft.mic.listen` | `MycroftMicListenMessage` |
| `ovos.languages.stt` | `OvosLanguagesSttMessage` |

| Message type | Class |
|---|---|
| `ovos.languages.stt.response` | `OvosLanguagesSttResponseMessage` |
| `opm.ww.query` | `OpmWwQueryMessage` |

### Intent Pipeline

| Message type | Class |
|---|---|
| `ovos.utterance.handled` | `OvosUtteranceHandledMessage` |
| `ovos.utterance.cancelled` | `OvosUtteranceCancelledMessage` |
| `complete_intent_failure` | `CompleteIntentFailureMessage` |
| `add_context` | `AddContextMessage` |

| Message type | Class |
|---|---|
| `remove_context` | `RemoveContextMessage` |
| `clear_context` | `ClearContextMessage` |
| `intent.service.skills.activate` | `IntentServiceSkillsActivateMessage` |
| `intent.service.skills.deactivate` | `IntentServiceSkillsDeactivateMessage` |

| Message type | Class |
|---|---|
| `skill.converse.pong` | `SkillConversePongMessage` |
| `skill.converse.response` | `SkillConverseResponseMessage` |
| `ovos.skills.fallback.register` | `OvosSkillsFallbackRegisterMessage` |
| `ovos.skills.fallback.ping` | `OvosSkillsFallbackPingMessage` |

| Message type | Class |
|---|---|
| `ovos.skills.fallback.pong` | `OvosSkillsFallbackPongMessage` |
| `stop:global` | `StopGlobalMessage` |
| `stop:skill` | `StopSkillMessage` |
| `mycroft.stop` | `MycroftStopMessage` |

| Message type | Class |
|---|---|
| `mycroft.skills.abort_question` | `MycroftSkillsAbortQuestionMessage` |
| `mycroft.skills.abort_execution` | `MycroftSkillsAbortExecutionMessage` |

### Skill Manager / Core

| Message type | Class |
|---|---|
| `mycroft.ready` | `MycroftReadyMessage` |
| `mycroft.skills.ready` | `MycroftSkillsReadyMessage` |
| `mycroft.skills.is_ready` | `MycroftSkillsIsReadyMessage` |
| `mycroft.skills.is_ready.response` | `MycroftSkillsIsReadyResponseMessage` |

| Message type | Class |
|---|---|
| `mycroft.skills.list` | `MycroftSkillsListMessage` |
| `skillmanager.list` | `SkillManagerListMessage` |
| `skillmanager.deactivate` | `SkillManagerDeactivateMessage` |
| `mycroft.skills.error` | `MycroftSkillsErrorMessage` |

| Message type | Class |
|---|---|
| `skill.settings.change` | `SkillSettingsChangeMessage` |
| `ovos.skills.settings_changed` | `OvosSkillsSettingsChangedMessage` |
| `ovos.skills.install` | `OvosSkillsInstallMessage` |
| `ovos.skills.install.failed` | `OvosSkillsInstallFailedMessage` |

| Message type | Class |
|---|---|
| `ovos.pip.install` | `OvosPipInstallMessage` |
| `ovos.session.sync` | `OvosSessionSyncMessage` |
| `ovos.session.update_default` | `OvosSessionUpdateDefaultMessage` |

### OCP (Common Play)

| Message type | Class |
|---|---|
| `ovos.common_play.query` | `OvosCommonPlayQueryMessage` |
| `ovos.common_play.query.response` | `OvosCommonPlayQueryResponseMessage` |
| `ovos.common_play.announce` | `OvosCommonPlayAnnounceMessage` |
| `ovos.common_play.player.state` | `OvosCommonPlayPlayerStateMessage` |

| Message type | Class |
|---|---|
| `ovos.common_play.skills.detach` | `OvosCommonPlaySkillsDetachMessage` |
| `ovos.common_play.register_keyword` | `OvosCommonPlayRegisterKeywordMessage` |
| `ovos.common_play.skill.play` | `OvosCommonPlaySkillPlayMessage` |

### Common Query

| Message type | Class |
|---|---|
| `question:query` | `QuestionQueryMessage` |
| `question:query.response` | `QuestionQueryResponseMessage` |

### GUI / Homescreen

| Message type | Class |
|---|---|
| `homescreen.manager.app` | `HomescreenManagerAppMessage` |

## Key Types

```python
from ovos_pydantic_models import (
    # Base
    OpenVoiceOSMessage, MessageContext, Session,
    # Enums
    UtteranceState, ListeningState,
    MediaType, PlaybackType, PlayerState, MediaState, MatchConfidence,
    OcpMediaState,  # IntEnum 0-8 (Qt QMediaPlayer states)
    FallbackMode, ConverseMode, CQSMatchLevel,
    # Data models
    MediaEntry, Playlist, PluginStream,
)
```

## Module Structure

```
ovos_pydantic_models/
  message.py          # OpenVoiceOSMessage base, MessageContext
  session.py          # Session, UtteranceState, IntentContextManager
  audio/
    playback.py       # Speak, AudioService messages
    ocp.py            # OcpMediaState (Qt IntEnum)
    opm.py            # OPM TTS query/response messages
  listener/
    recognizer_loop.py
    opm.py            # OPM STT/WW query messages
  intents/
    core.py           # context, utterance handled, intent get
    converse.py       # converse protocol (canonical)
    fallbacks.py      # fallback protocol (canonical)
    stop.py           # stop messages
  skills/
    ocp.py            # OCP enums, MediaEntry, query messages
    game.py           # game skill messages
    common_query.py   # question:query protocol
    converse.py       # re-exports from intents/converse.py
    fallback.py       # re-exports from intents/fallbacks.py
  core/
    skill_manager.py  # skill lifecycle messages
    skill_settings.py
    skill_installer.py
    session.py        # session sync messages
  gui/
    homescreen.py
  phal/
    connectivity.py
    volume.py
```

## Related Projects

- [OpenVoiceOS/ovos-messagebus](https://github.com/OpenVoiceOS/ovos-messagebus): the message bus these models validate.
- [OpenVoiceOS/ovos-bus-client](https://github.com/OpenVoiceOS/ovos-bus-client): the untyped client library this package complements.
- [OpenVoiceOS/ovos-audio](https://github.com/OpenVoiceOS/ovos-audio): the TTS and audio playback service that produces and consumes the audio messages.
- [OpenVoiceOS/ovos-dinkum-listener](https://github.com/OpenVoiceOS/ovos-dinkum-listener): the wake word and STT service that produces the listener messages.

## License

Apache 2.0. See [LICENSE](LICENSE).

---

## Credits

Developed by [TigreGótico](https://tigregotico.pt) for
[OpenVoiceOS](https://openvoiceos.org).

[![NGI0 Commons Fund](./ngi.png)](https://nlnet.nl/project/OpenVoiceOS)

This project was funded through the [NGI0 Commons Fund](https://nlnet.nl/commonsfund),
a fund established by [NLnet](https://nlnet.nl) with financial support from the
European Commission's [Next Generation Internet](https://ngi.eu) programme, under
the aegis of [DG Communications Networks, Content and Technology](https://commission.europa.eu/about-european-commission/departments-and-executive-agencies/communications-networks-content-and-technology_en)
under grant agreement No [101135429](https://cordis.europa.eu/project/id/101135429).
