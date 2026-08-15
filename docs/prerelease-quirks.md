# Pre-release quirks

Behavior changes since the last stable release, newest first. This file is
reset at each stable release.

## 0.2.2a1

- `phal/ggwave.py` confirmation models now declare the topics the ggwave
  audio transformer plugin actually emits: `ovos.ggwave.enabled` and
  `ovos.ggwave.disabled` (previously the unprefixed `ggwave.enabled` /
  `ggwave.disabled`, which matched nothing on the bus). Anything validating
  against the old constants was validating a topic that never fires.
