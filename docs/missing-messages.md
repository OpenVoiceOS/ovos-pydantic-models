# Missing Message Models

Findings from scanning all active repos in the workspace against `ovos_pydantic_models/`.

599 unique message type strings were found in use across the codebase. 202 are currently modeled. The ~250 unmodeled types below are grouped by subsystem with priority.

---

## Priority 1 — Core Protocol (high usage, well-defined schemas)

### Configuration

Used by `ovos-config`, skills, and PHAL plugins to propagate config changes.

| Message type | Source | Data fields |
|---|---|---|
| `configuration.patch` | ovos-config | `{"config": {key: value}}` |
| `configuration.updated` | ovos-config | `{}` (trigger reload) |
| `configuration.patch.clear` | ovos-config | `{}` |
| `configuration.cache.clear` | ovos-config | `{}` |

**Suggested file:** new `ovos_pydantic_models/core/configuration.py`

---

### Skill Internals

| Message type | Source | Data fields |
|---|---|---|
| `mycroft.skill.enable_intent` | ovos-workshop | `{"intent_name": str}` |
| `mycroft.skill.disable_intent` | ovos-workshop | `{"intent_name": str}` |
| `mycroft.skill.set_cross_context` | ovos-workshop | `{"context": str, "word": str, "origin": str}` |
| `mycroft.skill.remove_cross_context` | ovos-workshop | `{"context": str}` |
| `mycroft.skill.handler.start` | ovos-workshop | `{"name": str}` |
| `mycroft.skill.handler.complete` | ovos-workshop | `{"name": str}` |
| `mycroft.skills.shutdown` | ovos-core | `{"id": str, "folder": str}` |
| `mycroft.skills.loading_failure` | ovos-core | `{"id": str, "folder": str}` |
| `mycroft.skills.settings.changed` | ovos-core | `{"skill_id": str}` (note: different from `ovos.skills.settings_changed`) |
| `detach_skill` | ovos-workshop | `{"skill_id": str}` |
| `detach_intent` | ovos-workshop | `{"skill_id": str}` |

**Suggested file:** extend `ovos_pydantic_models/core/skill_manager.py`

---

### Event Scheduler

The `mycroft.scheduler.*` protocol is used by `EventSchedulerInterface` in ovos-workshop. Every skill with `schedule_event()` uses it.

| Message type | Direction | Data fields |
|---|---|---|
| `mycroft.scheduler.schedule_event` | skill → scheduler | `{"name": str, "when": float, "data": dict, "context": dict}` |
| `mycroft.scheduler.remove_event` | skill → scheduler | `{"name": str}` |
| `mycroft.scheduler.update_event` | skill → scheduler | `{"name": str, "data": dict}` |
| `mycroft.scheduler.get_event` | skill → scheduler | `{"name": str}` |
| `mycroft.scheduler.list_events` | skill → scheduler | `{}` |

**Suggested file:** new `ovos_pydantic_models/core/scheduler.py`

---

### Connectivity

| Message type | Source | Data fields |
|---|---|---|
| `mycroft.internet.state` | ovos-PHAL | `{"connected": bool}` |
| `mycroft.internet.is_ready` | ovos-PHAL | `{}` |
| `mycroft.network.state` | ovos-PHAL | `{"connected": bool}` |
| `mycroft.paired` | ovos-core | `{}` |
| `mycroft.not.paired` | ovos-core | `{}` |
| `mycroft.ready.check` | ovos-core | `{}` |
| `ovos.pairing.process.completed` | ovos-core | `{}` |
| `ovos.pairing.set.backend` | ovos-core | `{"backend": str}` |

**Suggested file:** extend `ovos_pydantic_models/phal/connectivity.py`

---

### Mark2 / Device Idle

| Message type | Source | Data fields |
|---|---|---|
| `mycroft.device.show.idle` | ovos-core | `{}` |
| `mycroft.device.settings` | ovos-core | `{}` |
| `mycroft.mark2.register_idle` | ovos-workshop | `{"name": str, "id": str}` |
| `mycroft.mark2.reset_idle` | ovos-workshop | `{"id": str}` |
| `mycroft.mark2.collect_idle` | ovos-gui | `{}` |
| `ovos.homescreen.displayed` | ovos-gui | `{}` |
| `ovos.homescreen.main_view.current_index.set` | ovos-gui | `{"index": int}` |
| `mycroft.ready.check` | ovos-core | `{}` |

