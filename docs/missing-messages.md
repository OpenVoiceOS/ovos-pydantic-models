# Missing / Incomplete Message Models

Tracking doc for coverage gaps. Items marked ✅ are now modeled. Items marked ❌ are still missing.

Current coverage: **545 message classes** across all subsystems.

---

## Fully Implemented ✅

| Subsystem | File |
|---|---|
| Configuration patch/update | `core/configuration.py` |
| Event scheduler | `core/scheduler.py` |
| Skill manager internals | `core/skill_manager.py` |
| GUI namespace / page control | `gui/namespace.py` |
| GUI media player service | `gui/media_player.py` (deprecated) |
| GUI notifications | `gui/notifications.py` (deprecated) |
| GUI widgets | `gui/widgets.py` (deprecated) |
| OCP extended protocol (100+ messages) | `skills/ocp.py` |
| Legacy audio service `ovos.*` namespace | `audio/audioservice.py` |
| Video service | `audio/video_service.py` (beta) |
| Web service | `audio/web_service.py` (beta) |
| PHAL network manager | `phal/network_manager.py` |
| PHAL WiFi setup | `phal/wifi_setup.py` (deprecated) |
| PHAL system | `phal/system.py` |
| PHAL brightness | `phal/brightness.py` |
| PHAL wallpaper manager | `phal/wallpaper.py` |
| PHAL camera | `phal/camera.py` |
| PHAL sensors | `phal/sensors.py` |
| PHAL configuration provider | `phal/configuration_provider.py` (deprecated) |
| PHAL OAuth | `phal/oauth.py` |
| Mark1 enclosure | `phal/enclosure.py` |
| PHAL connectivity | `phal/connectivity.py` |
| Adapt pipeline plugin messages | `intents/adapt.py` (legacy) |
| Padatious pipeline plugin messages | `intents/padatious.py` (legacy) |

---

## Still Missing ❌

### Core / Skill Internals

Some `mycroft.skill.*` messages emitted by `ovos-workshop` are not yet modeled:

| Message type | Data | Notes |
|---|---|---|
| `mycroft.skill.enable_intent` | `{"intent_name": str}` | Enable a disabled intent |
| `mycroft.skill.disable_intent` | `{"intent_name": str}` | Disable an intent |
| `mycroft.skill.set_cross_context` | `{"context": str, "word": str, "origin": str}` | Cross-skill context |
| `mycroft.skill.remove_cross_context` | `{"context": str}` | Remove cross-skill context |
| `mycroft.skill.handler.start` | `{"name": str}` | Intent handler started |
| `mycroft.skill.handler.complete` | `{"name": str}` | Intent handler finished |
| `mycroft.skills.shutdown` | `{"id": str, "folder": str}` | Skill shutdown event |
| `mycroft.skills.loading_failure` | `{"id": str, "folder": str}` | Skill failed to load |

**Suggested file:** extend `core/skill_manager.py`

---

### GUI — Homescreen

| Message type | Data | Notes |
|---|---|---|
| `mycroft.mark2.register_idle` | `{"name": str, "id": str}` | Register homescreen idle display |
| `mycroft.mark2.reset_idle` | `{"id": str}` | Reset idle display |
| `mycroft.mark2.collect_idle` | `{}` | Collect idle displays from skills |
| `ovos.homescreen.displayed` | `{}` | Homescreen is now shown |
| `mycroft.device.show.idle` | `{}` | Request device show idle/homescreen |

**Suggested file:** extend `gui/homescreen.py`

---

### Language

| Message type | Source | Data |
|---|---|---|
| `ovos.language.output.force` | ovos-workshop | `{"lang": str}` |
| `ovos.language.output.reset` | ovos-workshop | `{}` |
| `ovos.ipgeo.update` | ovos-PHAL-plugin-ipgeo | `{"location": dict}` |

**Suggested file:** extend `core/configuration.py` or new `core/language.py`

---

### OPM Microphone Queries

| Message type | Description |
|---|---|
| `opm.mic.query` | Query available microphone plugins |
| `opm.mic.query.response` | Reply with mic plugin list |

**Suggested file:** extend `listener/opm.py`

---

### Enclosure — Additional

| Message type | Data | Notes |
|---|---|---|
| `enclosure.eyes.rgb` | `{"pixels": list}` | ✅ Added |
| `enclosure.eyes.rgb.get` | `{}` | ✅ Added |
| `enclosure.system.blink` | `{"times": int}` | ✅ Added |
| `enclosure.mouth.display_image` | `{img_path, xOffset, yOffset, invert, clearPrev}` | ✅ Added |
| `enclosure.weather.display` | `{"img_code": str, "temp": int}` | ✅ Added |
| `enclosure.active_skill` | `{"skill_id": str}` | ✅ Added (deprecated) |

All enclosure messages are now modeled.

---

## Excluded (not worth modeling)

| Category | Reason |
|---|---|
| `spotifyd.*` | Plugin-specific, not part of OVOS protocol |
| `persona.*` | Project-specific, low reuse |
| `ovos.ggwave.*` | Plugin-specific |
| `ovos.mass.*` | HiveMind-specific |
| `ovos.mpv.*` | Plugin-specific |
| `*.openvoiceos.*` | Skill-specific dynamic types |
| `fallback_cycle_test` | Test artifact |
