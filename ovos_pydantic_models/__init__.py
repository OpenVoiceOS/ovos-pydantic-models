# Base message types
from ovos_pydantic_models.version import __version__
from ovos_pydantic_models.message import OpenVoiceOSMessage, MessageContext
from ovos_pydantic_models.session import (Session, UtteranceState, IntentContextManager, IntentContextManagerFrame,
                                          ContextEntity, SessionHandler, ResponseMode)

# Audio — playback / TTS
from ovos_pydantic_models.audio.playback import (
    SpeakData, SpeakMessage,
    SpeakB64AudioData, SpeakB64AudioMessage, SpeakB64AudioReplyData, SpeakB64AudioResponseMessage,
    MycroftAudioQueueData, MycroftAudioQueueMessage,
    MycroftAudioPlaySoundData, MycroftAudioPlaySoundMessage, MycroftAudioPlaySoundResponseMessage,
    MycroftSpeechStopMessage, MycroftAudioSpeakStatusMessage,
    MycroftAudioIsSpeakingData, MycroftAudioIsSpeakingMessage,
)

# Audio — legacy audio service
from ovos_pydantic_models.audio.audioservice import (
    AudioServicePlayData, AudioServicePlayMessage,
    AudioServiceQueueData, AudioServiceQueueMessage,
    AudioServicePauseMessage, AudioServiceResumeMessage,
    AudioServiceNextMessage, AudioServicePrevMessage, AudioServiceStopMessage,
    AudioPlayingTrackData, AudioPlayingTrackMessage,
    AudioQueueEndMessage,
    AudioServiceTrackInfoReplyData, AudioServiceTrackInfoReplyMessage,
    AudioServiceListBackendsMessage, AudioServiceListBackendsReplyData, AudioServiceListBackendsResponseMessage,
    AudioServiceGetTrackLengthMessage, AudioServiceGetTrackLengthReplyData, AudioServiceGetTrackLengthResponseMessage,
    AudioServiceGetTrackPositionMessage, AudioServiceGetTrackPositionReplyData, AudioServiceGetTrackPositionResponseMessage,
    AudioServiceSetTrackPositionData, AudioServiceSetTrackPositionMessage,
    AudioServiceSeekForwardData, AudioServiceSeekForwardMessage,
    AudioServiceSeekBackwardData, AudioServiceSeekBackwardMessage,
)

# Audio — OCP audio layer
from ovos_pydantic_models.audio.ocp import (
    OcpMediaState, MediaState,  # MediaState is a backward-compat alias for OcpMediaState
    OvosCommonPlayMediaStateData, OvosCommonPlayMediaStateMessage,
    OvosCommonPlayCorkMessage, OvosCommonPlayDuckMessage,
    OvosCommonPlayUncorkMessage, OvosCommonPlayUnduckMessage,
)

# Audio — OPM (plugin manager queries for TTS/audio)
from ovos_pydantic_models.audio.opm import (
    OvosLanguagesTtsMessage, OvosLanguagesTtsReplyData, OvosLanguagesTtsResponseMessage,
    OpmTtsQueryMessage, OpmTtsQueryReplyData, OpmTtsQueryResponseMessage,
    OpmAudioQueryMessage, OpmAudioQueryReplyData, OpmAudioQueryResponseMessage,
    OpmG2pQueryMessage, OpmG2pQueryReplyData, OpmG2pQueryResponseMessage,
)

# Audio — recognizer loop audio output events
from ovos_pydantic_models.audio.recognizer_loop import (
    RecognizerLoopAudioOutputStartMessage,
    RecognizerLoopAudioOutputEndMessage,
)

# Listener — speech recognition
from ovos_pydantic_models.listener.recognizer_loop import (
    ListeningState,
    RecognizerLoopUtteranceData, RecognizerLoopUtteranceMessage,
    RecognizerLoopWakeWordData,
    RecognizerLoopWakeWordMessage, RecognizerLoopHotwordMessage,
    RecognizerLoopStopwordMessage, RecognizerLoopWakeupWordMessage,
    RecognizerLoopB64TranscribeData, RecognizerLoopB64TranscribeMessage,
    RecognizerLoopB64TranscribeReplyData, RecognizerLoopB64TranscribeResponseMessage,
    RecognizerLoopB64AudioData, RecognizerLoopB64AudioMessage, RecognizerLoopB64AudioResponseMessage,
    RecognizerLoopRecordStopMessage, RecognizerLoopRecordBeginMessage, RecognizerLoopRecordEndMessage,
    RecognizerLoopStateSetData, RecognizerLoopStateSetMessage,
    RecognizerLoopStateGetMessage, RecognizerLoopStateGetReplyData, RecognizerLoopStateResponseMessage,
    RecognizerLoopSpeechRecognitionUnknownMessage,
    RecognizerLoopSleepMessage, RecognizerLoopWakeUpMessage,
    MycroftAwokenMessage,
    MycroftMicMuteMessage, MycroftMicUnmuteMessage, MycroftMicMuteToggleMessage,
    MycroftMicGetStatusMessage, MycroftMicGetStatusReplyData, MycroftMicGetStatusResponseMessage,
    MycroftMicListenMessage,
)

