from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


class OvosWallpaperManagerRegisterProviderData(BaseModel):
    """Payload for registering a wallpaper source plugin with the wallpaper manager."""
    provider_name: str = Field(..., description="Unique name for the wallpaper provider.")


class OvosWallpaperManagerRegisterProviderMessage(OpenVoiceOSMessage):
    """Register a wallpaper source plugin with the OVOS wallpaper manager.

    Emitted by a wallpaper provider PHAL plugin during startup to announce
    its availability. The wallpaper manager records the provider under
    `provider_name` and can subsequently request its collection via
    `ovos.wallpaper.manager.get.collection.from.provider`. Multiple providers
    can coexist (e.g. a local file provider, an online image provider, a
    user-upload provider); the active one is selected via
    `ovos.wallpaper.manager.set.active.provider`.
    """
    message_type: str = "ovos.wallpaper.manager.register.provider"
    data: OvosWallpaperManagerRegisterProviderData


class OvosWallpaperManagerSetActiveProviderData(BaseModel):
    """Payload for selecting which registered wallpaper provider should be active."""
    provider_name: str = Field(..., description="Name of the provider to make active.")


class OvosWallpaperManagerSetActiveProviderMessage(OpenVoiceOSMessage):
    """Set the active wallpaper source provider in the OVOS wallpaper manager.

    Emitted by the settings GUI when the user selects a different wallpaper
    source. The wallpaper manager switches to sourcing wallpapers from the
    named provider. If the provider is unknown (not yet registered), the
    manager may queue the request until the provider registers. The current
    wallpaper collection is refreshed from the new provider.
    """
    message_type: str = "ovos.wallpaper.manager.set.active.provider"
    data: OvosWallpaperManagerSetActiveProviderData


class OvosWallpaperManagerGetActiveProviderMessage(OpenVoiceOSMessage):
    """Query the OVOS wallpaper manager for the currently active wallpaper provider.

    Emitted by the settings GUI or other components that need to know which
    wallpaper source is currently in use. The wallpaper manager replies with
    a response message containing the active provider's name.
    """
    message_type: str = "ovos.wallpaper.manager.get.active.provider"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosWallpaperManagerGetRegisteredProvidersMessage(OpenVoiceOSMessage):
    """Query the OVOS wallpaper manager for all registered wallpaper providers.

    Emitted by the settings GUI to populate a provider selection list. The
    wallpaper manager replies with a list of all provider names that have
    registered via `ovos.wallpaper.manager.register.provider`. The GUI uses
    this to present the user with available wallpaper source options.
    """
    message_type: str = "ovos.wallpaper.manager.get.registered.providers"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosWallpaperManagerSetWallpaperData(BaseModel):
    """Payload for setting a specific wallpaper image on the homescreen."""
    url: str = Field(..., description="URL or file path of the wallpaper image.")


class OvosWallpaperManagerSetWallpaperMessage(OpenVoiceOSMessage):
    """Set a specific image as the homescreen wallpaper.

    Emitted by the settings GUI or a skill when the user selects a particular
    wallpaper image. The wallpaper manager applies the image at `url` (which
    may be a local file path or remote URL) to the homescreen background
    immediately. If a remote URL is provided, the manager downloads and caches
    the image before applying it.
    """
    message_type: str = "ovos.wallpaper.manager.set.wallpaper"
    data: OvosWallpaperManagerSetWallpaperData


class OvosWallpaperManagerGetWallpaperMessage(OpenVoiceOSMessage):
    """Query the OVOS wallpaper manager for the currently active wallpaper.

    Emitted by the settings GUI or homescreen components that need to know
    which wallpaper is currently displayed. The wallpaper manager replies
    with the URL or path of the current wallpaper image.
    """
    message_type: str = "ovos.wallpaper.manager.get.wallpaper"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosWallpaperManagerChangeWallpaperMessage(OpenVoiceOSMessage):
    """Advance to the next wallpaper in the current provider's collection.

    Emitted by the settings GUI (e.g. a "next wallpaper" button), a scheduled
    auto-rotation timer, or a skill handling 'change wallpaper' voice commands.
    The wallpaper manager picks the next image from the active provider's
    collection and applies it as the new homescreen background. Wraps around
    to the first image when the end of the collection is reached.
    """
    message_type: str = "ovos.wallpaper.manager.change.wallpaper"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosWallpaperManagerGetCollectionMessage(OpenVoiceOSMessage):
    """Query the OVOS wallpaper manager for the complete wallpaper collection.

    Emitted by the settings GUI to display a thumbnail grid of all available
    wallpapers from all registered providers. The wallpaper manager aggregates
    and returns the merged collection from all providers.
    """
    message_type: str = "ovos.wallpaper.manager.get.collection"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosWallpaperManagerGetCollectionFromProviderData(BaseModel):
    """Payload for requesting the wallpaper collection from a specific provider."""
    provider_name: str = Field(..., description="Provider to fetch the collection from.")


class OvosWallpaperManagerGetCollectionFromProviderMessage(OpenVoiceOSMessage):
    """Request the wallpaper image collection from a specific registered provider.

    Emitted by the wallpaper manager internally when it needs to refresh the
    image list from a particular provider. The targeted provider plugin
    replies with `ovos.wallpaper.manager.collect.collection.response`
    containing its current list of wallpaper URLs or file paths. This is
    used to populate the manager's internal collection cache.
    """
    message_type: str = "ovos.wallpaper.manager.get.collection.from.provider"
    data: OvosWallpaperManagerGetCollectionFromProviderData


