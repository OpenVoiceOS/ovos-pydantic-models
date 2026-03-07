# Skill Manager Messages

Messages related to skill lifecycle management, settings, runtime installation, and session synchronization.

## System Readiness

| Message type | Class | Description |
|---|---|---|
| `mycroft.ready` | `MycroftReadyMessage` | All core services are up and ready |
| `mycroft.skills.is_ready` | `MycroftSkillsIsReadyMessage` | Query whether the skills service is ready |
| `mycroft.skills.is_ready.response` | `MycroftSkillsIsReadyResponseMessage` | Reply: `status: bool` |
| `mycroft.skills.ready` | `MycroftSkillsReadyMessage` | Skills service has finished loading |
| `mycroft.skills.initialized` | `MycroftSkillsInitializedMessage` | Skills service initialized (before training) |
| `mycroft.skills.error` | `MycroftSkillsErrorMessage` | Skills failed to load completely |

```python
from ovos_pydantic_models.core.skill_manager import (
    MycroftReadyMessage,
    MycroftSkillsIsReadyMessage, MycroftSkillsIsReadyReplyData, MycroftSkillsIsReadyResponseMessage,
    MycroftSkillsReadyMessage, MycroftSkillsInitializedMessage,
    MycroftSkillsErrorData, MycroftSkillsErrorMessage,
)

# Check if skills are ready
request = MycroftSkillsIsReadyMessage()
reply = MycroftSkillsIsReadyResponseMessage(
    data=MycroftSkillsIsReadyReplyData(status=True)
)

# Skills failed to fully load (e.g. some internet-only skills skipped)
error = MycroftSkillsErrorMessage(
    data=MycroftSkillsErrorData(
        internet_loaded=False,
        network_loaded=True,
        error="Some internet-only skills failed to load",
    )
)
```

**`MycroftSkillsErrorData`**

| Field | Type | Description |
|---|---|---|
| `internet_loaded` | `bool` | Internet-dependent skills were loaded |
| `network_loaded` | `bool` | Network-dependent skills were loaded |
| `error` | `str \| None` | Error description |

---

## Skill List

| Message type | Class | Description |
|---|---|---|
| `skillmanager.list` | `SkillManagerListMessage` | Request list of all loaded skills |
| `mycroft.skills.list` | `MycroftSkillsListMessage` | Reply: dict keyed by skill_id |

**`MycroftSkillsListData`** — open model, keys are skill IDs, values are dicts:

```python
# example data payload
{
    "skill-weather.mycroft": {"active": True, "id": "skill-weather.mycroft"},
    "skill-timer.mycroft": {"active": False, "id": "skill-timer.mycroft"},
}
```

---

## Skill Activation / Deactivation

| Message type | Class | Key field |
|---|---|---|
| `mycroft.skills.activate` | `MycroftSkillsActivateMessage` | `skill_id` |
| `mycroft.skills.deactivate` | `MycroftSkillsDeactivateMessage` | `skill_id` |
| `skillmanager.activate` | `SkillManagerActivateMessage` | `skill` (ID or `"all"`) |
| `skillmanager.activate.response` | `SkillManagerActivateResponseMessage` | optional error data |
| `skillmanager.deactivate` | `SkillManagerDeactivateMessage` | `skill` |
| `skillmanager.deactivate.response` | `SkillManagerDeactivateResponseMessage` | optional error data |
| `skillmanager.keep` | `SkillManagerKeepMessage` | `skill` (keep this, deactivate all others) |
| `skillmanager.keep.response` | `SkillManagerKeepResponseMessage` | optional error data |

---

## Intent Training

| Message type | Class | Description |
|---|---|---|
| `mycroft.skills.train` | `MycroftSkillsTrainMessage` | Request intent re-training |
| `mycroft.skills.trained` | `MycroftSkillsTrainedMessage` | Reply: `error \| None` |

---

## Skill Settings

```python
from ovos_pydantic_models.core.skill_settings import (
    SkillSettingsChangeData, SkillSettingsChangeMessage,
    SkillSettingsUpdatedData, SkillSettingsUpdatedMessage,
    OvosSkillsSettingsChangedData, OvosSkillsSettingsChangedMessage,
)
```

| Message type | Class | Description |
|---|---|---|
| `skill.settings.change` | `SkillSettingsChangeMessage` | Settings values have changed |
| `skill.settings.updated` | `SkillSettingsUpdatedMessage` | Settings have been persisted |
| `ovos.skills.settings_changed` | `OvosSkillsSettingsChangedMessage` | The skill's `settings.json` file changed on disk |

