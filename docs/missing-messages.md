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
| Skill-specific private APIs | `async.chatgpt.fallback`, `hello.world` | Private APIs used only within a single skill, not reusable protocol |

| Category | Message type(s) | Reason |
|---|---|---|
| Skill-specific dynamic types | `skill-laugh.openvoiceos.home`, `skill-ovos-weather.openvoiceos.*`, `*.openvoiceos.*` | Skill-ID-embedded dynamic types, skill-private |

---
[← Skill manager](skill-manager.md) · [Home](index.md)
