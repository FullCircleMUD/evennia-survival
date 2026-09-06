# SPDX-License-Identifier: BSD-3-Clause
"""Unit tests for evennia-survival. Run via ``python runtests.py``.

Every test carries its case ID from docs/test-plan.md as its docstring, so
the coverage trail reads in both directions.
"""

from unittest import TestCase

import evennia_survival
from evennia_survival.log import survival_log
from evennia_survival.stages import SurvivalStage


class HungerStageStub(SurvivalStage):
    """A consumer's stage enum, as the library expects to receive one.

    Values are consecutive and rise as the character gets better fed, which
    is the convention the library documents and cannot enforce. Every member
    is declared the same way — a value and both message strings.
    """

    STARVING = (1, "You are starving.", "$You() $conj(look) close to collapse.")
    FAMISHED = (2, "You are famished.", "$You() $conj(look) badly underfed.")
    HUNGRY = (3, "You are hungry.", "$You() $conj(look) hungry.")
    PECKISH = (4, "You could eat.", "$You() $conj(eye) the stew pot.")
    FULL = (5, "You are full.", "$You() $conj(look) well fed.")


class ScaffoldTests(TestCase):
    """SC — the library is installed and the runner reaches it."""

    def test_sc_01_the_package_is_importable_and_versioned(self):
        """SC-01"""
        self.assertTrue(evennia_survival.__version__)

    def test_sc_02_the_log_shim_is_a_no_op_outside_evennia(self):
        """SC-02"""
        self.assertIsNone(survival_log("scaffold check"))


class SurvivalStageTests(TestCase):
    """ST — the stage base class."""

    def test_st_01_a_member_carries_its_value_and_both_messages(self):
        """ST-01"""
        stage = HungerStageStub.HUNGRY

        self.assertEqual(stage.value, 3)
        self.assertEqual(stage.first_person, "You are hungry.")
        self.assertEqual(stage.third_person, "$You() $conj(look) hungry.")

    def test_st_02_a_member_missing_its_messages_is_refused(self):
        """ST-02"""
        with self.assertRaises(TypeError):

            class BareStageStub(SurvivalStage):
                FULL = 5

    def test_st_03_members_compare_in_value_order(self):
        """ST-03"""
        self.assertLess(HungerStageStub.STARVING, HungerStageStub.HUNGRY)
        self.assertGreater(HungerStageStub.FULL, HungerStageStub.PECKISH)
        self.assertLessEqual(HungerStageStub.FAMISHED, HungerStageStub.FAMISHED)

    def test_st_04_shifting_returns_the_member_that_many_values_away(self):
        """ST-04"""
        self.assertIs(HungerStageStub.HUNGRY.shifted(-1), HungerStageStub.FAMISHED)
        self.assertIs(HungerStageStub.HUNGRY.shifted(2), HungerStageStub.FULL)

    def test_st_05_shifting_past_the_lowest_value_clamps(self):
        """ST-05"""
        self.assertIs(HungerStageStub.FAMISHED.shifted(-5), HungerStageStub.STARVING)

    def test_st_06_shifting_past_the_highest_value_clamps(self):
        """ST-06"""
        self.assertIs(HungerStageStub.PECKISH.shifted(9), HungerStageStub.FULL)
