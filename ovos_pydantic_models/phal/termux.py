from typing import Dict, Any, List

from pydantic import BaseModel, Field

from ovos_pydantic_models.message import OpenVoiceOSMessage


# --- Termux PHAL Plugin Messages ---
# These messages are handled by ovos-PHAL-plugin-termux, which bridges
# OVOS to Android hardware features via the Termux:API app.


class OvosPhalPhoneCallData(BaseModel):
    """Payload to initiate a phone call via Termux."""
    number: str = Field(..., description="Phone number to call.")


class OvosPhalPhoneCallMessage(OpenVoiceOSMessage):
    """Request the Termux PHAL plugin to initiate a phone call.

    Emitted by skills that handle 'call [contact/number]' voice commands
    on Android. The Termux PHAL plugin delegates to `termux-telephony-call`.
    Only valid when running inside a Termux environment on Android.
    """
    message_type: str = "ovos.phal.phone.call"
    data: OvosPhalPhoneCallData


class OvosPhalPhoneContactsMessage(OpenVoiceOSMessage):
    """Request the full phone contact list from Termux.

    Emitted by skills that need to resolve a contact name to a phone number
    before calling or texting. The Termux PHAL plugin queries
    `termux-contact-list` and replies via `message.response()` with a list
    of contact objects. Only valid inside Termux on Android.
    """
    message_type: str = "ovos.phal.phone.contacts"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalPhoneSmsListMessage(OpenVoiceOSMessage):
    """Request the SMS inbox from Termux.

    Emitted by skills that read messages aloud or summarize recent texts.
    The Termux PHAL plugin queries `termux-sms-list` and replies via
    `message.response()` with a list of SMS message objects.
    Only valid inside Termux on Android.
    """
    message_type: str = "ovos.phal.phone.sms.list"
    data: Dict[str, Any] = Field(default_factory=dict)


class OvosPhalPhoneSmsSendData(BaseModel):
    """Payload to send an SMS message via Termux."""
    number: str = Field(..., description="Recipient phone number.")
    message: str = Field(..., description="SMS message body text.")


class OvosPhalPhoneSmsSendMessage(OpenVoiceOSMessage):
    """Request the Termux PHAL plugin to send an SMS message.

    Emitted by skills that handle 'send a text to [contact]' voice commands
    on Android. The Termux PHAL plugin delegates to `termux-sms-send`.
    Only valid when running inside a Termux environment on Android.
    """
    message_type: str = "ovos.phal.phone.sms.send"
    data: OvosPhalPhoneSmsSendData