# Listener — OPM plugin queries
from ovos_pydantic_models.listener.opm import (
    OvosLanguagesSttMessage, OvosLanguagesSttReplyData, OvosLanguagesSttResponseMessage,
    OpmSttQueryMessage, OpmSttQueryReplyData, OpmSttQueryResponseMessage,
    OpmWwQueryMessage, OpmWwQueryReplyData, OpmWwQueryResponseMessage,
    OpmVadQueryMessage, OpmVadQueryReplyData, OpmVadQueryResponseMessage,
)

# Intents — core (context, intent get/reply, utterance handled)
from ovos_pydantic_models.intents.core import (
    IntentServicePipelinesReloadMessage,
    OvosUtteranceCancelledMessage,
    OvosUtteranceHandledMessage,
    CompleteIntentFailureData, CompleteIntentFailureMessage,
    AddContextData, AddContextMessage,
    RemoveContextData, RemoveContextMessage,
    ClearContextMessage,
    IntentServiceIntentGetData, IntentServiceIntentGetMessage,
    IntentServiceIntentReplyIntentData, IntentServiceIntentReplyData, IntentServiceIntentReplyMessage,
    SkillActivateData, SkillActivateMessage,
    SkillDeactivateData, SkillDeactivateMessage,
)

# Intents — INTENT-4 registration wire
from ovos_pydantic_models.intents.registration import (
    IntentMethod, VocabularyDescriptor,
    OvosIntentRegisterKeywordData, OvosIntentRegisterKeywordMessage,
    OvosIntentRegisterTemplateData, OvosIntentRegisterTemplateMessage,
    OvosEntityRegisterData, OvosEntityRegisterMessage,
    OvosIntentDeregisterData, OvosIntentDeregisterMessage,
    OvosIntentEnableMessage, OvosIntentDisableMessage,
    OvosEntityDeregisterData, OvosEntityDeregisterMessage,
    OvosSkillDeregisterData, OvosSkillDeregisterMessage,
    OvosIntentListData, OvosIntentListMessage,
    IntentManifestEntry, OvosIntentListResponseData, OvosIntentListResponseMessage,
    OvosIntentDescribeData, OvosIntentDescribeMessage,
    IntentDefinitionEntry, OvosIntentDescribeResponseData, OvosIntentDescribeResponseMessage,
)

# Intents — PIPELINE-1 utterance lifecycle
from ovos_pydantic_models.intents.pipeline import (
    OvosUtteranceHandleData, OvosUtteranceHandleMessage,
    OvosIntentMatchedData, OvosIntentMatchedMessage,
    OvosIntentUnmatchedData, OvosIntentUnmatchedMessage,
    IntentHandlerLifecycleData,
    OvosIntentHandlerStartMessage, OvosIntentHandlerCompleteMessage,
    IntentHandlerErrorData, OvosIntentHandlerErrorMessage,
)

# Intents — converse protocol
from ovos_pydantic_models.intents.converse import (
    IntentHandlerMatch,
    ConverseMode, ConverseActivationMode,
    IntentServiceSkillsActivateData, IntentServiceSkillsActivateMessage,
    IntentServiceSkillsActivatedData, IntentServiceSkillsActivatedMessage,
    IntentServiceActiveSkillsGetMessage,
    IntentServiceActiveSkillsReplyData, IntentServiceActiveSkillsReplyMessage,
    SkillConverseGetResponseEnableData, SkillConverseGetResponseEnableMessage,
    SkillConverseGetResponseDisableData, SkillConverseGetResponseDisableMessage,
    ConverseSkillData, ConverseSkillMessage,
    SkillConverseRequestData, SkillConverseRequestMessage,
    IntentServiceSkillsDeactivateData, IntentServiceSkillsDeactivateMessage,
    IntentServiceSkillsDeactivatedData, IntentServiceSkillsDeactivatedMessage,
    SkillConversePongData, SkillConversePongMessage,
    SkillConversePingData, SkillConversePingMessage,
    SkillConverseGetResponseMatchData,
    SkillConverseResponseData, SkillConverseResponseMessage,
    SkillConverseKilledData, SkillConverseKilledMessage,
    ConversationalIntentData, ConversationalIntentMessage,
    ConverseErrorCode,
    OvosConversePingData, OvosConversePingMessage,
    OvosConversePongData, OvosConversePongMessage,
)

# Intents — fallback protocol
from ovos_pydantic_models.intents.fallbacks import (
    FallbackMode,
    OvosSkillsFallbackRegisterData, OvosSkillsFallbackRegisterMessage,
    OvosSkillsFallbackDeregisterData, OvosSkillsFallbackDeregisterMessage,
    OvosSkillsFallbackPingData, OvosSkillsFallbackPingMessage,
    OvosSkillsFallbackPongData, OvosSkillsFallbackPongMessage,
    OvosSkillsFallbackRequestData, OvosSkillsFallbackRequestMessage,
    OvosSkillsFallbackStartMessage,
    OvosSkillsFallbackResponseData, OvosSkillsFallbackResponseMessage,
    OvosSkillsFallbackKilledData, OvosSkillsFallbackKilledMessage,
    OvosSkillsFallbackForceTimeoutData, OvosSkillsFallbackForceTimeoutMessage,
    OvosFallbackPingData, OvosFallbackPingMessage,
    OvosFallbackPongData, OvosFallbackPongMessage,
)

