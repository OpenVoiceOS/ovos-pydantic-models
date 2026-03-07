# OCP Messages

Messages for the OVOS Common Play (OCP) framework — the media playback system that coordinates between media skills and the OCP player.

## Enums

```python
from ovos_pydantic_models.skills.ocp import (
    MediaType, MediaState, PlaybackType, PlaybackMode,
    PlayerState, LoopState, TrackState, MatchConfidence,
)
```

### MediaType

| Value | String |
|---|---|
| `GENERIC` | `"generic"` |
| `AUDIO` | `"audio"` |
| `MUSIC` | `"music"` |
| `VIDEO` | `"video"` |
| `SILENCE` | `"silence"` |
| `PODCAST` | `"podcast"` |
| `RADIO` | `"radio"` |
| `NEWS` | `"news"` |
| `AD` | `"advertisement"` |
| `ANNOUNCEMENT` | `"announcement"` |
| `COMMUNICATION` | `"communication"` |
| `ALARM` | `"alarm"` |
| `TIMER` | `"timer"` |
| `NOTIFICATION` | `"notification"` |
| `GAME` | `"game"` |
| `OTHER` | `"other"` |

### PlaybackType

| Value | String |
|---|---|
| `AUDIO` | `"audio"` |
| `VIDEO` | `"video"` |
| `WEBVIEW` | `"webview"` |
| `SKILL` | `"skill"` (game/skill-rendered media) |

### PlayerState (OCP player state)

| Value | String |
|---|---|
| `STOPPED` | `"stopped"` |
| `PLAYING` | `"playing"` |
| `PAUSED` | `"paused"` |
| `LOADING` | `"loading"` |
| `BUFFERING` | `"buffering"` |

### MediaState (OCP media pipeline state)

| Value | String |
|---|---|
| `IDLE` | `"idle"` |
| `LOADING` | `"loading"` |
| `PLAYING` | `"playing"` |
| `PAUSED` | `"paused"` |
| `STOPPED` | `"stopped"` |
| `END_OF_STREAM` | `"eos"` |
| `BUFFERING` | `"buffering"` |
| `ERROR` | `"error"` |

> Note: This is the OCP pipeline state (str Enum). For the Qt QMediaPlayer integer state (`OcpMediaState`), see [audio.md](audio.md).

### MatchConfidence

| Value | Float |
|---|---|
| `EXACT` | `1.0` |
| `VERY_HIGH` | `0.9` |
| `HIGH` | `0.8` |
| `AVERAGE` | `0.5` |
| `LOW` | `0.3` |
| `NO_MATCH` | `0.0` |

### PlaybackMode / LoopState / TrackState

```python
PlaybackMode: NORMAL, LOOP, SHUFFLE, SINGLE_LOOP
LoopState:    NONE, PLAYLIST, TRACK
TrackState:   QUEUED, PLAYING, PAUSED, STOPPED, ERROR, BUFFERING
```

---

## Media Data Models

### MediaEntry

Represents a single playable media item. Open model (extra fields allowed).

```python
from ovos_pydantic_models.skills.ocp import MediaEntry

entry = MediaEntry(
    uri="https://example.com/song.mp3",
    title="My Song",
    artist="My Artist",
    media_type=MediaType.MUSIC,
    playback=PlaybackType.AUDIO,
    match_confidence=MatchConfidence.HIGH,
)
```

| Field | Type | Default | Description |
|---|---|---|---|
| `uri` | `str` | required | Media URI |
| `title` | `str \| None` | `None` | Track title |
| `artist` | `str \| None` | `None` | Artist name |
| `album` | `str \| None` | `None` | Album name |
| `image` | `str \| None` | `None` | Artwork URL |
| `playback` | `PlaybackType` | `AUDIO` | How this media is rendered |
| `match_confidence` | `MatchConfidence` | `AVERAGE` | How well this result matches the query |
| `media_type` | `MediaType` | `GENERIC` | Type of media |
| `skill_id` | `str \| None` | `None` | Owning skill |
| `length` | `int \| None` | `None` | Duration in milliseconds |
| `position` | `int \| None` | `None` | Current position in milliseconds |
| `bg_image` | `str \| None` | `None` | Background image URL |

### PluginStream

Extends `MediaEntry` with plugin-specific fields:

