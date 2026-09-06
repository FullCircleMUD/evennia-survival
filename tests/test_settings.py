# SPDX-License-Identifier: BSD-3-Clause
"""Minimal Django settings for evennia-survival unit tests.

Imports Evennia's defaults, adds the library to INSTALLED_APPS, and runs a
single in-memory sqlite database. No gamedir required.
"""
import os
import sys
import tempfile

import evennia

# Evennia 6.0.0+ ships migrations that import ``typeclasses.objects``
# (a gamedir module). Put Evennia's game_template on sys.path so the
# import resolves without requiring a real gamedir.
_game_template = os.path.join(os.path.dirname(evennia.__file__), "game_template")
if _game_template not in sys.path:
    sys.path.insert(0, _game_template)

from evennia.settings_default import *  # noqa: F401, F403, E402

# Evennia path bits — point at safe scratch locations so settings_default's
# path-derived defaults resolve without needing a real gamedir.
GAME_DIR = tempfile.gettempdir()
LOG_DIR = os.path.join(tempfile.gettempdir(), "evennia_survival_test_logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Library under test
INSTALLED_APPS = list(INSTALLED_APPS) + [  # noqa: F405
    "evennia_survival",
]

# One database. The library owns no tables — the meters are character state,
# which belongs to the consumer's game database.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "TEST": {"NAME": "file:evennia_survival_test_default?mode=memory&cache=shared"},
    },
}

# The stages for each meter. Required — the library refuses to boot without
# them, so the suite declares them as any configured instance would. They point
# at `tests/stage_stubs.py`, which imports nothing but the library: `ready()`
# resolves these during `django.setup()`, while the app registry is still being
# built. The library does not distinguish the two meters, so one stub serves
# both.
SURVIVAL_HUNGER_STAGES = "tests.stage_stubs.HungerStageStub"
SURVIVAL_THIRST_STAGES = "tests.stage_stubs.HungerStageStub"

# The two clocks, in seconds. Required for the same reason as the stages: the
# library declines to pick a cadence on a game's behalf.
SURVIVAL_METER_INTERVAL = 1200
SURVIVAL_REGEN_INTERVAL = 20

# Required Django bits
SECRET_KEY = "test-only-secret"
TEST_ENVIRONMENT = True
ROOT_URLCONF = "tests.urls"