# Intents — stop protocol
from ovos_pydantic_models.intents.stop import (
    StopGlobalMessage, StopSkillData, StopSkillMessage,
    MycroftStopMessage,
    SkillStopPingData, SkillStopPingMessage,
    SkillStopPongData, SkillStopPongMessage,
    SkillStopRequestMessage,
    SkillStopResponseData, SkillStopResponseMessage,
    MycroftSkillsAbortQuestionData, MycroftSkillsAbortQuestionMessage,
    MycroftSkillsAbortExecutionData, MycroftSkillsAbortExecutionMessage,
    OvosSkillsConverseForceTimeoutData, OvosSkillsConverseForceTimeoutMessage,
    MycroftAudioSpeechStopData, MycroftAudioSpeechStopMessage,
    MycroftStopHandledData, MycroftStopHandledMessage,
)

# Skills — OCP (Common Play)
from ovos_pydantic_models.skills.ocp import (
    MediaType, PlaybackType, PlaybackMode, PlayerState, LoopState, TrackState,
    MediaState as OcpPlaybackState,  # str Enum — distinct from audio/ocp.py OcpMediaState (IntEnum)
    MatchConfidence,
    BaseMediaEntry, MediaEntry, PluginStream, Playlist,
    OvosCommonPlayQueryData, OvosCommonPlayQueryMessage,
    OvosCommonPlayFeaturedTracksPlayData, OvosCommonPlayFeaturedTracksPlayMessage,
    OvosCommonPlaySkillsGetMessage,
    OvosCommonPlaySkillPlayData as OvosCommonPlaySkillPlayRequestData,
    OvosCommonPlaySkillPlayMessage as OvosCommonPlaySkillPlayRequestMessage,
    OvosCommonPlaySkillPauseData, OvosCommonPlaySkillPauseMessage,
    OvosCommonPlaySkillResumeData, OvosCommonPlaySkillResumeMessage,
    OvosCommonPlaySkillNextData, OvosCommonPlaySkillNextMessage,
    OvosCommonPlaySkillPreviousData, OvosCommonPlaySkillPreviousMessage,
    OvosCommonPlaySkillStopData, OvosCommonPlaySkillStopMessage,
    OvosCommonPlaySearchStopMessage,
    OvosCommonPlayAnnounceData, OvosCommonPlayAnnounceMessage,
    OvosCommonPlayPlayData, OvosCommonPlayPlayMessage,
    OvosCommonPlayPlayerStateData, OvosCommonPlayPlayerStateMessage,
    OvosCommonPlaySkillSearchStartData, OvosCommonPlaySkillSearchStartMessage,
    OvosCommonPlayQueryResponseData, OvosCommonPlayQueryResponseMessage,
    OvosCommonPlaySkillSearchEndData, OvosCommonPlaySkillSearchEndMessage,
    OvosCommonPlayRegisterKeywordData, OvosCommonPlayRegisterKeywordMessage,
    OvosCommonPlayDeregisterKeywordData, OvosCommonPlayDeregisterKeywordMessage,
    OvosCommonPlaySkillsDetachData, OvosCommonPlaySkillsDetachMessage,
    OvosCommonPlayPauseMessage, OvosCommonPlayResumeMessage,
    OvosCommonPlayStopMessage,
    OvosCommonPlayStopResponseData, OvosCommonPlayStopResponseMessage,
    OvosCommonPlayNextMessage, OvosCommonPlayPreviousMessage,
    OvosCommonPlaySeekData, OvosCommonPlaySeekMessage,
    OvosCommonPlaySetTrackPositionData, OvosCommonPlaySetTrackPositionMessage,
    OvosCommonPlayGetTrackPositionMessage, OvosCommonPlayGetTrackLengthMessage,
    OvosCommonPlayPlaybackTimeData, OvosCommonPlayPlaybackTimeMessage,
    OvosCommonPlayPlayPauseMessage,
    OvosCommonPlaySimplePlayData, OvosCommonPlaySimplePlayMessage,
    OvosCommonPlayHomeMessage, OvosCommonPlayPingMessage,
    OvosCommonPlayRepeatSetMessage, OvosCommonPlayRepeatUnsetMessage, OvosCommonPlayRepeatToggleMessage,
    OvosCommonPlayShuffleSetMessage, OvosCommonPlayShuffleUnsetMessage, OvosCommonPlayShuffleToggleMessage,
    OvosCommonPlayPlaylistQueueData, OvosCommonPlayPlaylistQueueMessage,
    OvosCommonPlayPlaylistSetData, OvosCommonPlayPlaylistSetMessage,
    OvosCommonPlayPlaylistClearMessage, OvosCommonPlayPlaylistPlayMessage,
    OvosCommonPlayTrackInfoMessage,
    OvosCommonPlayTrackInfoResponseData, OvosCommonPlayTrackInfoResponseMessage,
    OvosCommonPlayTrackStateData, OvosCommonPlayTrackStateMessage,
    OvosCommonPlayStatusMessage,
    OvosCommonPlayStatusResponseData, OvosCommonPlayStatusResponseMessage,
    OvosCommonPlayPlayerStatusData, OvosCommonPlayPlayerStatusMessage,
    OvosCommonPlayListBackendsMessage,
    OvosCommonPlayLikeMessage, OvosCommonPlayUnlikeMessage, OvosCommonPlayLikedTracksPlayMessage,
    OvosCommonPlaySearchData, OvosCommonPlaySearchMessage,
    OvosCommonPlayPlaySearchData, OvosCommonPlayPlaySearchMessage,
    OvosCommonPlaySearchStartData, OvosCommonPlaySearchStartMessage,
    OvosCommonPlaySearchEndMessage,
    OvosCommonPlaySearchPopulateData, OvosCommonPlaySearchPopulateMessage,
    OvosCommonPlaySearchPlayMessage,
    OvosCommonPlayGuiEnableAppTimeoutMessage,
    OvosCommonPlayGuiSetAppTimeoutData, OvosCommonPlayGuiSetAppTimeoutMessage,
    OvosCommonPlayGuiTimeoutModeData, OvosCommonPlayGuiTimeoutModeMessage,
    OvosCommonPlaySeiGetMessage,
    OvosCommonPlaySeiGetResponseData, OvosCommonPlaySeiGetResponseMessage,
)

