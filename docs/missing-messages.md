# Intentionally Excluded Messages

Messages found in the workspace scan that are **not modeled** and will not be. They are plugin-private, project-specific, or not part of the reusable OVOS bus protocol.

Run `python tools/scan_for_messages.py --unmodeled-only` to verify coverage.

---

| Category | Message type(s) | Reason |
|---|---|---|
| `spotifyd.*` | `spotifyd.change`, `spotifyd.load`, `spotifyd.pause`, `spotifyd.play`, etc. | Internal signals from the spotifyd daemon, not OVOS bus protocol |
| `ovos.mass.*` | `ovos.mass.ping` | HiveMind-specific, not part of OVOS |
| `hive.*` / `hivemind:*` | `hive.send.downstream`, `hivemind:ask` | HiveMind networking layer, separate project |
| `hass.action` | n/a | Home Assistant pipeline, HA-specific |

| Category | Message type(s) | Reason |
|---|---|---|
| `ovos.mpv.*` | `ovos.mpv.timeout_check` | Internal MPV plugin state, not a bus API |
| `ocp:*` | `ocp:play`, `ocp:pause`, `ocp:next`, `ocp:legacy_cps`, etc. | ML classifier output **labels** (model categories inside ocp-pipeline-plugin), not actual bus message types |
| `ovos.ggwave.*` / `ggwave.*` | `ovos.ggwave.enable/disable/enabled/disabled`, `ggwave.enabled/disabled` | Plugin-specific, single-skill private API |
| Skill-specific private APIs | `ovos.alerts.*`, `ovos.gui.show.active.*`, `ovos.display.screenshot.*`, `async.chatgpt.fallback`, `hello.world` | Private APIs used only within a single skill, not reusable protocol |

| Category | Message type(s) | Reason |
|---|---|---|
| Skill-specific dynamic types | `skill-laugh.openvoiceos.home`, `skill-ovos-weather.openvoiceos.*`, `*.openvoiceos.*` | Skill-ID-embedded dynamic types, skill-private |
| `mycroft.skill.loaded` (singular) | n/a | Test-only string. Production code uses `mycroft.skills.loaded` (plural, modeled) |
| `mycroft.schedule.update_event` | n/a | Typo in ovos-bus-client for `mycroft.scheduler.update_event` (modeled) |

---
[← Skill manager](skill-manager.md) · [Home](index.md)
