from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


class OvosPhalConfigurationProviderGetData(BaseModel):
    """Payload for requesting configuration from the PHAL configuration provider."""
    group: Optional[str] = Field(None, description="Configuration group to retrieve; None for all groups.")


class OvosPhalConfigurationProviderGetMessage(OpenVoiceOSMessage):
    """Request configuration data from the PHAL configuration provider plugin.

    **Deprecated** — `ovos-PHAL-plugin-configuration-provider` is archived.
    These messages are documented for historical reference only.

    Emitted by skills, GUI components, or other PHAL plugins that need to read
    hardware or platform-specific settings managed by a PHAL configuration
    provider. If `group` is None the entire configuration is returned; otherwise
    only the named group is returned. The provider replies with
    `ovos.phal.configuration.provider.get.response`.
    """
    message_type: str = "ovos.phal.configuration.provider.get"
    data: OvosPhalConfigurationProviderGetData


class OvosPhalConfigurationProviderGetResponseData(BaseModel):
    """Configuration data returned by the PHAL configuration provider."""
    config: Dict[str, Any] = Field(default_factory=dict, description="Retrieved configuration dict.")


class OvosPhalConfigurationProviderGetResponseMessage(OpenVoiceOSMessage):
    """Return configuration data from the PHAL configuration provider.

    Emitted by the PHAL configuration provider in response to
    `ovos.phal.configuration.provider.get`. The `config` dict contains the
    requested group's key-value pairs, or the full configuration if no group
    was specified. Consumers use this to initialize hardware-specific defaults.
    """
    message_type: str = "ovos.phal.configuration.provider.get.response"
    data: OvosPhalConfigurationProviderGetResponseData


class OvosPhalConfigurationProviderListGroupsMessage(OpenVoiceOSMessage):
    """Query the PHAL configuration provider for its available configuration groups.

    Emitted by GUI settings panels or management tools that need to enumerate
    which platform-specific configuration groups exist before presenting them
    to the user. The provider replies with
    `ovos.phal.configuration.provider.list.groups.response`.
    """
    message_type: str = "ovos.phal.configuration.provider.list.groups"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalConfigurationProviderListGroupsResponseData(BaseModel):
    """List of available configuration group names from the PHAL configuration provider."""
    groups: List[str] = Field(default_factory=list, description="List of available configuration group names.")


class OvosPhalConfigurationProviderListGroupsResponseMessage(OpenVoiceOSMessage):
    """Return the list of available configuration groups from the PHAL configuration provider.

    Emitted by the PHAL configuration provider in response to
    `ovos.phal.configuration.provider.list.groups`. Each group name in `groups`
    can subsequently be requested individually via
    `ovos.phal.configuration.provider.get` with the `group` field set.
    """
    message_type: str = "ovos.phal.configuration.provider.list.groups.response"
    data: OvosPhalConfigurationProviderListGroupsResponseData


class OvosPhalConfigurationProviderSetData(BaseModel):
    """Payload for writing configuration values to the PHAL configuration provider."""
    group: str = Field(..., description="Configuration group to update.")
    config: Dict[str, Any] = Field(..., description="Key-value pairs to set in the group.")


class OvosPhalConfigurationProviderSetMessage(OpenVoiceOSMessage):
    """Write configuration values to the PHAL configuration provider plugin.

    Emitted by GUI settings panels, onboarding flows, or admin tools when
    hardware-specific settings need to be persisted. The `group` identifies
    which configuration section to update; `config` contains the key-value
    pairs to write. The PHAL configuration provider stores these persistently
    and applies them to the relevant hardware subsystem immediately or on
    next restart depending on the provider implementation.
    """
    message_type: str = "ovos.phal.configuration.provider.set"
    data: OvosPhalConfigurationProviderSetData
