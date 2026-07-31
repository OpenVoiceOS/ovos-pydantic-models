# OCP: OVOS Common Play

OCP is the OVOS media playback framework. It coordinates between OCP skills (which supply media results) and the OCP player (which handles playback). OCP messages live in their own **OCP** category in the interactive reference.

> **Beta**: `ovos-media` (the OCP player) is still pre-release (`0.0.1a*`). The `audio.video_service` and `audio.web_service` sub-protocols are also beta.

---

## Module layout

| Module | Description |
|---|---|
| `ovos_pydantic_models.audio.ocp` | Low-level OCP audio state signals (`OcpMediaState` IntEnum) |
| `ovos_pydantic_models.skills.ocp` | Skill-side OCP API: query, announce, playback control, enums, data models |
| `ovos_pydantic_models.audio.video_service` | `ovos.video.service.*` messages (beta) |
| `ovos_pydantic_models.audio.web_service` | `ovos.web.service.*` messages (beta) |

---

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

| Value | String |
|---|---|
| `SILENCE` | `"silence"` |
| `PODCAST` | `"podcast"` |
| `RADIO` | `"radio"` |
| `NEWS` | `"news"` |

| Value | String |
|---|---|
| `AD` | `"advertisement"` |
| `ANNOUNCEMENT` | `"announcement"` |
| `COMMUNICATION` | `"communication"` |
| `ALARM` | `"alarm"` |

| Value | String |
|---|---|
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

### PlayerState

| Value | String |
|---|---|
| `STOPPED` | `"stopped"` |
| `PLAYING` | `"playing"` |
| `PAUSED` | `"paused"` |
| `LOADING` | `"loading"` |

| Value | String |
|---|---|
| `BUFFERING` | `"buffering"` |

### MediaState (OCP pipeline state)

| Value | String |
|---|---|
| `IDLE` | `"idle"` |
| `LOADING` | `"loading"` |
| `PLAYING` | `"playing"` |
| `PAUSED` | `"paused"` |

| Value | String |
|---|---|
| `STOPPED` | `"stopped"` |
| `END_OF_STREAM` | `"eos"` |
| `BUFFERING` | `"buffering"` |
| `ERROR` | `"error"` |

> Distinct from `audio.ocp::OcpMediaState` (IntEnum, Qt QMediaPlayer constants). See [audio.md](audio.md).

### MatchConfidence

| Value | Float |
|---|---|
| `EXACT` | `1.0` |
| `VERY_HIGH` | `0.9` |
| `HIGH` | `0.8` |
| `AVERAGE` | `0.5` |

| Value | Float |
|---|---|
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
from ovos_pydantic_models.skills.ocp import MediaEntry, MediaType, PlaybackType, MatchConfidence

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

| Field | Type | Default | Description |
|---|---|---|---|
| `image` | `str \| None` | `None` | Artwork URL |
| `playback` | `PlaybackType` | `AUDIO` | How this media is rendered |
| `match_confidence` | `MatchConfidence` | `AVERAGE` | How well this result matches the query |
| `media_type` | `MediaType` | `GENERIC` | Type of media |

| Field | Type | Default | Description |
|---|---|---|---|
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

| Field | Type | Default |
|---|---|---|
| `url` | `str \| None` | `None` |
| `entries` | `list[MediaEntry]` | `[]` |

---

## Query Protocol

OCP broadcasts a query when the user requests media. Skills respond with results.

### `ovos.common_play.query`

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

Skills send this back with their results. `searching=True` allows streaming partial results.

**`OvosCommonPlayQueryResponseData`**

| Field | Type | Default | Description |
|---|---|---|---|
| `phrase` | `str` | required | Original search phrase |
| `skill_id` | `str` | required | Responding skill |
| `skill_name` | `str` | required | Skill display name |
| `thumbnail` | `str` | required | Skill icon |

| Field | Type | Default | Description |
|---|---|---|---|
| `results` | `list[MediaEntry \| Playlist \| PluginStream]` | `[]` | Found results |
| `searching` | `bool` | required | `True` if still searching |
| `timeout` | `float \| None` | `None` | Optional timeout extension |

### Search lifecycle

| Message type | Class | Description |
|---|---|---|
| `ovos.common_play.search` | `OvosCommonPlaySearchMessage` | Start a new search |
| `ovos.common_play.play_search` | `OvosCommonPlayPlaySearchMessage` | Search and immediately play best result |
| `ovos.common_play.search.start` | `OvosCommonPlaySearchStartMessage` | OCP signals search phase started |
| `ovos.common_play.search.end` | `OvosCommonPlaySearchEndMessage` | OCP signals search phase ended |