| Additional Field | Type | Description |
|---|---|---|
| `plugin_id` | `str` | Plugin identifier |
| `stream_id` | `str` | Stream identifier within the plugin |

### Playlist

```python
from ovos_pydantic_models.skills.ocp import Playlist

playlist = Playlist(
    title="Jazz Collection",
    entries=[entry1, entry2, entry3],
)
```

| Field | Type | Default |
|---|---|---|
| `title` | `str \| None` | `None` |
| `author` | `str \| None` | `None` |
| `image` | `str \| None` | `None` |
| `thumbnail` | `str \| None` | `None` |
| `url` | `str \| None` | `None` |
| `entries` | `list[MediaEntry]` | `[]` |

---

## Query Protocol

Skills respond to OCP queries to offer media results.

### `ovos.common_play.query`

OCP broadcasts this when the user requests media playback.

```python
from ovos_pydantic_models.skills.ocp import OvosCommonPlayQueryData, OvosCommonPlayQueryMessage

msg = OvosCommonPlayQueryMessage(
    data=OvosCommonPlayQueryData(phrase="play some jazz", question_type=MediaType.MUSIC)
)
```

**`OvosCommonPlayQueryData`**

| Field | Type | Default | Description |
|---|---|---|---|
| `phrase` | `str` | required | User's search phrase |
| `question_type` | `MediaType` | `GENERIC` | Requested media type |

### `ovos.common_play.query.response`

Skills send this back to OCP with their results.

```python
from ovos_pydantic_models.skills.ocp import OvosCommonPlayQueryResponseData, OvosCommonPlayQueryResponseMessage

data = OvosCommonPlayQueryResponseData(
    phrase="play some jazz",
    skill_id="skill-jazz.mycroft",
    skill_name="Jazz Radio",
    thumbnail="https://example.com/icon.png",
    results=[entry1, entry2],
    searching=False,
)
```

**`OvosCommonPlayQueryResponseData`**

| Field | Type | Default | Description |
|---|---|---|---|
| `phrase` | `str` | required | Original search phrase |
| `skill_id` | `str` | required | Responding skill |
| `skill_name` | `str` | required | Skill display name |
| `thumbnail` | `str` | required | Skill icon |
| `results` | `list[MediaEntry \| Playlist \| PluginStream]` | `[]` | Found results |
| `searching` | `bool` | required | `True` if still searching (streaming response) |
| `timeout` | `float \| None` | `None` | Optional timeout extension |

---

## OCP Player Control

### Skill Announce

OCP skills announce their capabilities on startup.

```python
from ovos_pydantic_models.skills.ocp import OvosCommonPlayAnnounceData, OvosCommonPlayAnnounceMessage

msg = OvosCommonPlayAnnounceMessage(
    data=OvosCommonPlayAnnounceData(
        skill_id="skill-jazz.mycroft",
        skill_name="Jazz Radio",
        thumbnail="https://example.com/icon.png",
        media_type=MediaType.MUSIC,
        featured_tracks=True,
    )
)
```

### Player State

```python
from ovos_pydantic_models.skills.ocp import OvosCommonPlayPlayerStateData, OvosCommonPlayPlayerStateMessage

msg = OvosCommonPlayPlayerStateMessage(
    data=OvosCommonPlayPlayerStateData(state=PlayerState.PLAYING)
)
```

### Skill-specific Playback (dynamic message types)

These messages are sent to a specific skill's OCP handler:

| Message type | Class | Description |
|---|---|---|
| `ovos.common_play.{skill_id}.play` | `OvosCommonPlaySkillPlayMessage` | Request skill to play `media` |
| `ovos.common_play.{skill_id}.pause` | `OvosCommonPlaySkillPauseMessage` | Pause playback |
| `ovos.common_play.{skill_id}.resume` | `OvosCommonPlaySkillResumeMessage` | Resume playback |
| `ovos.common_play.{skill_id}.next` | `OvosCommonPlaySkillNextMessage` | Skip to next track |
| `ovos.common_play.{skill_id}.previous` | `OvosCommonPlaySkillPreviousMessage` | Go to previous track |
| `ovos.common_play.{skill_id}.stop` | `OvosCommonPlaySkillStopMessage` | Stop playback |

**`OvosCommonPlaySkillPlayData`** (dynamic `{skill_id}.play` sent from OCP to a specific skill)