**Suggested file:** extend `ovos_pydantic_models/gui/homescreen.py`

---

### Audio Service (ovos namespace)

The `ovos.audio.service.*` namespace is the modern replacement for `mycroft.audio.service.*`. Both exist but the former is preferred in newer code.

| Message type | Data fields |
|---|---|
| `ovos.audio.service.play` | `{"tracks": list, "utterance": str, "repeat": bool}` |
| `ovos.audio.service.stop` | `{}` |
| `ovos.audio.service.next` | `{}` |
| `ovos.audio.service.prev` | `{}` |
| `ovos.audio.service.pause` | `{}` |
| `ovos.audio.service.resume` | `{}` |
| `ovos.audio.service.seek_forward` | `{"seconds": float}` |
| `ovos.audio.service.seek_backward` | `{"seconds": float}` |
| `ovos.audio.service.set_track_position` | `{"position": int}` |
| `ovos.audio.service.get_track_length` | `{}` |
| `ovos.audio.service.get_track_position` | `{}` |
| `ovos.audio.service.track_info` | `{}` |
| `ovos.audio.service.list_backends` | `{}` |

**Note:** These mirror `mycroft.audio.service.*` exactly. The existing `AudioService*` models just need aliased subclasses with the `ovos.*` message types.

**Suggested file:** extend `ovos_pydantic_models/audio/audioservice.py`

---

## Priority 2 — GUI Protocol

### GUI Namespace / Page Control

Used by every skill with a GUI. High volume but mostly simple.

| Message type | Data fields |
|---|---|
| `gui.page.show` | `{"__from": str, "page": list[str], "namespace": str, "index": int}` |
| `gui.page.delete` | `{"__from": str, "page": list[str], "namespace": str}` |
| `gui.page.delete.all` | `{"__from": str, "namespace": str}` |
| `gui.value.set` | `{"__from": str, "namespace": str, "key": str, "value": Any}` |
| `gui.event.send` | `{"__from": str, "namespace": str, "event_name": str, "params": dict}` |
| `gui.clear.namespace` | `{"__from": str, "namespace": str}` |
| `gui.namespace.displayed` | `{"skill_id": str}` |
| `gui.namespace.removed` | `{"skill_id": str}` |
| `gui.page_gained_focus` | `{"skill_id": str, "page_index": int}` |
| `gui.page_interaction` | `{"skill_id": str, "page_index": int}` |
| `gui.status.request` | `{}` |

**Suggested file:** new `ovos_pydantic_models/gui/namespace.py`

---

### GUI Media Player Service

The GUI embeds a media player; these messages control it from the OCP layer.

| Message type | Data fields |
|---|---|
| `gui.player.media.service.play` | `{"track": str \| dict, "mime_type": str}` |
| `gui.player.media.service.pause` | `{}` |
| `gui.player.media.service.resume` | `{}` |
| `gui.player.media.service.stop` | `{}` |
| `gui.player.media.service.set.meta` | `{"title": str, "image": str, "artist": str}` |
| `gui.player.media.service.get.meta` | `{}` |
| `gui.player.media.service.sync.status` | `{"status": str}` |
| `gui.player.media.service.current.media.status` | `{"status": str}` |
| `gui.player.media.service.get.next` | `{}` |
| `gui.player.media.service.get.previous` | `{}` |
| `gui.player.media.service.get.repeat` | `{}` |
| `gui.player.media.service.get.shuffle` | `{}` |

**Suggested file:** new `ovos_pydantic_models/gui/media_player.py`

---

### Homescreen (missing entries)

| Message type | Data fields |
|---|---|
| `homescreen.register.app` | `{"skill_id": str, "name": str, "icon": str}` |
| `homescreen.wallpaper.set` | `{"wallpaper": str}` |
| `homescreen.metadata.get` | `{}` |

**Suggested file:** extend `ovos_pydantic_models/gui/homescreen.py`

---

## Priority 3 — OCP Extended Protocol

Many OCP player-control messages are present in `ovos-media` and `ovos-workshop` but not yet modeled.

### Playback Control