| Message type | Class | Description |
|---|---|---|
| `ovos.common_play.search.stop` | `OvosCommonPlaySearchStopMessage` | Abort all ongoing searches |
| `ovos.common_play.search.populate` | `OvosCommonPlaySearchPopulateMessage` | Push results into GUI list |
| `ovos.common_play.search.play` | `OvosCommonPlaySearchPlayMessage` | Play a result from the search list |
| `ovos.common_play.skill.search_start` | `OvosCommonPlaySkillSearchStartMessage` | Skill signals its search started |

| Message type | Class | Description |
|---|---|---|
| `ovos.common_play.skill.search_end` | `OvosCommonPlaySkillSearchEndMessage` | Skill signals its search done |

---

## Playback Control

Global OCP player commands:

| Message type | Class | Key data |
|---|---|---|
| `ovos.common_play.play` | `OvosCommonPlayPlayMessage` | `media`, `disambiguation`, `playlist` |
| `ovos.common_play.simple.play` | `OvosCommonPlaySimplePlayMessage` | `uri`, `mime_type` |
| `ovos.common_play.pause` | `OvosCommonPlayPauseMessage` | n/a |
| `ovos.common_play.resume` | `OvosCommonPlayResumeMessage` | n/a |

| Message type | Class | Key data |
|---|---|---|
| `ovos.common_play.stop` | `OvosCommonPlayStopMessage` | n/a |
| `ovos.common_play.stop.response` | `OvosCommonPlayStopResponseMessage` | `result: bool` |
| `ovos.common_play.next` | `OvosCommonPlayNextMessage` | n/a |
| `ovos.common_play.previous` | `OvosCommonPlayPreviousMessage` | n/a |

| Message type | Class | Key data |
|---|---|---|
| `ovos.common_play.play_pause` | `OvosCommonPlayPlayPauseMessage` | n/a |
| `ovos.common_play.seek` | `OvosCommonPlaySeekMessage` | `position: int` (ms) |
| `ovos.common_play.set_track_position` | `OvosCommonPlaySetTrackPositionMessage` | `position: int` |
| `ovos.common_play.get_track_position` | `OvosCommonPlayGetTrackPositionMessage` | n/a |

| Message type | Class | Key data |
|---|---|---|
| `ovos.common_play.get_track_length` | `OvosCommonPlayGetTrackLengthMessage` | n/a |
| `ovos.common_play.playback_time` | `OvosCommonPlayPlaybackTimeMessage` | `position`, `length` |
| `ovos.common_play.home` | `OvosCommonPlayHomeMessage` | n/a |
| `ovos.common_play.ping` | `OvosCommonPlayPingMessage` | n/a |

| Message type | Class | Key data |
|---|---|---|
| `ovos.common_play.duck` | `OvosCommonPlayDuckMessage` | n/a |
| `ovos.common_play.unduck` | `OvosCommonPlayUnduckMessage` | n/a |
| `ovos.common_play.cork` | `OvosCommonPlayCorkMessage` | n/a |
| `ovos.common_play.uncork` | `OvosCommonPlayUncorkMessage` | n/a |

---

## Skill-Specific Playback (dynamic message types)

OCP routes these to the specific skill currently playing:

| Format | Class | Description |
|---|---|---|
| `ovos.common_play.{skill_id}.play` | `OvosCommonPlaySkillPlayMessage` | OCP asks skill to play `media` |
| `ovos.common_play.{skill_id}.pause` | `OvosCommonPlaySkillPauseMessage` | Pause |
| `ovos.common_play.{skill_id}.resume` | `OvosCommonPlaySkillResumeMessage` | Resume |
| `ovos.common_play.{skill_id}.next` | `OvosCommonPlaySkillNextMessage` | Next track |

| Format | Class | Description |
|---|---|---|
| `ovos.common_play.{skill_id}.previous` | `OvosCommonPlaySkillPreviousMessage` | Previous track |
| `ovos.common_play.{skill_id}.stop` | `OvosCommonPlaySkillStopMessage` | Stop |

**`OvosCommonPlaySkillPlayData`**

| Field | Type | Required |
|---|---|---|
| `media` | `MediaEntry \| PluginStream \| dict` | yes |
| `disambiguation` | `list` | yes |
| `playlist` | `list` | yes |

---

## Player State & Status