# Skills — game
from ovos_pydantic_models.skills.game import (
    OvosCommonPlaySkillPlayData, OvosCommonPlaySkillPlayMessage,
    SkillGameCommandData, SkillGameCommandMessage,
)

# Skills — common query
from ovos_pydantic_models.skills.common_query import (
    CQSMatchLevel,
    QuestionQueryData, QuestionQueryMessage,
    QuestionActionData, QuestionActionMessage,
    OvosCommonQueryPingMessage,
    OvosCommonQueryPongData, OvosCommonQueryPongMessage,
    OvosCommonQueryPongLegacyData, OvosCommonQueryPongLegacyMessage,
    QuestionQueryResponseData, QuestionQueryResponseMessage,
)

# Core — skill manager
from ovos_pydantic_models.core.skill_manager import (
    MycroftReadyMessage,
    MycroftSkillsIsReadyMessage, MycroftSkillsIsReadyReplyData, MycroftSkillsIsReadyResponseMessage,
    MycroftSkillsReadyMessage,
    MycroftSkillsActivateData, MycroftSkillsActivateMessage,
    MycroftSkillsDeactivateData, MycroftSkillsDeactivateMessage,
    SkillManagerListMessage,
    MycroftSkillsListData, MycroftSkillsListMessage,
    SkillManagerDeactivateData, SkillManagerDeactivateMessage, SkillManagerDeactivateResponseMessage,
    SkillManagerKeepData, SkillManagerKeepMessage, SkillManagerKeepResponseMessage,
    SkillManagerActivateData, SkillManagerActivateMessage, SkillManagerActivateResponseMessage,
    MycroftSkillsErrorData, MycroftSkillsErrorMessage,
    MycroftSkillsInitializedMessage,
    MycroftSkillsTrainMessage, MycroftSkillsTrainedData, MycroftSkillsTrainedMessage,
    MycroftSkillEnableIntentData, MycroftSkillEnableIntentMessage,
    MycroftSkillDisableIntentData, MycroftSkillDisableIntentMessage,
    MycroftSkillSetCrossContextData, MycroftSkillSetCrossContextMessage,
    MycroftSkillRemoveCrossContextData, MycroftSkillRemoveCrossContextMessage,
    MycroftSkillHandlerStartData, MycroftSkillHandlerStartMessage,
    MycroftSkillHandlerCompleteData, MycroftSkillHandlerCompleteMessage,
    MycroftSkillsShutdownData, MycroftSkillsShutdownMessage,
    MycroftSkillsLoadingFailureData, MycroftSkillsLoadingFailureMessage,
    MycroftSkillsSettingsChangedData, MycroftSkillsSettingsChangedMessage,
    DetachSkillData, DetachSkillMessage,
    DetachIntentData, DetachIntentMessage,
)

# Core — session management
from ovos_pydantic_models.core.session import (
    OvosSessionSyncMessage,
    OvosSessionUpdateDefaultData, OvosSessionUpdateDefaultMessage,
)

# Core — skill settings
from ovos_pydantic_models.core.skill_settings import (
    SkillSettingsChangeData, SkillSettingsChangeMessage,
    SkillSettingsUpdatedData, SkillSettingsUpdatedMessage,
    OvosSkillsSettingsChangedData, OvosSkillsSettingsChangedMessage,
)

# Core — skill installer
from ovos_pydantic_models.core.skill_installer import (
    InstallError,
    OvosSkillsInstallData, OvosSkillsInstallMessage,
    OvosSkillsInstallFailedData, OvosSkillsInstallFailedMessage,
    OvosSkillsInstallCompleteMessage,
    OvosSkillsUninstallData, OvosSkillsUninstallMessage,
    OvosSkillsUninstallFailedData, OvosSkillsUninstallFailedMessage,
    OvosSkillsUninstallCompleteMessage,
    OvosPipInstallData, OvosPipInstallMessage,
    OvosPipInstallFailedData, OvosPipInstallFailedMessage,
    OvosPipInstallCompleteMessage,
    OvosPipUninstallData, OvosPipUninstallMessage,
    OvosPipUninstallFailedData, OvosPipUninstallFailedMessage,
    OvosPipUninstallCompleteMessage,
)