| Field | Type | Required |
|---|---|---|
| `media` | `MediaEntry \| PluginStream \| dict` | yes |
| `disambiguation` | `list` | yes |
| `playlist` | `list` | yes |

### Other OCP Messages

| Message type | Class | Description |
|---|---|---|
| `ovos.common_play.play` | `OvosCommonPlayPlayMessage` | Request OCP to play (from skill to OCP) |
| `ovos.common_play.skill.play` | `OvosCommonPlaySkillPlayMessage` (game.py) | Fixed-type play for game skills |
| `ovos.common_play.skills.get` | `OvosCommonPlaySkillsGetMessage` | Request list of OCP skills |
| `ovos.common_play.skills.detach` | `OvosCommonPlaySkillsDetachMessage` | Skill detaches from OCP |
| `ovos.common_play.search.stop` | `OvosCommonPlaySearchStopMessage` | Stop ongoing search |
| `ovos.common_play.featured_tracks.play` | `OvosCommonPlayFeaturedTracksPlayMessage` | Play featured tracks |
| `ovos.common_play.skill.search_start` | `OvosCommonPlaySkillSearchStartMessage` | Skill signals search started |
| `ovos.common_play.skill.search_end` | `OvosCommonPlaySkillSearchEndMessage` | Skill signals search done |

---

## Keyword Registration

OCP skills can register entity keywords for better query parsing.

```python
from ovos_pydantic_models.skills.ocp import (
    OvosCommonPlayRegisterKeywordData, OvosCommonPlayRegisterKeywordMessage,
    OvosCommonPlayDeregisterKeywordData, OvosCommonPlayDeregisterKeywordMessage,
)

msg = OvosCommonPlayRegisterKeywordMessage(
    data=OvosCommonPlayRegisterKeywordData(
        skill_id="skill-jazz.mycroft",
        label="artist_name",
        media_type=MediaType.MUSIC,
        samples=["Miles Davis", "John Coltrane", "Frank Sinatra"],
    )
)
```

**`OvosCommonPlayRegisterKeywordData`**

| Field | Type | Description |
|---|---|---|
| `skill_id` | `str` | Registering skill |
| `label` | `str` | Slot label (e.g. `"artist_name"`, `"movie_name"`) |
| `media_type` | `MediaType` | Associated media type |
| `samples` | `list[str] \| None` | Example keyword values |
| `csv` | `str \| None` | Path to CSV file with many samples |

---

## Common Query Skill (CQS) Protocol

Separate from OCP — for skills that answer factual questions via `question:query`.

```python
from ovos_pydantic_models.skills.common_query import (
    CQSMatchLevel, CQSVisualMatchLevel,
    QuestionQueryData, QuestionQueryMessage,
    QuestionQueryResponseData, QuestionQueryResponseMessage,
    QuestionActionData, QuestionActionMessage,
    OvosCommonQueryPingMessage,
    OvosCommonQueryPongData, OvosCommonQueryPongMessage,
)
```

**`CQSMatchLevel`** (IntEnum)

| Value | Int | Description |
|---|---|---|
| `EXACT` | `1` | Skill found a specific answer |
| `CATEGORY` | `2` | Answer from a category in the query |
| `GENERAL` | `3` | General query processing |

### `question:query` / `question:query.response`

```python
query = QuestionQueryMessage(
    data=QuestionQueryData(phrase="what is the capital of France?")
)
```

**`QuestionQueryResponseData`**

| Field | Type | Default | Description |
|---|---|---|---|
| `phrase` | `str` | required | Original question |
| `skill_id` | `str` | required | Responding skill |
| `searching` | `bool` | required | Still searching? |
| `answer` | `str \| None` | `None` | Speakable answer |
| `handles_speech` | `bool \| None` | `None` | Skill handled its own speech |
| `callback_data` | `dict \| None` | `None` | Passed to `CQS_action` |
| `conf` | `float \| None` | `None` | Confidence (0.0–1.0) |

### `question:action`

Sent to the winning skill after selection, triggering `CQS_action`.

| Field | Type | Description |
|---|---|---|
| `phrase` | `str` | Original question |
| `skill_id` | `str` | Selected skill |
| `callback_data` | `dict \| None` | From the skill's query response |

### Discovery

| Message type | Class |
|---|---|
| `ovos.common_query.ping` | `OvosCommonQueryPingMessage` |
| `ovos.common_query.pong` | `OvosCommonQueryPongMessage` |
