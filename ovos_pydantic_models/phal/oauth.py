from typing import Dict, Any

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


class OauthPingMessage(OpenVoiceOSMessage):
    """Check whether the OVOS OAuth PHAL plugin is running and responsive.

    Emitted by skills that require OAuth authentication before attempting to
    register or start an OAuth flow. The OAuth PHAL plugin replies with
    `oauth.pong` (if implemented) or the skill may simply proceed if no
    error is returned within a timeout. Use this to guard against calling
    OAuth messages when the plugin is not loaded on the current platform.
    """
    message_type: str = "oauth.ping"
    data: Dict[str, Any] = Field(default_factory=dict)


class OauthRegisterData(BaseModel):
    """Payload for registering an OAuth application with the PHAL OAuth plugin."""
    skill_id: str = Field(..., description="Skill registering for OAuth.")
    client_id: str = Field(..., description="OAuth client ID.")
    client_secret: str = Field(..., description="OAuth client secret.")
    auth_endpoint: str = Field(..., description="Authorization endpoint URL.")
    token_endpoint: str = Field(..., description="Token endpoint URL.")
    callback_url: str = Field(..., description="OAuth callback/redirect URL.")


class OauthRegisterMessage(OpenVoiceOSMessage):
    """Register an OAuth application with the OVOS OAuth PHAL plugin.

    Emitted by a skill during `initialize()` to declare its OAuth credentials
    to the PHAL OAuth plugin. The plugin stores `client_id`, `client_secret`,
    and endpoint URLs associated with `skill_id`. Registration is a prerequisite
    before calling `oauth.start` or `oauth.get`. Skills typically call this once
    at startup so the OAuth plugin knows how to handle authorization requests
    for that skill.

    The `callback_url` must be reachable from the browser during the
    authorization flow; the OAuth plugin typically hosts a local redirect
    server accessible via the device's IP.
    """
    message_type: str = "oauth.register"
    data: OauthRegisterData


class OauthGetData(BaseModel):
    """Payload for requesting stored OAuth tokens for a specific skill."""
    skill_id: str = Field(..., description="Skill ID whose OAuth token to retrieve.")


class OauthGetMessage(OpenVoiceOSMessage):
    """Retrieve stored OAuth access/refresh tokens for a skill.

    Emitted by a skill when it needs to make an authenticated API call and
    requires its current access token. The OAuth PHAL plugin looks up the
    tokens stored for `skill_id` and returns them. If no token exists or the
    token has expired, the skill should initiate `oauth.start` to begin a
    new authorization flow, or `oauth.refresh` to attempt a token refresh
    without user interaction.
    """
    message_type: str = "oauth.get"
    data: OauthGetData


class OauthGetAppHostInfoMessage(OpenVoiceOSMessage):
    """Query the OAuth PHAL plugin for its callback server host information.

    Emitted by skills or the settings GUI when constructing the OAuth
    redirect/callback URL. The OAuth plugin runs a local HTTP server to
    receive the authorization code after the user authenticates in a browser.
    The response includes the IP address and port of that local server, which
    must be incorporated into the `callback_url` registered with the OAuth
    provider. Replies with `oauth.get.app.host.info.response` containing
    `host` and `port` fields.
    """
    message_type: str = "oauth.get.app.host.info"
    data: Dict[str, Any] = Field(default_factory=dict)


class OauthStartData(BaseModel):
    """Payload for initiating the OAuth authorization flow for a specific skill."""
    skill_id: str = Field(..., description="Skill ID to start the OAuth flow for.")


class OauthStartMessage(OpenVoiceOSMessage):
    """Initiate the OAuth user authorization flow for a skill.

    Emitted by a skill when it needs the user to grant OAuth permission —
    for example, on first use of a skill that integrates with a third-party
    service. The OAuth PHAL plugin opens the authorization URL in the device's
    browser (or presents it via QR code on headless devices) and waits for
    the callback. On success, it stores the resulting tokens and they become
    available via `oauth.get`.

    On headless/screen-less devices without a browser, use `oauth.generate.qr.request`
    instead so the user can scan the authorization URL with a phone.
    """
    message_type: str = "oauth.start"
    data: OauthStartData


class OauthRefreshData(BaseModel):
    """Payload for refreshing an expired OAuth access token for a specific skill."""
    skill_id: str = Field(..., description="Skill ID whose token to refresh.")


class OauthRefreshMessage(OpenVoiceOSMessage):
    """Refresh an expired OAuth access token using the stored refresh token.

    Emitted by a skill (or the OAuth PHAL plugin's token expiry monitor) when
    an API call fails with a 401 Unauthorized response indicating the access
    token has expired. The OAuth plugin uses the stored `refresh_token` to
    obtain a new `access_token` from the `token_endpoint` without requiring
    user interaction. If the refresh token is also expired or revoked, the
    skill must restart the full authorization flow via `oauth.start`.
    """
    message_type: str = "oauth.refresh"
    data: OauthRefreshData


class OauthGenerateQrRequestData(BaseModel):
    """Payload for requesting a QR code for OAuth authorization."""
    skill_id: str = Field(..., description="Skill ID requesting QR code generation.")


class OauthGenerateQrRequestMessage(OpenVoiceOSMessage):
    """Request a QR code image representing the OAuth authorization URL for a skill.

    Emitted by a skill on headless or screen-less devices where opening a
    browser directly is not possible. The OAuth PHAL plugin generates a QR
    code from the authorization URL and emits
    `ovos.shell.oauth.display.qr.code` for the GUI shell to display. The
    user scans the QR code with a phone to complete authorization, after
    which the plugin receives the callback and stores the resulting tokens.
    """
    message_type: str = "oauth.generate.qr.request"
    data: OauthGenerateQrRequestData


class OvosShellOauthDisplayQrCodeData(BaseModel):
    """Payload carrying a QR code for displaying the OAuth authorization URL."""
    qr_code: str = Field(..., description="Base64-encoded QR code image or URL.")


class OvosShellOauthDisplayQrCodeMessage(OpenVoiceOSMessage):
    """Tell the GUI shell to display an OAuth authorization QR code on screen.

    Emitted by the OAuth PHAL plugin in response to `oauth.generate.qr.request`.
    The OVOS shell GUI receives this message and renders the QR code image
    full-screen so the user can scan it with a mobile device to complete the
    OAuth authorization flow. After the user scans and authorizes, the OAuth
    plugin receives the redirect callback and stores the tokens.
    """
    message_type: str = "ovos.shell.oauth.display.qr.code"
    data: OvosShellOauthDisplayQrCodeData


class OvosShellOauthRegisterCredentialsData(BaseModel):
    """Payload for storing OAuth credentials returned via the shell GUI OAuth flow."""
    skill_id: str = Field(..., description="Skill ID to register credentials for.")
    credentials: Dict[str, Any] = Field(..., description="OAuth credential dict (access_token, refresh_token, etc.).")


class OvosShellOauthRegisterCredentialsMessage(OpenVoiceOSMessage):
    """Store OAuth credentials received through the OVOS shell GUI OAuth flow.

    Emitted by the OVOS shell GUI (or a companion app) after the user has
    completed the OAuth authorization flow via a QR code or in-browser flow
    orchestrated by the shell rather than the PHAL plugin directly. The OAuth
    PHAL plugin receives this message and persists the `credentials` dict
    (containing `access_token`, `refresh_token`, expiry, and scope) for the
    specified `skill_id`. After this, the skill can retrieve tokens via
    `oauth.get` as normal.
    """
    message_type: str = "ovos.shell.oauth.register.credentials"
    data: OvosShellOauthRegisterCredentialsData