# Audio — OVOS audio service (ovos.audio.service.* namespace)
from ovos_pydantic_models.audio.audioservice import (
    OvosAudioServicePlayMessage,
    OvosAudioServiceQueueMessage,
    OvosAudioServicePauseMessage, OvosAudioServiceResumeMessage,
    OvosAudioServiceNextMessage, OvosAudioServicePrevMessage, OvosAudioServiceStopMessage,
    OvosAudioServiceSeekForwardMessage, OvosAudioServiceSeekBackwardMessage,
    OvosAudioServiceSetTrackPositionMessage,
    OvosAudioServiceGetTrackLengthMessage, OvosAudioServiceGetTrackPositionMessage,
    OvosAudioServiceTrackInfoMessage, OvosAudioServiceListBackendsMessage,
)

# Audio — video service
from ovos_pydantic_models.audio.video_service import (
    OvosVideoServicePlayData, OvosVideoServicePlayMessage,
    OvosVideoServiceStopMessage, OvosVideoServicePauseMessage, OvosVideoServiceResumeMessage,
    OvosVideoServiceNextMessage, OvosVideoServicePrevMessage,
    OvosVideoServiceSeekForwardData, OvosVideoServiceSeekForwardMessage,
    OvosVideoServiceSeekBackwardData, OvosVideoServiceSeekBackwardMessage,
    OvosVideoServiceSetTrackPositionData, OvosVideoServiceSetTrackPositionMessage,
    OvosVideoServiceGetTrackPositionMessage, OvosVideoServiceGetTrackLengthMessage,
    OvosVideoServiceTrackInfoMessage, OvosVideoServiceListBackendsMessage,
)

# Audio — web service
from ovos_pydantic_models.audio.web_service import (
    OvosWebServicePlayData, OvosWebServicePlayMessage,
    OvosWebServiceStopMessage, OvosWebServicePauseMessage, OvosWebServiceResumeMessage,
    OvosWebServiceNextMessage, OvosWebServicePrevMessage,
    OvosWebServiceSeekForwardData, OvosWebServiceSeekForwardMessage,
    OvosWebServiceSeekBackwardData, OvosWebServiceSeekBackwardMessage,
    OvosWebServiceSetTrackPositionData, OvosWebServiceSetTrackPositionMessage,
    OvosWebServiceGetTrackPositionMessage, OvosWebServiceGetTrackLengthMessage,
    OvosWebServiceTrackInfoMessage, OvosWebServiceListBackendsMessage,
)

# Core — configuration
from ovos_pydantic_models.core.configuration import (
    ConfigurationPatchData, ConfigurationPatchMessage,
    ConfigurationUpdatedMessage,
    ConfigurationPatchClearMessage,
    ConfigurationCacheClearMessage,
    OvosLanguageOutputForceData, OvosLanguageOutputForceMessage,
    OvosLanguageOutputResetMessage,
    OvosIpGeoUpdateData, OvosIpGeoUpdateMessage,
)

# Core — scheduler
from ovos_pydantic_models.core.scheduler import (
    SchedulerScheduleEventData, SchedulerScheduleEventMessage,
    SchedulerRemoveEventData, SchedulerRemoveEventMessage,
    SchedulerUpdateEventData, SchedulerUpdateEventMessage,
    SchedulerGetEventData, SchedulerGetEventMessage,
    SchedulerListEventsMessage,
)

# GUI — homescreen
from ovos_pydantic_models.gui.homescreen import (
    HomescreenManagerAddData, HomescreenManagerAddMessage,
    HomescreenManagerRemoveData, HomescreenManagerRemoveMessage,
    HomescreenManagerListMessage,
    HomescreenManagerListReplyData, HomescreenManagerListResponseMessage,
    HomescreenManagerGetActiveMessage,
    HomescreenManagerGetActiveReplyData, HomescreenManagerGetActiveResponseMessage,
    HomescreenManagerSetActiveData, HomescreenManagerSetActiveMessage,
    HomescreenManagerDisableActiveMessage, HomescreenManagerShowActiveMessage,
    HomescreenManagerReloadListMessage,
    HomescreenManagerActivateDisplayData, HomescreenManagerActivateDisplayMessage,
    HomescreenRegisterExamplesData, HomescreenRegisterExamplesMessage,
    HomescreenManagerAppData, HomescreenManagerAppMessage,
    HomescreenRegisterAppData, HomescreenRegisterAppMessage,
    HomescreenWallpaperSetData, HomescreenWallpaperSetMessage,
    HomescreenMetadataGetMessage,
    MycroftDeviceShowIdleMessage, MycroftDeviceSettingsMessage,
    MycroftMark2RegisterIdleData, MycroftMark2RegisterIdleMessage,
    MycroftMark2ResetIdleData, MycroftMark2ResetIdleMessage,
    MycroftMark2CollectIdleMessage,
    OvosHomescreenDisplayedMessage,
    OvosHomescreenMainViewCurrentIndexSetData, OvosHomescreenMainViewCurrentIndexSetMessage,
)