**`SkillSettingsChangeData`**

| Field | Type | Description |
|---|---|---|
| `skill_id` | `str` | Owning skill |
| `settings` | `dict` | New settings values |

```python
from ovos_pydantic_models.core.skill_settings import SkillSettingsChangeData, SkillSettingsChangeMessage

msg = SkillSettingsChangeMessage(
    data=SkillSettingsChangeData(
        skill_id="skill-weather.mycroft",
        settings={"units": "metric", "location": "London"},
    )
)
```

---

## Runtime Skill Installer

```python
from ovos_pydantic_models.core.skill_installer import (
    InstallError,
    OvosSkillsInstallData, OvosSkillsInstallMessage,
    OvosSkillsInstallCompleteMessage,
    OvosSkillsInstallFailedData, OvosSkillsInstallFailedMessage,
    OvosSkillsUninstallData, OvosSkillsUninstallMessage,
    OvosSkillsUninstallCompleteMessage,
    OvosSkillsUninstallFailedData, OvosSkillsUninstallFailedMessage,
    OvosPipInstallData, OvosPipInstallMessage,
    OvosPipInstallCompleteMessage,
    OvosPipInstallFailedData, OvosPipInstallFailedMessage,
    OvosPipUninstallData, OvosPipUninstallMessage,
    OvosPipUninstallCompleteMessage,
    OvosPipUninstallFailedData, OvosPipUninstallFailedMessage,
)
```

**`InstallError`** (str Enum)

| Value | String |
|---|---|
| `DISABLED` | `"pip disabled in mycroft.conf"` |
| `PIP_ERROR` | `"error in pip subprocess"` |
| `BAD_URL` | `"skill url validation failed"` |
| `NO_PKGS` | `"no packages to install"` |

### Skill Install / Uninstall

| Message type | Class | Key field |
|---|---|---|
| `ovos.skills.install` | `OvosSkillsInstallMessage` | `url: str` (GitHub URL) |
| `ovos.skills.install.complete` | `OvosSkillsInstallCompleteMessage` | — |
| `ovos.skills.install.failed` | `OvosSkillsInstallFailedMessage` | `error: InstallError` |
| `ovos.skills.uninstall` | `OvosSkillsUninstallMessage` | `skill_id \| package_name` |
| `ovos.skills.uninstall.complete` | `OvosSkillsUninstallCompleteMessage` | — |
| `ovos.skills.uninstall.failed` | `OvosSkillsUninstallFailedMessage` | `error: InstallError \| str` |

### Pip Install / Uninstall

| Message type | Class | Key field |
|---|---|---|
| `ovos.pip.install` | `OvosPipInstallMessage` | `packages: list[str]` |
| `ovos.pip.install.complete` | `OvosPipInstallCompleteMessage` | — |
| `ovos.pip.install.failed` | `OvosPipInstallFailedMessage` | `error: InstallError` |
| `ovos.pip.uninstall` | `OvosPipUninstallMessage` | `packages: list[str]` |
| `ovos.pip.uninstall.complete` | `OvosPipUninstallCompleteMessage` | — |
| `ovos.pip.uninstall.failed` | `OvosPipUninstallFailedMessage` | `error: InstallError` |

```python
from ovos_pydantic_models.core.skill_installer import OvosPipInstallData, OvosPipInstallMessage

msg = OvosPipInstallMessage(
    data=OvosPipInstallData(packages=["requests", "beautifulsoup4"])
)
```

---

## Session Synchronization

```python
from ovos_pydantic_models.core.session import (
    OvosSessionSyncMessage,
    OvosSessionUpdateDefaultData, OvosSessionUpdateDefaultMessage,
)
```

| Message type | Class | Description |
|---|---|---|
| `ovos.session.sync` | `OvosSessionSyncMessage` | Request the current default session |
| `ovos.session.update_default` | `OvosSessionUpdateDefaultMessage` | Broadcast updated default session |

`OvosSessionUpdateDefaultData` is a `Session` subclass — the full session model is the data payload.

```python
from ovos_pydantic_models.session import Session
from ovos_pydantic_models.core.session import OvosSessionUpdateDefaultData, OvosSessionUpdateDefaultMessage

session = Session(session_id="default", lang="es-es")
msg = OvosSessionUpdateDefaultMessage(data=OvosSessionUpdateDefaultData(**session.model_dump()))
```

See [message-base.md](message-base.md) for the full `Session` field reference.