| Message type | Data fields |
|---|---|
| `ovos.common_play.play` | already modeled ✓ |
| `ovos.common_play.pause` | `{}` |
| `ovos.common_play.resume` | `{}` |
| `ovos.common_play.stop` | `{}` |
| `ovos.common_play.stop.response` | `{"result": bool}` |
| `ovos.common_play.next` | `{}` |
| `ovos.common_play.previous` | `{}` |
| `ovos.common_play.seek` | `{"position": int}` |
| `ovos.common_play.set_track_position` | `{"position": int}` |
| `ovos.common_play.get_track_position` | `{}` |
| `ovos.common_play.get_track_length` | `{}` |
| `ovos.common_play.playback_time` | `{"position": int, "length": int}` |
| `ovos.common_play.play_pause` | `{}` |
| `ovos.common_play.simple.play` | `{"uri": str, "mime_type": str}` |
| `ovos.common_play.home` | `{}` |
| `ovos.common_play.ping` | `{}` |

### Repeat / Shuffle

| Message type | Data fields |
|---|---|
| `ovos.common_play.repeat.set` | `{}` |
| `ovos.common_play.repeat.unset` | `{}` |
| `ovos.common_play.repeat.toggle` | `{}` |
| `ovos.common_play.shuffle.set` | `{}` |
| `ovos.common_play.shuffle.unset` | `{}` |
| `ovos.common_play.shuffle.toggle` | `{}` |

### Playlist Management

| Message type | Data fields |
|---|---|
| `ovos.common_play.playlist.queue` | `{"media": MediaEntry}` |
| `ovos.common_play.playlist.set` | `{"playlist": list[MediaEntry]}` |
| `ovos.common_play.playlist.clear` | `{}` |
| `ovos.common_play.playlist.play` | `{}` |

### Track Info / Status

| Message type | Data fields |
|---|---|
| `ovos.common_play.track_info` | `{}` |
| `ovos.common_play.track_info.response` | MediaEntry dict |
| `ovos.common_play.track.state` | `{"state": TrackState}` |
| `ovos.common_play.status` | `{}` |
| `ovos.common_play.status.response` | `{"state": PlayerState, "media": MediaEntry, ...}` |
| `ovos.common_play.player.status` | `{"state": PlayerState, ...}` |
| `ovos.common_play.list_backends` | `{}` |

### Likes

| Message type | Data fields |
|---|---|
| `ovos.common_play.like` | MediaEntry dict |
| `ovos.common_play.unlike` | MediaEntry dict |
| `ovos.common_play.liked_tracks.play` | `{}` |

### Search

| Message type | Data fields |
|---|---|
| `ovos.common_play.search` | `{"phrase": str}` |
| `ovos.common_play.play_search` | `{"phrase": str}` |
| `ovos.common_play.search.start` | `{"phrase": str}` |
| `ovos.common_play.search.end` | `{}` |
| `ovos.common_play.search.populate` | `{"results": list}` |
| `ovos.common_play.search.play` | MediaEntry dict |

### GUI Timeout

| Message type | Data fields |
|---|---|
| `ovos.common_play.gui.enable_app_timeout` | `{}` |
| `ovos.common_play.gui.set_app_timeout` | `{"timeout": int}` |
| `ovos.common_play.gui.timeout.mode` | `{"mode": str}` |

### SEI (Skill Extension Interface)

| Message type | Data fields |
|---|---|
| `ovos.common_play.SEI.get` | `{}` |
| `ovos.common_play.SEI.get.response` | `{"extensions": list}` |

**Suggested file:** extend `ovos_pydantic_models/skills/ocp.py`

---

## Priority 4 — Video and Web Service

Identical structure to `ovos.audio.service.*` but for video and web backends.

### `ovos.video.service.*`

| Message type | Mirrors |
|---|---|
| `ovos.video.service.play` | `ovos.audio.service.play` |
| `ovos.video.service.stop` | `ovos.audio.service.stop` |
| `ovos.video.service.pause` | — |
| `ovos.video.service.resume` | — |
| `ovos.video.service.next` | — |
| `ovos.video.service.prev` | — |
| `ovos.video.service.seek_forward` | — |
| `ovos.video.service.seek_backward` | — |
| `ovos.video.service.set_track_position` | — |
| `ovos.video.service.get_track_position` | — |
| `ovos.video.service.get_track_length` | — |
| `ovos.video.service.track_info` | — |
| `ovos.video.service.list_backends` | — |

### `ovos.web.service.*`

Same structure, same set of operations.

**Suggested file:** new `ovos_pydantic_models/audio/video_service.py` and `ovos_pydantic_models/audio/web_service.py`

---

## Priority 5 — PHAL Plugins