# GUI — namespace / page control
from ovos_pydantic_models.gui.namespace import (
    GuiPageShowMessage, GuiPageDeleteMessage, GuiPageDeleteAllMessage,
    GuiValueSetMessage, GuiEventSendMessage, GuiClearNamespaceMessage,
    GuiNamespaceDisplayedData, GuiNamespaceDisplayedMessage,
    GuiNamespaceRemovedData, GuiNamespaceRemovedMessage,
    GuiPageGainedFocusData, GuiPageGainedFocusMessage,
    GuiPageInteractionData, GuiPageInteractionMessage,
    GuiStatusRequestMessage,
)


# GUI — media player service
from ovos_pydantic_models.gui.media_player import (
    GuiPlayerMediaPlayData, GuiPlayerMediaPlayMessage,
    GuiPlayerMediaPauseMessage, GuiPlayerMediaResumeMessage, GuiPlayerMediaStopMessage,
    GuiPlayerMediaSetMetaData, GuiPlayerMediaSetMetaMessage,
    GuiPlayerMediaGetMetaMessage,
    GuiPlayerMediaSyncStatusData, GuiPlayerMediaSyncStatusMessage,
    GuiPlayerMediaCurrentStatusData, GuiPlayerMediaCurrentStatusMessage,
    GuiPlayerMediaGetNextMessage, GuiPlayerMediaGetPreviousMessage,
    GuiPlayerMediaGetRepeatMessage, GuiPlayerMediaGetShuffleMessage,
)

# GUI — notifications
from ovos_pydantic_models.gui.notifications import (
    OvosNotificationApiSetData, OvosNotificationApiSetMessage,
    OvosNotificationApiSetControlledData, OvosNotificationApiSetControlledMessage,
    OvosNotificationApiRemoveControlledData, OvosNotificationApiRemoveControlledMessage,
    OvosNotificationApiRequestStorageModelMessage,
    OvosNotificationApiStorageClearMessage,
    OvosNotificationApiStorageClearItemData, OvosNotificationApiStorageClearItemMessage,
    OvosNotificationApiPopClearMessage, OvosNotificationApiPopClearDeleteMessage,
    OvosNotificationUpdateCounterData, OvosNotificationUpdateCounterMessage,
    OvosNotificationUpdateStorageModelData, OvosNotificationUpdateStorageModelMessage,
    OvosNotificationControlledTypeShowData, OvosNotificationControlledTypeShowMessage,
    OvosNotificationControlledTypeRemoveData, OvosNotificationControlledTypeRemoveMessage,
    OvosNotificationShowData, OvosNotificationShowMessage,
    OvosNotificationDataMessage,
)

# GUI — widgets
from ovos_pydantic_models.gui.widgets import (
    OvosWidgetsDisplayData, OvosWidgetsDisplayMessage,
    OvosWidgetsRemoveData, OvosWidgetsRemoveMessage,
    OvosWidgetsUpdateData, OvosWidgetsUpdateMessage,
    OvosWidgetsTimerDisplayData, OvosWidgetsTimerDisplayMessage,
    OvosWidgetsTimerUpdateData, OvosWidgetsTimerUpdateMessage,
    OvosWidgetsTimerRemoveData, OvosWidgetsTimerRemoveMessage,
    OvosWidgetsAlarmDisplayData, OvosWidgetsAlarmDisplayMessage,
    OvosWidgetsAlarmUpdateData, OvosWidgetsAlarmUpdateMessage,
    OvosWidgetsAlarmRemoveData, OvosWidgetsAlarmRemoveMessage,
    OvosWidgetsMediaDisplayData, OvosWidgetsMediaDisplayMessage,
    OvosWidgetsMediaUpdateData, OvosWidgetsMediaUpdateMessage,
    OvosWidgetsMediaRemoveMessage,
)

# PHAL — connectivity
from ovos_pydantic_models.phal.connectivity import (
    OvosPhalInternetCheckMessage,
    OvosPhalInternetCheckReplyData, OvosPhalInternetCheckResponseMessage,
    MycroftNetworkDisconnectedMessage, MycroftInternetDisconnectedMessage,
    MycroftNetworkConnectedMessage, MycroftInternetConnectedMessage,
    MycroftInternetStateData, MycroftInternetStateMessage,
    MycroftInternetIsReadyMessage,
    MycroftNetworkStateData, MycroftNetworkStateMessage,
    MycroftPairedMessage, MycroftNotPairedMessage,
    MycroftReadyCheckMessage,
    OvosPairingProcessCompletedMessage,
    OvosPairingSetBackendData, OvosPairingSetBackendMessage,
)