class OvosWallpaperManagerUpdateCollectionData(BaseModel):
    """Payload for a provider to push an updated wallpaper list to the manager."""
    collection: List[str] = Field(default_factory=list, description="List of wallpaper URLs/paths.")


class OvosWallpaperManagerUpdateCollectionMessage(OpenVoiceOSMessage):
    """Push an updated wallpaper collection from a provider to the wallpaper manager.

    Emitted by a wallpaper provider plugin when its collection changes —
    for example, after downloading new images, detecting new files in a
    watched directory, or syncing with a remote source. The wallpaper manager
    updates its internal cache with the new `collection` list and makes the
    new images available for display and rotation.
    """
    message_type: str = "ovos.wallpaper.manager.update.collection"
    data: OvosWallpaperManagerUpdateCollectionData


class OvosWallpaperManagerCollectCollectionResponseData(BaseModel):
    """Payload returning a wallpaper provider's image collection to the manager."""
    provider_name: str = Field(..., description="Provider that returned the collection.")
    collection: List[str] = Field(default_factory=list, description="List of wallpaper URLs.")


class OvosWallpaperManagerCollectCollectionResponseMessage(OpenVoiceOSMessage):
    """Return a wallpaper provider's image collection to the wallpaper manager.

    Emitted by a wallpaper provider plugin in response to
    `ovos.wallpaper.manager.get.collection.from.provider`. Contains the
    provider's current list of available wallpaper URLs or file paths.
    The wallpaper manager merges this into its collection cache and uses it
    for display and rotation.
    """
    message_type: str = "ovos.wallpaper.manager.collect.collection.response"
    data: OvosWallpaperManagerCollectCollectionResponseData


class OvosWallpaperManagerGetAutoRotationMessage(OpenVoiceOSMessage):
    """Query whether the OVOS wallpaper manager's auto-rotation is enabled.

    Emitted by the settings GUI to display the current state of the
    auto-rotation toggle. The wallpaper manager replies with a response
    message indicating whether auto-rotation is currently active.
    """
    message_type: str = "ovos.wallpaper.manager.get.auto.rotation"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosWallpaperManagerEnableAutoRotationMessage(OpenVoiceOSMessage):
    """Enable automatic wallpaper rotation in the OVOS wallpaper manager.

    Emitted by the settings GUI or a skill handling 'enable wallpaper rotation'
    voice commands. When enabled, the wallpaper manager periodically advances
    to the next image in the collection (interval configured in PHAL plugin
    settings). Confirms with `ovos.wallpaper.manager.auto.rotation.enabled`.
    """
    message_type: str = "ovos.wallpaper.manager.enable.auto.rotation"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosWallpaperManagerDisableAutoRotationMessage(OpenVoiceOSMessage):
    """Disable automatic wallpaper rotation in the OVOS wallpaper manager.

    Emitted by the settings GUI or a skill handling 'disable wallpaper rotation'
    voice commands. When disabled, the current wallpaper stays fixed until the
    user manually changes it. Confirms with
    `ovos.wallpaper.manager.auto.rotation.disabled`.
    """
    message_type: str = "ovos.wallpaper.manager.disable.auto.rotation"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosWallpaperManagerAutoRotationEnabledMessage(OpenVoiceOSMessage):
    """Signal that automatic wallpaper rotation has been enabled.

    Emitted by the wallpaper manager after successfully enabling auto-rotation
    in response to `ovos.wallpaper.manager.enable.auto.rotation`. The settings
    GUI updates its toggle to reflect the new state.
    """
    message_type: str = "ovos.wallpaper.manager.auto.rotation.enabled"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosWallpaperManagerAutoRotationDisabledMessage(OpenVoiceOSMessage):
    """Signal that automatic wallpaper rotation has been disabled.

    Emitted by the wallpaper manager after successfully disabling auto-rotation
    in response to `ovos.wallpaper.manager.disable.auto.rotation`. The settings
    GUI updates its toggle to reflect the new state.
    """
    message_type: str = "ovos.wallpaper.manager.auto.rotation.disabled"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosWallpaperManagerLoadedMessage(OpenVoiceOSMessage):
    """Signal that the OVOS wallpaper manager is fully initialized and ready.

    Emitted by the wallpaper manager PHAL plugin after completing startup —
    loading its configuration, discovering registered providers, and applying
    the initial wallpaper. Homescreen GUI components and wallpaper providers
    can subscribe to this message to know when it is safe to register
    themselves or query the manager's state.
    """
    message_type: str = "ovos.wallpaper.manager.loaded"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalWallpaperManagerProviderRegisteredMessage(OpenVoiceOSMessage):
    """Signal that a wallpaper provider plugin has successfully registered.

    Emitted by the wallpaper manager PHAL plugin after a provider calls
    `ovos.wallpaper.manager.register.provider` and the manager has verified
    and stored the registration. The provider can now receive
    `ovos.wallpaper.manager.get.collection.from.provider` requests.
    """
    message_type: str = "ovos.phal.wallpaper.manager.provider.registered"
    data: Dict[str, Any] = Field(default_factory=dict)
