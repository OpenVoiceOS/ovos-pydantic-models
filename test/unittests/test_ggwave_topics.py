"""The ggwave models must declare the topics the plugin actually uses
(ovos-audio-transformer-plugin-ggwave emits/binds ovos.ggwave.*)."""
import unittest

from ovos_pydantic_models.phal.ggwave import (OvosGgwaveEnableMessage,
                                              OvosGgwaveDisableMessage,
                                              GgwaveEnabledMessage,
                                              GgwaveDisabledMessage)


class TestGgwaveTopics(unittest.TestCase):
    def test_topics_match_plugin(self):
        self.assertEqual(OvosGgwaveEnableMessage().message_type, "ovos.ggwave.enable")
        self.assertEqual(OvosGgwaveDisableMessage().message_type, "ovos.ggwave.disable")
        self.assertEqual(GgwaveEnabledMessage().message_type, "ovos.ggwave.enabled")
        self.assertEqual(GgwaveDisabledMessage().message_type, "ovos.ggwave.disabled")