# PHAL — system
from ovos_pydantic_models.phal.system import (
    SystemRebootMessage, SystemRebootStartMessage,
    SystemShutdownMessage, SystemShutdownStartMessage,
    SystemFactoryResetMessage, SystemFactoryResetPingMessage,
    SystemFactoryResetRegisterData, SystemFactoryResetRegisterMessage,
    SystemFactoryResetPhalMessage, SystemFactoryResetPhalCompleteMessage,
    SystemSshEnableMessage, SystemSshEnabledMessage,
    SystemSshDisableMessage, SystemSshDisabledMessage,
    SystemSshStatusData, SystemSshStatusMessage,
    SystemMycroftServiceRestartMessage, SystemMycroftServiceRestartStartMessage,
    SystemClockSyncedMessage,
    SystemConfigureLanguageData, SystemConfigureLanguageMessage,
    SystemConfigureLanguageCompleteData, SystemConfigureLanguageCompleteMessage,
    SystemDisplayHomescreenMessage, SystemWifiSetupMessage,
)

# PHAL — network manager
from ovos_pydantic_models.phal.network_manager import (
    OvosPhalNmScanMessage,
    OvosPhalNmScanCompleteData, OvosPhalNmScanCompleteMessage,
    OvosPhalNmConnectData, OvosPhalNmConnectMessage,
    OvosPhalNmConnectOpenNetworkData, OvosPhalNmConnectOpenNetworkMessage,
    OvosPhalNmConnectionSuccessfulData, OvosPhalNmConnectionSuccessfulMessage,
    OvosPhalNmConnectionFailureData, OvosPhalNmConnectionFailureMessage,
    OvosPhalNmDisconnectMessage, OvosPhalNmDisconnectionSuccessfulMessage,
    OvosPhalNmDisconnectionFailureData, OvosPhalNmDisconnectionFailureMessage,
    OvosPhalNmForgetData, OvosPhalNmForgetMessage,
    OvosPhalNmForgetSuccessfulData, OvosPhalNmForgetSuccessfulMessage,
    OvosPhalNmForgetFailureData, OvosPhalNmForgetFailureMessage,
    OvosPhalNmIsConnectedMessage, OvosPhalNmIsNotConnectedMessage,
    OvosPhalNmGetConnectedMessage, OvosPhalNmReconnectMessage,
    OvosPhalNmSetBackendData, OvosPhalNmSetBackendMessage,
    OvosPhalNmBackendNotSupportedMessage,
)

# PHAL — WiFi setup
from ovos_pydantic_models.phal.wifi_setup import (
    OvosPhalWifiPluginAliveMessage,
    OvosPhalWifiPluginRegisterClientData, OvosPhalWifiPluginRegisterClientMessage,
    OvosPhalWifiPluginClientRegisteredData, OvosPhalWifiPluginClientRegisteredMessage,
    OvosPhalWifiPluginClientRegistrationFailureData, OvosPhalWifiPluginClientRegistrationFailureMessage,
    OvosPhalWifiPluginDeregisterClientData, OvosPhalWifiPluginDeregisterClientMessage,
    OvosPhalWifiPluginClientDeregisteredData, OvosPhalWifiPluginClientDeregisteredMessage,
    OvosPhalWifiPluginSetActiveClientData, OvosPhalWifiPluginSetActiveClientMessage,
    OvosPhalWifiPluginRemoveActiveClientData, OvosPhalWifiPluginRemoveActiveClientMessage,
    OvosPhalWifiPluginGetRegisteredClientsMessage,
    OvosPhalWifiPluginRegisteredClientsData, OvosPhalWifiPluginRegisteredClientsMessage,
    OvosPhalWifiPluginUserActivatedMessage, OvosPhalWifiPluginSetupLaunchedMessage,
    OvosPhalWifiPluginSetupFailedData, OvosPhalWifiPluginSetupFailedMessage,
    OvosPhalWifiPluginStopSetupEventMessage, OvosPhalWifiPluginSkipSetupMessage,
    OvosPhalWifiPluginFullyOfflineMessage,
    OvosPhalWifiPluginStatusData, OvosPhalWifiPluginStatusMessage,
    OvosPhalWifiPluginClientSelectData, OvosPhalWifiPluginClientSelectMessage,
    OvosPhalWifiPluginClientSelectPageRemovedMessage,
    OvosPhalWifiPluginClientSetupFailureData, OvosPhalWifiPluginClientSetupFailureMessage,
    OvosWifiSetupCompletedMessage,
    OvosPhalWifiScanMessage,
    OvosPhalWifiInfoData, OvosPhalWifiInfoMessage,
)

# PHAL — brightness
from ovos_pydantic_models.phal.brightness import (
    PhalBrightnessControlGetMessage,
    PhalBrightnessControlGetResponseData, PhalBrightnessControlGetResponseMessage,
    PhalBrightnessControlSetData, PhalBrightnessControlSetMessage,
    PhalBrightnessControlSyncMessage,
    PhalBrightnessControlAutoDimUpdateData, PhalBrightnessControlAutoDimUpdateMessage,
    PhalBrightnessControlAutoNightModeEnabledMessage,
)