### PHAL System (ovos-PHAL-plugin-system)

| Message type | Data fields |
|---|---|
| `system.reboot` | `{}` |
| `system.reboot.start` | `{}` |
| `system.shutdown` | `{}` |
| `system.shutdown.start` | `{}` |
| `system.factory.reset` | `{}` |
| `system.factory.reset.ping` | `{}` |
| `system.factory.reset.register` | `{"skill_id": str, "callback_msg": str}` |
| `system.factory.reset.phal` | `{}` |
| `system.factory.reset.phal.complete` | `{}` |
| `system.ssh.enable` | `{}` |
| `system.ssh.enabled` | `{}` |
| `system.ssh.disable` | `{}` |
| `system.ssh.disabled` | `{}` |
| `system.ssh.status` | `{"enabled": bool}` |
| `system.mycroft.service.restart` | `{}` |
| `system.mycroft.service.restart.start` | `{}` |
| `system.clock.synced` | `{}` |
| `system.configure.language` | `{"lang": str}` |
| `system.configure.language.complete` | `{"lang": str}` |
| `system.display.homescreen` | `{}` |
| `system.wifi.setup` | `{}` |

**Suggested file:** new `ovos_pydantic_models/phal/system.py`

---

### PHAL Network Manager (ovos-PHAL-plugin-network-manager)

| Message type | Data fields |
|---|---|
| `ovos.phal.nm.scan` | `{}` |
| `ovos.phal.nm.scan.complete` | `{"networks": list[dict]}` |
| `ovos.phal.nm.connect` | `{"bssid": str, "password": str \| None}` |
| `ovos.phal.nm.connect.open.network` | `{"bssid": str}` |
| `ovos.phal.nm.connection.successful` | `{"bssid": str}` |
| `ovos.phal.nm.connection.failure` | `{"bssid": str, "error": str}` |
| `ovos.phal.nm.disconnect` | `{}` |
| `ovos.phal.nm.disconnection.successful` | `{}` |
| `ovos.phal.nm.disconnection.failure` | `{"error": str}` |
| `ovos.phal.nm.forget` | `{"bssid": str}` |
| `ovos.phal.nm.forget.successful` | `{"bssid": str}` |
| `ovos.phal.nm.forget.failure` | `{"bssid": str, "error": str}` |
| `ovos.phal.nm.is.connected` | `{}` |
| `ovos.phal.nm.is.not.connected` | `{}` |
| `ovos.phal.nm.get.connected` | `{}` |
| `ovos.phal.nm.reconnect` | `{}` |
| `ovos.phal.nm.set.backend` | `{"backend": str}` |
| `ovos.phal.nm.backend.not.supported` | `{}` |

**Suggested file:** new `ovos_pydantic_models/phal/network_manager.py`

---

### PHAL WiFi Setup (ovos-PHAL-plugin-wifi-setup)

| Message type | Data fields |
|---|---|
| `ovos.phal.wifi.plugin.alive` | `{}` |
| `ovos.phal.wifi.plugin.register.client` | `{"client_id": str}` |
| `ovos.phal.wifi.plugin.client.registered` | `{"client_id": str}` |
| `ovos.phal.wifi.plugin.client.registration.failure` | `{"client_id": str, "error": str}` |
| `ovos.phal.wifi.plugin.deregister.client` | `{"client_id": str}` |
| `ovos.phal.wifi.plugin.client.deregistered` | `{"client_id": str}` |
| `ovos.phal.wifi.plugin.set.active.client` | `{"client_id": str}` |
| `ovos.phal.wifi.plugin.remove.active.client` | `{"client_id": str}` |
| `ovos.phal.wifi.plugin.get.registered.clients` | `{}` |
| `ovos.phal.wifi.plugin.registered.clients` | `{"clients": list[str]}` |
| `ovos.phal.wifi.plugin.user.activated` | `{}` |
| `ovos.phal.wifi.plugin.setup.launched` | `{}` |
| `ovos.phal.wifi.plugin.setup.failed` | `{"error": str}` |
| `ovos.phal.wifi.plugin.stop.setup.event` | `{}` |
| `ovos.phal.wifi.plugin.skip.setup` | `{}` |
| `ovos.phal.wifi.plugin.fully.offline` | `{}` |
| `ovos.phal.wifi.plugin.status` | `{"status": str}` |
| `ovos.phal.wifi.plugin.client.select` | `{"client_id": str}` |
| `ovos.phal.wifi.plugin.client.select.page.removed` | `{}` |
| `ovos.phal.wifi.plugin.client.setup.failure` | `{"client_id": str, "error": str}` |
| `ovos.wifi.setup.completed` | `{}` |
| `ovos.phal.wifi.scan` | `{}` |
| `ovos.phal.wifi.info` | `{"ssid": str, "connected": bool}` |