| Message type | Class | Key data |
|---|---|---|
| `ovos.common_play.player.state` | `OvosCommonPlayPlayerStateMessage` | `state: PlayerState` |
| `ovos.common_play.media.state` | `OvosCommonPlayMediaStateMessage` | `state: MediaState` |
| `ovos.common_play.track.state` | `OvosCommonPlayTrackStateMessage` | `state: TrackState` |
| `ovos.common_play.player.status` | `OvosCommonPlayPlayerStatusMessage` | full status dict |

| Message type | Class | Key data |
|---|---|---|
| `ovos.common_play.status` | `OvosCommonPlayStatusMessage` | n/a (request) |
| `ovos.common_play.status.response` | `OvosCommonPlayStatusResponseMessage` | `state`, `media`, etc. |
| `ovos.common_play.track_info` | `OvosCommonPlayTrackInfoMessage` | n/a (request) |
| `ovos.common_play.track_info.response` | `OvosCommonPlayTrackInfoResponseMessage` | `MediaEntry` fields |

| Message type | Class | Key data |
|---|---|---|
| `ovos.common_play.list_backends` | `OvosCommonPlayListBackendsMessage` | n/a |

---

## Repeat / Shuffle

| Message type | Class |
|---|---|
| `ovos.common_play.repeat.set` | `OvosCommonPlayRepeatSetMessage` |
| `ovos.common_play.repeat.unset` | `OvosCommonPlayRepeatUnsetMessage` |
| `ovos.common_play.repeat.toggle` | `OvosCommonPlayRepeatToggleMessage` |
| `ovos.common_play.shuffle.set` | `OvosCommonPlayShuffleSetMessage` |

| Message type | Class |
|---|---|
| `ovos.common_play.shuffle.unset` | `OvosCommonPlayShuffleUnsetMessage` |
| `ovos.common_play.shuffle.toggle` | `OvosCommonPlayShuffleToggleMessage` |

---

## Playlist Management

| Message type | Class | Key data |
|---|---|---|
| `ovos.common_play.playlist.queue` | `OvosCommonPlayPlaylistQueueMessage` | `MediaEntry` |
| `ovos.common_play.playlist.set` | `OvosCommonPlayPlaylistSetMessage` | `list[MediaEntry]` |
| `ovos.common_play.playlist.clear` | `OvosCommonPlayPlaylistClearMessage` | n/a |
| `ovos.common_play.playlist.play` | `OvosCommonPlayPlaylistPlayMessage` | n/a |

---

## Likes

| Message type | Class | Data |
|---|---|---|
| `ovos.common_play.like` | `OvosCommonPlayLikeMessage` | `MediaEntry` fields |
| `ovos.common_play.unlike` | `OvosCommonPlayUnlikeMessage` | `MediaEntry` fields |
| `ovos.common_play.liked_tracks.play` | `OvosCommonPlayLikedTracksPlayMessage` | n/a |

---

## Skill Registration & Discovery

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

| Message type | Class | Description |
|---|---|---|
| `ovos.common_play.announce` | `OvosCommonPlayAnnounceMessage` | Skill announces itself to OCP on startup |
| `ovos.common_play.skills.get` | `OvosCommonPlaySkillsGetMessage` | Request list of registered OCP skills |
| `ovos.common_play.skills.detach` | `OvosCommonPlaySkillsDetachMessage` | Skill detaches from OCP |
| `ovos.common_play.featured_tracks.play` | `OvosCommonPlayFeaturedTracksPlayMessage` | Play featured tracks for a skill |

| Message type | Class | Description |
|---|---|---|
| `ovos.common_play.skill.play` | `OvosCommonPlaySkillPlayMessage` | Fixed-type play for game skills |

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
        samples=["Miles Davis", "John Coltrane"],
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

| Field | Type | Description |
|---|---|---|
| `csv` | `str \| None` | Path to CSV file with many samples |

---

## SEI (Skill Extension Interface)

| Message type | Class | Description |
|---|---|---|
| `ovos.common_play.SEI.get` | `OvosCommonPlaySeiGetMessage` | Request registered SEI list |
| `ovos.common_play.SEI.get.response` | `OvosCommonPlaySeiGetResponseMessage` | Reply with `extensions: list` |

---

## Common Query Skill (CQS) Protocol

Separate from OCP. For skills that answer factual questions.

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

| Field | Type | Default | Description |
|---|---|---|---|
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

---
[← Audio](audio.md) · [Home](index.md) · [Intent pipeline →](intent-pipeline.md)