# PHAL — wallpaper
from ovos_pydantic_models.phal.wallpaper import (
    OvosWallpaperManagerRegisterProviderData, OvosWallpaperManagerRegisterProviderMessage,
    OvosWallpaperManagerSetActiveProviderData, OvosWallpaperManagerSetActiveProviderMessage,
    OvosWallpaperManagerGetActiveProviderMessage, OvosWallpaperManagerGetRegisteredProvidersMessage,
    OvosWallpaperManagerSetWallpaperData, OvosWallpaperManagerSetWallpaperMessage,
    OvosWallpaperManagerGetWallpaperMessage, OvosWallpaperManagerChangeWallpaperMessage,
    OvosWallpaperManagerGetCollectionMessage,
    OvosWallpaperManagerGetCollectionFromProviderData, OvosWallpaperManagerGetCollectionFromProviderMessage,
    OvosWallpaperManagerUpdateCollectionData, OvosWallpaperManagerUpdateCollectionMessage,
    OvosWallpaperManagerCollectCollectionResponseData, OvosWallpaperManagerCollectCollectionResponseMessage,
    OvosWallpaperManagerGetAutoRotationMessage,
    OvosWallpaperManagerEnableAutoRotationMessage, OvosWallpaperManagerDisableAutoRotationMessage,
    OvosWallpaperManagerAutoRotationEnabledMessage, OvosWallpaperManagerAutoRotationDisabledMessage,
    OvosWallpaperManagerLoadedMessage,
)

# PHAL — camera
from ovos_pydantic_models.phal.camera import (
    OvosPhalCameraPingMessage, OvosPhalCameraPongMessage,
    OvosPhalCameraOpenMessage, OvosPhalCameraCloseMessage, OvosPhalCameraGetMessage,
)

# PHAL — sensors
from ovos_pydantic_models.phal.sensors import (
    OvosPhalSensorData, OvosPhalSensorMessage,
    OvosPhalBinarySensorData, OvosPhalBinarySensorMessage,
)

# PHAL — configuration provider
from ovos_pydantic_models.phal.configuration_provider import (
    OvosPhalConfigurationProviderGetData, OvosPhalConfigurationProviderGetMessage,
    OvosPhalConfigurationProviderGetResponseData, OvosPhalConfigurationProviderGetResponseMessage,
    OvosPhalConfigurationProviderListGroupsMessage,
    OvosPhalConfigurationProviderListGroupsResponseData, OvosPhalConfigurationProviderListGroupsResponseMessage,
    OvosPhalConfigurationProviderSetData, OvosPhalConfigurationProviderSetMessage,
)

# PHAL — OAuth
from ovos_pydantic_models.phal.oauth import (
    OauthPingMessage,
    OauthRegisterData, OauthRegisterMessage,
    OauthGetData, OauthGetMessage,
    OauthGetAppHostInfoMessage,
    OauthStartData, OauthStartMessage,
    OauthRefreshData, OauthRefreshMessage,
    OauthGenerateQrRequestData, OauthGenerateQrRequestMessage,
    OvosShellOauthDisplayQrCodeData, OvosShellOauthDisplayQrCodeMessage,
    OvosShellOauthRegisterCredentialsData, OvosShellOauthRegisterCredentialsMessage,
)

# PHAL — Mark1 enclosure
from ovos_pydantic_models.phal.enclosure import (
    EnclosureEyesOnMessage, EnclosureEyesOffMessage,
    EnclosureEyesColorData, EnclosureEyesColorMessage,
    EnclosureEyesBlinkData, EnclosureEyesBlinkMessage,
    EnclosureEyesSpinMessage,
    EnclosureEyesTimedSpinData, EnclosureEyesTimedSpinMessage,
    EnclosureEyesNarrowMessage,
    EnclosureEyesLookData, EnclosureEyesLookMessage,
    EnclosureEyesLevelData, EnclosureEyesLevelMessage,
    EnclosureEyesVolumeData, EnclosureEyesVolumeMessage,
    EnclosureEyesFillData, EnclosureEyesFillMessage,
    EnclosureEyesResetMessage,
    EnclosureEyesSetPixelData, EnclosureEyesSetPixelMessage,
    EnclosureMouthResetMessage, EnclosureMouthTalkMessage,
    EnclosureMouthThinkMessage, EnclosureMouthListenMessage, EnclosureMouthSmileMessage,
    EnclosureMouthVisemeData, EnclosureMouthVisemeMessage,
    EnclosureMouthVisemeListData, EnclosureMouthVisemeListMessage,
    EnclosureMouthDisplayData, EnclosureMouthDisplayMessage,
    EnclosureMouthTextData, EnclosureMouthTextMessage,
    EnclosureMouthEventsActivateMessage, EnclosureMouthEventsDeactivateMessage,
    EnclosureResetMessage, EnclosureStartedMessage, EnclosureNotifyNoInternetMessage,
    EnclosureSystemResetMessage, EnclosureSystemMuteMessage, EnclosureSystemUnmuteMessage,
)

# PHAL — volume
from ovos_pydantic_models.phal.volume import (
    MycroftVolumeGetMessage, MycroftVolumeGetReplyData, MycroftVolumeGetResponseMessage,
    VolumeSetPercentData, VolumeSetPercentMessage,
    MycroftVolumeIncreaseDecreaseData, MycroftVolumeIncreaseMessage, MycroftVolumeDecreaseMessage,
    MycroftVolumeSetData, MycroftVolumeSetMessage,
    MycroftVolumeUnmuteMessage, MycroftVolumeMuteMessage,
)