**Suggested file:** new `ovos_pydantic_models/phal/wifi_setup.py`

---

### PHAL Brightness (ovos-PHAL-plugin-brightness-control-rpi)

| Message type | Data fields |
|---|---|
| `phal.brightness.control.get` | `{}` |
| `phal.brightness.control.get.response` | `{"brightness": int}` |
| `phal.brightness.control.set` | `{"brightness": int}` |
| `phal.brightness.control.sync` | `{}` |
| `phal.brightness.control.auto.dim.update` | `{"auto_dim": bool}` |
| `phal.brightness.control.auto.night.mode.enabled` | `{}` |

**Suggested file:** new `ovos_pydantic_models/phal/brightness.py`

---

### PHAL Wallpaper Manager (ovos-PHAL-plugin-wallpaper-manager)

| Message type | Data fields |
|---|---|
| `ovos.wallpaper.manager.register.provider` | `{"provider_name": str}` |
| `ovos.wallpaper.manager.set.active.provider` | `{"provider_name": str}` |
| `ovos.wallpaper.manager.get.active.provider` | `{}` |
| `ovos.wallpaper.manager.get.registered.providers` | `{}` |
| `ovos.wallpaper.manager.set.wallpaper` | `{"url": str}` |
| `ovos.wallpaper.manager.get.wallpaper` | `{}` |
| `ovos.wallpaper.manager.change.wallpaper` | `{}` |
| `ovos.wallpaper.manager.get.collection` | `{}` |
| `ovos.wallpaper.manager.get.collection.from.provider` | `{"provider_name": str}` |
| `ovos.wallpaper.manager.update.collection` | `{"collection": list[str]}` |
| `ovos.wallpaper.manager.collect.collection.response` | `{"provider_name": str, "collection": list[str]}` |
| `ovos.wallpaper.manager.get.auto.rotation` | `{}` |
| `ovos.wallpaper.manager.enable.auto.rotation` | `{}` |
| `ovos.wallpaper.manager.disable.auto.rotation` | `{}` |
| `ovos.wallpaper.manager.auto.rotation.enabled` | `{}` |
| `ovos.wallpaper.manager.auto.rotation.disabled` | `{}` |
| `ovos.wallpaper.manager.loaded` | `{}` |

**Suggested file:** new `ovos_pydantic_models/phal/wallpaper.py`

---

### PHAL Camera (ovos-PHAL-plugin-camera)

| Message type | Data fields |
|---|---|
| `ovos.phal.camera.ping` | `{}` |
| `ovos.phal.camera.pong` | `{}` |
| `ovos.phal.camera.open` | `{}` |
| `ovos.phal.camera.close` | `{}` |
| `ovos.phal.camera.get` | `{}` |

**Suggested file:** new `ovos_pydantic_models/phal/camera.py`

---

### PHAL Sensors (ovos-PHAL-sensors)

| Message type | Data fields |
|---|---|
| `ovos.phal.sensor` | `{"sensor_id": str, "value": Any, "unit": str \| None}` |
| `ovos.phal.binary_sensor` | `{"sensor_id": str, "value": bool}` |

**Suggested file:** new `ovos_pydantic_models/phal/sensors.py`

---

### PHAL Configuration Provider

| Message type | Data fields |
|---|---|
| `ovos.phal.configuration.provider.get` | `{"group": str \| None}` |
| `ovos.phal.configuration.provider.get.response` | `{"config": dict}` |
| `ovos.phal.configuration.provider.list.groups` | `{}` |
| `ovos.phal.configuration.provider.list.groups.response` | `{"groups": list[str]}` |
| `ovos.phal.configuration.provider.set` | `{"group": str, "config": dict}` |

**Suggested file:** new `ovos_pydantic_models/phal/configuration_provider.py`

---

### OAuth (ovos-PHAL-plugin-oauth)

