# SPDX-License-Identifier: BSD-3-Clause
"""The Django app, and the one thing it does at boot.

``ready()`` validates the consumer's configuration and nothing else. Checking
here rather than at first use is the point: validation deferred to whenever a
meter first ticks means a misconfigured instance starts cleanly, runs, and
then fails somewhere that says nothing about the setting that was wrong.
"""

from django.apps import AppConfig


class SurvivalConfig(AppConfig):
    """Refuses the boot when the consumer's stage settings are unusable."""

    name = "evennia_survival"
    label = "evennia_survival"
    verbose_name = "Evennia Survival"

    def ready(self):
        from evennia_survival.config import check_settings

        check_settings()