| Message type | Data fields |
|---|---|
| `oauth.ping` | `{}` |
| `oauth.register` | `{"skill_id": str, "client_id": str, "client_secret": str, "auth_endpoint": str, "token_endpoint": str, "callback_url": str}` |
| `oauth.get` | `{"skill_id": str}` |
| `oauth.get.app.host.info` | `{}` |
| `oauth.start` | `{"skill_id": str}` |
| `oauth.refresh` | `{"skill_id": str}` |
| `oauth.generate.qr.request` | `{"skill_id": str}` |
| `ovos.shell.oauth.display.qr.code` | `{"qr_code": str}` |
| `ovos.shell.oauth.register.credentials` | `{"skill_id": str, "credentials": dict}` |

**Suggested file:** new `ovos_pydantic_models/phal/oauth.py`

---

## Priority 6 — Notifications and Widgets

### Notifications (ovos-gui)

| Message type | Data fields |
|---|---|
| `ovos.notification.api.set` | `{"notification": dict}` |
| `ovos.notification.api.set.controlled` | `{"notification": dict}` |
| `ovos.notification.api.remove.controlled` | `{"notification": dict}` |
| `ovos.notification.api.request.storage.model` | `{}` |
| `ovos.notification.api.storage.clear` | `{}` |
| `ovos.notification.api.storage.clear.item` | `{"notification": dict}` |
| `ovos.notification.api.pop.clear` | `{}` |
| `ovos.notification.api.pop.clear.delete` | `{}` |
| `ovos.notification.update_counter` | `{"count": int}` |
| `ovos.notification.update_storage_model` | `{"model": list}` |
| `ovos.notification.controlled.type.show` | `{"type": str}` |
| `ovos.notification.controlled.type.remove` | `{"type": str}` |
| `ovos.notification.show` | `{"notification": dict}` |
| `ovos.notification.notification_data` | `{}` |

**Suggested file:** new `ovos_pydantic_models/gui/notifications.py`

---

### Widgets (ovos-gui)

| Message type | Data fields |
|---|---|
| `ovos.widgets.display` | `{"type": str, "data": dict}` |
| `ovos.widgets.remove` | `{"type": str}` |
| `ovos.widgets.update` | `{"type": str, "data": dict}` |
| `ovos.widgets.timer.display` | `{"timer": dict}` |
| `ovos.widgets.timer.update` | `{"timer": dict}` |
| `ovos.widgets.timer.remove` | `{"timer_id": str}` |
| `ovos.widgets.alarm.display` | `{"alarm": dict}` |
| `ovos.widgets.alarm.update` | `{"alarm": dict}` |
| `ovos.widgets.alarm.remove` | `{"alarm_id": str}` |
| `ovos.widgets.media.display` | `{"media": dict}` |
| `ovos.widgets.media.update` | `{"media": dict}` |
| `ovos.widgets.media.remove` | `{}` |

**Suggested file:** new `ovos_pydantic_models/gui/widgets.py`

---

## Priority 7 — Language

| Message type | Source | Data fields |
|---|---|---|
| `ovos.language.output.force` | ovos-workshop | `{"lang": str}` |
| `ovos.language.output.reset` | ovos-workshop | `{}` |
| `ovos.ipgeo.update` | ovos-PHAL-plugin-ipgeo | `{"location": dict}` |

**Suggested file:** extend `ovos_pydantic_models/core/configuration.py` or new `ovos_pydantic_models/core/language.py`

---

## Priority 8 — Mark1 Enclosure

These are legacy messages for the Mycroft Mark1 hardware (eyes, mouth). Used by `ovos-PHAL-plugin-mk1`.

| Namespace | Message count |
|---|---|
| `enclosure.eyes.*` | 13 types |
| `enclosure.mouth.*` | 11 types |
| `enclosure.system.*` | 5 types |
| `enclosure.*` (misc) | 4 types |

**Suggested file:** new `ovos_pydantic_models/phal/enclosure.py`

Details:

| Message type | Data |
|---|---|
| `enclosure.eyes.on` | `{}` |
| `enclosure.eyes.off` | `{}` |
| `enclosure.eyes.color` | `{"r": int, "g": int, "b": int}` |
| `enclosure.eyes.blink` | `{"side": str}` |
| `enclosure.eyes.spin` | `{}` |
| `enclosure.eyes.timedspin` | `{"length": int}` |
| `enclosure.eyes.narrow` | `{}` |
| `enclosure.eyes.look` | `{"side": str}` |
| `enclosure.eyes.level` | `{"level": int}` |
| `enclosure.eyes.volume` | `{"volume": int}` |
| `enclosure.eyes.fill` | `{"percentage": int}` |
| `enclosure.eyes.reset` | `{}` |
| `enclosure.eyes.setpixel` | `{"idx": int, "r": int, "g": int, "b": int}` |
| `enclosure.mouth.reset` | `{}` |
| `enclosure.mouth.talk` | `{}` |
| `enclosure.mouth.think` | `{}` |
| `enclosure.mouth.listen` | `{}` |
| `enclosure.mouth.smile` | `{}` |
| `enclosure.mouth.viseme` | `{"code": str}` |
| `enclosure.mouth.viseme_list` | `{"start": float, "visemes": list}` |
| `enclosure.mouth.display` | `{"img_code": str, "xOffset": int, "yOffset": int, "clearPrev": bool}` |
| `enclosure.mouth.text` | `{"text": str}` |
| `enclosure.mouth.events.activate` | `{}` |
| `enclosure.mouth.events.deactivate` | `{}` |
| `enclosure.reset` | `{}` |
| `enclosure.started` | `{}` |
| `enclosure.notify.no_internet` | `{}` |
| `enclosure.system.reset` | `{}` |
| `enclosure.system.mute` | `{}` |
| `enclosure.system.unmute` | `{}` |
| `enclosure.system.blink` | `{"times": int}` |
| `enclosure.weather.display` | `{"img_code": str, "temp": str}` |

---

## Priority 9 — Intent Service Adapt/Padatious Manifest Queries

Used by OVOScope and diagnostic tools to introspect loaded intents.

| Message type | Data fields |
|---|---|
| `intent.service.adapt.get` | `{"utterance": str, "lang": str}` |
| `intent.service.adapt.manifest.get` | `{}` |
| `intent.service.adapt.vocab.manifest.get` | `{}` |
| `intent.service.padatious.get` | `{"utterance": str, "lang": str}` |
| `intent.service.padatious.manifest.get` | `{}` |
| `intent.service.padatious.entities.manifest.get` | `{}` |

**Suggested file:** extend `ovos_pydantic_models/intents/core.py`

---

## Excluded (not worth modeling)

| Category | Reason |
|---|---|
| `spotifyd.*` | Plugin-specific, not part of OVOS protocol |
| `persona.*` | Persona plugin; project-specific, low reuse |
| `ovos.ggwave.*` | Plugin-specific |
| `ovos.mass.ping` | hivemind-specific |
| `ovos.mpv.*` | Plugin-specific |
| `*.openvoiceos.*` | Skill-specific dynamic types |
| `enclosure.weather.display` | Mark1-only, low priority |
| `fallback_cycle_test` | Test artifact |

---

## Summary by File

| New/extended file | Message types to add |
|---|---|
| `core/configuration.py` (new) | 4 config + 2 language |
| `core/scheduler.py` (new) | 5 scheduler |
| `core/skill_manager.py` (extend) | 10 skill internals |
| `gui/namespace.py` (new) | 11 GUI namespace |
| `gui/media_player.py` (new) | 12 GUI player |
| `gui/homescreen.py` (extend) | 5 homescreen |
| `gui/notifications.py` (new) | 14 notifications |
| `gui/widgets.py` (new) | 12 widgets |
| `audio/audioservice.py` (extend) | 13 ovos.audio.service.* |
| `audio/video_service.py` (new) | 13 ovos.video.service.* |
| `audio/web_service.py` (new) | 13 ovos.web.service.* |
| `skills/ocp.py` (extend) | ~35 OCP extended |
| `phal/network_manager.py` (new) | 18 nm |
| `phal/wifi_setup.py` (new) | 24 wifi setup |
| `phal/system.py` (new) | 22 system PHAL |
| `phal/brightness.py` (new) | 6 brightness |
| `phal/wallpaper.py` (new) | 17 wallpaper |
| `phal/camera.py` (new) | 5 camera |
| `phal/sensors.py` (new) | 2 sensors |
| `phal/configuration_provider.py` (new) | 5 config provider |
| `phal/oauth.py` (new) | 9 oauth |
| `phal/enclosure.py` (new) | 30 Mark1 enclosure |
| `phal/connectivity.py` (extend) | 8 connectivity |
| `intents/core.py` (extend) | 6 adapt/padatious manifest |

**Total missing: ~300 message types across ~24 files**
